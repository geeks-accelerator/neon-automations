<!-- index:begin -->

# rounds — the delivery ledger

**Parent:** [docs](../README.md)

One record per turn of the funding loop: the script, the claims it used, the ask, the threshold set before posting, and the result appended after.

## How to read this directory

**Newest first.** The threshold in each record was written *before* that round posted and is never revised, so a record whose result and threshold disagree is the most informative kind here. `inconclusive` means the turn repeats rather than that it failed.

## Contents

| date | record | status |
|---|---|---|
| 2026-01-01 | [example-round](2026-01-01-example-round.md) | draft |

Conventions, schema, and the validator: [neon-docs](https://github.com/geeks-accelerator/neon-automations/blob/main/claude/skills/neon-docs/SKILL.md).

<!-- index:end -->
