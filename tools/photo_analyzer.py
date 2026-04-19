#!/usr/bin/env python3
"""
Photo metadata analyzer.

Extracts EXIF metadata (date/location/camera context) and builds a timeline.
Does not analyze image content itself.

Usage:
    python photo_analyzer.py --dir ~/Photos/with_her --output timeline.txt
"""

import sys
import struct
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def extract_exif_date(file_path: str) -> str | None:
    """Extract EXIF DateTimeOriginal from JPEG without PIL."""
    try:
        with open(file_path, "rb") as f:
            if f.read(2) != b"\xff\xd8":
                return None

            while True:
                marker = f.read(2)
                if len(marker) < 2:
                    break
                if marker[0] != 0xFF:
                    break

                if marker[1] == 0xE1:
                    length = struct.unpack(">H", f.read(2))[0]
                    exif_data = f.read(length - 2)

                    date_pattern = rb"\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}"
                    import re

                    matches = re.findall(date_pattern, exif_data)
                    if matches:
                        return matches[0].decode("ascii")
                    return None

                if marker[1] in (0xD9, 0xDA):
                    break

                length = struct.unpack(">H", f.read(2))[0]
                f.seek(length - 2, 1)

    except Exception:
        pass

    return None


def get_photo_date(file_path: Path) -> str:
    """Get photo date from EXIF; fallback to file mtime."""
    exif_date = extract_exif_date(str(file_path))
    if exif_date:
        try:
            dt = datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")


def scan_photos(directory: str) -> list[dict]:
    """Scan photo files recursively."""
    photo_extensions = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tiff", ".bmp"}
    photos = []

    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Error: directory does not exist: {directory}", file=sys.stderr)
        return []

    for file_path in sorted(dir_path.rglob("*")):
        if file_path.is_file() and file_path.suffix.lower() in photo_extensions:
            photos.append({
                "path": str(file_path),
                "filename": file_path.name,
                "date": get_photo_date(file_path),
                "size_kb": file_path.stat().st_size // 1024,
            })

    return photos


def group_by_date(photos: list[dict]) -> dict[str, list]:
    """Group photos by date."""
    groups = defaultdict(list)
    for photo in photos:
        groups[photo["date"]].append(photo)
    return dict(sorted(groups.items()))


def format_output(photo_dir: str, groups: dict, total: int) -> str:
    """Format timeline output."""
    lines = [
        "# Photo Timeline",
        f"Directory: {photo_dir}",
        f"Total photos: {total}",
        f"Range: {min(groups.keys()) if groups else 'N/A'} ~ {max(groups.keys()) if groups else 'N/A'}",
        "",
        "---",
        "",
    ]

    for date, photos in groups.items():
        lines.append(f"## {date} ({len(photos)} photos)")
        for p in photos[:10]:
            lines.append(f"  - {p['filename']} ({p['size_kb']} KB)")
        if len(photos) > 10:
            lines.append(f"  - ... {len(photos) - 10} more")
        lines.append("")

    lines += [
        "---",
        "",
        "## Usage",
        "",
        "This is a metadata timeline summary.",
        "If you want to inspect specific photos, provide a date or filename.",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze photo metadata and build timeline")
    parser.add_argument("--dir", required=True, help="Photo directory path")
    parser.add_argument("--output", default=None, help="Output file path")

    args = parser.parse_args()

    photos = scan_photos(args.dir)
    if not photos:
        print("Warning: no photo files found", file=sys.stderr)

    groups = group_by_date(photos)
    output = format_output(args.dir, groups, len(photos))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output} with {len(photos)} photos across {len(groups)} dates")
    else:
        print(output)


if __name__ == "__main__":
    main()
