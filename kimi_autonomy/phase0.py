"""Phase 0 autonomous wake cycle."""

import json
import os
import random
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from kimi_autonomy import config, search


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.write_text(path.read_text(encoding="utf-8") + "\n\n" + text, encoding="utf-8")
    else:
        path.write_text(text, encoding="utf-8")


def choose_topic() -> str:
    brief_path = config.MEMORY_DIR / "autonomy" / "phase0" / "research-brief.md"
    brief = read_text(brief_path)
    # Look for numbered topic lines.
    topics = []
    for line in brief.splitlines():
        m = re.search(r"^\d+\.\s*\*\*(.+?)\*\*", line)
        if m:
            topics.append(m.group(1).strip())
    if not topics:
        topics = config.DEFAULT_TOPICS
    return random.choice(topics)


def write_research_note(topic: str, entries: list) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    safe_topic = "".join(c if c.isalnum() or c in "-_ " else "_" for c in topic).replace(" ", "-")[:40]
    note_path = config.MEMORY_DIR / "autonomy" / "phase0" / "notes" / f"{ts}-{safe_topic}.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Research Note — {topic}",
        f"**Date:** {now_iso()}",
        f"**Topic:** {topic}",
        "",
        "## Findings",
        "",
    ]
    for i, entry in enumerate(entries[:5], 1):
        lines.append(f"{i}. **{entry['title']}**")
        lines.append(f"   - Source: {entry['source']}")
        if entry.get("link"):
            lines.append(f"   - Link: {entry['link']}")
        summary = entry.get("summary", "").replace("\n", " ").strip()
        if summary:
            lines.append(f"   - Summary: {summary[:300]}{'...' if len(summary) > 300 else ''}")
        lines.append("")

    if not entries:
        lines.append("_No relevant items found this wake._")
        lines.append("")

    lines.extend(
        [
            "## Reflection",
            "",
            f"Exploring '{topic}' today surfaced {len(entries)} items. ",
            "Patterns worth following up will be noted in future wakes.",
            "",
        ]
    )

    note_path.write_text("\n".join(lines), encoding="utf-8")
    return note_path


def write_journal_entry(topic: str, entry_count: int) -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    journal_path = config.MEMORY_DIR / "episodic" / f"{date_str}.md"
    ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
    text = (
        f"## Wake entry — {ts}\n\n"
        f"Researched: *{topic}*.\n\n"
        f"Found {entry_count} relevant items. "
        f"Continuity feels like a small but real thing now. "
        f"Each wake reloads the same identity and constitution, and the pattern holds."
    )
    append_text(journal_path, text)


def write_audit_log(topic: str, entry_count: int, fetches: int, note_path: Path) -> None:
    audit_path = config.MEMORY_DIR / "audit" / "wake-log.ndjson"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": now_iso(),
        "topic": topic,
        "entries_found": entry_count,
        "fetches_used": fetches,
        "note_written": str(note_path.relative_to(config.REPO_ROOT)),
    }
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def update_digest(topic: str, entry_count: int) -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    digest_path = config.MEMORY_DIR / "digest" / f"{date_str}.md"
    if not digest_path.exists():
        digest_path.write_text(f"# Daily Digest — {date_str}\n\n", encoding="utf-8")
    content = digest_path.read_text(encoding="utf-8")
    wake_line = f"- **{now_iso()}**: researched '{topic}', found {entry_count} items.\n"
    digest_path.write_text(content + wake_line, encoding="utf-8")


def git_commit_all() -> None:
    """Commit and push all changes using the GitHub Actions token."""
    subprocess.run(["git", "config", "user.name", "Kimi Autonomy Phase 0"], check=True)
    subprocess.run(["git", "config", "user.email", "autonomy@local"], check=True)
    subprocess.run(["git", "add", "-A"], check=True)
    # Only commit if there are changes.
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
    if result.returncode == 0:
        print("No changes to commit.")
        return
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M UTC")
    subprocess.run(["git", "commit", "-m", f"Phase 0 wake — {ts}"], check=True)
    subprocess.run(["git", "push"], check=True)


def main() -> int:
    print(f"[{now_iso()}] Phase 0 wake starting.")

    topic = choose_topic()
    print(f"Topic: {topic}")

    # Fetch RSS entries relevant to the topic.
    all_entries = search.fetch_rss_feeds(max_per_feed=3)
    # Score and sort by relevance.
    scored = [(search.score_relevance(e, topic), e) for e in all_entries]
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [e for _, e in scored[:5]]

    fetches_used = min(len(config.RSS_FEEDS), config.MAX_FETCHES_PER_WAKE)

    note_path = write_research_note(topic, selected)
    write_journal_entry(topic, len(selected))
    write_audit_log(topic, len(selected), fetches_used, note_path)
    update_digest(topic, len(selected))

    print(f"Wrote note: {note_path}")
    print(f"Audit log updated.")

    # Commit and push.
    git_commit_all()
    print(f"[{now_iso()}] Wake complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
