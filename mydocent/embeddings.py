from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from collections import Counter
from typing import List


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError()


class DummyEmbeddingProvider(EmbeddingProvider):
    """A deterministic, lightweight embedding provider for local testing.

    Produces a fixed-size vector by hashing tokens into buckets and summing counts.
    This is NOT a semantic embedding; it's a stopgap for offline testing and integration.
    """

    def __init__(self, dim: int = 128) -> None:
        self.dim = int(dim)

    def _tokenize(self, text: str) -> List[str]:
        return [t for t in __import__('re').findall(r"[a-z0-9]+", text.lower())]

    def embed(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        counts = Counter(tokens)
        vec = [0.0] * self.dim
        for token, cnt in counts.items():
            h = hashlib.sha256(token.encode('utf-8')).digest()
            idx = int.from_bytes(h[:4], 'big') % self.dim
            vec[idx] += float(cnt)

        # simple L2 normalize
        norm = sum(x * x for x in vec) ** 0.5
        if norm == 0:
            return vec
        return [x / norm for x in vec]
