#!/usr/bin/env python3
"""Report which research scans the pitch actually consumes, and which it does not.

The validator enforces one direction: a claim citing a scan id must resolve to a
real scan. Nothing enforced the reverse, and the reverse is where the recorded
failure lives -- a `format` scan in this project was scope-noted, correctly, and
then left with no consumer at all. Accurate research, still in the tree, feeding
nothing.

That failure recurred. On 2026-08-24 an 80-video corpus produced three scans and
none of them fed anything, while mode derivation would still have said
"turn -- no trigger fired".

    scans.py --docs <tree>              # which current scans have a consumer
    scans.py --docs <tree> --since SHA  # which changed since SHA (the trigger-7 question)

Two rules make the count mean something, and both were found by getting it wrong:

**A scan's own `Cited by:` line is not evidence.** It is a hand-maintained
backlink, and on the tree this was written against it was wrong in both
directions -- three scans with real consumers (a decision record, an
architecture doc, the-ask.md) carried no backlink at all. Read the tree, not
the claim about the tree.

**A sibling scan does not count as a consumer.** Scans cross-reference each
other in their Related sections, so three scans published together cite each
other and every one of them looks consumed. That is the check nodding at
itself: the question is whether research reaches the *pitch*, and a citation
that never leaves docs/research/ has not.

An uncited scan is NOT an error. A project may research something it has not
pitched yet. What is an error is not knowing -- so this prints the list to
answer, and the answer may be "not applicable, because ...".

stdlib only.
"""
import argparse
import os
import re
import subprocess
import sys

FIELD = re.compile(r"^(status|mode|conducted):\s*(.+)$", re.M)
CITED_BY = re.compile(r"^-\s*\*\*Cited by:\*\*\s*(.+)$", re.M)

# Modes a pitch draws on. A scan outside these may legitimately have no pitch
# consumer. `regulation` is included even though no phase names it, because what
# may lawfully be offered bounds every ask in the tree.
PITCH_MODES = {"format", "distribution", "regulation", "pricing", "landscape"}


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def load_scans(research):
    out = []
    for name in sorted(os.listdir(research)):
        if not name.endswith(".md") or name == "README.md":
            continue
        text = read(os.path.join(research, name))
        fm = dict(FIELD.findall(text.split("---", 2)[1])) if text.startswith("---") else {}
        m = CITED_BY.search(text)
        out.append({
            "id": name[:-3],
            "mode": fm.get("mode", "?").strip(),
            "status": fm.get("status", "?").strip(),
            "declared": m.group(1).strip() if m else None,
            "consumers": [],
        })
    return out


def find_consumers(docs, rows):
    """Every .md under docs/ that names a scan id, minus research/ itself.

    Excluding the whole research directory is deliberate and is the entire
    correction: a sibling's Related section is navigation between scans, not a
    consumer of one.
    """
    research = os.path.join(docs, "research")
    index = {}
    for dirpath, _, names in os.walk(docs):
        if os.path.abspath(dirpath).startswith(os.path.abspath(research)):
            continue
        for n in names:
            if n.endswith(".md"):
                p = os.path.join(dirpath, n)
                index[os.path.relpath(p, os.path.dirname(docs))] = read(p)
    for s in rows:
        s["consumers"] = sorted(rel for rel, text in index.items() if s["id"] in text)
    return rows


def changed_since(root, sha):
    """Scan ids modified since SHA -- including ones never committed.

    `git diff` alone answers this in the wrong direction. A scan written today
    and not yet committed is untracked, so a diff against any SHA returns
    nothing, and the trigger would report "no new research" over exactly the
    files that prompted the question -- which is when this runs, since the
    natural moment to ask is right after writing a scan and before committing
    it. Reasoned, not observed: the tree this was written against had already
    committed its new scans, and `--since` was correct to return zero there.
    """
    def git(*args):
        try:
            r = subprocess.run(["git", "-C", root, *args],
                               capture_output=True, text=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return None
        return r.stdout.split()

    tracked = git("diff", "--name-only", sha, "--", "docs/research")
    if tracked is None:
        return None
    untracked = git("ls-files", "--others", "--exclude-standard", "--", "docs/research") or []
    return {os.path.basename(p)[:-3] for p in tracked + untracked if p.endswith(".md")}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--since", metavar="SHA",
                    help="report which scans changed since SHA -- the trigger-7 question")
    args = ap.parse_args()

    docs = os.path.abspath(args.docs)
    research = os.path.join(docs, "research")
    if not os.path.isdir(research):
        print(f"no research directory under {docs}")
        return 0

    rows = [s for s in find_consumers(docs, load_scans(research)) if s["status"] == "current"]
    if not rows:
        print("no current scans")
        return 0

    print(f"--- {len(rows)} current scan(s)")
    for s in rows:
        first = s["consumers"][0] if s["consumers"] else "NO CONSUMER OUTSIDE research/"
        extra = f"  (+{len(s['consumers']) - 1})" if len(s["consumers"]) > 1 else ""
        print(f" {'  ' if s['consumers'] else '->'} {s['mode']:<13} {s['id'][:50]:<50} {first}{extra}")

    # A backlink that disagrees with the tree is worse than an absent one: it
    # reports coverage that is not there, or hides coverage that is.
    stale = [s for s in rows if bool(s["declared"]) != bool(s["consumers"])]
    if stale:
        print(f"\n{len(stale)} scan(s) whose `Cited by:` line disagrees with the tree:")
        for s in stale:
            said = s["declared"] or "nothing"
            found = f"{len(s['consumers'])} consumer(s)" if s["consumers"] else "none"
            print(f"      {s['id']}\n        says {said!r}, tree has {found}")

    orphan = [s for s in rows if not s["consumers"] and s["mode"] in PITCH_MODES]
    if orphan:
        print(f"\n{len(orphan)} scan(s) in a pitch mode with no consumer outside research/:\n")
        for s in orphan:
            sib = "cited only by sibling scans" if s["declared"] else "uncited"
            print(f"  {s['id']}\n      {s['mode']}, {sib}")
        print("\nEach needs a deliberate answer: cite it from claims.md, or write the"
              "\n'not applicable, because ...' line in the pitch index. Silence is the"
              "\nfailure this check exists to catch, not the absence of a citation.")
    else:
        print("\nevery current scan in a pitch mode reaches something outside research/")

    if args.since:
        new = changed_since(os.path.dirname(docs), args.since)
        if new is None:
            # Trigger 7 exists because research can land that contradicts a live
            # claim while mode derivation reports "no trigger fired". A --since
            # that cannot read history answers nothing, and returning 0 makes
            # that indistinguishable from "nothing changed" -- the same silence
            # the trigger was added to break.
            print(f"\n--since could not read git history at {os.path.dirname(docs)}."
                  "\nThis is not an answer of 'no new research'. Re-run where the history"
                  "\nis readable, or drop --since and check trigger 7 by hand.")
            return 1
        else:
            hit = [s for s in rows if s["id"] in new]
            print(f"\nchanged since {args.since}: {len(hit)}")
            for s in hit:
                print(f"      {s['mode']:<13} {s['id']}")
            if hit:
                reg = [s["id"] for s in hit if s["mode"] == "regulation"]
                print("\nTrigger 7: does any of this change what the pitch should say?"
                      "\nA regulation scan is the strong case -- " +
                      (", ".join(reg) if reg else "none among these."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
