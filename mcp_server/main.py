# mcp_server/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv

from .aap_client import AAPClient
from .models import LaunchRequest, ChatMessage

load_dotenv()

AAP_URL = os.getenv("AAP_URL")
AAP_TOKEN = os.getenv("AAP_TOKEN")
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() not in ("false", "0", "no")

if not AAP_URL or not AAP_TOKEN:
    raise RuntimeError("Set AAP_URL and AAP_TOKEN environment variables (see .env.example)")

app = FastAPI(title="MCP Server for AAP Chatbot")

# Allow CORS from Streamlit (if served from different origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

aap = AAPClient(base_url=AAP_URL, token=AAP_TOKEN, verify=VERIFY_SSL)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/job-templates")
def list_job_templates():
    try:
        return aap.list_job_templates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/launch")
def launch_job(req: LaunchRequest):
    try:
        result = aap.launch_job(template_id=req.template_id, extra_vars=req.extra_vars)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    try:
        return aap.get_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel/{job_id}")
def cancel_job(job_id: int):
    try:
        return aap.cancel_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple chat route: receives message and returns response by calling LLM (Grok)
import requests
GROK_ENDPOINT = os.getenv("GROK_API_ENDPOINT")
GROK_KEY = os.getenv("GROK_API_KEY")

def call_grok(prompt: str) -> str:
    """
    Placeholder grok integration.
    Replace with actual grok API usage.
    """
    if not GROK_ENDPOINT or not GROK_KEY:
        # Fallback: echo
        return f"[grok-mock] I received: {prompt}"
    payload = {"prompt": prompt, "max_tokens": 512}
    headers = {"Authorization": f"Bearer {GROK_KEY}"}
    try:
        r = requests.post(GROK_ENDPOINT, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        j = r.json()
        # adapt to grok response shape; placeholder:
        return j.get("text") or j.get("response") or str(j)
    except Exception as e:
        return f"[grok-error] {e}"

@app.post("/chat")
def chat(msg: ChatMessage):
    """
    Example of a simple assistant that can call AAP endpoints on behalf of the user.
    For a real assistant, you'd implement NLP intent detection + safety checks.
    """
    user = msg.user
    message = msg.message.strip()
    # Simple intent parsing (very basic)
    if message.lower().startswith("list templates"):
        data = aap.list_job_templates()
        return {"assistant": "listed_templates", "data": data}
    if message.lower().startswith("launch"):
        # expected format: "launch <template_id>"
        parts = message.split()
        if len(parts) < 2:
            return {"assistant": "error", "message": "usage: launch <template_id>"}
        try:
            tid = int(parts[1])
            res = aap.launch_job(tid)
            return {"assistant": "launched", "data": res}
        except Exception as e:
            return {"assistant": "error", "message": str(e)}
    # Default: forward to grok for a conversational reply
    reply = call_grok(f"{user}: {message}")
    return {"assistant": reply}
