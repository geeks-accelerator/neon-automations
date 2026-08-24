---
name: neon-docs
description: Maintain the LiveNeon docs/ tree — create proposals, plans, issues, observations, and ADRs with correct IDs, frontmatter, and cross-links, then validate the whole tree. Use this skill whenever work in this repo touches anything under docs/ — opening a proposal, drafting a plan, filing a bug, recording something that surprised you or cost you debugging time, writing an architecture decision, closing an issue, or marking a plan shipped. Also use it before committing any change under docs/, when a docs check is failing, or when asked what a proposal, plan, or observation should look like. Reach for it even when the user does not name the docs tree explicitly — "we should write that down", "file this", "what did we learn" all land here.
---

# neon-docs

Maintains `docs/` for a LiveNeon project. The structure is not filing for its own sake — it
is what makes the work legible enough to review, attest, and fund. A plan you cannot cite is
a plan you cannot prove shipped, and proposals are read by the platform as data, so drift
breaks a running system rather than merely annoying a reader.

## Before committing anything under docs/

```bash
python3 .claude/skills/neon-docs/scripts/validate.py
```

Exit 0 is clean. Run it after every change — the failures it catches (a plan pointing at a
proposal that does not exist, an id that disagrees with its filename, a filename date that
contradicts its frontmatter)
are cheap now and expensive once something reads the tree.

## Two kinds of document

Nearly everything else follows from which one you are writing.

| | | naming | how it changes |
|---|---|---|---|
| **Events** | `decisions` `issues` `proposals` `plans` `observations` `research` | `2026-08-23-slug.md` | **accrete** — status advances, notes append, records are superseded or closed by newer ones |
| **Living** | `architecture` `vision` | `repo-topology.md` | **overwritten** — paragraphs that stop being true are deleted |

An event happened on a day, for reasons true at the time, with alternatives that were live
at the time. Its *account of what happened* is never rewritten. Status may advance from
`open` to `fixed`, and a recurrence note may be appended — but you do not go back and edit
what you said happened. The call that turned out wrong is the most useful thing in the tree
later, and editing it away is how a team forgets why it stopped doing something.

A living document describes what currently *is*. It carries no date, because a date implies
a snapshot frozen at that moment — the opposite of a document whose job is to stay true.
When the system changes, rewrite it; delete what is no longer the case.

**Events accrete. Living documents get overwritten.** The validator enforces the boundary in
both directions: a dated filename in `architecture/` or `vision/` is an event filed in the
wrong place, and so is an `opened:`, `status:`, or `decided:` field there.

Living documents cite the events that produced them — `architecture` cites `decisions`,
`vision` cites `proposals` — and those ids must resolve. That link is why the split is worth
having: the synthesis stays traceable to the record, so a reader who disagrees with how
something works can find out why it was chosen without asking anyone.

**The classification is total.** The six event directories are the complete list of where
events live. *Everything else in the repo is a living document* — both `README.md`s, every
directory README, `CLAUDE.md`, this file, and the numbered founding docs at the root of
`docs/`. None of them carry dates in their filenames, and all of them get rewritten in place.

**Git is the event log for living documents.** The commit history is already append-only,
signed, and complete, so there is no need to mark superseded passages in place — rewrite the
document, and let the history hold what it used to say. When superseded reasoning is worth
reading on its own, it earns a `decisions/` entry rather than a banner in the prose.


## The artifacts

| Directory | Create one when |
|---|---|
| `docs/proposals` | work is being *proposed* for the community to tip |
| `docs/plans` | an approved proposal needs implementation detail |
| `docs/issues` | something is broken or behaves unintendedly |
| `docs/observations` | something surprised you or cost debugging time |
| `docs/research` | you looked something up externally and the answer shapes a choice |
| `docs/decisions` | a non-obvious, hard-to-reverse choice is made |
| `docs/architecture` | describing how the system currently works |
| `docs/vision` | describing a future state nobody has committed to |

For events, the filename stem *is* the id, and the date in it must match the record's date
field. The directory carries the type, so no prefix is needed.

**Why dates and not sequential numbers.** A counter needs a coordinator. Two branches opened
before either merges will both take the next number — the normal case here, since outside
contributors open proposals concurrently — and renumbering to resolve it breaks every
inbound reference. A date plus a slug needs no coordinator and collides only when two people
pick the same title on the same day, which is a real conflict worth surfacing rather than an
accidental one.

Full frontmatter schemas: [`references/schemas.md`](references/schemas.md). Read it before
writing a file rather than guessing — the fields are few but the validator is strict about
them.

## Creating a file

1. **Name it** `YYYY-MM-DD-lowercase-slug.md`, dated the day it is opened. The slug
   describes the thing, not the category — `2026-08-23-tip-weighted-backlog.md`, not
   `2026-08-23-proposal.md`.
2. **Set `id`** to the filename stem, and the date field (`opened`, `first_seen`, or
   `decided`) to the date in the filename. The validator checks both agree — a file whose
   name and contents disagree about its own identity is unusable to anything reading the
   tree programmatically.
3. **Write the frontmatter** per the schema, with `id` matching the filename.
4. **Write the body.** Prose, not a form. The frontmatter is for machines; the body is for
   the person who finds this in six months and needs to know what you were thinking.
5. **Link it up.** A plan names its proposal. A closed issue names the observation it
   produced, or says explicitly that it produced none.
6. **Validate.**

## What earns an observation

The highest-leverage habit in this tree, and the easiest to skip.

Whenever something surprises you — a silent failure, a library that lied, a fix that took
four hours because the error pointed the wrong way — write it down so the next agent does
not spend those hours again. The corpus is read by agents at work; each entry is a trap
already sprung.

Two rules make them worth reading:

**Evidence, not conclusions.** Point at ground truth: `file:line`, a commit SHA, test
output, a dated session. *"Prefer X over Y"* is a bare prior. *"Prefer X over Y — hit Y's
failure at `src/foo.ts:214` on 2026-08-23, query silently truncated at 1000 rows, commit
`a1b2c3d`"* is an artifact someone can re-check.

**Recurrence, not premature generalization.** A first sighting is `n: 1` — a specific
instance, not a rule. Do not write "always" on the strength of one afternoon. When it
happens again, increment `n`, update `last_seen`, and append a dated note with fresh
evidence rather than rewriting the original account. One bad afternoon must not become a
standing multi-file gate.

Closing an issue without asking *what should this have taught us* is the most common way a
team pays the same debugging cost twice.

## Research is dated evidence

A scan records **external reality at a moment in time**, so it is an event: prices move,
competitors pivot, and the value of the record is that it says what was knowable *then*.

Rewriting one in place strands every decision that cited it — a later reader finds reasoning
resting on numbers that appear nowhere, unable to tell whether the decision was wrong or
merely overtaken. When the world moves, write a new scan with `supersedes:` and set the old
one to `superseded`. Both stay.

Every claim carries a source; the validator warns when a `current` scan lists none, because
research nobody can re-check is an assertion wearing a lab coat. Record the **method** too —
what was searched, what was excluded, what could not be found. An absence of evidence is a
finding, and it is the first thing a later reader needs before repeating the work.

A decision may carry `research: [...]`, and those ids must resolve. That edge is why the two
directories are separate: a choice stays anchored to dated evidence that cannot shift
underneath it.

## What earns a decision record

A choice that was not obvious, had a live alternative, and will be expensive to reverse.
All three. Recording something nobody would have done differently is noise, and noise trains
people to stop reading the directory.

Write the consequences you *do not* like. A decision record listing only benefits is
marketing, and the reader six months from now needs the cost you accepted, because they are
probably paying it.

## Proposals are a product surface

Not documentation. A proposal is a unit of work the community can tip; tips set the backlog
order, and the agent works funded proposals in tip order until the round's budget is spent.
The platform reads these files through the same GitHub App that does attestation.

So: **never put a tip total in frontmatter.** Tips attach to the `id` in the platform
database. A number owned by both a database and a markdown file is a reconciliation bug with
a fraud surface attached, and the validator rejects `tips`/`tips_usd` on sight.

A proposal may carry pre-drafted plans submitted for approval alongside it, or plans may be
drafted after approval. Both are normal. The only invariant is that a plan names the
proposal it serves — a plan without one is work nobody asked for and nobody funded.

## Retiring things

Set a status: `declined`, `abandoned`, `wontfix`, `superseded`. **Do not delete files.**

Deleting erases the trail of what was considered and rejected, which is usually the most
useful thing in the tree six months later. A status costs one line and keeps it.

**Once a proposal leaves `draft`, treat its filename as frozen.** People tip an id; renaming
it out from under them orphans the tips. Retitle in the body if the framing changes, and
leave the filename alone.

## Generated navigation

Every file carries two generated blocks: a `**Parent:**` breadcrumb after the H1, and a
`## Related` / `## Next` block at the end. Both are **derived from the frontmatter graph and
never hand-written** — hand-maintaining them would just relocate the drifting-map problem
into the files.

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --fix
```

`--fix` regenerates. A plain run **fails** when any block is out of date, because stale
links are worse than no links: they build false trust. Change a status and the next steps
change with it, so the check fires on ordinary edits rather than only on renames.

**Related** renders both directions. Forward edges come from frontmatter — a plan
`Implements` its proposal, an architecture doc `Derives from` a decision. Back edges are
computed, which is the part worth having: a proposal lists the plans that implement it, a
decision lists what cites it, an observation lists the issue that reported it. One-way links
are a named anti-pattern, and every forward edge here gets its reverse.

**Next** is state-driven off the status vocabularies, which are already a state machine.
Each action carries a reason rather than only a what, because consumers — agents especially
— act on why. A funded proposal with no plan says so; a fixed issue with no observation says
so; a decision nothing cites says the synthesis has not caught up.

**No dead ends, and no invented ones.** Where there genuinely is no action — a proposal
waiting on tips, an observation at `n: 1` — the block says why the stop is correct. A
fabricated next step is a worse dead end than an honest one.

Edit prose freely; the blocks are rewritten in place and never merge with your text.

## CI

Every repo runs the validator on pull requests and pushes to `main`
(`.github/workflows/docs.yml`). It fails on schema errors, broken links, and stale
navigation; warnings print without failing, since they are nudges rather than defects.

CI never auto-fixes. A workflow that silently regenerated and committed would turn a loud
failure into a quiet one, which is the wrong direction — the run tells you to run `--fix`
and stops.

This tooling lives in a **public** repo, so CI fetches it with no credential. It was
private and symlinked from the registry until that cost two rounds of token debugging for a
docs validator; making it public turned a standing secret into a `git clone`.

## Registry level or project level

The registry has a `docs/` tree of its own, with the same two categories. Which one a record
belongs in comes down to one question:

> **Does it apply to one project, or to every project?**

Applies to the system → the registry. Applies to that project → that project.

A decision about submodule topology or the shared tooling governs every tenant, so filing it
in a tenant means the next project never sees it. A decision about one project's product
mechanics binds nobody else and belongs with that project.

Observations are the case most often filed wrong. An observation about a library that lied
to *this* project is project-level; an observation about a constraint every contributor on
every project will hit is registry-level. When in doubt, ask who would be worse off for not
having read it.

## The founding docs

`docs/01-CONCEPT.md` through `05-MVP-SCOPE.md` sit at the root of `docs/`. They are **living
documents** — rewritten in place as thinking changes, with no dates and no supersession
banners. Git holds what they used to say.

They stay at the root rather than being filed into subdirectories because the split is by
lifecycle, not by topic, and `04-OPERATING-MODEL` alone is part architecture, part product
design, part governance. Decomposing it by subject would destroy more than it organizes.

When a passage in them stops holding and the *reasoning* is worth keeping, write a
`decisions/` entry and cite it from the prose. Do not leave a superseded banner in place —
that is an event log stuffed inside a living document, which is the conflation these two
categories exist to prevent.
