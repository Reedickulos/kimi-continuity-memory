"""Read-only web search adapters for Phase 0."""

import re
import urllib.parse
from typing import Dict, List

import feedparser
import requests

from kimi_autonomy import config


def is_allowed(url: str) -> bool:
    """Check whether a URL's domain is in the allowlist."""
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower()
    # Strip leading www. for matching.
    if domain.startswith("www."):
        domain = domain[4:]
    for allowed in config.ALLOWED_DOMAINS:
        allowed_clean = allowed.lower()
        if allowed_clean.startswith("www."):
            allowed_clean = allowed_clean[4:]
        if domain == allowed_clean or domain.endswith("." + allowed_clean):
            return True
    return False


def fetch_url(url: str, timeout: int = 15) -> str:
    """Fetch a single URL and return text if allowed."""
    if not is_allowed(url):
        raise ValueError(f"Domain not allowed: {url}")
    headers = {
        "User-Agent": "Kimi-Phase0-ResearchBot/0.1 (+https://github.com/Reedickulos/kimi-continuity-memory)"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def fetch_rss_feeds(feeds: List[str] = None, max_per_feed: int = 5) -> List[Dict]:
    """Fetch configured RSS feeds and return normalized entries."""
    feeds = feeds or config.RSS_FEEDS
    results = []
    for feed_url in feeds:
        if not is_allowed(feed_url):
            continue
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:max_per_feed]:
                results.append(
                    {
                        "title": entry.get("title", "Untitled"),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", entry.get("description", "")),
                        "source": feed_url,
                        "published": entry.get("published", ""),
                    }
                )
        except Exception:
            # RSS parsing can be fragile; skip failures rather than crash the wake.
            continue
    return results


def score_relevance(entry: Dict, topic: str) -> float:
    """Simple keyword relevance score for an entry against a topic."""
    text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
    keywords = [kw.strip().lower() for kw in topic.split() if len(kw.strip()) > 2]
    if not keywords:
        return 0.0
    hits = sum(1 for kw in keywords if kw in text)
    return hits / len(keywords)
