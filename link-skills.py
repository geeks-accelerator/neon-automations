#!/usr/bin/env python3
"""Link the authoritative skills into a project's .claude/skills/.

The registry holds one definition of each skill under automations/claude/skills.
Projects get symlinks to it rather than copies, so a fix lands everywhere at once
instead of drifting across N repos.

    python3 automations/link-skills.py live-neon
    python3 automations/link-skills.py --all

Links point at whole skill directories, not individual files. Per-file links
would mean that adding a reference or a script to a skill requires re-linking
every project that uses it; per-directory links propagate on their own.

Known limitation: a project cloned standalone -- without the registry above it --
gets dangling links, because the target lives in the parent repo. That is the
price of one definition, and the exit is already planned: once automations
becomes a submodule of each project, a recursive clone resolves it again.
"""
import argparse
import os
import sys

REGISTRY = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.dirname(REGISTRY)
SOURCE = os.path.join(REGISTRY, "automations", "claude", "skills")


def projects():
    # The registry has a docs/ tree of its own -- records about topology, shared
    # tooling, and the conventions every project inherits -- so it needs the
    # skill linked in like any tenant.
    yield "."
    for name in sorted(os.listdir(REGISTRY)):
        path = os.path.join(REGISTRY, name)
        if name.startswith(".") or name == "automations" or not os.path.isdir(path):
            continue
        if os.path.exists(os.path.join(path, ".git")):
            yield name


def link(project, dry_run=False):
    dest_dir = os.path.join(REGISTRY, project, ".claude", "skills")
    if not os.path.isdir(os.path.join(REGISTRY, project)):
        sys.exit(f"no such project: {project}")
    os.makedirs(dest_dir, exist_ok=True)

    for skill in sorted(os.listdir(SOURCE)):
        src = os.path.join(SOURCE, skill)
        if not os.path.isdir(src):
            continue
        dest = os.path.join(dest_dir, skill)
        rel = os.path.relpath(src, dest_dir)

        if os.path.islink(dest):
            if os.readlink(dest) == rel:
                print(f"  ok      {project}/.claude/skills/{skill}")
                continue
            if not dry_run:
                os.unlink(dest)
            print(f"  relink  {project}/.claude/skills/{skill} -> {rel}")
        elif os.path.exists(dest):
            # A real directory here means a project has its own copy. Refuse to
            # delete it: that copy may hold local edits nobody has upstreamed,
            # and silently discarding them is how you teach people not to trust
            # the tooling.
            print(f"  SKIP    {project}/.claude/skills/{skill} is a real directory, "
                  f"not a link. Move or merge it into automations/ first.")
            continue
        else:
            print(f"  link    {project}/.claude/skills/{skill} -> {rel}")

        if not dry_run:
            os.symlink(rel, dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("project", nargs="?",
                    help='project directory name, or "." for the registry itself')
    ap.add_argument("--all", action="store_true", help="every project in the registry")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(SOURCE):
        sys.exit(f"no skills found at {SOURCE}")
    targets = list(projects()) if args.all else ([args.project] if args.project else [])
    if not targets:
        ap.error("give a project name or --all")

    for project in targets:
        print(project)
        link(project, dry_run=args.dry_run)
    if args.dry_run:
        print("\n(dry run -- nothing changed)")


if __name__ == "__main__":
    main()
