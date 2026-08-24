---
name: research
description: Conduct an external research pass and file it as a dated, sourced record that decisions can cite. Use this skill whenever a choice turns on facts from outside the codebase — pricing, a regulation, what a competitor does, what a format costs, whether an approach is already taken — and whenever `validate.py --preflight` reports an open question. Also use it when asked to "look into", "find out", "check what X costs", "see if anyone else is doing this", or to resolve something a proposal or plan says it cannot answer yet. Reach for it before writing a decision that rests on external facts, not after.
---

# research

Produces a dated scan in `docs/research/` that a decision can cite. Record shape and
frontmatter are in [`neon-docs`](../neon-docs/SKILL.md); this is the method.

## Why the record is dated and immutable

A scan says what was knowable **then**. Rewrite it in place and every decision that cited it
silently loses its justification — a later reader finds reasoning resting on numbers that
appear nowhere, unable to tell whether the decision was wrong or merely overtaken.

When the world moves, write a new scan with `supersedes:` and set the old one to
`superseded`. Both stay. A superseded scan is not wrong, it is **expired**.

## Separate findings from implications

Two headings, always. This is the load-bearing convention, not a formatting preference.

**Findings** — what the sources say. Each claim carries its source. No inference.
**Implications** — what you think it means here. Labelled as inference.

The separation earns its keep when either half fails. A reader who disagrees with your
reasoning keeps the evidence; a reader who finds a source was wrong knows exactly which
conclusions to revisit. Blended, the whole document goes in the bin when either does.

## Record the method

What you searched, what you excluded, and what you could not find. Say when sources are
secondary — *"citing primary studies, primary papers not read"* — so a reader knows the
percentages are directional rather than precise.

**An absence of evidence is a finding.** It tells the next reader the ground was covered.

But it deserves care, because it is where research most easily becomes advocacy: **an empty
niche is equally consistent with an opportunity and with the thing not working.** Say so
when you cannot distinguish them, rather than implying the flattering reading. A scan that
only ever surfaces encouraging absences is not research.

## Sources are the whole point

Every claim links to where it came from. The validator warns when a `current` scan lists no
`sources`, because research nobody can re-check is an assertion wearing a lab coat.

Prefer primary where the number matters. Where you use a secondary source citing a study,
say so rather than presenting it as first-hand.

## Closing an open question

A record blocked on research carries `needs_research: [slug]`. Close it by listing that slug
in the scan's `answers:`, then confirm:

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --preflight
```

**Scope to the question that was raised.** A scan that wanders past it costs the time of
everyone who reads it later looking for the answer.

The other honest close is to **drop the need** because it stopped bearing on the decision.
Use it when true — a question carried forward past its relevance teaches people to override
the gate.
