import requests
from typing import Optional, Dict, Any


class OllamaClient:

    def __init__(self, host: str, timeout_s: int):
        self.host = host
        self.timeout_s = timeout_s

    def generate(self, model: str, prompt: str, system: Optional[str] = None):
        url = f"{self.host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        r = requests.post(url, json=payload, timeout=self.timeout_s)
        if not r.ok:
            raise RuntimeError(
                f"Request failed with status {r.status_code}: {r.text}"
            )
        data = r.json()
        return data.get("response", "")