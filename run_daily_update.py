from __future__ import annotations

import argparse
from pathlib import Path

from mydocent.news import crawl_topic
from mydocent.vector_store import KnowledgeBase


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect trusted news for a topic and update the knowledge base")
    parser.add_argument("topic", help="Topic keyword to collect news about")
    parser.add_argument("--db", default="knowledge_base.json", help="Path to the JSON knowledge base")
    args = parser.parse_args()

    articles = crawl_topic(args.topic)
    kb = KnowledgeBase(Path(args.db))
    kb.update_topic(args.topic, articles)
    print(f"Updated knowledge base with {len(articles)} articles for topic '{args.topic}'")


if __name__ == "__main__":
    main()
