# What the validator enforces

Every check `scripts/validate.py` performs, with the remedy for each. **Errors** fail the run
and fail CI. **Warnings** print and pass — they are nudges, not defects. A few checks block
only under `--preflight`.

Derived from the source; if the two disagree, the source is right and this file is a bug.

**One structural limit, worth knowing before you read the rest.** `entries()` lists each
directory one level deep, so a *subdirectory* under an event directory is checked by nothing
here — not naming, not frontmatter, not cross-references. That is deliberate: a corpus filed
under `docs/research/` is not N research records and should not need N dated filenames. It now
warns once per directory naming what is skipped, because invisible and silent are different
things, and a record misfiled one level down used to look validated.

---

## Naming and identity

| check | level | remedy |
|---|---|---|
| Event filename is `YYYY-MM-DD-slug.md` | error | rename; events are dated because they happened on a day |
| Event `id` matches the filename stem | error | make them agree — a file disagreeing with itself is unusable to anything reading the tree |
| Filename date matches the record's date field (`opened` / `decided` / `conducted` / `first_seen`) | error | fix whichever is wrong |
| Living filename is a plain lowercase slug, no date prefix | error | `LIVING_NAME_RE` is `^[a-z0-9][a-z0-9-]*\.md$` — **uppercase is rejected**, so `01-CONCEPT.md` fails inside a living directory |
| Living filename encodes a stage rather than a job | *not checked* | judgement, not a rule — but `mvp-scope.md` goes stale the day the boundary moves, and renaming it costs every inbound reference |
| Living record carries no `opened` / `status` / `decided` | error | same — those fields mean it is an event |
| No dated file at the `docs/` root | error | move it into an event directory |

## Fields and vocabularies

| check | level | remedy |
|---|---|---|
| Required fields present for the type | error | see [schemas.md](schemas.md) |
| `status` is in the type's vocabulary | error | see [schemas.md](schemas.md) |
| `severity` is in `low` / `medium` / `high` | error | issues only |
| `pitch_mode` is `full` / `turn` | error | rounds only |
| Dates are real ISO dates | error | `YYYY-MM-DD` |
| Research `mode` is a known mode | error | add it to `RESEARCH_MODES` if it is a genuinely new kind of fact |
| Research `current` with no `sources` | warn | research nobody can re-check is an assertion |
| Research `current` with no `mode` | warn | staleness cannot be checked without one |
| A scan that `opens:` and `answers:` the same slug | error | a question raised and closed in one document was never open |

## Cross-references — all must resolve

`plan.proposal` · `issue.observation` · `decision.supersedes` · `decision.research` ·
`research.supersedes` · `architecture.decisions` · `vision.proposals` · `pitch.research` ·
`round.claims` and `round.demoted` (against the rows of `docs/pitch/claims.md`)

All errors. A dangling reference means either a typo or a record that was deleted instead of
retired.

**`rounds/` and `pitch/` are optional**: their absence is not an error, because they are the
output of raising funding rounds and most projects never do. Present means held to schema.

## Semantics

| check | level | remedy |
|---|---|---|
| A `shipped` plan has a `release` tag | error | the attestation service reads it; without one, delivery cannot be proven |
| A `building` / `shipped` proposal has an approved plan | error | draft one, or the status is ahead of reality |
| A proposal carries no `tips` / `tips_usd` | error | tips live in the platform database; two systems owning one number is a reconciliation bug |
| Observation `n` is an integer ≥ 1 | error | a sighting count starts at 1 |
| Observation `last_seen` ≥ `first_seen` | error | |
| Observation at `n: 1` whose prose says "always" / "never" | warn | one sighting is an instance, not a rule — wait for recurrence |
| Round `turn` is an integer ≥ 1, unique across rounds | error | the ordinal is how rounds get referred to |
| A `posted` (or later) round has a `threshold:` | error | it is written before posting — a number chosen after seeing the result is not a threshold |
| A `passed` / `failed` / `inconclusive` round has a `result:` | error | the outcome is what the record holds next to the threshold |
| `docs/pitch/` exists with a `claims.md` | error | every claim originates in the ledger; a pitch tree without one cannot hold the round invariant |
| Every `\| C-NNN \|` row in `claims.md` carries exactly one provenance tag | error / warn | untagged is an error; two tags warn — only a composite built from existing rows may carry both, with its counting convention declared |
| Claim ids in `claims.md` are unique | error | ids are what rounds cite; two rows answering to one id makes every citation ambiguous |

Rows inside fenced code blocks in `claims.md` are **not** parsed — a fenced example is
documentation about the format, not a claim. Without that guard the ledger's own "how to
write a row" section would error as a duplicate id, the recorded pattern of marker-matching
tools eating the documents that describe them.

## Links

| check | level | remedy |
|---|---|---|
| Relative links resolve on disk | error | fix or remove |
| No relative link crosses a **symlink** | error | link the target repo's URL — GitHub renders a symlink as a text blob, so it 404s on the web |
| No relative link reaches **into a submodule** | error | link the target repo's URL — the web UI 404s on deep paths into one |
| Link text names a `.md` file the link does not point at | warn | retitle, or fix the target — a citation naming one document and pointing at another. Fires only when the text contains something filename-shaped, so prose text ("the decision", "here") is never a candidate |
| An absolute `github.com/<org>/<repo>/blob/…` URL whose repo is checked out locally, whose path is missing there | warn | the other side renamed something. Warn and not error because the local checkout sits at whatever commit its pointer names, not necessarily the `<ref>` in the URL |

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
| A directory README has content but no `index:begin`/`index:end` markers | error | add the marker pair where the index belongs. **This errors under `--fix` too** — regeneration refuses rather than rewriting a file it cannot parse, because the alternative is destroying hand-written content silently. An *empty* README is the bootstrap path and is filled normally |

`--fix` regenerates **before** validating, so it can always recover from its own output. That
ordering is load-bearing: a deleted record leaves a dangling link in a generated index, and
gating regeneration on a clean run would make the one command that repairs it refuse to run.

## History rules — `--since REF` only

Applied when comparing against a base ref, because the tree alone cannot show them.

**Both ways they can fail to run now say so.** An unresolvable base is skipped deliberately —
a new branch has nothing to compare against — and warns. A base that resolves and then fails
to diff also warns, where it used to return silently: all three rules stopping with no output
is the one way a gate switches itself off without anyone noticing.

| check | level | remedy |
|---|---|---|
| No record deleted from an event directory | error | retire with a status — `declined`, `abandoned`, `wontfix`, `superseded` |
| A proposal's filename is unchanged once it left `draft` | error | retitle in the body and leave the filename; people tip an id, and renaming orphans the tips |
| A round's `threshold:` is unchanged once it left `draft` | error | it froze at posting; revising it to match the result is the failure the field exists to prevent — renaming the file in the same commit does not evade this |

Renaming a proposal **while still `draft`** is allowed — nothing is attached to it yet, and
the same applies to tuning a draft round's threshold: both freeze at the moment they go
public, not before.

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
| A `current` scan's `opens:` slug with no answering scan | same — a gap a scan surfaced gates until chased or dropped |
| A `current` scan past its mode's horizon | re-run that mode and supersede, or set `status: superseded` |

An answering scan must be `current` — a superseded scan's `answers:` no longer count,
because an expired answer is not an answer.

Staleness warns on ordinary runs and blocks here. A build that breaks because a date passed,
with nothing changed, is a bad CI signal — but committing publicly to expired numbers is
worse, and this is the gate in front of doing that.
