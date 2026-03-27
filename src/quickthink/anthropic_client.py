from __future__ import annotations

from typing import Any
import os

import httpx


class AnthropicClient:
    def __init__(self, timeout_s: float = 180.0) -> None:
        self.timeout_s = timeout_s
        self.base_url = "https://api.anthropic.com/v1/messages"

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
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is required for Anthropics calls")

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            # Anthropic models reject simultaneous temperature + top_p; prefer temperature and omit top_p.
            "stream": False,
        }
        # `think` parameter is not applicable to Anthropic; ignore if provided.

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        with httpx.Client(timeout=self.timeout_s) as client:
            resp = client.post(self.base_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text_parts: list[str] = []
        for block in data.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(str(block.get("text", "")))
        response_text = "".join(text_parts) if text_parts else str(data.get("stop_reason", ""))

        return {"response": response_text}
