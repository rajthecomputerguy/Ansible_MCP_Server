# mcp_server/models.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class LaunchRequest(BaseModel):
    template_id: int
    extra_vars: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    user: str
    message: str
