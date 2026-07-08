from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

import requests

TRUSTED_DOMAINS = {
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "bbc.co.uk",
    "theguardian.com",
    "nytimes.com",
    "washingtonpost.com",
    "finance.yahoo.com",
    "wsj.com",
    "ft.com",
    "economist.com",
    "bloomberg.com",
    "forbes.com",
}


def is_trusted_source(url: str) -> bool:
    parsed = urlparse(url)
    hostname = parsed.netloc.lower()
    return any(hostname == domain or hostname.endswith(f".{domain}") for domain in TRUSTED_DOMAINS)


def parse_rss_feed(rss_xml: str) -> List[Dict[str, Any]]:
    articles: List[Dict[str, Any]] = []
    root = ET.fromstring(rss_xml)

    for item in root.findall(".//item"):
        link = (item.findtext("link") or "").strip()
        title = (item.findtext("title") or "").strip()
        description = (item.findtext("description") or item.findtext("summary") or "").strip()
        if not link or not is_trusted_source(link):
            continue
        articles.append(
            {
                "title": title or "Untitled",
                "url": link,
                "summary": description,
                "source": urlparse(link).netloc,
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return articles


def crawl_topic(topic: str, rss_urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    rss_urls = rss_urls or [
        f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}"
    ]

    all_articles: List[Dict[str, Any]] = []
    for rss_url in rss_urls:
        response = requests.get(rss_url, timeout=20)
        response.raise_for_status()
        articles = parse_rss_feed(response.text)
        all_articles.extend(articles)

    # Deduplicate by URL
    unique_articles: List[Dict[str, Any]] = []
    seen_urls = set()
    for article in all_articles:
        if article["url"] in seen_urls:
            continue
        seen_urls.add(article["url"])
        unique_articles.append(article)
    return unique_articles
