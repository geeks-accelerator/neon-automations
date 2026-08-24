#!/usr/bin/env python3
"""Validate a project's docs/ tree against the neon-docs conventions.

Run from anywhere inside a project. Exits 1 if anything is wrong.
No third-party dependencies -- a validator that needs `pip install` before it
runs is a validator nobody runs.

There are two kinds of document, and nearly everything follows from which one
you are writing:

  EVENTS happened on a day.  docs/{decisions,issues,proposals,plans,observations,research}
    Dated filenames. The account of what happened is never rewritten -- status
    advances, notes append, records are superseded or closed by newer ones. The
    call that turned out wrong is the most useful thing in the tree later, and
    editing it away is how a team forgets why it stopped doing something.

  LIVING documents describe what currently is.  docs/{architecture,vision}
    Plain slugs, no dates -- a date implies a snapshot frozen at that moment,
    which is the opposite of a living document. These get wholly rewritten
    whenever the thing they describe changes; paragraphs that stop being true
    are deleted rather than appended to.

Events accrete. Living documents get overwritten.
"""
import argparse
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nav


def find_root():
    """Locate the project root from the working directory, not from this file.

    This script is shared: the authoritative copy lives in the registry's
    automations/ and is symlinked into each project. Deriving the root from
    __file__ would resolve to wherever the script physically sits, which is a
    different repo.
    """
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, "docs")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            sys.exit("no docs/ directory found above the working directory -- "
                     "run this from inside a project")
        d = parent


ROOT = find_root()
DOCS = os.path.join(ROOT, "docs")

EVENTS = {
    "proposals": {
        "date_field": "opened",
        "required": ["id", "title", "status", "opened"],
        "status": ["draft", "open", "funded", "approved", "building",
                   "shipped", "declined", "dormant"],
    },
    "plans": {
        "date_field": "opened",
        "required": ["id", "title", "proposal", "status", "opened"],
        "status": ["draft", "approved", "in-progress", "shipped", "abandoned"],
    },
    "issues": {
        "date_field": "opened",
        "required": ["id", "title", "status", "severity", "opened"],
        "status": ["open", "confirmed", "fixed", "wontfix", "duplicate"],
        "severity": ["low", "medium", "high"],
    },
    "observations": {
        "date_field": "first_seen",
        "required": ["id", "title", "n", "first_seen", "last_seen", "evidence"],
    },
    "research": {
        "date_field": "conducted",
        "required": ["id", "title", "status", "conducted"],
        "status": ["current", "superseded"],
    },
    "decisions": {
        "date_field": "decided",
        "required": ["id", "title", "status", "decided"],
        "status": ["proposed", "accepted", "superseded", "deprecated"],
    },
}

# field name in the living doc -> directory its ids must resolve against.
# This link is why the two categories are worth separating: the synthesis stays
# traceable to the record that produced it, so a reader who disagrees with how
# something works can find out why without asking anyone.
LIVING = {
    "architecture": {"cites": ("decisions", "decisions")},
    "vision": {"cites": ("proposals", "proposals")},
}

EVENT_NAME_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>[a-z0-9][a-z0-9-]*)\.md$")
LIVING_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.md$")
DATED_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GENERAL_RE = re.compile(r"(?<![-\w])(always|never|every time|all projects)(?![-\w])", re.I)

errors, warnings = [], []


def err(path, msg):
    errors.append(f"{os.path.relpath(path, ROOT)}: {msg}")


def warn(path, msg):
    warnings.append(f"{os.path.relpath(path, ROOT)}: {msg}")


def parse_frontmatter(path):
    """Return (dict, error_or_None). Handles the key: value and key: [a, b] subset."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---\n"):
        return None, "missing YAML frontmatter (file must start with ---)"
    end = text.find("\n---", 3)
    if end == -1:
        return None, "frontmatter is not terminated by ---"
    data = {}
    for lineno, raw in enumerate(text[4:end].split("\n"), start=2):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#") or line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            return None, f"line {lineno}: expected 'key: value', got {line!r}"
        key, _, value = line.partition(":")
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        else:
            value = value.strip("'\"")
        data[key.strip()] = value
    return data, None


def check_date(path, field, value):
    if not isinstance(value, str) or not ISO_RE.match(value):
        err(path, f"{field} must be an ISO date (YYYY-MM-DD), got {value!r}")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        err(path, f"{field} is not a real date: {value!r}")
        return None


def entries(kind):
    d = os.path.join(DOCS, kind)
    if not os.path.isdir(d):
        err(d, "directory is missing")
        return
    for name in sorted(os.listdir(d)):
        if name.endswith(".md") and name != "README.md":
            yield name, os.path.join(d, name)


def collect_events(kind):
    """Parse one event directory. Returns {id: (path, frontmatter)}."""
    spec, found = EVENTS[kind], {}
    for name, path in entries(kind):
        m = EVENT_NAME_RE.match(name)
        if not m:
            err(path, f"{kind} are events -- name it 2026-08-23-some-slug.md")
            continue
        fm, perr = parse_frontmatter(path)
        if perr:
            err(path, perr)
            continue

        for field in spec["required"]:
            if field not in fm or fm[field] in ("", [], None):
                err(path, f"missing required field: {field}")
        file_id = name[:-3]
        if fm.get("id") and fm["id"] != file_id:
            err(path, f"frontmatter id {fm['id']!r} does not match filename {file_id!r}")
        df = spec["date_field"]
        if fm.get(df) and fm[df] != m.group("date"):
            err(path, f"filename date {m.group('date')} does not match {df}: {fm[df]}")
        for field in ("status", "severity"):
            allowed = spec.get(field)
            if allowed and fm.get(field) and fm[field] not in allowed:
                err(path, f"{field} {fm[field]!r} not in {allowed}")
        for field in ("opened", "decided", "first_seen", "last_seen", "shipped", "closed"):
            if fm.get(field):
                check_date(path, field, fm[field])
        found[file_id] = (path, fm)
    return found


def collect_living(kind, resolvable):
    """Parse one living directory. Frontmatter optional; prose is welcome."""
    cite_field, cite_dir = LIVING[kind]["cites"]
    count = 0
    for name, path in entries(kind):
        count += 1
        if DATED_PREFIX_RE.match(name):
            err(path, f"dated filename in {kind}/ -- a dated record is an event and belongs "
                      f"in docs/{{decisions,issues,proposals,plans,observations,research}}; "
                      f"{kind} describes what currently is")
            continue
        if not LIVING_NAME_RE.match(name):
            err(path, f"{kind} filenames are plain slugs like repo-topology.md")
            continue

        fm, perr = parse_frontmatter(path)
        if perr:
            continue          # prose without frontmatter is fine here
        for field in ("decided", "status", "opened"):
            if field in fm:
                err(path, f"{field!r} is an event field -- if this is a record of something "
                          f"that happened, it does not belong in {kind}/")
        if fm.get("updated"):
            check_date(path, "updated", fm["updated"])
        refs = fm.get(cite_field) or []
        if isinstance(refs, str):
            refs = [refs]
        for ref in refs:
            if ref not in resolvable:
                err(path, f"cites {ref!r}, which does not exist in docs/{cite_dir}")
    return count


def generalizes(path):
    """Does the prose state a general rule? Only meaningful at n=1.

    Strip frontmatter, code spans, quotes, and blockquotes first. A well-written
    observation often *discusses* generalizing in order to reject it, and a check
    that fires on those is a check people learn to ignore. The lookarounds keep
    hyphenated compounds like "always-on" from matching.
    """
    body = open(path, encoding="utf-8").read()
    body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.S)
    body = re.sub(r"`[^`]*`", "", body)
    body = re.sub(r'"[^"]*"', "", body)
    body = re.sub(r"^>.*$", "", body, flags=re.M)
    return bool(GENERAL_RE.search(body))


def cross_check(data):
    proposals = data["proposals"]

    for path, fm in data["plans"].values():
        ref = fm.get("proposal")
        if ref and ref not in proposals:
            err(path, f"proposal {ref!r} does not exist -- a plan nobody proposed is "
                      "work nobody funded")
        if fm.get("status") == "shipped" and not fm.get("release"):
            err(path, "shipped plans need a release tag; the attestation service reads it")

    by_proposal = {}
    for _, fm in data["plans"].values():
        by_proposal.setdefault(fm.get("proposal"), []).append(fm)
    for pid, (path, fm) in proposals.items():
        if fm.get("status") in ("building", "shipped"):
            kids = by_proposal.get(pid, [])
            if not any(k.get("status") in ("approved", "in-progress", "shipped") for k in kids):
                err(path, f"status is {fm['status']} but no approved plan references it")
        if "tips" in fm or "tips_usd" in fm:
            err(path, "tip totals belong in the platform database, not in frontmatter -- "
                      "two systems owning one number is a reconciliation bug")

    for path, fm in data["issues"].values():
        ref = fm.get("observation")
        if ref and ref not in data["observations"]:
            err(path, f"observation {ref!r} does not exist in docs/observations")

    for path, fm in data["observations"].values():
        try:
            n = int(fm.get("n", 0))
        except (TypeError, ValueError):
            err(path, f"n must be an integer, got {fm.get('n')!r}")
            continue
        if n < 1:
            err(path, "n must be at least 1")
        first, last = fm.get("first_seen"), fm.get("last_seen")
        if all(isinstance(v, str) and ISO_RE.match(v) for v in (first, last)):
            if date.fromisoformat(last) < date.fromisoformat(first):
                err(path, "last_seen is before first_seen")
        if n == 1 and generalizes(path):
            warn(path, "n=1 but the body generalizes ('always'/'never'). One sighting is an "
                       "instance, not a rule -- wait for recurrence before writing it as one.")

    for path, fm in data["decisions"].values():
        for ref in (fm.get("supersedes") or []):
            if ref not in data["decisions"]:
                err(path, f"supersedes {ref!r}, which does not exist in docs/decisions")
        # a decision citing research is the edge that keeps a justification
        # traceable: research is dated and immutable, so the reasoning cannot
        # shift under the decision after the fact
        for ref in (fm.get("research") or []):
            if ref not in data["research"]:
                err(path, f"cites research {ref!r}, which does not exist in docs/research")

    for path, fm in data["research"].values():
        for ref in (fm.get("supersedes") or []):
            if ref not in data["research"]:
                err(path, f"supersedes {ref!r}, which does not exist in docs/research")
        if fm.get("status") == "current" and not fm.get("sources"):
            warn(path, "no sources listed -- research nobody can re-check is an assertion")


# Two different roots, and conflating them is the bug this comment exists to
# prevent. The PROJECT root comes from the working directory, because this script
# is shared and its own location is a different repo. TOOLING assets come from
# realpath(__file__), which resolves the symlink back to the registry's
# automations/ -- that is exactly where they should be read from.
TOOLING = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))))
SHARED_SRC = os.path.join(TOOLING, "CLAUDE-shared.md")
SHARED_BEGIN, SHARED_END = "<!-- shared:begin -->", "<!-- shared:end -->"
SHARED_RE = re.compile(re.escape(SHARED_BEGIN) + r".*?" + re.escape(SHARED_END), re.S)


def check_shared_block(fix):
    """CLAUDE.md carries a duplicated block; make the duplication checked.

    Agents read CLAUDE.md automatically, so a failed @import would be silent --
    duplication is the right call there. But duplication is a drift source, so
    the copy is compared against the canonical file and a mismatch fails.
    """
    target = os.path.join(ROOT, "CLAUDE.md")
    if not os.path.exists(target) or not os.path.exists(SHARED_SRC):
        return
    text = open(target, encoding="utf-8").read()
    if SHARED_BEGIN not in text:
        warn(target, "no shared conventions block -- this project is not carrying "
                     "the common rules; add one or opt out deliberately")
        return
    canonical = open(SHARED_SRC, encoding="utf-8").read().strip()
    block = f"{SHARED_BEGIN}\n\n{canonical}\n\n{SHARED_END}"
    if SHARED_RE.search(text).group(0) == block:
        return
    if fix:
        open(target, "w", encoding="utf-8").write(SHARED_RE.sub(lambda _: block, text, count=1))
        print("  fixed shared block in CLAUDE.md")
    else:
        err(target, "shared conventions block has drifted from "
                    "automations/claude/CLAUDE-shared.md -- run with --fix")


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def check_links():
    """Every relative markdown link must resolve.

    Navigation without link checking is worse than no navigation, because a link
    that once worked builds trust that a 404 then betrays. The frontmatter graph
    is already validated; this covers the links written in prose, which is where
    a file move quietly breaks things.

    External URLs are skipped -- reaching the network would make the check slow
    and flaky, and a private repo's raw URLs are unreachable from CI anyway.
    """
    for dirpath, dirnames, filenames in os.walk(DOCS):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for target in LINK_RE.findall(text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                resolved = os.path.normpath(
                    os.path.join(dirpath, target.split("#", 1)[0]))
                if not os.path.exists(resolved):
                    err(path, f"broken link: {target}")


def check_strays():
    """Files directly under docs/ are living documents -- the founding docs and
    the tree's own README. A dated filename there is an event that missed its
    directory, and nothing else would catch it."""
    for name in sorted(os.listdir(DOCS)):
        path = os.path.join(DOCS, name)
        if not os.path.isfile(path) or not name.endswith(".md"):
            continue
        if DATED_PREFIX_RE.match(name):
            err(path, "dated filename at the docs/ root -- events belong in "
                      "docs/{decisions,issues,proposals,plans,observations,research}; "
                      "everything else here is a living document")


def check_nav(data, fix):
    """Generated navigation must be current.

    Stale links are worse than none, because they build false trust -- so this
    runs on every invocation rather than only when someone remembers. --fix
    rewrites; a plain run reports what is out of date.
    """
    cites = {k: v["cites"] for k, v in LIVING.items()}
    back = nav.build_graph(data, cites, DOCS, parse_frontmatter)
    stale = []

    for kind in list(EVENTS) + list(LIVING):
        d = os.path.join(DOCS, kind)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".md"):
                continue
            path = os.path.join(d, name)
            is_readme = name == "README.md"
            fm = {}
            if not is_readme:
                fm, perr = parse_frontmatter(path)
                if perr:
                    if kind in EVENTS:
                        continue          # already reported as a schema error
                    fm = {}               # living prose without frontmatter still gets nav
            doc_id = name[:-3]
            parent, block = nav.render(path, kind, fm, doc_id, data, back, DOCS,
                                       is_readme, cites)
            if nav.apply(path, parent, block, fix):
                stale.append(os.path.relpath(path, ROOT))
    return stale


def main():
    ap = argparse.ArgumentParser(description="Validate a docs/ tree.")
    ap.add_argument("--fix", action="store_true",
                    help="regenerate stale navigation blocks in place")
    args = ap.parse_args()

    data = {kind: collect_events(kind) for kind in EVENTS}
    check_strays()
    check_links()
    check_shared_block(args.fix)
    cross_check(data)
    living = {kind: collect_living(kind, set(data[LIVING[kind]["cites"][1]]))
              for kind in LIVING}

    stale = [] if errors else check_nav(data, args.fix)
    if stale and not args.fix:
        for f in stale:
            errors.append(f"{f}: navigation block is out of date -- run with --fix")

    counts = " ".join(f"{k}={len(v)}" for k, v in data.items())
    counts += " | " + " ".join(f"{k}={n}" for k, n in living.items())
    print(f"events: {counts}")
    for w in warnings:
        print(f"  warn  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    if stale and args.fix:
        print(f"  fixed navigation in {len(stale)} file(s)")
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"\nclean ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
