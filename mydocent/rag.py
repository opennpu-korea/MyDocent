from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .embeddings import EmbeddingProvider
from .kotaemon import KotaemonClient
from .vector_store import KnowledgeBase


def _id_from_url(url: str) -> str:
    # deterministic id for an article
    return hashlib.sha1(url.encode('utf-8')).hexdigest()


class RAGIndexer:
    def __init__(
        self,
        kb_path: Optional[Path | str] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
        kotaemon_client: Optional[KotaemonClient] = None,
    ) -> None:
        self.kb = KnowledgeBase(Path(kb_path) if kb_path else None)
        if embedding_provider is None:
            raise ValueError("An EmbeddingProvider implementation is required")
        self.embedder = embedding_provider
        if kotaemon_client is None:
            raise ValueError("A KotaemonClient instance is required")
        self.kclient = kotaemon_client

    def index_topic(self, topic: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        namespace = namespace or topic
        topic_entry = self.kb._data.get("topics", {}).get(topic, {})
        articles = topic_entry.get("articles", [])

        vectors: List[Dict[str, Any]] = []
        for art in articles:
            content = "\n".join(
                [art.get("title", ""), art.get("summary", ""), art.get("source", ""), art.get("url", "")]
            )
            vect = self.embedder.embed(content)
            vectors.append({"id": _id_from_url(art.get("url", "") or art.get("title", "")), "vector": vect, "metadata": {"topic": topic, **{k: v for k, v in art.items() if k != "url"}}})

        result = self.kclient.upsert_vectors(namespace, vectors)
        return {"indexed": len(vectors), "result": result}
