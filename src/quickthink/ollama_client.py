from __future__ import annotations

from typing import Any

import httpx


class OllamaClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            },
        }
        with httpx.Client(timeout=90.0) as client:
            response = client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()
