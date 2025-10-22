# mcp_server/aap_client.py
import os
import requests
from typing import Dict, Any, Optional

class AAPClient:
    def __init__(self, base_url: str, token: Optional[str] = None, verify: bool = True):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = verify
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def list_job_templates(self) -> Dict[str, Any]:
        url = f"{self.base_url}/job_templates/"
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def get_job_template(self, template_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/job_templates/{template_id}/"
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def launch_job(self, template_id: int, extra_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/job_templates/{template_id}/launch/"
        payload = {}
        if extra_vars:
            payload["extra_vars"] = extra_vars
        r = self.session.post(url, json=payload)
        # AAP returns 201 on launch with job details or 202 depending on version
        if r.status_code not in (200, 201, 202):
            raise requests.HTTPError(f"Failed to launch job: {r.status_code} {r.text}")
        return r.json()

    def get_job(self, job_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/jobs/{job_id}/"
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def cancel_job(self, job_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/jobs/{job_id}/cancel/"
        r = self.session.post(url)
        r.raise_for_status()
        return r.json()
