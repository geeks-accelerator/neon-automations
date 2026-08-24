---
id: 2026-01-01-example-round
title: An example round
turn: 1
pitch_mode: full
status: draft
opened: 2026-01-01
claims: [C-001]
threshold: ">=30 starts with >=40% completion passes; <=15% fails"
---

# An example round

<!-- nav:parent -->
**Parent:** [rounds](README.md) · [docs](../README.md)
<!-- /nav:parent -->

## Script

The ~225 words that get narrated. Every claim it makes appears in `docs/pitch/claims.md`;
one that does not is unsourced by construction.

## The ask

Itemized from real prices, published rather than summarised.

## Threshold

The machine-readable number lives in the `threshold:` frontmatter field — that is what the
validator freezes the moment `status` reaches `posted`, comparing against the base ref under
`--since`. This section explains it; the field enforces it. Written **before** the round
posts and never revised afterwards: that immutability is the entire reason a round is an
event record and not a living document. When the numbers come back, they land in `result:`,
and a resolved round without one is an error.

<!-- nav -->

## Next

1. **Post it, and set status to `posted`** — the threshold freezes at that moment -- while draft it may still be tuned, so nothing is measured until this goes out.

<!-- /nav -->
