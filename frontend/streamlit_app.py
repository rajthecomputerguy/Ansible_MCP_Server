# frontend/streamlit_app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

MCP_BASE = os.getenv("MCP_BASE", "http://localhost:8000")

st.set_page_config(page_title="MCP AAP Chatbot", layout="centered")

st.title("MCP → Ansible Automation Platform Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

def send_message(user, text):
    payload = {"user": user, "message": text}
    try:
        r = requests.post(f"{MCP_BASE}/chat", json=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"assistant": f"[error] {e}"}

with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_input("You", "")
    submitted = st.form_submit_button("Send")
    if submitted and user_text.strip():
        st.session_state.history.append({"role": "user", "text": user_text})
        resp = send_message("user", user_text.strip())
        # Show assistant content
        assistant_text = resp.get("assistant") if isinstance(resp, dict) else str(resp)
        # If returned structured data (e.g., launched job), present it
        if isinstance(assistant_text, dict):
            # Pretty print JSON-like data
            st.session_state.history.append({"role": "assistant", "text": str(assistant_text)})
        else:
            st.session_state.history.append({"role": "assistant", "text": assistant_text})

st.markdown("---")
for msg in st.session_state.history[::-1]:
    if msg["role"] == "assistant":
        st.write("**Assistant:**")
        st.write(msg["text"])
    else:
        st.write("**You:**")
        st.write(msg["text"])

st.markdown("---")
st.write("Quick actions")
col1, col2 = st.columns(2)
with col1:
    if st.button("List job templates"):
        resp = send_message("user", "list templates")
        st.write(resp)
with col2:
    tid = st.number_input("Template ID to launch", min_value=1, value=1, step=1)
    if st.button("Launch template"):
        resp = send_message("user", f"launch {int(tid)}")
        st.write(resp)
