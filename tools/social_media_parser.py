#!/usr/bin/env python3
"""
Social media export parser.

Supported platforms:
1. WhatsApp channels/chats (TXT/JSON)
2. Instagram (JSON)
3. Plain text posts

Usage:
    python social_media_parser.py --file whatsapp_export.txt --platform whatsapp --target "sample_crush" --output output.txt
    python social_media_parser.py --file posts.txt --platform text --target "sample_crush" --output output.txt
"""

import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime


def parse_whatsapp(file_path: str, target: str) -> list[dict]:
    """Parse WhatsApp TXT/JSON export."""
    posts = []
    file = Path(file_path)
    if file.suffix.lower() == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        items = data if isinstance(data, list) else data.get("messages", data.get("data", []))
        for item in items:
            if not isinstance(item, dict):
                continue
            sender = str(item.get("sender") or item.get("author") or item.get("name") or "")
            if target and target.lower() not in sender.lower():
                continue
            text = str(item.get("text") or item.get("content") or item.get("message") or "").strip()
            if not text:
                continue
            posts.append({
                "text": text,
                "date": str(item.get("date") or item.get("timestamp") or ""),
                "likes": 0,
                "comments": 0,
                "platform": "WhatsApp",
            })
        return posts

    pattern = re.compile(
        r"^(?:\[)?(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)"
        r"(?:\])?\s+-\s+(?P<sender>[^:]+):\s(?P<text>.+)$"
    )
    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            m = pattern.match(line)
            if not m:
                continue
            sender = m.group("sender").strip()
            if target and target.lower() not in sender.lower():
                continue
            text = m.group("text").strip()
            if not text:
                continue
            posts.append({
                "text": text,
                "date": m.group("date").strip(),
                "likes": 0,
                "comments": 0,
                "platform": "WhatsApp",
            })
    return posts


def parse_instagram(file_path: str, target: str) -> list[dict]:
    """Parse Instagram JSON export."""
    posts = []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data if isinstance(data, list) else data.get("posts", data.get("data", []))

    for item in items:
        if not isinstance(item, dict):
            continue

        text = ""
        media = item.get("media", [{}])
        if isinstance(media, list) and media:
            text = media[0].get("title", "") or media[0].get("caption", "")

        text = text or item.get("title", "") or item.get("caption", "")
        date = item.get("creation_timestamp", "")
        if isinstance(date, (int, float)):
            date = datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M")

        if not text.strip():
            continue

        posts.append({
            "text": text.strip(),
            "date": str(date),
            "likes": 0,
            "comments": 0,
            "platform": "Instagram",
        })

    return posts


def parse_text(file_path: str, target: str) -> list[dict]:
    """Parse generic text posts."""
    posts = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    entries = re.split(r"\n={3,}\n|\n-{3,}\n|\n\n\n+", content)

    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue

        date_match = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})", entry)
        date = date_match.group(1) if date_match else ""

        posts.append({
            "text": entry,
            "date": date,
            "likes": 0,
            "comments": 0,
            "platform": "Text",
        })

    return posts


def format_output(target: str, posts: list[dict]) -> str:
    """Format output for downstream analysis."""
    lines = [
        "# Social Media Extraction",
        f"Target: {target}",
        f"Total posts: {len(posts)}",
        "",
        "---",
        "",
    ]

    long_posts = [p for p in posts if len(p["text"]) > 100]
    short_posts = [p for p in posts if len(p["text"]) <= 100]

    lines += ["## Long Posts (high weight)", ""]

    for p in long_posts:
        date_str = f"[{p['date']}] " if p["date"] else ""
        platform = f"({p['platform']}) " if p.get("platform") else ""
        lines.append(f"{date_str}{platform}{p['text']}")
        lines.append("")

    lines += ["---", "", "## Short Posts (style reference)", ""]

    for p in short_posts[:100]:
        date_str = f"[{p['date']}] " if p["date"] else ""
        platform = f"({p['platform']}) " if p.get("platform") else ""
        lines.append(f"{date_str}{platform}{p['text']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Parse social media export files")
    parser.add_argument("--file", required=True, help="Input file path")
    parser.add_argument(
        "--platform",
        required=True,
        choices=["whatsapp", "instagram", "text"],
        help="Platform type",
    )
    parser.add_argument("--target", default="", help="Target person (optional filter)")
    parser.add_argument("--output", default=None, help="Output file path")

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    parsers = {
        "whatsapp": parse_whatsapp,
        "instagram": parse_instagram,
        "text": parse_text,
    }

    posts = parsers[args.platform](str(file_path), args.target)

    if not posts:
        print("Warning: no post content extracted", file=sys.stderr)

    output = format_output(args.target or "unspecified", posts)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output} with {len(posts)} posts")
    else:
        print(output)


if __name__ == "__main__":
    main()
