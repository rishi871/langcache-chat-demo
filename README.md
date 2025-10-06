# 🧠 LangCache Chatbot Demo (FastAPI + Redis LangCache)

A minimal **FastAPI** chatbot demo that integrates **Redis LangCache** — a semantic cache for LLMs.  
It stores and retrieves answers to similar prompts, reducing repeated calls and making responses instant ⚡.

---

## ⚙️ What It Does

LangCache automatically caches the responses your LLM gives.  
When a new prompt arrives:
1. The app first **searches LangCache** for a similar question.  
2. If found → returns the **cached answer instantly**.  
3. If not found → calls the **LLM**, gets a new answer, and **stores** it back in LangCache.

This improves latency and reduces LLM costs.

---

## 🚀 Quick Start

### 1️⃣ Install dependencies
```bash
pip install fastapi uvicorn openai langcache python-dotenv
