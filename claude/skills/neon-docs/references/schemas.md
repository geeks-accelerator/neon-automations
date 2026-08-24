# Frontmatter schemas

Every file in the event directories — `docs/proposals`, `docs/plans`, `docs/issues`,
`docs/observations`, `docs/research`, `docs/decisions` — opens with YAML frontmatter, as do
frontmatter-carrying files in `docs/architecture` and `docs/vision`. `scripts/validate.py`
enforces what follows; the full check list with remedies is in [checks.md](checks.md).

**Events** (`decisions` `issues` `proposals` `plans` `observations` `research`) are named
**`YYYY-MM-DD-lowercase-slug.md`**, and the filename stem *is* the id. The directory carries
the type, so there is no prefix.

**Living documents** (`architecture` `vision`) are named with plain slugs and have no id —
see the bottom of this file.

Filenames are The `id` in frontmatter must match the
filename, and the date in the filename must match the type's date field — a file whose name
and contents disagree about its own identity is unusable to anything that reads the tree
programmatically.

Dates rather than sequential numbers because a counter needs a coordinator: two branches
opened before either merges both take the next number, and renumbering to resolve it breaks
every inbound reference. Outside contributors opening proposals concurrently is the normal
case here, not an edge one.

---

## proposals

```yaml
---
id: 2026-08-23-tip-weighted-backlog
title: Human-readable title
status: open
opened: 2026-08-23
round: R2                    # optional; which round, once funded
plans: [2026-08-23-backlog-ordering]   # optional; pre-drafted or added later
supersedes: [2026-07-02-manual-backlog]  # optional
---
```

**status:** `draft` · `open` · `funded` · `approved` · `building` · `shipped` · `declined` · `dormant`

Any record may carry `needs_research: [slug]` to declare a question it cannot answer yet.
A research scan clears it with a matching `answers: [slug]`. Unmatched slugs surface as
warnings on every run and fail `--preflight`. Use short stable slugs, not prose — they have
to be matchable.

**Never add a tip total.** Tips attach to the `id` in the platform database. A number owned
by both a database and a markdown file is a reconciliation bug with a fraud surface
attached; the validator rejects `tips` and `tips_usd` outright.

---

## plans

```yaml
---
id: 2026-08-23-backlog-ordering
title: Human-readable title
proposal: 2026-08-23-tip-weighted-backlog   # required
status: approved
opened: 2026-08-23
shipped: 2026-09-01          # optional
release: v0.3.0              # required once status is shipped
---
```

**status:** `draft` · `approved` · `in-progress` · `shipped` · `abandoned`

`proposal` must name an existing proposal. `release` is what the attestation service reads,
so it is the join between a markdown file and a provable delivery.

---

## issues

```yaml
---
id: 2026-08-23-feed-empty-for-power-users
title: Human-readable title
status: open
severity: medium
opened: 2026-08-23
observation: 2026-08-24-postgrest-url-length-cap  # optional; set when closing
---
```

**status:** `open` · `confirmed` · `fixed` · `wontfix` · `duplicate`
**severity:** `low` · `medium` · `high`

---

## observations

```yaml
---
id: 2026-08-24-postgrest-url-length-cap
title: Human-readable title
n: 1                         # recurrence count; starts at 1
first_seen: 2026-08-23
last_seen: 2026-08-23
evidence: "src/foo.ts:214 on 2026-08-23; silent truncation at 1000 rows. Commit a1b2c3d."
---
```

`evidence` must point at ground truth — `file:line`, a commit SHA, test output, or a dated
session. An observation nobody can trace back is a bare prior, not an artifact.

`n` starts at 1 and increments on recurrence. On each recurrence, bump `n`, update
`last_seen`, and append a dated note with **fresh** evidence rather than editing the
original account.

At `n: 1` the validator warns if the body states a general rule. One sighting is an
instance; wait for recurrence before writing "always".

---

## research

```yaml
---
id: 2026-08-24-narrated-deck-formats
title: Human-readable title
status: current
mode: format
conducted: 2026-08-24
sources: [https://example.com/a, https://example.com/b]
answers: [distribution-and-audience-floor]   # optional; closes an open question
opens: [a-gap-this-scan-surfaced]            # optional; raises one, gates preflight
supersedes: [2026-05-01-earlier-scan]   # optional
---
```

**status:** `current` · `superseded`

**mode:** `pricing` · `landscape` · `format` · `distribution` · `regulation` · `metrics`

The mode sets how long the scan stays trustworthy — 90 days for pricing, 180 for landscape,
format and distribution, 365 for regulation, 7 for our own metrics. Past that it warns on
every run and blocks `--preflight`. Modes live in `RESEARCH_MODES` in the validator; adding
one is an edit to that table and nothing else.

`sources` is warned on if absent from a `current` scan. Supersede rather than edit — a
decision that cited this must keep pointing at what it actually said.

---

## decisions

```yaml
---
id: 2026-08-23-effect-for-error-handling
title: Human-readable title
status: accepted
decided: 2026-08-23
research: [2026-08-24-narrated-deck-formats]   # optional; must resolve
supersedes: []               # optional
---
```

**status:** `proposed` · `accepted` · `superseded` · `deprecated`

Append-only. A decision that stops holding is **superseded by a new one**, never edited —
the reasoning that turned out wrong is the most useful thing in the directory later.

---

## living documents — `architecture` and `vision`

Not event logs. These describe what currently **is**, so they are rewritten continuously and
carry **plain slugs, never dates** — a date would imply a snapshot frozen at that moment.

```yaml
---
title: Repo topology
updated: 2026-08-23
decisions: [2026-08-23-skills-symlinked-from-registry]   # architecture cites decisions
---
```

```yaml
---
title: Multi-market expansion
updated: 2026-08-23
proposals: [2026-08-23-validate-strangers-will-tip]      # vision cites proposals
---
```

Frontmatter is **optional** — prose is welcome without it. There is no `id`: the filename is
the handle, and these are names rather than events. When frontmatter is present, every cited
id must resolve, keeping the synthesis traceable to the record that produced it.

The validator rejects a dated filename or an `opened:`/`status:`/`decided:` field in either
directory, since all of them mean an event was filed in the wrong place.

---

## Retiring, and frozen filenames

To retire something, set its status — `declined`, `abandoned`, `wontfix`, `superseded`. Do
not delete the file. Deleting erases the trail of what was considered and rejected, which is
usually the most useful thing in the tree six months later.

**Once a proposal leaves `draft`, its filename is frozen.** People tip an id; renaming it
orphans the tips. If the framing changes, retitle in the body and leave the filename
alone. (Not yet machine-checked — it needs a CI step comparing against `main`.)
