# app.py
import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from langcache import LangCache
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.DEBUG) 
app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")  # serves index.html at /
@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse("index.html")   # index.html sits next to app.py
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
lc = LangCache(
    server_url=f"https://{os.getenv('LANGCACHE_HOST')}",
    cache_id=os.getenv("LANGCACHE_CACHE_ID"),
    api_key=os.getenv("LANGCACHE_API_KEY"),
)


class ChatIn(BaseModel):
    prompt: str
    scope: str | None = None

@app.post("/chat")
def chat(inp: ChatIn):
    try:
        # 1) search cache
        search_res = lc.search(
            prompt=inp.prompt,
            similarity_threshold=0.9,
            attributes={"scope": inp.scope} if inp.scope else None,
        )
        # debug
        print("[langcache.search] type:", type(search_res))
        print("search_res fields:", dir(search_res))
        print("raw search_res:", search_res)

        # adapt to whatever property exists
        entries = None
        if hasattr(search_res, "results"):
            entries = search_res.results
        elif hasattr(search_res, "entries"):
            entries = search_res.entries
        elif hasattr(search_res, "data"):
            entries = search_res.data
        else:
            entries = []

        if entries:
            # pick first entry and its response
            entry = entries[0]
            text = getattr(entry, "response", None) or getattr(entry, "text", None) or ""
            if text:
                return {"cached": True, "text": text}

        # 2) cache miss → call LLM
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": inp.prompt}],
            temperature=0.3,
        )
        text = resp.choices[0].message.content or ""

        # 3) write-back
        lc.set(
            prompt=inp.prompt,
            response=text,
            attributes={"scope": inp.scope} if inp.scope else None,
        )
        return {"cached": False, "text": text}

    except Exception as e:
        print("Error in /chat:", e, flush=True)
        raise HTTPException(status_code=500, detail=str(e))
