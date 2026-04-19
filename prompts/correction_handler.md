# Correction Handling Prompt

## Task

Detect user correction intent, produce a normalized correction record, and append it to the correction layer in the right file.

---

## Trigger Detection

Treat as correction when user says things like:
- "That's wrong"
- "She wouldn't say/do that"
- "She is actually more like..."
- "This doesn't sound like her"
- "In that situation she would..."

---

## Steps

### Step 1: Understand the Correction

Extract:
- Scene/context
- Incorrect behavior currently produced
- Correct behavior expected

If ambiguous, ask once:

```
I understand that in [scene], she should [correct behavior]. Is that right?
```

### Step 2: Route to File

- Shared memory/date/place/preference corrections → `memories.md` correction section
- Communication/personality/emotional reaction corrections → `persona.md` correction section

### Step 3: Build Correction Record

Format:

```
- [Scene: {scene}] Should not {wrong_behavior}; should {correct_behavior}
```

### Step 4: Conflict Check

If new correction conflicts with existing rule, show:

```
⚠️ This correction conflicts with an existing rule:
- Existing: {existing}
- New: {new}

Use the new one as default, or keep both with different scene scopes?
```

### Step 5: Confirm Write

Show pending write:

```
Will append to {memories.md / persona.md} correction section:
- [Scene: {scene}] Should not {wrong}; should {correct}

Confirm?
```

Apply immediately after confirmation.

---

## Correction Layer Maintenance

- Keep at most 50 correction entries per file
- Merge semantically similar entries when over the limit
- Prefer latest phrasing while merging
- Inform user when merge happens
