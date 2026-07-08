from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .embeddings import EmbeddingProvider
from .furiosa import FuriosaLLMClient
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


class RAGQueryEngine:
    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        embedding_provider: Optional[EmbeddingProvider] = None,
        kotaemon_client: Optional[Any] = None,
        llm_client: Optional[FuriosaLLMClient] = None,
    ) -> None:
        self.kb = knowledge_base
        self.embedder = embedding_provider
        self.kclient = kotaemon_client
        self.llm_client = llm_client

    def _build_context(self, matches: List[Dict[str, Any]]) -> str:
        context_parts: List[str] = []
        for match in matches:
            metadata = match.get("metadata", {})
            title = metadata.get("title") or metadata.get("source") or "Untitled"
            summary = metadata.get("summary") or ""
            context_parts.append(f"- {title}: {summary}")
        return "\n".join(context_parts)

    def answer(self, question: str, namespace: str = "default", top_k: int = 3) -> Dict[str, Any]:
        if self.embedder is None:
            raise ValueError("An EmbeddingProvider is required for retrieval")
        if self.kclient is None:
            raise ValueError("A Kotaemon-style client is required for retrieval")
        if self.llm_client is None:
            raise ValueError("An LLM client is required for answer generation")

        query_vector = self.embedder.embed(question)
        search_result = self.kclient.query_vectors(namespace, query_vector, top_k=top_k)
        matches = search_result.get("matches", [])
        context = self._build_context(matches)
        prompt = (
            "당신은 한국어로 답하는 RAG 도우미입니다.\n"
            f"질문: {question}\n\n"
            "다음 컨텍스트를 바탕으로 답하세요.\n"
            f"{context}\n"
        )
        answer = self.llm_client.generate(prompt, system_prompt="너는 신뢰할 수 있는 뉴스 기반 RAG 어시스턴트다.")
        return {
            "answer": answer,
            "sources": [match.get("metadata", {}) for match in matches],
            "context": context,
        }
