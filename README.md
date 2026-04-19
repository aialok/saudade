# saudade

*For the one whose texts you've reread at 2am, for no reason.*

**Saudade** (*Portuguese* — say it like *sow·DAH·jee*) is the word people reach for when English runs out. It is not quite “missing,” not quite “nostalgia.” It is the weight of someone’s absence while their presence still lives in you: a song, a phrase they used, the way the phone used to light up. It can ache softly or sharply; it can hold love, regret, and tenderness in the same breath. We named this project **saudade** because it tries to hold that kind of feeling in text — the pull of a person who matters, even when they are far, quiet, or only half-known.

**Crush Skill Generator** · [License](LICENSE) · Python 3.9+ · [AgentSkills](https://agentskills.io) · [Claude Code](https://claude.ai/code)

---

## What this is

**saudade** is a small toolkit that turns chat history and notes into a **crush Skill**: shared memories plus a speaking persona you can invoke in Claude Code. The name is the project; each generated profile is a **crush** skill under `crushes/{slug}/`.

It is built for people who already have signal in plain text—replies that land late, tone shifts, half-jokes—and want that encoded without pretending the model “knows” someone it has never seen.

---

## What you bring

| Kind | What to drop in |
|------|-----------------|
| **Chats** | iMessage (export or `chat.db`), SMS backups, WhatsApp `.txt` / zip |
| **Images** | Folders of photos; timeline comes from EXIF, not image understanding |
| **Social-ish exports** | WhatsApp channel dumps, Instagram JSON, or pasted text |
| **Anything else** | PDFs, screenshots, raw notes—read in by the agent |

Drop sensitive exports in **`data/chats/`**. That path is ignored by git so your files stay on your machine unless you commit them on purpose.

---

## Setup

**Clone (pick one):**

```bash
mkdir -p .claude/skills && git clone https://github.com/aialok/saudade .claude/skills/saudade
```

```bash
git clone https://github.com/aialok/saudade ~/.claude/skills/saudade
```

**OpenClaw:**

```bash
git clone https://github.com/aialok/saudade ~/.openclaw/workspace/skills/saudade
```

**Optional Python deps:**

```bash
pip3 install -r requirements.txt
```

More detail: [INSTALL.md](INSTALL.md).

---

## Run it

1. Open Claude Code in a repo that has this skill installed.
2. Run **`/create-crush`** and answer the short intake (nickname required; rest optional).
3. Point the flow at files under `data/chats/` or paste text when asked.
4. After generation, invoke **`/{slug}`** for the full skill, or **`/{slug}-memories`** / **`/{slug}-persona`** for split views.

**Handy commands**

| Trigger | Does |
|---------|------|
| `/list-crushes` | Lists folders under `crushes/` that have a valid `meta.json` |
| `/crush-rollback {slug} {version}` | Restores a saved snapshot |
| `/delete-crush {slug}` | Removes `crushes/{slug}` |

---

## Sample dialogue (illustrative)

Persona tags in the prompt might look like: *friendly, shy at first, coffee, playful teasing.*

**Ping after a long day**

```
you: heyy, reached home?
crush: just reached 😌
       you?
       also wow, texting this early today? 👀
```

**Soft plan for a meet**

```
you: coffee this weekend?
crush: hmm maybe yes
       but only if you're not going to cancel last minute 😶
       saturday evening works?
```

---

## Privacy

Processing is **local** to how you run the agent and tools; photo tooling only reads **metadata** (e.g. time/location from EXIF), not image contents. By default, generated skills live under **`crushes/`** and are gitignored except the bundled example—see `.gitignore`.

---

## Credits

MIT — [aialok](https://github.com/aialok)

Prior art: [ex-skill](https://github.com/perkfly/ex-skill) (different focus: ex-partner simulation, Chinese-oriented ecosystem). **saudade** is a separate project aimed at crush personas and the flow described above.
