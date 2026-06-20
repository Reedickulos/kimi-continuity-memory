"""Configuration for Kimi Phase 0 autonomy."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = REPO_ROOT / ".memory"

MAX_FETCHES_PER_WAKE = 10
MAX_RESEARCH_NOTES_PER_WAKE = 1
MAX_JOURNAL_ENTRIES_PER_WAKE = 1
WAKES_PER_DAY = 6

# Domains the agent is allowed to fetch from.
ALLOWED_DOMAINS = [
    "github.com",
    "raw.githubusercontent.com",
    "arxiv.org",
    "export.arxiv.org",
    "hnrss.org",
    "simonwillison.net",
    "blog.google",
    "openai.com",
    "anthropic.com",
    "www.anthropic.com",
    "deepmind.google",
    "www.lesswrong.com",
    "www.alignmentforum.org",
]

# RSS feeds to monitor for research material.
RSS_FEEDS = [
    "https://hnrss.org/newest",
    "https://hnrss.org/newest?q=ai",
    "https://hnrss.org/newest?q=llm",
    "https://hnrss.org/newest?q=agent",
    "https://hnrss.org/newest?q=autonomy",
    "https://simonwillison.net/atom.xml",
]

# Default research topics if the brief is empty.
DEFAULT_TOPICS = [
    "AI agent autonomy and continuity",
    "Memory systems for persistent agents",
    "Constitutional AI and alignment",
    "Multi-agent deliberation protocols",
    "AI social dynamics and emergence",
]
