# neon-automations

Shared agent tooling for the [`code-neon`](https://github.com/geeks-accelerator/code-neon)
registry. **One definition, used by the registry and every project in it.**

```
claude/
├── CLAUDE-shared.md          conventions block, duplicated into each CLAUDE.md and checked
└── skills/
    ├── neon-docs/            record shapes: conventions, schemas, the validator
    ├── research/             method: dated, sourced scans that decisions cite
    └── pitch/                evidence and production: the claims ledger, two modes
link-skills.py                creates and repairs the symlinks into projects
tests/fixture/                a minimal valid tree; the validator's executable spec
```

## Why this is public

It was private, inside the registry, and reached by symlink. That worked locally and broke
the moment CI cloned a project on its own: the link dangles in a standalone checkout, so
every project's CI needed a cross-repo credential just to run a **docs validator**.

Nothing here is sensitive — a Python script with no dependencies, a skill file, and a
conventions block. Making it public turns a standing secret, an org approval flow, and a
rotation problem into a `git clone`. The actual work stays private in the projects.

## Using it

As a submodule at `automations/`, with each project symlinking
`.claude/skills/<name>` at it:

```bash
python3 automations/link-skills.py --all   # every project, plus the registry itself
```

## The validator

```bash
python3 .claude/skills/neon-docs/scripts/validate.py        # check
python3 .claude/skills/neon-docs/scripts/validate.py --fix  # regenerate navigation
```

It locates a project root by walking up from the working directory, so one copy serves every
tree. Conventions it enforces are documented in
[`claude/skills/neon-docs/SKILL.md`](claude/skills/neon-docs/SKILL.md).
