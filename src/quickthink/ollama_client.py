from __future__ import annotations

from typing import Any

import httpx


class OllamaClient:
    def __init__(self, base_url: str, timeout_s: float = 180.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
        think: bool | str | None = None,
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
        if think is not None:
            payload["think"] = think
        with httpx.Client(timeout=self.timeout_s) as client:
            response = client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()
