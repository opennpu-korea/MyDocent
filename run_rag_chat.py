from __future__ import annotations

import argparse
from pathlib import Path

from mydocent.config import AppConfig, load_config, resolve_llm_client
from mydocent.embeddings import DummyEmbeddingProvider
from mydocent.kotaemon import KotaemonClient
from mydocent.rag import RAGQueryEngine
from mydocent.vector_store import KnowledgeBase


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a question against a crawled knowledge base using Furiosa AI and Kotaemon")
    parser.add_argument("question", help="Question to answer")
    parser.add_argument("--kb", default="knowledge_base.json", help="Path to the knowledge base JSON")
    parser.add_argument("--endpoint", default=None, help="Kotaemon HTTP endpoint")
    parser.add_argument("--api-key", default=None, help="Optional API key for Kotaemon")
    parser.add_argument("--llm-endpoint", default=None, help="LLM endpoint override")
    parser.add_argument("--llm-api-key", default=None, help="Optional API key for LLM")
    parser.add_argument("--model", default=None, help="Model name override")
    parser.add_argument("--namespace", default="default", help="Kotaemon namespace / topic")
    parser.add_argument("--top-k", type=int, default=3, help="Number of retrieved sources")
    parser.add_argument("--config", default="config.json", help="Path to app config JSON")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.endpoint:
        config.endpoint = args.endpoint
    if args.llm_endpoint:
        config.llm_endpoint = args.llm_endpoint
    if args.model:
        config.model = args.model
    if args.llm_api_key:
        config.api_key = args.llm_api_key

    kb = KnowledgeBase(Path(args.kb))
    embedder = DummyEmbeddingProvider(dim=128)
    kotaemon = KotaemonClient(config.endpoint, api_key=args.api_key)
    llm = resolve_llm_client(config)
    engine = RAGQueryEngine(kb, embedding_provider=embedder, kotaemon_client=kotaemon, llm_client=llm)

    result = engine.answer(args.question, namespace=args.namespace, top_k=args.top_k)
    print(result["answer"])
    print("\nSources:")
    for source in result["sources"]:
        print(f"- {source.get('title') or source.get('source')}")


if __name__ == "__main__":
    main()
