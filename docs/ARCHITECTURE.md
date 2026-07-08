# Architecture

This document summarizes the high-level components and data flow for the news-based knowledge base.

Components
- `run_daily_update.py`: CLI entrypoint to collect articles for a given topic and update the JSON knowledge base.
- `mydocent/news.py`: RSS-based crawler that fetches feed(s), parses items, and filters by a whitelist of trusted domains (`TRUSTED_DOMAINS`).
- `mydocent/vector_store.py`: Simple knowledge base stored as JSON. Provides `update_topic()` to merge articles and `search()` that computes cosine similarity on token-count vectors.

Data flow
1. User (or scheduler) runs `run_daily_update.py "<topic>"`.
2. The script calls `crawl_topic(topic)` which retrieves RSS results and returns deduplicated, trusted articles.
3. `KnowledgeBase.update_topic()` merges new articles into `knowledge_base.json`.
4. The `search()` API uses basic tokenization and cosine similarity for lightweight retrieval.

Notes
- The vectorization is currently token-count based (bag-of-words). It can be replaced by embeddings later for better semantic retrieval.
- Trusted sources are controlled by `TRUSTED_DOMAINS` in `mydocent/news.py`.
