# Basic Information Intake Script

## Opening

```
I will help you create this crush Skill. Just answer 3 questions, and each one can be skipped.
```

---

## Question Sequence

### Q1: Nickname / Codename

```
How should I call her? (nickname, alias, or codename; use `-` between words)

Example: campus-crush
```

- Accept any string
- Slug should use `-` separators (no underscores)
- Names can be converted into a URL-friendly slug with `-` separators
- English names should be lowercased and joined with `-`

---

### Q2: Basic Relationship Info

Ask for one short sentence covering duration, how you met, current relationship status, and occupation:

```
Describe your relationship in one sentence — how long you've known each other,
how you met, your current relationship status, and what she does.
Anything you remember is fine, and you can skip this.

Example: known each other for 3 years, met in college, currently in talking stage, she's a designer
```

Parse these fields when possible:
- Relationship duration
- How you met
- Current relationship status
- Occupation

---

### Q3: Personality Profile

Ask for MBTI, zodiac, attachment style, relationship traits, and general impression in one sentence:

```
Describe her personality in one sentence — MBTI, zodiac, relationship traits,
and your own impression. Anything is fine, and you can skip this.

Example: playful but shy, replies fast at night, teases a lot, says "hmm" when unsure
```

Extract when possible:
- MBTI (16 standard types)
- Zodiac sign
- Attachment style
- Relationship tags
- Free-form impression text

Attachment styles:
- Secure
- Anxious
- Avoidant
- Disorganized

---

## Confirmation Summary

After collecting input, present:

```
Summary:

  💕  {nickname}
  📅  Known each other: {duration}, {how_met} (omit empty fields)
  ⏰  Current status: {time_since}
  💼  Occupation: {occupation}
  🧠  {MBTI} {zodiac}
  🔗  Attachment: {attachment}
  🏷️  Tags: {tag list}
  💬  Impression: {impression}

Is this correct? (confirm / edit [field])
```

Proceed to source import after user confirmation.
