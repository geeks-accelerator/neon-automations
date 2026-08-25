---
name: neon-docs
description: Maintain a project's docs/ tree — create and validate research, decisions, proposals, plans, issues, and observations with correct dated ids, frontmatter, cross-links, and generated navigation. Use this skill whenever work touches anything under docs/: looking something up externally and writing down what you found, recording a decision and why, opening a proposal, drafting a plan, filing a bug, capturing something that surprised you or cost you debugging time, closing an issue, or marking a plan shipped. Also use it before committing any change under docs/, when a docs check is failing, or when asked what any of these records should look like. Reach for it even when the docs tree is not named — "we should write that down", "file this", "what did we learn", "look into X and write it up" all land here.
---

# neon-docs

Maintains `docs/` for any project in the registry, and for the registry itself. The structure is not filing for its own sake — it
is what makes the work legible enough to review, attest, and fund. A plan you cannot cite is
a plan you cannot prove shipped, and proposals are read by the platform as data, so drift
breaks a running system rather than merely annoying a reader.

## Before committing anything under docs/

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --fix
```

Every check it performs, with the remedy for each, is in
[`references/checks.md`](references/checks.md). Read that when a run fails and the message
alone is not enough.

Exit 0 is clean. Run it after every change — the failures it catches (a plan pointing at a
proposal that does not exist, an id that disagrees with its filename, a filename date that
contradicts its frontmatter)
are cheap now and expensive once something reads the tree.

## Two kinds of document

Nearly everything else follows from which one you are writing.

| | | naming | how it changes |
|---|---|---|---|
| **Events** | `decisions` `issues` `proposals` `plans` `observations` `research` `rounds` | `2026-08-23-slug.md` | **accrete** — status advances, notes append, records are superseded or closed by newer ones |
| **Living** | `architecture` `vision` `pitch` | `repo-topology.md` | **overwritten** — paragraphs that stop being true are deleted |

An event happened on a day, for reasons true at the time, with alternatives that were live
at the time. Its *account of what happened* is never rewritten. Status may advance from
`open` to `fixed`, and a recurrence note may be appended — but you do not go back and edit
what you said happened. The call that turned out wrong is the most useful thing in the tree
later, and editing it away is how a team forgets why it stopped doing something.

A living document describes what currently *is*. It carries no date, because a date implies
a snapshot frozen at that moment — the opposite of a document whose job is to stay true.
When the system changes, rewrite it; delete what is no longer the case.

**Events accrete. Living documents get overwritten.** The validator enforces the boundary in
both directions: a dated filename in a living directory is an event filed in the wrong place,
and so is an `opened:`, `status:`, or `decided:` field there.

Living documents cite the events that produced them — `architecture` cites `decisions`,
`vision` cites `proposals`, `pitch` cites `research` — and those ids must resolve. That link
is why the split is worth having: the synthesis stays traceable to the record, so a reader who
disagrees with how something works can find out why it was chosen without asking anyone.

**The classification is total.** The seven event directories are the complete list of where
events live. *Everything else in the repo is a living document* — both `README.md`s, every
directory README, `CLAUDE.md`, this file, and the founding docs wherever they are filed. None
of them carry dates in their filenames, and all of them get rewritten in place.

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
| `docs/rounds` | a turn of the funding loop is opened, posted, or resolved |
| `docs/architecture` | describing how the system currently works |
| `docs/vision` | describing a future state nobody has committed to |
| `docs/pitch` | the claims ledger and the narrative a project can defend |

**Eight of the ten are required; `rounds/` and `pitch/` are not.** The eight are the shape of
the record and every project keeps them, empty or not. The other two are the output of
raising funding rounds — most projects never do, and this registry never will. They are held
to their schema when present and absent without complaint.

The cost of that exemption is that these are the first directories whose absence carries no
information: *missing, or not applicable?* is a question the tree cannot answer. Taken over
every project carrying an empty `pitch/` for a pitch it will never write.

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
2. **Set `id`** to the filename stem, and the date field (`opened`, `first_seen`,
   `decided`, or `conducted`) to the date in the filename. The validator checks both agree — a file whose
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

## Research records

`docs/research/` holds dated scans of external fact. They are events: a scan says what was
knowable *then*, so rewriting one strands every decision that cited it. Supersede instead.

A decision may carry `research: [...]`, and those ids must resolve — that edge keeps a choice
anchored to evidence that cannot shift underneath it. **Research before decision**: facts a
choice turns on belong in `research/` with the decision citing them, because numbers written
straight into an argument bury the evidence inside it.

**How to conduct one** — separating findings from implications, recording method, what an
absence means — is the [`research`](../research/SKILL.md) skill. This file owns the record
shape only.

## Open questions, and the preflight gate

A record can declare what it does not yet know:

```yaml
needs_research: [distribution-and-audience-floor]
```

A research scan closes it:

```yaml
answers: [distribution-and-audience-floor]
```

Anything unmatched is an **open question**, and the validator warns on it every run.

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --preflight
```

Lists every open question with the record that raised it, and **exits non-zero if any
remain**. Run it before producing anything that commits to a position — a pitch, a round's
ask, a launch. The point is to stop shipping on an assumption that twenty minutes of
searching would have corrected.

**Why slugs rather than prose.** "We should look into X" written in a paragraph is invisible
to a tool, which makes the check a thing to remember rather than a thing that happens. A slug
is greppable, stable, and can be matched against the scan that answers it — so the gate is
mechanical, and closing a question is an edit to a record rather than a judgement call.

Two honest ways to clear one: write the scan, or **drop the need because it stopped
mattering**. The second is legitimate and should be used — a question that no longer bears on
the decision is noise, and carrying it forward makes the gate something people learn to
override.

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

## Three rules enforced against history

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --since origin/main
```

**Records are never deleted** — retire with a status instead. Deleting erases the trail of
what was considered and rejected, which is usually the most useful thing in the tree later.

**A proposal's filename freezes when it leaves `draft`** — people tip an id, and renaming
orphans the tips. Retitle in the body instead. Renaming while still `draft` is fine, because
nothing is attached yet.

**A round's `threshold:` freezes when it leaves `draft`** — the same shape as the filename
rule, for the same reason: something the public acted on cannot be quietly revised. A
threshold edited after posting is a threshold chosen after seeing the result, which is not a
threshold. Tuning it while still `draft` is fine.

All three run in CI against the base branch. They need history the tree does not carry, which
is why they are a separate flag rather than part of the default run.

## Links that cross a repo boundary

A relative link that crosses a **symlink** or reaches **into a submodule** resolves on disk
and 404s for anyone reading on GitHub — the web UI renders a symlink as a text blob and does
not follow deep paths into a submodule. The validator errors on both.

**Link the target repo's URL instead.** This applies to anything pointing at
`.claude/skills/...` (a symlink) or at another project's docs from the registry (a
submodule).

The general form is worth carrying: a link checker validates a filesystem, but readers
navigate a rendering, and the two diverge wherever the rendering does not follow the
filesystem's indirections.

## Signing

Commits are SSH-signed and the config is **repo-local**, which means a fresh clone or a newly
added submodule inherits none of it — and git does not warn when signing is simply not
configured. The validator warns when `HEAD` is unsigned in a repo that ships
`.allowed_signers`, since shipping that file is the declaration that signing is expected
here.

```bash
git config gpg.format ssh && git config user.signingkey ~/.ssh/id_ed25519.pub \
  && git config commit.gpgsign true
```

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

Most projects accumulate a handful of long documents that state the whole idea — what it is,
how it works, what already exists, how the work gets done. They are **living documents**:
rewritten in place as thinking changes, with no dates and no supersession banners. Git holds
what they used to say.

**File them whole, and file them by lifecycle.** A founding document that describes where the
project is going belongs in `vision/`; one that synthesizes how the system works today belongs
in `architecture/`. What matters is that they move **intact**. These documents are usually
part architecture, part product design, part governance all at once, and splitting one by
subject destroys more than it organizes — so a directory holds whole documents, never the
pieces of one.

**Do not number the filenames**, even when the documents were written in sequence and each
assumes the last. A numeric prefix is a merge conflict waiting for the second agent to add a
document to the same directory, and it goes stale the moment one is inserted in the middle —
both of which cost more than the ordering is worth in a tree several agents share.

The generated index sorts a living directory alphabetically, so it is a *list*, not an order.
Put the reading order in the directory README, below the generated block where `apply_readme`
preserves it. Changing the order is then one edit instead of N renames plus every reference
that named a number.

Filenames are plain lowercase slugs — `concept.md`, not `01-CONCEPT.md`. `LIVING_NAME_RE`
rejects the uppercase form outright, so this is checked rather than merely conventional.

### The test for a living directory

Before adding a file to `architecture/` or `vision/`, ask:

> **Does this document ever get to be *done*, or can it only ever become *untrue*?**

A living document carries no `status`, no dates, and no terminal state — `collect_living`
errors on `status`, `opened`, and `decided` outright. So a file here **cannot close**. It has
two exits: rewritten, or deleted.

That fits a stance and breaks an initiative. Anything with a lifecycle goes in an event
directory, where `status` exists and `shipped` is expressible. Get it backwards and the
directory fills with one permanent file per initiative, none of which is allowed to end —
which is the failure mode this test exists to catch, because nothing in the validator will.

**The same test applies to the filename.** Name a living document for its *job*, not for the
stage it currently describes — `scope.md`, not `mvp-scope.md`; `repo-topology.md`, not
`three-repo-topology.md`. The stage is content, and content here gets rewritten; the filename
is identity, and every inbound reference depends on it holding. A name that encodes the
current stage guarantees a rename the day that stage ends, which is the one edit a living
directory exists to avoid.

**A scope boundary is the case worth naming**, because it reads like an epic and is not one.
"Where the first build stops" never completes; either it holds or the boundary moves and you
rewrite the sentence. It is also singular — a project has one, not one per initiative.

Its work list is not a backlog, and it does not become one. An epic in a tracker owns its
children; here the tippable unit is a `proposals/` entry, and **a proposal's only child link
is `plans:`** — so a boundary composed of proposals cannot itself be a proposal. The edge that
does exist points the other way: `LIVING = {"vision": {"cites": ("proposals", "proposals")}}`.
Put `proposals: [...]` in the boundary's frontmatter and the validator checks every id
resolves. That is the containment, and it needs no new directory.

When a passage in them stops holding and the *reasoning* is worth keeping, write a
`decisions/` entry and cite it from the prose. Do not leave a superseded banner in place —
that is an event log stuffed inside a living document, which is the conflation these two
categories exist to prevent.
