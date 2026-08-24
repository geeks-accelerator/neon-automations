---
title: Claims ledger
updated: 2026-01-01
research: [2026-01-01-example-scan]
---

# Claims ledger

<!-- nav:parent -->
**Parent:** [pitch](README.md) · [docs](../README.md)
<!-- /nav:parent -->

Every claim the pitch makes appears here once, tagged and cited. A claim that cannot be
written into this file does not go into the pitch.

| id | claim | tag | citation |
|---|---|---|---|
| C-001 | The repository contains one example decision | `EXTRACTED` | `docs/decisions/2026-01-01-example-decision.md` |
| C-002 | The example scan reports a price | `RESEARCHED` | [2026-01-01-example-scan](../research/2026-01-01-example-scan.md) |
| C-003 | This fixture is representative of a real tree | `ASSERTED` | nothing independent backs it |

The tag is a statement about evidence, not confidence. `EXTRACTED` means the repository
*demonstrates* it — a citation that merely locates prose saying so is `EXTRACTED` for
*the repository states X*, which is a weaker and different claim.

A fenced example row is documentation, not a claim — the parser must not read this one:

```markdown
| C-001 | a fenced example the parser must skip | `EXTRACTED` | would be a duplicate id |
```

<!-- nav -->

## Related

- **Derives from:** [2026-01-01-example-scan](../research/2026-01-01-example-scan.md)

## Next

The ledger. Every claim in the tree appears here once, tagged and cited, and a claim that cannot be written here does not go in the pitch. On a re-run, check citations *before* writing anything and **demote** what no longer verifies -- a stale `EXTRACTED` claim is worse than an `ASSERTED` one, because it carries authority it no longer has.

<!-- /nav -->
