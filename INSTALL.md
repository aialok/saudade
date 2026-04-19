# saudade Installation Guide

---

## Choose Your Platform

### A. Claude Code (Recommended)

This repository follows the [AgentSkills](https://agentskills.io) standard. The whole repository is the skill directory. Clone it into your Claude skills path:

```bash
# ⚠️ Must run at your git repository root
cd $(git rev-parse --show-toplevel)

# Option 1: Install to current project
mkdir -p .claude/skills
git clone https://github.com/aialok/saudade .claude/skills/saudade

# Option 2: Install globally (all projects)
git clone https://github.com/aialok/saudade ~/.claude/skills/saudade
```

Then run `/create-crush` in Claude Code.

Generated skills are written to `./crushes/` by default.

---

### B. OpenClaw

```bash
git clone https://github.com/aialok/saudade ~/.openclaw/workspace/skills/saudade
```

Restart the OpenClaw session and run `/create-crush`.

---

## Dependency Setup

```bash
# Base requirement (Python 3.9+)
# iMessage direct read (macOS)
# No extra package needed, but Full Disk Access must be granted to terminal/Claude Code

# Photo EXIF analysis
# Built-in JPEG EXIF parsing works without extra packages
# For broader image format support:
pip3 install Pillow
```

---

## Data Preparation

Before import, place chat files in:

```bash
data/chats/
```

This folder is ignored by git (except `.gitkeep`), so personal exports stay local.

### iMessage

**Method 1: Direct read** (macOS)
- Grant Full Disk Access to terminal/Claude Code in system settings
- Use `--direct`

**Method 2: Export file**
- Export with tools like [iMazing](https://imazing.com/)
- Export as txt or csv

### Photos

Put relevant photos in one folder:
- The tool extracts EXIF metadata (date/location)
- Generates a timeline summary
- You can inspect selected images directly via Claude `Read`

### Social Media

- **WhatsApp channels/chats**: Export as txt/json with your preferred tool
- **Instagram**: Settings → Your Activity → Download your information

---

## Quick Validation

```bash
cd ~/.claude/skills/saudade   # or project .claude/skills/saudade

# Test iMessage parser
python3 tools/imessage_parser.py --help

# Test photo analyzer
python3 tools/photo_analyzer.py --help

# List generated crush skills
python3 tools/skill_writer.py --action list --base-dir ./crushes
```

---

## Directory Structure

```
saudade/                 <- clone to .claude/skills/saudade/
├── SKILL.md              # skill entry (AgentSkills frontmatter)
├── prompts/              # analysis and generation prompt templates
├── tools/                # Python helper tools
├── data/
│   └── chats/            # local chat exports (gitignored)
│
└── crushes/              # generated crush skills (.gitignore)
    └── {slug}/
        ├── SKILL.md
        ├── memories.md
        ├── persona.md
        ├── meta.json
        ├── versions/
        └── knowledge/
```
