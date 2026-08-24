# CLAUDE.md — neon-automations

**The authoritative tooling.** Every project in the
[`code-neon`](https://github.com/geeks-accelerator/code-neon) registry — and the registry
itself — consumes this repo: skills by symlink, the shared conventions block by checked
duplication, CI by fetching `main`.

That last part is the standing hazard to respect: **consumers track `main`, so a defective
push here breaks every project's CI at once**, with no signal at the source beyond this
repo's own checks. Treat edits accordingly — this repo's blast radius is the whole registry.

## Editing rules

- **Edit here, never through a project's symlink or copy.** A change through the link lands
  here anyway; a change to a copy silently forks the tooling.
- **Skills live under `claude/skills/<name>/`** — `neon-docs` (record shapes, validator),
  `research` (method), `pitch` (production). The seam is shape vs. method: schemas and
  enforcement in `neon-docs`, procedure in the others.
- **`claude/CLAUDE-shared.md` is the canonical conventions block.** Each consuming repo
  carries a checked duplicate; after editing it, run `validate.py --fix` in every consumer.
- **Enforcement belongs in the validator, not in skill prose.** Skills instruct; the
  validator enforces. A rule that matters gets a check.

## After any change to the validator or nav

Run it in a consuming repo before pushing — the scripts resolve the project root from the
working directory and tooling assets through `realpath(__file__)`, and only a real consumer
exercises both:

```bash
cd ../  # the registry
python3 .claude/skills/neon-docs/scripts/validate.py --fix
```

CI here runs the same thing against `tests/fixture/`: warning-free validation, a clean
preflight, an idempotence check, a broken-tree rejection (plain **and** preflight), a
dynamic open-question gate test with the clock injected at runtime, and a check that every
research mode the validator defines is documented in the skill docs. Keep the fixture
minimal; it is the only executable spec of the validator.

## Commits are SSH-signed

Repo-local config, deliberately — and **a fresh clone or submodule checkout inherits none of
it**. Configure before the first commit in any new working copy:

```bash
git config gpg.format ssh && git config user.signingkey ~/.ssh/id_ed25519.pub \
  && git config commit.gpgsign true
```

`.allowed_signers` ships in the repo; the validator warns when HEAD is unsigned in a repo
that ships one.
