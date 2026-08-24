# What the validator enforces

Every check `scripts/validate.py` performs, with the remedy for each. **Errors** fail the run
and fail CI. **Warnings** print and pass — they are nudges, not defects. A few checks block
only under `--preflight`.

Derived from the source; if the two disagree, the source is right and this file is a bug.

---

## Naming and identity

| check | level | remedy |
|---|---|---|
| Event filename is `YYYY-MM-DD-slug.md` | error | rename; events are dated because they happened on a day |
| Event `id` matches the filename stem | error | make them agree — a file disagreeing with itself is unusable to anything reading the tree |
| Filename date matches the record's date field (`opened` / `decided` / `conducted` / `first_seen`) | error | fix whichever is wrong |
| Living filename is a plain slug, no date prefix | error | a dated record is an event; move it to an event directory |
| Living record carries no `opened` / `status` / `decided` | error | same — those fields mean it is an event |
| No dated file at the `docs/` root | error | move it into an event directory |

## Fields and vocabularies

| check | level | remedy |
|---|---|---|
| Required fields present for the type | error | see [schemas.md](schemas.md) |
| `status` is in the type's vocabulary | error | see [schemas.md](schemas.md) |
| `severity` is in `low` / `medium` / `high` | error | issues only |
| Dates are real ISO dates | error | `YYYY-MM-DD` |
| Research `mode` is a known mode | error | add it to `RESEARCH_MODES` if it is a genuinely new kind of fact |
| Research `current` with no `sources` | warn | research nobody can re-check is an assertion |
| Research `current` with no `mode` | warn | staleness cannot be checked without one |

## Cross-references — all must resolve

`plan.proposal` · `issue.observation` · `decision.supersedes` · `decision.research` ·
`research.supersedes` · `architecture.decisions` · `vision.proposals`

All errors. A dangling reference means either a typo or a record that was deleted instead of
retired.

## Semantics

| check | level | remedy |
|---|---|---|
| A `shipped` plan has a `release` tag | error | the attestation service reads it; without one, delivery cannot be proven |
| A `building` / `shipped` proposal has an approved plan | error | draft one, or the status is ahead of reality |
| A proposal carries no `tips` / `tips_usd` | error | tips live in the platform database; two systems owning one number is a reconciliation bug |
| Observation `n` is an integer ≥ 1 | error | a sighting count starts at 1 |
| Observation `last_seen` ≥ `first_seen` | error | |
| Observation at `n: 1` whose prose says "always" / "never" | warn | one sighting is an instance, not a rule — wait for recurrence |

## Links

| check | level | remedy |
|---|---|---|
| Relative links resolve on disk | error | fix or remove |
| No relative link crosses a **symlink** | error | link the target repo's URL — GitHub renders a symlink as a text blob, so it 404s on the web |
| No relative link reaches **into a submodule** | error | link the target repo's URL — the web UI 404s on deep paths into one |

The last two exist because a filesystem check passes links that are dead for anyone browsing
on GitHub. See the observation on
[web-invisible links](https://github.com/geeks-accelerator/code-neon/blob/main/docs/observations/2026-08-24-filesystem-link-checks-miss-web-invisible-links.md).

## Generated content

| check | level | remedy |
|---|---|---|
| Navigation blocks current | error | `--fix` |
| Directory README indexes current | error | `--fix` |
| `CLAUDE.md` shared block matches `automations/claude/CLAUDE-shared.md` | error | `--fix` |
| `CLAUDE.md` has no shared block at all | warn | add one, or opt out deliberately |

`--fix` regenerates **before** validating, so it can always recover from its own output. That
ordering is load-bearing: a deleted record leaves a dangling link in a generated index, and
gating regeneration on a clean run would make the one command that repairs it refuse to run.

## Repository hygiene

| check | level | remedy |
|---|---|---|
| `HEAD` is signed in a repo shipping `.allowed_signers` | warn | configure signing in this working copy — it is repo-local and does not survive a clone |

Presence check only, no verification, so a CI runner without signing config cannot
false-positive. Warning rather than error because GitHub synthesizes PR merge refs unsigned.

## `--preflight` only

All three block with a non-zero exit; the last two fail neither an ordinary run nor CI.

| check | remedy |
|---|---|
| Any validation error | fix it first — a gate that passes on a broken tree is no gate, and "preflight clean" must never be printable over a tree the plain run rejects |
| Open `needs_research` with no answering scan | write a scan whose `answers:` lists the slug, or drop the need if it stopped mattering |
| A `current` scan past its mode's horizon | re-run that mode and supersede, or set `status: superseded` |

An answering scan must be `current` — a superseded scan's `answers:` no longer count,
because an expired answer is not an answer.

Staleness warns on ordinary runs and blocks here. A build that breaks because a date passed,
with nothing changed, is a bad CI signal — but committing publicly to expired numbers is
worse, and this is the gate in front of doing that.
