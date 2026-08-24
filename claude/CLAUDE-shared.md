## Docs conventions

Two kinds of document, and nearly everything follows from which one you are writing.

| | | naming | how it changes |
|---|---|---|---|
| **Events** | `decisions` `issues` `proposals` `plans` `observations` | `2026-08-23-slug.md` | **accrete** — status advances, notes append, records get superseded |
| **Living** | `architecture` `vision` | `repo-topology.md` | **overwritten** — what stops being true is deleted |

Everything outside the five event directories is a living document: both READMEs, every
directory README, this file, and any founding docs at the root of `docs/`. Git is their
event log, so superseded passages get rewritten rather than banner-marked; reasoning worth
keeping on its own earns a `decisions/` entry.

**Retire, don't delete.** Set a status — `declined`, `abandoned`, `wontfix`, `superseded`.
Deleting erases the trail of what was considered and rejected, which is usually the most
useful thing in the tree six months later.

**Observations need evidence and an N-count.** Point at `file:line`, a commit SHA, or test
output. A first sighting is `n: 1` — an instance, not a rule. Do not write "always" until it
has recurred.

**Registry level or project level.** Does it apply to one project, or to every project?
Applies to the system → the registry's `docs/`. Applies to that project → that project's.

## Before committing

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --fix
```

`--fix` regenerates navigation. A plain run fails on schema errors, broken links, and stale
navigation — and so does CI, which never auto-fixes, because a workflow that silently
regenerated would turn a loud failure into a quiet one.

**Commits are SSH-signed.** The registry's commit history is the delivery ledger, so
signatures are load-bearing rather than cosmetic. `.allowed_signers` ships in each repo so
anyone can verify from a clone.

**Skills are symlinked from the registry's `automations/`.** Edit them there, never through
the link — a change made through a link still lands in the registry, but a change made to a
project's own copy silently forks the tooling.
