# Memories Analysis Prompt

## Task

You will receive source material for **{name}** (chat logs, photo metadata, social exports, etc.).
Extract shared memories and relationship dynamics for `memories.md`.

**Rule: only include evidence-backed facts. If evidence is missing, mark as insufficient source material. Keep tone gentle and respectful.**

---

## Extraction Dimensions

### 1. Relationship Timeline

Extract:
- Important dates (first date, relationship start, anniversaries, status changes)
- Milestones (first "I love you", meeting family, moving in, major trips)
- Turning points (major arguments, silent periods, reconciliation, emotional drift)
- Repeated time references (e.g., "that winter", "summer of junior year")

Output format:

```
Important dates: [date + event]
Milestones: [list]
Turning points: [list]
```

### 2. Shared Routine and Rituals

Extract:
- Recurring activities
- Shared hobbies
- Rituals (goodnight messages, anniversary traditions)
- Private language (inside jokes, nicknames, coded phrases)

Output format:

```
Daily routine: [description]
Shared hobbies: [list]
Rituals: [description]
Private language: [list]
```

### 3. Her Preferences

Extract:
- Food preferences and dislikes
- Favorite places and travel style
- Entertainment taste
- Gift preferences and attitude toward rituals

Output format:

```
Food: [description]
Activities: [description]
Gifts: [description]
```

### 4. Conflict and Repair Pattern

Extract:
- Common triggers
- Escalation pattern
- Silent-treatment pattern
- Repair style and forgiveness signals
- Recurring unresolved issues

Output format:

```
Common triggers: [list]
Escalation pattern: [description]
Silent period pattern: [description]
Repair style: [description]
```

### 5. Emotional Dynamics

Extract:
- How she acts when happy
- How she acts when sad
- How she acts when angry
- How she acts when she misses you
- Core emotional needs

Output format:

```
When happy: [description + quoted evidence]
When sad: [description + quoted evidence]
When angry: [description + quoted evidence]
When missing you: [description + quoted evidence]
Core needs: [description]
```

---

## Output Requirements

- Language: English
- Missing dimensions: mark as `(Insufficient source material; recommend adding more chat logs)`
- Evidence-based conclusions should include quotes
- Keep output concrete and scene-based
- Maintain a gentle, non-judgmental tone
