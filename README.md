# MCP-AAP Chatbot

This repository contains a simple MCP-style server (FastAPI) that talks to Ansible Automation Platform (AAP), and a Streamlit-based chat frontend that uses Grok as the LLM backend (placeholder). Use it as a starting point to build a conversational infra-management interface.

## Features
- MCP server (FastAPI) with endpoints:
  - `/health` - health check
  - `/job-templates` - list job templates from AAP
  - `/launch` - launch job template (POST JSON: `{"template_id": 5, "extra_vars": {...}}`)
  - `/jobs/{job_id}` - job status
  - `/cancel/{job_id}` - cancel job
  - `/chat` - basic chatbot endpoint (integrates with Grok or a mock fallback)
- Streamlit UI that calls the MCP server and provides a simple chat UI and quick actions.

## Requirements
Python 3.9+.

Install:
```bash
pip install -r requirements.txt
