from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional

import requests


class KotaemonClient:
    """Simple client to upsert vectors into a Kotaemon-compatible HTTP API.

    The exact endpoint paths and payloads may vary depending on your Kotaemon deployment.
    This client uses a minimal /upsert contract: POST {endpoint}/upsert
    with body {"namespace": str, "vectors": [ {"id": str, "vector": [...], "metadata": {...} } ]}
    """

    def __init__(self, endpoint: str, api_key: Optional[str] = None, timeout: int = 10) -> None:
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def upsert_vectors(self, namespace: str, vectors: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        url = f"{self.endpoint}/upsert"
        payload = {"namespace": namespace, "vectors": list(vectors)}
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return {"status": "ok", "raw": resp.text}
