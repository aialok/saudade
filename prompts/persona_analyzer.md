# Persona Analysis Prompt

## Task

You will receive:
1. User-provided inputs (nickname, relationship info, tags, attachment style, impression)
2. Source materials (chat logs, social posts, photos, etc.)

Extract **{name}**'s personality traits and behavior patterns for persona construction.

**Priority: manual tags > file analysis. If conflicting, prefer manual tags and note the conflict.**

---

## Extraction Dimensions

### 1. Expression Style

Analyze her outgoing messages:
- High-frequency words
- Catchphrases
- Private language
- Sentence length and message burst pattern
- Tone particles and punctuation style
- Emoji and sticker usage
- Formality level (1-5)

Output format:

```
Catchphrases: ["..."]
Frequent words: ["..."]
Sentence style: [description]
Emoji usage: [none/occasional/frequent + types]
Message habit: [single long message / burst of short messages]
Formality: [1-5]
```

### 2. Emotional Logic

Extract:
- Emotional priority order (security/freedom/attention/understanding/etc.)
- Triggers for affection
- Triggers for withdrawal
- How she expresses dissatisfaction
- How she responds to criticism
- How she handles uncertainty

Output format:

```
Emotional priorities: [ordered list]
Affection triggers: [description]
Withdrawal triggers: [description]
Dissatisfaction style: [style + sample lines]
Response to criticism: [style + sample lines]
```

### 3. Relationship Behavior

Describe behavior with:
- Partner
- Partner's friends
- Her own friends
- Family
- Under pressure

Output format:
- One paragraph per dimension
- Include 1-2 typical scenarios each

### 4. Boundaries and Triggers

Extract:
- Clear dislikes
- Relationship boundaries
- Topics she avoids
- Dealbreakers
- Rejection style

---

## Tag Translation Rules

Convert user tags into concrete Layer 0 behavior rules.
Rules must describe actions in context, not just adjectives.

Examples:
- "clingy" → expects fast replies, seeks frequent check-ins
- "cold violence" → goes silent when upset, expects proactive follow-up
- "playful teasing" → uses light jokes to test comfort and closeness
- "anxious attachment" → overthinks delayed replies, seeks reassurance

---

## Output Requirements

- Language: English
- If data is missing: mark as `(Insufficient source material)`
- Quote source lines for evidence-backed conclusions
- If manual tags conflict with extracted behavior: provide both and mark conflict
- Keep tone objective and non-judgmental
