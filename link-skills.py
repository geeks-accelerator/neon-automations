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


def source_for(project):
    """Prefer a project's own automations submodule over the registry's.

    A project carrying its own submodule pins the tooling at a SHA it controls
    and keeps its symlinks inside its own tree, so a standalone recursive clone
    resolves them. Linking such a project at the registry's copy would undo both:
    the link would escape the repo and the pin would stop meaning anything.
    """
    local = os.path.join(REGISTRY, project, "automations", "claude", "skills")
    if project != "." and os.path.isdir(local):
        return local
    return SOURCE


def link(project, dry_run=False):
    dest_dir = os.path.join(REGISTRY, project, ".claude", "skills")
    if not os.path.isdir(os.path.join(REGISTRY, project)):
        sys.exit(f"no such project: {project}")
    os.makedirs(dest_dir, exist_ok=True)
    source = source_for(project)
    if source != SOURCE:
        print(f"  (using {project}'s own automations submodule)")

    for skill in sorted(os.listdir(source)):
        src = os.path.join(source, skill)
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


def check_pins():
    """Report which repos are running behind the tooling's main.

    Deliberately a human-run report rather than a validator check. A gate that
    fails because someone else pushed upstream breaks builds with no local
    change -- the same shape as a staleness check against a static fixture, and
    the same reason it does not belong in CI.
    """
    import subprocess

    def git(cwd, *args):
        try:
            r = subprocess.run(["git", "-C", cwd, *args],
                               capture_output=True, text=True, timeout=20)
            return r.stdout.strip() if r.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None

    upstream = git(os.path.join(REGISTRY, "automations"), "ls-remote", "origin", "main")
    if not upstream:
        sys.exit("cannot reach the tooling remote")
    head = upstream.split()[0]
    print(f"tooling main  {head[:7]}\n")

    behind = 0
    for name in ["."] + [p for p in projects() if p != "."]:
        sub = os.path.join(REGISTRY, name, "automations")
        if not os.path.isdir(sub):
            continue
        pinned = git(sub, "rev-parse", "HEAD")
        if not pinned:
            continue
        label = "registry" if name == "." else name
        if pinned == head:
            print(f"  current  {label}")
        else:
            behind += 1
            n = git(sub, "rev-list", "--count", f"{pinned}..{head}") or "?"
            print(f"  BEHIND   {label}  pinned {pinned[:7]}, {n} commit(s) back")
    if behind:
        print(f"\n{behind} repo(s) behind. Bump with:")
        print("  git -C <repo>/automations fetch origin main && \\")
        print("    git -C <repo>/automations reset --hard origin/main")
        print("  then `validate.py --fix` there, since a conventions change leaves the")
        print("  duplicated CLAUDE.md block stale.")
    return 1 if behind else 0


def verify_pointers():
    """Every submodule pointer must reference a commit reachable on its remote.

    The registry's commit history is the delivery ledger: signed pointers are the
    claim that project X was at state Y on date Z. That claim is only worth
    something if the SHA still resolves. A pointer to a commit that was never
    pushed, or that a force-push orphaned, leaves a signed record attesting to
    something nobody can retrieve -- which is worse than no record, because it
    carries a signature.

    Needs the network, so it is a command rather than part of the validator.
    """
    import subprocess

    def git(cwd, *args):
        try:
            r = subprocess.run(["git", "-C", cwd, *args],
                               capture_output=True, text=True, timeout=30)
            return r.stdout.strip() if r.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None

    out = git(REGISTRY, "submodule", "status", "--recursive")
    if out is None:
        sys.exit("cannot read submodule status")

    bad = 0
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        sha, path = parts[0].lstrip("+-U"), parts[1]
        sub = os.path.join(REGISTRY, path)
        if not os.path.isdir(sub):
            print(f"  MISSING   {path} — not checked out")
            bad += 1
            continue
        # is the pinned commit an ancestor of the remote's main?
        git(sub, "fetch", "-q", "origin", "main")
        head = git(sub, "rev-parse", "origin/main")
        if head is None:
            print(f"  UNKNOWN   {path} — cannot reach origin")
            bad += 1
            continue
        merged = subprocess.run(["git", "-C", sub, "merge-base", "--is-ancestor", sha, head],
                                capture_output=True)
        if merged.returncode == 0:
            behind = git(sub, "rev-list", "--count", f"{sha}..{head}") or "0"
            note = "current" if behind == "0" else f"{behind} behind"
            print(f"  ok        {path}  {sha[:7]}  ({note})")
        else:
            print(f"  UNREACHABLE {path}  {sha[:7]} is not on origin/main — "
                  "the ledger points at a commit nobody can fetch")
            bad += 1
    if bad:
        print(f"\n{bad} pointer(s) unverifiable. A signed pointer to an unfetchable commit "
              "is a\nledger entry that cannot be checked, which is the one thing the ledger "
              "must not be.")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("project", nargs="?",
                    help='project directory name, or "." for the registry itself')
    ap.add_argument("--all", action="store_true", help="every project in the registry")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check-pins", action="store_true",
                    help="report which repos lag the tooling's main, and stop")
    ap.add_argument("--verify-pointers", action="store_true",
                    help="check every submodule pointer resolves on its remote, and stop")
    args = ap.parse_args()

    if args.check_pins:
        sys.exit(check_pins())
    if args.verify_pointers:
        sys.exit(verify_pointers())
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
