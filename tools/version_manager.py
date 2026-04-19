#!/usr/bin/env python3
"""
Skill version manager.

Handles version snapshots and rollback operations.

Usage:
    python version_manager.py --action list --slug sample_crush --base-dir ./crushes
    python version_manager.py --action backup --slug sample_crush --base-dir ./crushes
    python version_manager.py --action rollback --slug sample_crush --version v2 --base-dir ./crushes
"""

from __future__ import annotations

import json
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

MAX_VERSIONS = 10


def backup_current(skill_dir: Path) -> str:
    """Backup current files into versions directory."""
    meta_path = skill_dir / "meta.json"
    current_version = "v1"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            current_version = meta.get("version", "v1")
        except json.JSONDecodeError:
            pass

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"{current_version}_backup_{stamp}"
    backup_dir = skill_dir / "versions" / backup_name
    backup_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for fname in ("SKILL.md", "memories.md", "persona.md"):
        src = skill_dir / fname
        if src.exists():
            shutil.copy2(src, backup_dir / fname)
            copied.append(fname)

    if copied:
        print(f"Backup created: {backup_name} ({', '.join(copied)})")
    else:
        print(f"Backup created: {backup_name} (no files copied)")
    return backup_name


def list_versions(skill_dir: Path) -> list:
    """List historical versions."""
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        return []

    versions = []
    for v_dir in sorted(versions_dir.iterdir()):
        if not v_dir.is_dir():
            continue

        mtime = v_dir.stat().st_mtime
        archived_at = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
        files = [f.name for f in v_dir.iterdir() if f.is_file()]

        versions.append({
            "version": v_dir.name,
            "archived_at": archived_at,
            "files": files,
            "path": str(v_dir),
        })

    return versions


def rollback(skill_dir: Path, target_version: str) -> bool:
    """Rollback to a specific version."""
    version_dir = skill_dir / "versions" / target_version

    if not version_dir.exists():
        print(f"Error: version '{target_version}' does not exist", file=sys.stderr)
        return False

    meta_path = skill_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        current_version = meta.get("version", "v?")
        backup_dir = skill_dir / "versions" / f"{current_version}_before_rollback"
        backup_dir.mkdir(parents=True, exist_ok=True)
        for fname in ("SKILL.md", "memories.md", "persona.md"):
            src = skill_dir / fname
            if src.exists():
                shutil.copy2(src, backup_dir / fname)

    restored_files = []
    for fname in ("SKILL.md", "memories.md", "persona.md"):
        src = version_dir / fname
        if src.exists():
            shutil.copy2(src, skill_dir / fname)
            restored_files.append(fname)

    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["version"] = target_version + "_restored"
        meta["updated_at"] = datetime.now(timezone.utc).isoformat()
        meta["rollback_from"] = meta.get("version", "unknown")
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Rolled back to {target_version}; restored: {', '.join(restored_files)}")
    return True


def cleanup_old_versions(skill_dir: Path, max_versions: int = MAX_VERSIONS):
    """Delete oldest versions beyond max_versions."""
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        return

    version_dirs = sorted(
        [d for d in versions_dir.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
    )

    to_delete = version_dirs[:-max_versions] if len(version_dirs) > max_versions else []
    for old_dir in to_delete:
        shutil.rmtree(old_dir)
        print(f"Deleted old version: {old_dir.name}")


def main():
    parser = argparse.ArgumentParser(description="Skill version manager")
    parser.add_argument("--action", required=True, choices=["backup", "list", "rollback", "cleanup"])
    parser.add_argument("--slug", required=True, help="Crush skill slug")
    parser.add_argument("--version", help="Target version (for rollback)")
    parser.add_argument("--base-dir", default="./crushes", help="Crush skill base directory")

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()
    skill_dir = base_dir / args.slug

    if not skill_dir.exists():
        print(f"Error: skill directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    if args.action == "backup":
        backup_current(skill_dir)

    elif args.action == "list":
        versions = list_versions(skill_dir)
        if not versions:
            print(f"No version history for {args.slug}")
        else:
            print(f"Version history for {args.slug}:\n")
            for v in versions:
                print(f"  {v['version']}  archived: {v['archived_at']}  files: {', '.join(v['files'])}")

    elif args.action == "rollback":
        if not args.version:
            print("Error: --version is required for rollback", file=sys.stderr)
            sys.exit(1)
        rollback(skill_dir, args.version)

    elif args.action == "cleanup":
        cleanup_old_versions(skill_dir)
        print("Cleanup complete")


if __name__ == "__main__":
    main()
