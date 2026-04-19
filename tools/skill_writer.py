#!/usr/bin/env python3
"""
Skill file writer.

Writes memories.md and persona.md into the correct directory structure,
and generates meta.json and the complete SKILL.md.

Usage:
    python3 skill_writer.py --action create --slug sample_crush --meta meta.json \
        --memories memories_content.md --persona persona_content.md \
        --base-dir ./crushes

    python3 skill_writer.py --action update --slug sample_crush \
        --memories-patch memories_patch.md --persona-patch persona_patch.md \
        --base-dir ./crushes

    python3 skill_writer.py --action list --base-dir ./crushes
"""

from __future__ import annotations

import json
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


SKILL_MD_TEMPLATE = """\
---
name: crush_{slug}
description: {name}, {identity}
user-invocable: true
---

# {name}

{identity}

---

## PART A: Shared Memories

{memories_content}

---

## PART B: Persona

{persona_content}

---

## Runtime Rules

For every incoming message:

1. **Use PART B first**: decide if and how she replies
2. **Use PART A next**: pull relevant shared memory details
3. **Reply in PART B style**: wording, cadence, emoji preference

**Layer 0 rules in PART B always have highest priority.**
"""


def slugify(name: str) -> str:
    """Convert a name to slug."""
    result = []
    for char in name.lower():
        if char.isascii() and (char.isalnum() or char in ("-", "_")):
            result.append(char)
        elif char == " ":
            result.append("_")

    import re

    slug = "".join(result)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug if slug else "crush"


def build_identity_string(meta: dict) -> str:
    """Build identity description from meta."""
    profile = meta.get("profile", {})
    parts = []

    duration = profile.get("duration", "")
    how_met = profile.get("how_met", "")
    relationship_status = profile.get("relationship_status", "")
    occupation = profile.get("occupation", "")

    if duration:
        parts.append(f"known for {duration}")
    if how_met:
        parts.append(how_met)
    if relationship_status:
        parts.append(f"status: {relationship_status}")

    identity = ", ".join(parts) if parts else "crush"

    if occupation:
        identity += f", {occupation}"

    mbti = profile.get("mbti", "")
    if mbti:
        identity += f", MBTI {mbti}"

    return identity


def create_skill(
    base_dir: Path,
    slug: str,
    meta: dict,
    memories_content: str,
    persona_content: str,
) -> Path:
    """Create a new crush skill structure."""

    skill_dir = base_dir / slug
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "versions").mkdir(exist_ok=True)
    (skill_dir / "knowledge" / "chats").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "photos").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "social").mkdir(parents=True, exist_ok=True)

    (skill_dir / "memories.md").write_text(memories_content, encoding="utf-8")
    (skill_dir / "persona.md").write_text(persona_content, encoding="utf-8")

    name = meta.get("name", slug)
    identity = build_identity_string(meta)

    skill_md = SKILL_MD_TEMPLATE.format(
        slug=slug,
        name=name,
        identity=identity,
        memories_content=memories_content,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    memories_only = (
        f"---\nname: crush_{slug}_memories\n"
        f"description: Shared memories of {name} (Memories only, no Persona)\n"
        f"user-invocable: true\n---\n\n{memories_content}\n"
    )
    (skill_dir / "memories_skill.md").write_text(memories_only, encoding="utf-8")

    persona_only = (
        f"---\nname: crush_{slug}_persona\n"
        f"description: Persona of {name} (Persona only, no shared memories)\n"
        f"user-invocable: true\n---\n\n{persona_content}\n"
    )
    (skill_dir / "persona_skill.md").write_text(persona_only, encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat()
    meta["slug"] = slug
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["version"] = "v1"
    meta.setdefault("corrections_count", 0)

    (skill_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return skill_dir


def update_skill(
    skill_dir: Path,
    memories_patch: Optional[str] = None,
    persona_patch: Optional[str] = None,
    correction: Optional[dict] = None,
) -> str:
    """Update existing skill and snapshot previous version."""

    meta_path = skill_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    current_version = meta.get("version", "v1")
    try:
        version_num = int(current_version.lstrip("v").split("_")[0]) + 1
    except ValueError:
        version_num = 2
    new_version = f"v{version_num}"

    version_dir = skill_dir / "versions" / current_version
    version_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("SKILL.md", "memories.md", "persona.md"):
        src = skill_dir / fname
        if src.exists():
            shutil.copy2(src, version_dir / fname)

    if memories_patch:
        current_memories = (skill_dir / "memories.md").read_text(encoding="utf-8")
        (skill_dir / "memories.md").write_text(current_memories + "\n\n" + memories_patch, encoding="utf-8")

    if persona_patch or correction:
        current_persona = (skill_dir / "persona.md").read_text(encoding="utf-8")

        if correction:
            correction_line = (
                f"\n- [Scene: {correction.get('scene', 'general')}] "
                f"Should not {correction['wrong']}; should {correction['correct']}"
            )
            target = "## Correction Log"
            if target in current_persona:
                insert_pos = current_persona.index(target) + len(target)
                rest = current_persona[insert_pos:]
                placeholder = "\n\n(No records yet)"
                if rest.startswith(placeholder):
                    rest = rest[len(placeholder):]
                new_persona = current_persona[:insert_pos] + correction_line + rest
            else:
                new_persona = current_persona + f"\n\n## Correction Log\n{correction_line}\n"
            meta["corrections_count"] = meta.get("corrections_count", 0) + 1
        else:
            new_persona = current_persona + "\n\n" + persona_patch

        (skill_dir / "persona.md").write_text(new_persona, encoding="utf-8")

    memories_content = (skill_dir / "memories.md").read_text(encoding="utf-8")
    persona_content = (skill_dir / "persona.md").read_text(encoding="utf-8")
    name = meta.get("name", skill_dir.name)
    identity = build_identity_string(meta)

    skill_md = SKILL_MD_TEMPLATE.format(
        slug=skill_dir.name,
        name=name,
        identity=identity,
        memories_content=memories_content,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    meta["version"] = new_version
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return new_version


def list_crushes(base_dir: Path) -> list:
    """List all created crush skills."""
    crushes = []

    if not base_dir.exists():
        return crushes

    for skill_dir in sorted(base_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        meta_path = skill_dir / "meta.json"
        if not meta_path.exists():
            continue

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        crushes.append({
            "slug": meta.get("slug", skill_dir.name),
            "name": meta.get("name", skill_dir.name),
            "identity": build_identity_string(meta),
            "version": meta.get("version", "v1"),
            "updated_at": meta.get("updated_at", ""),
            "corrections_count": meta.get("corrections_count", 0),
        })

    return crushes


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill file writer")
    parser.add_argument("--action", required=True, choices=["create", "update", "list"])
    parser.add_argument("--slug", help="Crush slug (directory name)")
    parser.add_argument("--name", help="Crush display name")
    parser.add_argument("--meta", help="Path to meta.json")
    parser.add_argument("--memories", help="Path to memories.md content")
    parser.add_argument("--persona", help="Path to persona.md content")
    parser.add_argument("--memories-patch", help="Path to memories patch content")
    parser.add_argument("--persona-patch", help="Path to persona patch content")
    parser.add_argument("--base-dir", default="./crushes", help="Crush skill base directory")

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()

    if args.action == "list":
        crushes = list_crushes(base_dir)
        if not crushes:
            print("No crush skills created yet")
        else:
            print(f"Created {len(crushes)} crush skills:\n")
            for e in crushes:
                updated = e["updated_at"][:10] if e["updated_at"] else "unknown"
                print(f"  [{e['slug']}]  {e['name']} - {e['identity']}")
                print(f"    version: {e['version']}  corrections: {e['corrections_count']}  updated: {updated}")
                print()

    elif args.action == "create":
        if not args.slug and not args.name:
            print("Error: create requires --slug or --name", file=sys.stderr)
            sys.exit(1)

        meta: dict = {}
        if args.meta:
            meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
        if args.name:
            meta["name"] = args.name

        slug = args.slug or slugify(meta.get("name", "crush"))

        memories_content = Path(args.memories).read_text(encoding="utf-8") if args.memories else ""
        persona_content = Path(args.persona).read_text(encoding="utf-8") if args.persona else ""

        skill_dir = create_skill(base_dir, slug, meta, memories_content, persona_content)
        print(f"Skill created: {skill_dir}")
        print(f"Trigger command: /{slug}")

    elif args.action == "update":
        if not args.slug:
            print("Error: update requires --slug", file=sys.stderr)
            sys.exit(1)

        skill_dir = base_dir / args.slug
        if not skill_dir.exists():
            print(f"Error: skill directory not found: {skill_dir}", file=sys.stderr)
            sys.exit(1)

        memories_patch = Path(args.memories_patch).read_text(encoding="utf-8") if args.memories_patch else None
        persona_patch = Path(args.persona_patch).read_text(encoding="utf-8") if args.persona_patch else None

        new_version = update_skill(skill_dir, memories_patch, persona_patch)
        print(f"Skill updated to {new_version}: {skill_dir}")


if __name__ == "__main__":
    main()
