---
id: 2026-01-02-marker-in-frontmatter
title: Frontmatter naming a nav marker must survive regeneration
n: 1
first_seen: 2026-01-02
last_seen: 2026-01-02
evidence: "A quoted YAML value naming <!-- nav --> once matched as a block opener and the replacement ate the frontmatter and the whole body. Backtick masking does not help inside YAML quotes."
---

# Frontmatter naming a nav marker must survive regeneration

<!-- nav:parent -->
**Parent:** [observations](README.md) · [docs](../README.md)
<!-- /nav:parent -->

This body is the regression. If the generator ever searches frontmatter for markers again,
everything from the `evidence:` field down disappears and this paragraph goes with it.

<!-- nav -->

## Next

N=1. Nothing to do: this is an instance, not a rule. On recurrence, increment `n`, update `last_seen`, and append dated evidence.

<!-- /nav -->
