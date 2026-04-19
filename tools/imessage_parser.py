#!/usr/bin/env python3
"""
iMessage parser.

Supported formats:
1. Direct read from macOS chat.db (requires Full Disk Access)
2. TXT/CSV exports from iMazing/PhoneView/etc.
3. Manually organized text files

Usage:
    python imessage_parser.py --file messages.txt --target "+8613800138000" --output output.txt
    python imessage_parser.py --direct --target "sample_crush" --output output.txt
"""

import re
import csv
import sys
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime, timezone


CHAT_DB_PATH = Path.home() / "Library" / "Messages" / "chat.db"
APPLE_EPOCH_OFFSET = 978307200


def parse_chat_db(target: str, limit: int = 5000) -> list[dict]:
    """Read iMessage directly from macOS chat.db."""
    if not CHAT_DB_PATH.exists():
        print(f"Error: chat.db not found: {CHAT_DB_PATH}", file=sys.stderr)
        print("Tip: Full Disk Access is required to read iMessage DB", file=sys.stderr)
        return []

    messages = []
    try:
        conn = sqlite3.connect(str(CHAT_DB_PATH))
        cursor = conn.cursor()

        query = """
        SELECT
            m.text,
            m.date,
            m.is_from_me,
            h.id AS handle_id
        FROM message m
        LEFT JOIN handle h ON m.handle_id = h.ROWID
        WHERE m.text IS NOT NULL
            AND m.text != ''
            AND m.is_from_me = 0
            AND (h.id LIKE ? OR h.id LIKE ?)
        ORDER BY m.date DESC
        LIMIT ?
        """

        cursor.execute(query, (f"%{target}%", f"%{target}%", limit))
        rows = cursor.fetchall()

        for text, date_val, is_from_me, handle_id in rows:
            if date_val and date_val > 1e15:
                ts = date_val / 1e9 + APPLE_EPOCH_OFFSET
            elif date_val:
                ts = date_val + APPLE_EPOCH_OFFSET
            else:
                ts = 0

            timestamp = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M") if ts else ""

            messages.append({
                "sender": handle_id or target,
                "content": text.strip(),
                "timestamp": timestamp,
            })

        conn.close()
        messages.reverse()

    except sqlite3.OperationalError as e:
        print(f"Error: cannot read chat.db: {e}", file=sys.stderr)
        print("Tip: grant Full Disk Access to terminal", file=sys.stderr)

    return messages


def parse_txt(file_path: str, target: str) -> list[dict]:
    """Parse TXT iMessage/SMS export."""
    messages = []

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pattern = re.compile(
        r"^(?P<time>\d{4}[-/]\d{1,2}[-/]\d{1,2}[\s\d:]*)\s+(?P<sender>.+?)[:：]\s*(?P<content>.+)$"
    )

    for line in lines:
        line = line.strip()
        if not line:
            continue

        m = pattern.match(line)
        if not m:
            continue

        sender = m.group("sender").strip()
        content = m.group("content").strip()
        timestamp = m.group("time").strip()

        if target and target not in sender:
            continue
        if not content:
            continue

        messages.append({"sender": sender, "content": content, "timestamp": timestamp})

    return messages


def parse_csv(file_path: str, target: str) -> list[dict]:
    """Parse CSV export."""
    messages = []

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sender = row.get("sender") or row.get("from") or row.get("Sender") or row.get("From") or ""
            content = (
                row.get("content") or row.get("text") or row.get("Content") or row.get("Text")
                or row.get("message") or row.get("Message") or ""
            )
            timestamp = row.get("timestamp") or row.get("time") or row.get("Date") or row.get("date") or ""

            if target and target not in str(sender):
                continue
            if not str(content).strip():
                continue

            messages.append({
                "sender": str(sender),
                "content": str(content).strip(),
                "timestamp": str(timestamp),
            })

    return messages


def extract_key_content(messages: list[dict]) -> dict:
    """Classify extracted messages."""
    long_messages = []
    emotional_messages = []
    daily_messages = []

    emotional_keywords = [
        "miss", "love", "hate", "angry", "sad", "happy", "sorry", "break up", "together", "see you",
    ]

    for msg in messages:
        content = msg["content"]
        if len(content) > 50:
            long_messages.append(msg)
        elif any(kw in content for kw in emotional_keywords):
            emotional_messages.append(msg)
        else:
            daily_messages.append(msg)

    return {
        "long_messages": long_messages,
        "emotional_messages": emotional_messages,
        "daily_messages": daily_messages,
        "total_count": len(messages),
    }


def format_output(target: str, extracted: dict) -> str:
    """Format extracted content."""
    lines = [
        "# iMessage Chat Extraction",
        f"Target: {target}",
        f"Total messages: {extracted['total_count']}",
        "",
        "---",
        "",
        "## Long Messages (highest weight)",
        "",
    ]

    for msg in extracted["long_messages"]:
        ts = f"[{msg['timestamp']}] " if msg["timestamp"] else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    lines += ["---", "", "## Emotional Messages", ""]

    for msg in extracted["emotional_messages"]:
        ts = f"[{msg['timestamp']}] " if msg["timestamp"] else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    lines += ["---", "", "## Daily Style Reference", ""]

    for msg in extracted["daily_messages"][:200]:
        ts = f"[{msg['timestamp']}] " if msg["timestamp"] else ""
        lines.append(f"{ts}{msg['content']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Parse iMessage chat records")
    parser.add_argument("--file", help="Input file path (.txt / .csv)")
    parser.add_argument("--direct", action="store_true", help="Read local chat.db directly")
    parser.add_argument("--target", required=True, help="Target person (name or phone number)")
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument("--limit", type=int, default=5000, help="Max messages in direct mode")

    args = parser.parse_args()

    if args.direct:
        messages = parse_chat_db(args.target, args.limit)
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        if file_path.suffix.lower() == ".csv":
            messages = parse_csv(str(file_path), args.target)
        else:
            messages = parse_txt(str(file_path), args.target)
    else:
        print("Error: provide --file or --direct", file=sys.stderr)
        sys.exit(1)

    if not messages:
        print(f"Warning: no messages found for '{args.target}'", file=sys.stderr)

    extracted = extract_key_content(messages)
    output = format_output(args.target, extracted)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output} with {len(messages)} messages")
    else:
        print(output)


if __name__ == "__main__":
    main()
