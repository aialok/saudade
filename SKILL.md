---
name: saudade
description: "Distill a crush into an AI Skill. Import iMessage/SMS/WhatsApp/photos, generate Memories + Persona, with continuous evolution."
argument-hint: "[crush-name-or-slug]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# saudade - Crush Skill Creator (Claude Code Edition)

## Trigger Conditions

Activate when the user says any of the following:
- `/create-crush`
- "Help me create a crush skill"
- "I want to distill a crush"
- "New crush"
- "Make a skill for XX"

Enter evolution mode when the user says:
- "I have new chat logs" / "append"
- "That's wrong" / "She wouldn't do that" / "She should be"
- `/update-crush {slug}`

List all generated crushes when the user says `/list-crushes`.

---

## Tool Usage Rules

This Skill runs in Claude Code with these tools:

| Task | Tool |
|------|------|
| Read PDF documents | `Read` |
| Read screenshots/images | `Read` |
| Read MD/TXT files | `Read` |
| Parse iMessage | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/imessage_parser.py` |
| Parse SMS | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/sms_parser.py` |
| Analyze photo metadata | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/photo_analyzer.py` |
| Parse social exports (Instagram/WhatsApp) | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/social_media_parser.py` |
| Write/update Skill files | `Write` / `Edit` |
| Version management | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |
| List Skills | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list` |

Base directory: `./crushes/{slug}/`.
Use `--base-dir ~/.openclaw/workspace/skills/crushes` for a global path.

---

## Main Flow: Create a New Crush Skill

### Step 1: Basic Info Collection (3 questions)

Use `${CLAUDE_SKILL_DIR}/prompts/intake.md` and ask only 3 questions:

1. **Nickname / Codename** (required)
2. **Basic info** (one sentence: relationship duration, how you met, current relationship status, occupation)
3. **Personality profile** (one sentence: MBTI, zodiac, attachment style, relationship tags, impression)

Everything except nickname can be skipped. Summarize and confirm before continuing.

### Step 2: Source Material Import

Ask how the user wants to provide source material:

```
How would you like to provide source materials?

  [A] iMessage / SMS / WhatsApp
      Mac chat.db or exported files

  [B] Photos
      Specify a folder and auto-extract timeline (EXIF metadata)

  [C] Social Media
      WhatsApp channels / Instagram exports

  [D] Upload Files
      PDF / screenshots / plain text

  [E] Paste Text
      Paste text directly

You can combine methods, or skip all and generate from manual info only.
```

#### Option A: iMessage / SMS / WhatsApp

iMessage file mode:
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/imessage_parser.py --file {path} --target "{phone_or_name}" --output /tmp/imessage_out.txt
```

iMessage direct mode:
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/imessage_parser.py --direct --target "{phone_or_name}" --output /tmp/imessage_out.txt
```

SMS:
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/sms_parser.py --file {path} --target "{phone_or_name}" --output /tmp/sms_out.txt
```

WhatsApp:
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/social_media_parser.py --file {path} --platform whatsapp --target "{name}" --output /tmp/whatsapp_out.txt
```

#### Option B: Photos

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/photo_analyzer.py --dir {photo_directory} --output /tmp/photo_timeline.txt
```
Then `Read /tmp/photo_timeline.txt`.

#### Option C: Social Media

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/social_media_parser.py \
  --file {path} \
  --platform {whatsapp|instagram|text} \
  --target "{name}" \
  --output /tmp/social_out.txt
```
Then `Read /tmp/social_out.txt`.

#### Option D: File Upload

- PDF / Images: `Read`
- Markdown / TXT: `Read`

#### Option E: Paste Text

Use user-pasted content directly.

If user says "no files" or "skip", generate from Step 1 info only.

### Step 3: Analyze Source Material

Analyze in two tracks:

**Track A (Memories)**
- Use `${CLAUDE_SKILL_DIR}/prompts/memories_analyzer.md`
- Extract timeline, routines, preferences, conflict patterns, emotional dynamics

**Track B (Persona)**
- Use `${CLAUDE_SKILL_DIR}/prompts/persona_analyzer.md`
- Translate tags into behavior rules
- Extract communication style, emotional logic, relationship behavior

### Step 4: Generate and Preview

Generate with:
- `${CLAUDE_SKILL_DIR}/prompts/memories_builder.md`
- `${CLAUDE_SKILL_DIR}/prompts/persona_builder.md`

Show both summaries and ask for confirmation.

### Step 5: Write Files

After confirmation:

1) Create folders
```bash
mkdir -p crushes/{slug}/versions
mkdir -p crushes/{slug}/knowledge/chats
mkdir -p crushes/{slug}/knowledge/photos
mkdir -p crushes/{slug}/knowledge/social
```

2) Write `memories.md`

3) Write `persona.md`

4) Write `meta.json`

5) Generate full `SKILL.md`

Then tell the user:

```
Crush Skill created.

Location: crushes/{slug}/
Commands: /{slug} (full)
          /{slug}-memories
          /{slug}-persona

If anything feels wrong, say "she wouldn't do that" and I will update it.
```

---

## Evolution Mode: Append Materials

When user provides new content:
1. Read new content via Step 2
2. Read existing `crushes/{slug}/memories.md` and `persona.md`
3. Use `${CLAUDE_SKILL_DIR}/prompts/merger.md`
4. Backup current version:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action backup --slug {slug} --base-dir ./crushes
   ```
5. Append updates with `Edit`
6. Regenerate `SKILL.md`
7. Update `meta.json` version and timestamp

---

## Evolution Mode: Conversation Correction

When user says output is wrong:
1. Use `${CLAUDE_SKILL_DIR}/prompts/correction_handler.md`
2. Route correction to memories or persona layer
3. Generate correction entry
4. Append to `## Correction Log`
5. Regenerate `SKILL.md`

---

## Management Commands

`/list-crushes`
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list --base-dir ./crushes
```

`/crush-rollback {slug} {version}`
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./crushes
```

`/delete-crush {slug}`
```bash
rm -rf crushes/{slug}
```
