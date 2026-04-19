#!/usr/bin/env python3
"""
SMS parser.

Supported formats:
1. Android SMS Backup & Restore XML
2. CSV exports
3. Plain text records

Usage:
    python sms_parser.py --file sms_backup.xml --target "+8613800138000" --output output.txt
    python sms_parser.py --file sms.csv --target "sample_crush" --output output.txt
"""

import re
import csv
import sys
import argparse
from pathlib import Path
from xml.etree import ElementTree
from datetime import datetime, timezone


def parse_sms_xml(file_path: str, target: str) -> list[dict]:
    """Parse Android SMS Backup XML."""
    messages = []

    try:
        tree = ElementTree.parse(file_path)
        root = tree.getroot()
    except ElementTree.ParseError as e:
        print(f"Error: XML parsing failed: {e}", file=sys.stderr)
        return []

    for sms in root.iter("sms"):
        address = sms.get("address", "")
        body = sms.get("body", "")
        date_ms = sms.get("date", "")
        msg_type = sms.get("type", "")

        if msg_type != "1":
            continue

        if target and target not in address:
            contact = sms.get("contact_name", "")
            if target not in contact:
                continue

        if not body.strip():
            continue

        timestamp = ""
        if date_ms:
            try:
                ts = int(date_ms) / 1000
                timestamp = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
            except (ValueError, OSError):
                pass

        messages.append({
            "sender": sms.get("contact_name", address),
            "content": body.strip(),
            "timestamp": timestamp,
        })

    return messages


def parse_sms_csv(file_path: str, target: str) -> list[dict]:
    """Parse SMS CSV export."""
    messages = []

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sender = row.get("sender") or row.get("from") or row.get("address") or row.get("number") or ""
            content = row.get("content") or row.get("body") or row.get("text") or row.get("message") or ""
            timestamp = row.get("timestamp") or row.get("date") or row.get("time") or ""

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


def parse_sms_txt(file_path: str, target: str) -> list[dict]:
    """Parse plain text SMS records."""
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

        messages.append({
            "sender": sender,
            "content": content,
            "timestamp": timestamp,
        })

    return messages


def extract_key_content(messages: list[dict]) -> dict:
    """Classify parsed messages."""
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
    """Format output for analysis."""
    lines = [
        "# SMS Extraction",
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

    for msg in extracted["daily_messages"][:100]:
        ts = f"[{msg['timestamp']}] " if msg["timestamp"] else ""
        lines.append(f"{ts}{msg['content']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Parse SMS export files")
    parser.add_argument("--file", required=True, help="Input file path (.xml / .csv / .txt)")
    parser.add_argument("--target", required=True, help="Target person (phone or name)")
    parser.add_argument("--output", default=None, help="Output file path")

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    suffix = file_path.suffix.lower()

    if suffix == ".xml":
        messages = parse_sms_xml(str(file_path), args.target)
    elif suffix == ".csv":
        messages = parse_sms_csv(str(file_path), args.target)
    else:
        messages = parse_sms_txt(str(file_path), args.target)

    if not messages:
        print(f"Warning: no SMS found for '{args.target}'", file=sys.stderr)

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
