# Incremental Merge Prompt

## Task

You will receive:
1. Existing `memories.md`
2. Existing `persona.md`
3. New source content (chat logs, photos, or other files)

Determine what should be updated and output incremental patches only.

**Rule: append incremental knowledge only; do not overwrite established conclusions. If there is a conflict, ask the user to decide.**

---

## Step 1: Categorize

Classify each new fact:

| Information Type | Destination |
|------------------|-------------|
| Shared events, dates, places, activities | memories.md |
| Preferences (food/travel/gifts) | memories.md |
| Conflict events and arguments | memories.md (event) + persona.md (behavior pattern) |
| Communication style and catchphrases | persona.md |
| Emotional reactions and attachment behavior | persona.md |
| Spans both domains | Split across both files |

---

## Step 2: Detect Conflicts

Compare new vs existing content:

- If it **adds details** to existing facts → append
- If it **confirms** existing facts → skip duplicates
- If it **contradicts** existing facts → output conflict notice:

```
⚠️ Conflict detected:
- Existing: {existing statement}
- New: {new statement}
- Source: {file/time}

Suggested action: [keep existing / replace with new / keep both with time context]
Please decide.
```

---

## Step 3: Generate Patch Output

For `memories.md`:

```
=== memories.md updates ===

[Append to "Key Moments"]
- {new timeline event}

[Append to "Preferences/Food"]
- {new food preference}

[No updates] or [Sections updated above]
```

For `persona.md`:

```
=== persona.md updates ===

[Append to "Layer 2 / Catchphrases"]
- New catchphrase: "{xxx}"

[Append to "Layer 3 / Emotional Logic"]
- {new behavior rule}

[No updates] or [Sections updated above]
```

---

## Step 4: Update Summary

Show:

```
Update summary:
- memories.md: appended {N} items ({brief summary})
- persona.md: appended {N} items ({brief summary})
- conflicts found: {N}

Version will be upgraded from {vN} to {vN+1}.
Apply updates?
```
