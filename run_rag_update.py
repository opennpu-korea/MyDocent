from __future__ import annotations

import argparse
from pathlib import Path

from mydocent.embeddings import DummyEmbeddingProvider
from mydocent.kotaemon import KotaemonClient
from mydocent.rag import RAGIndexer


def main() -> None:
    parser = argparse.ArgumentParser(description="Index topic articles from KB into Kotaemon vector DB")
    parser.add_argument("topic", help="Topic to index")
    parser.add_argument("--kb", default="knowledge_base.json", help="Path to knowledge base JSON")
    parser.add_argument("--endpoint", required=True, help="Kotaemon HTTP endpoint (e.g. http://localhost:8000)")
    parser.add_argument("--api-key", default=None, help="Optional API key for Kotaemon")
    parser.add_argument("--dim", type=int, default=128, help="Embedding dimension for DummyEmbeddingProvider")
    args = parser.parse_args()

    embedder = DummyEmbeddingProvider(dim=args.dim)
    kclient = KotaemonClient(args.endpoint, api_key=args.api_key)
    indexer = RAGIndexer(kb_path=Path(args.kb), embedding_provider=embedder, kotaemon_client=kclient)

    resp = indexer.index_topic(args.topic, namespace=args.topic)
    print(f"Indexed {resp['indexed']} vectors into Kotaemon: {resp['result']}")


if __name__ == "__main__":
    main()
