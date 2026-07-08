from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional


class KnowledgeBase:
    def __init__(self, path: Optional[Path | str] = None) -> None:
        self.path = Path(path or "knowledge_base.json")
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"topics": {}}
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self._data, handle, ensure_ascii=False, indent=2)

    def update_topic(self, topic: str, articles: List[Dict[str, Any]]) -> None:
        topic_entry = self._data.setdefault("topics", {}).setdefault(topic, {"articles": []})
        existing = {article["url"]: article for article in topic_entry.get("articles", [])}
        for article in articles:
            existing[article["url"]] = article
        topic_entry["articles"] = list(existing.values())
        self._save()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[a-z0-9]+", text.lower())

    @staticmethod
    def _vectorize(text: str) -> Counter[str]:
        return Counter(KnowledgeBase._tokenize(text))

    @staticmethod
    def _cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
        if not left or not right:
            return 0.0
        shared_terms = set(left) & set(right)
        if not shared_terms:
            return 0.0
        numerator = sum(left[token] * right[token] for token in shared_terms)
        denominator = (sum(value * value for value in left.values()) ** 0.5) * (
            sum(value * value for value in right.values()) ** 0.5
        )
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_vector = self._vectorize(query)
        results: List[Dict[str, Any]] = []
        for topic, entry in self._data.get("topics", {}).items():
            for article in entry.get("articles", []):
                content = " ".join(
                    [
                        topic,
                        article.get("title", ""),
                        article.get("summary", ""),
                        article.get("source", ""),
                    ]
                )
                doc_vector = self._vectorize(content)
                score = self._cosine_similarity(query_vector, doc_vector)
                if score > 0:
                    results.append({"topic": topic, **article, "score": round(score, 4)})

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]
