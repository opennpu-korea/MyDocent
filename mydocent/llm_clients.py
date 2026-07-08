from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class NvidiaGpuLLMClient:
    """OpenAI-compatible client for NVIDIA GPU inference servers."""

    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None, model: str = "mistral", timeout: int = 30) -> None:
        self.endpoint = (endpoint or "http://localhost:8000").rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        url = f"{self.endpoint}/v1/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload: Dict[str, Any] = {"model": self.model, "messages": messages, **kwargs}
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("NVIDIA LLM response did not contain any choices")
        return str(choices[0].get("message", {}).get("content", ""))
