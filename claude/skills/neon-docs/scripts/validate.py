#!/usr/bin/env python3
"""Validate a project's docs/ tree against the neon-docs conventions.

Run from anywhere inside a project. Exits 1 if anything is wrong.
No third-party dependencies -- a validator that needs `pip install` before it
runs is a validator nobody runs.

There are two kinds of document, and nearly everything follows from which one
you are writing:

  EVENTS happened on a day.  docs/{decisions,issues,proposals,plans,observations,research,rounds}
    Dated filenames. The account of what happened is never rewritten -- status
    advances, notes append, records are superseded or closed by newer ones. The
    call that turned out wrong is the most useful thing in the tree later, and
    editing it away is how a team forgets why it stopped doing something.

  LIVING documents describe what currently is.  docs/{architecture,vision,pitch}
    Plain slugs, no dates -- a date implies a snapshot frozen at that moment,
    which is the opposite of a living document. These get wholly rewritten
    whenever the thing they describe changes; paragraphs that stop being true
    are deleted rather than appended to.

Events accrete. Living documents get overwritten.

Eight of those ten are the shape of the record, and every project keeps them.
docs/rounds/ and docs/pitch/ are the output of raising funding rounds, which most
projects never do -- they are held to their schema when present and absent without
complaint. See OPTIONAL.
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

# Research modes. Adding one is an edit to this table and nothing else: the
# schema check, the staleness sweep, and --preflight all read from here, so a new
# kind of scan becomes checkable without touching any caller.
#
# The horizon is how long that kind of fact stays trustworthy, not how long the
# document stays interesting. Pricing moves quarterly; regulation moves slowly;
# our own metrics are stale in a week.
RESEARCH_MODES = {
    "pricing":    (90,  "API costs, subscription tiers, unit economics"),
    "landscape":  (180, "competitors, prior art, what already exists"),
    "format":     (180, "content and production conventions, what holds attention"),
    "distribution": (180, "channel mechanics, community rules, reachable audience"),
    "regulation": (365, "securities, licensing, terms of service"),
    "metrics":    (7,   "numbers from our own systems"),
}

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
    # A turn of the funding loop: the script, the claims it used, the ask, the
    # threshold, and -- appended after -- the result. An event rather than a
    # living document for one reason: the threshold has to be immutable. A number
    # chosen after seeing the result is not a threshold, and living semantics
    # would let it be revised to match with nothing in the tree showing it.
    "rounds": {
        "date_field": "opened",
        "required": ["id", "title", "turn", "pitch_mode", "status", "opened"],
        "status": ["draft", "posted", "passed", "failed", "inconclusive", "abandoned"],
        "pitch_mode": ["full", "turn"],
    },
}

# field name in the living doc -> directory its ids must resolve against.
# This link is why the two categories are worth separating: the synthesis stays
# traceable to the record that produced it, so a reader who disagrees with how
# something works can find out why without asking anyone.
LIVING = {
    "architecture": {"cites": ("decisions", "decisions")},
    "vision": {"cites": ("proposals", "proposals")},
    # The claims ledger and the narrative derived from it. It cites research/
    # rather than decisions/ because that is what makes the RESEARCHED tag
    # structural: a claim sourced from outside the repository has to point at a
    # dated scan carrying a staleness horizon, not at a URL in prose.
    "pitch": {"cites": ("research", "research")},
}

# Directories whose absence is not an error. The eight others are the shape of
# the record; these two are the output of an activity most projects never
# perform -- this registry raises no rounds and will never hold either. Present
# means held to the schema; absent means nothing.
#
# The cost is real: these are the first directories whose absence carries no
# information, so "missing, or not applicable?" becomes a question the tree
# cannot answer. Taken over every project carrying an empty pitch directory for
# a pitch it will never write.
OPTIONAL = frozenset({"rounds", "pitch"})

# Built from the table rather than written out, so adding an event directory
# does not leave a stale enumeration in three error messages.
EVENT_DIRS = "docs/{" + ",".join(EVENTS) + "}"

# A round's status vocabulary splits three ways, and two of the splits carry
# checks rather than only labels: once a round is public its threshold is
# frozen, and once numbers come back it owes a result.
ROUND_POSTED = ("posted", "passed", "failed", "inconclusive")
ROUND_RESOLVED = ("passed", "failed", "inconclusive")

# A claim row in docs/pitch/claims.md is a table row whose first cell is an id.
# Fixing the row format is what turns "every claim id referenced anywhere
# resolves to a row in the ledger" from a rule someone remembers into a check.
CLAIM_ROW_RE = re.compile(r"^\|\s*(C-\d+)\s*\|")
CLAIM_TAGS = ("EXTRACTED", "RESEARCHED", "ASSERTED", "CHECKED")

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
        return parse_fm_text(fh.read())


def parse_fm_text(text):
    """The parser, over text rather than a path -- history checks read a blob
    out of git and have no file to point at."""
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
    """The .md files directly inside docs/<kind>/ -- one level, not a walk.

    A subdirectory is therefore invisible to every check in this file: naming,
    frontmatter, ids, cross-references, all of it. That is deliberate, because
    a corpus filed under an event directory is a legitimate shape -- an 80-file
    research distillation is not eighty research records -- and recursing would
    demand every one of them carry a dated filename and full frontmatter.

    But invisible and silent are different things. The subtree used to pass
    without a word, so a record misfiled one level down looked validated and
    was not. It now warns once per directory, naming what is being skipped.
    """
    d = os.path.join(DOCS, kind)
    if not os.path.isdir(d):
        if kind not in OPTIONAL:
            err(d, "directory is missing")
        return
    subdirs = []
    for name in sorted(os.listdir(d)):
        full = os.path.join(d, name)
        if name.endswith(".md") and name != "README.md":
            yield name, full
        elif os.path.isdir(full) and not name.startswith("."):
            n = sum(1 for _, _, fs in os.walk(full) for f in fs if f.endswith(".md"))
            if n:
                subdirs.append(f"{name}/ ({n})")
    if subdirs:
        warn(d, "not validated -- entries() reads one level, so nothing in "
                f"{', '.join(subdirs)} is checked for naming, frontmatter or "
                "cross-references. A corpus belongs here; a record does not")


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
        for field in ("status", "severity", "pitch_mode"):
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
    found = {}
    for name, path in entries(kind):
        if DATED_PREFIX_RE.match(name):
            err(path, f"dated filename in {kind}/ -- a dated record is an event and belongs "
                      f"in {EVENT_DIRS}; {kind} describes what currently is")
            continue
        if not LIVING_NAME_RE.match(name):
            err(path, f"{kind} filenames are plain slugs like repo-topology.md")
            continue

        fm, perr = parse_frontmatter(path)
        if perr:
            found[name[:-3]] = (path, {})
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
        found[name[:-3]] = (path, fm)
    return found


def collect_claims():
    """Parse the claim ids out of docs/pitch/claims.md, checking each is tagged.

    Returns the id set, or None when there is no pitch tree to resolve against.
    The ledger is the one place a claim may originate, so an untagged row here
    is the exact defect the tags exist to prevent -- an ASSERTED claim reading
    like an EXTRACTED one.
    """
    d = os.path.join(DOCS, "pitch")
    if not os.path.isdir(d):
        return None
    path = os.path.join(d, "claims.md")
    if not os.path.exists(path):
        err(d, "docs/pitch/ exists without claims.md -- every claim originates in the "
               "ledger, and a pitch tree without one cannot hold the invariant that a "
               "round may only claim what is already written down")
        return None
    ids = {}
    fenced = False
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            # A fenced example row is documentation about the format, not a
            # claim. Without this, the ledger's own "how to write a row" section
            # parses as a duplicate id -- the recorded pattern of tools that
            # match literal markers eating the documents that describe them.
            if line.lstrip().startswith("```"):
                fenced = not fenced
                continue
            if fenced:
                continue
            m = CLAIM_ROW_RE.match(line)
            if not m:
                continue
            cid = m.group(1)
            if cid in ids:
                err(path, f"duplicate claim id {cid} on lines {ids[cid]} and {lineno} -- "
                          "ids are what rounds and scripts cite, so two rows answering to "
                          "one id makes every citation of it ambiguous")
            ids[cid] = lineno
            # Read the TAG COLUMN, not the whole row. A citation that explains
            # what would change a claim's tag -- "a WHOIS lookup would raise
            # this to `CHECKED`" -- named a second tag in prose and tripped the
            # dual-tag warning. The check was matching the sentence documenting
            # the rule, which is the same false positive shape as a gate that
            # greps for its own compliance note.
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            scope = cells[2] if len(cells) >= 4 else line
            tags = [t for t in CLAIM_TAGS if f"`{t}`" in scope]
            if not tags:
                err(path, f"claim {cid} carries no provenance tag -- one of "
                          f"{', '.join(CLAIM_TAGS)}")
            elif len(tags) > 1:
                warn(path, f"claim {cid} carries {len(tags)} tags ({', '.join(tags)}) -- "
                           "only a composite built from rows already in the ledger may, and "
                           "only with its counting convention declared beside it. A new "
                           "fact gets split into two claims instead of one hedged one")
    return set(ids)


def check_rounds(data, claim_ids):
    """Rules a round's status implies, and the ledger link.

    The threshold and result checks are the machine half of why a round is an
    event record at all: a threshold written after the numbers came back is not
    a threshold, and neither prose nor a convention can stop that on its own.
    """
    seen = {}
    for rid, (path, fm) in sorted(data["rounds"].items()):
        try:
            n = int(fm.get("turn"))
        except (TypeError, ValueError):
            n = None
        if n is None or n < 1:
            err(path, f"turn must be an integer >= 1, got {fm.get('turn')!r}")
        elif n in seen:
            err(path, f"turn {n} is already claimed by {seen[n]} -- the ordinal is how "
                      "rounds get referred to, and two records answering to one number "
                      "makes every later reference ambiguous")
        else:
            seen[n] = rid

        status = fm.get("status")
        if status in ROUND_POSTED and not fm.get("threshold"):
            err(path, f"a {status!r} round carries no threshold -- it has to be written "
                      "before the round posts. A number chosen after seeing the result is "
                      "not a threshold, and an experiment that cannot fail cannot succeed")
        if status in ROUND_RESOLVED and not fm.get("result"):
            err(path, f"a {status!r} round carries no result -- the outcome is what the "
                      "record exists to hold next to the threshold")

        # demoted ids resolve too: demotion changes a claim's standing, it does
        # not delete the row, so a demoted id that is not in the ledger is a typo
        # or a claim that was removed instead of demoted.
        for field in ("claims", "demoted"):
            refs = fm.get(field) or []
            if isinstance(refs, str):
                refs = [refs]
            for ref in refs:
                if claim_ids is None:
                    err(path, f"{field} lists {ref!r} with no docs/pitch/claims.md to "
                              "resolve it against -- a round may only reference what the "
                              "ledger already holds")
                elif ref not in claim_ids:
                    err(path, f"{field} lists {ref!r}, which is not a row in "
                              "docs/pitch/claims.md")


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


def tag_exists(name):
    """True when `name` is a git tag in this repository.

    True as well when git cannot answer -- no repository, no toolchain, a
    shallow checkout without tags. A missing tool must not turn into an
    accusation that a release was never cut.
    """
    out = _git_in(ROOT, "tag", "--list", name)
    return True if out is None else out != ""


def cross_check(data):
    proposals = data["proposals"]

    for path, fm in data["plans"].values():
        ref = fm.get("proposal")
        if ref and ref not in proposals:
            err(path, f"proposal {ref!r} does not exist -- a plan nobody proposed is "
                      "work nobody funded")
        if fm.get("status") == "shipped" and not fm.get("release"):
            err(path, "shipped plans need a release tag; the attestation service reads it")
        # ...and the tag has to exist. Checking only that the field is present
        # accepts a plan claiming `shipped` against a tag nobody cut, which is
        # the same shape as a documented verification command nobody runs: the
        # attestation service reads this name and finds nothing.
        rel = fm.get("release")
        if rel and not tag_exists(str(rel)):
            err(path, f"release tag {rel!r} does not exist -- `git tag` does not list it, "
                      f"so the delivery this plan claims cannot be verified")
        # A plan may cite observations as a list. The singular field is read
        # above for issues; without this the plural silently referenced nothing.
        for ref in (fm.get("observations") or []):
            if ref not in data["observations"]:
                err(path, f"observation {ref!r} does not exist in docs/observations")

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
        both = set(fm.get("opens") or []) & set(fm.get("answers") or [])
        if both:
            err(path, f"opens and answers the same slug(s): {sorted(both)} -- a question "
                      "a scan raises and closes itself was never open")
        mode = fm.get("mode")
        if mode and mode not in RESEARCH_MODES:
            err(path, f"mode {mode!r} not in {sorted(RESEARCH_MODES)}")
        elif not mode and fm.get("status") == "current":
            warn(path, "no mode set -- staleness cannot be checked without one")


# Two different roots, and conflating them is the bug this comment exists to
# prevent. The PROJECT root comes from the working directory, because this script
# is shared and its own location is a different repo. TOOLING assets come from
# realpath(__file__), which resolves the symlink back to the registry's
# automations/ -- that is exactly where they should be read from.
TOOLING = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))))
SHARED_SRC = os.path.join(TOOLING, "CLAUDE-shared.md")
RESEARCH_SKILL = os.path.join(TOOLING, "skills", "research", "SKILL.md")
MODE_ROW_RE = re.compile(r"^\|\s*`([a-z]+)`\s*\|\s*(\d+)d\s*\|\s*([^|]+?)\s*\|\s*$", re.M)
SHARED_BEGIN, SHARED_END = "<!-- shared:begin -->", "<!-- shared:end -->"
SHARED_RE = re.compile(re.escape(SHARED_BEGIN) + r".*?" + re.escape(SHARED_END), re.S)


def check_research_modes_doc():
    """The research skill restates RESEARCH_MODES; make that duplication checked.

    The table is worth having in the prose -- an agent writing a scan needs the
    modes and horizons without reading Python. But the skill also claimed that
    adding a mode is "an edit to RESEARCH_MODES in the validator and nothing
    else", which was false while a second copy of the table sat in the skill
    itself. Two homes for one set of numbers, and the doc asserting there was
    one.

    Same remedy as the shared CLAUDE block: keep the copy, check it. A mismatch
    errors rather than warns, because a wrong horizon in the doc sends someone
    to write a scan that expires on a schedule they did not intend, and a mode
    that is in the table but not the code fails validation at the far end.

    Absent skill: nothing to check. A project may vendor neon-docs alone.
    """
    if not os.path.exists(RESEARCH_SKILL):
        return
    try:
        text = open(RESEARCH_SKILL, encoding="utf-8").read()
    except OSError:
        return
    documented = {m.group(1): (int(m.group(2)), m.group(3))
                  for m in MODE_ROW_RE.finditer(text)}
    if not documented:
        err(RESEARCH_SKILL, "no research mode table found -- it should carry one "
                            "row per RESEARCH_MODES entry as `| `mode` | Nd | covers |`")
        return
    for mode, (days, covers) in RESEARCH_MODES.items():
        if mode not in documented:
            err(RESEARCH_SKILL, f"mode {mode!r} is in RESEARCH_MODES but not the table")
        elif documented[mode][0] != days:
            err(RESEARCH_SKILL, f"mode {mode!r} horizon is {documented[mode][0]}d in the "
                                f"table and {days}d in RESEARCH_MODES")
        elif documented[mode][1] != covers:
            err(RESEARCH_SKILL, f"mode {mode!r} description has drifted from RESEARCH_MODES")
    for mode in documented:
        if mode not in RESEARCH_MODES:
            err(RESEARCH_SKILL, f"mode {mode!r} is documented but not in RESEARCH_MODES -- "
                                "a scan declaring it would fail validation")


def check_tooling_unpushed():
    """Tooling commits that exist only here.

    The skills are edited in one checkout and consumed as a pinned submodule by
    every project, so an edit is worth nothing until it is pushed and the
    pointers move. Two ways it silently is not:

    A commit made on a **detached HEAD** belongs to no branch, and
    `git push origin main` then pushes the stale local `main`, prints
    "Everything up-to-date", and exits 0. Success output, no effect, and any
    `&&` chain after it carries on. That happened on 2026-08-24 and was caught
    two steps later by a bump that could not find the SHA it had just pushed.

    Or an ordinary forgotten push, which is the same defect wearing a friendlier
    face.

    A detached HEAD **with no local commits is normal and stays silent** -- that
    is exactly what a consumer's pinned submodule looks like, and warning there
    would train people to ignore this.
    """
    tooling_repo = os.path.dirname(TOOLING)
    # exists(), not isdir(): the tooling is a submodule in every consumer, and a
    # submodule's .git is a *file* holding `gitdir: ...`. isdir() returned False
    # for the only shape this check will ever run against.
    if not os.path.exists(os.path.join(tooling_repo, ".git")):
        return
    ahead = _git_in(tooling_repo, "log", "--oneline", "origin/main..HEAD")
    if not ahead:
        return
    n = len(ahead.splitlines())
    branch = _git_in(tooling_repo, "rev-parse", "--abbrev-ref", "HEAD")
    where = "on a detached HEAD, so they belong to no branch" if branch == "HEAD" \
        else f"on {branch!r}"
    warn(tooling_repo,
         f"{n} tooling commit(s) not on origin/main, {where} -- projects pin a "
         "SHA, so an unpushed edit reaches nobody. Push with "
         "'git push origin HEAD:main'; note that 'git push origin main' from a "
         "detached HEAD reports success and moves nothing")


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
# Same shape, keeping the link text. Separate rather than a second capture
# group on LINK_RE, whose .findall() callers expect a flat list of targets.
LINK_TEXT_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# A markdown filename appearing inside link text -- "[scope.md § X](...)".
MD_IN_TEXT_RE = re.compile(r"(?<![\w/.-])([a-z0-9][\w.-]*\.md)\b")
# github.com/<org>/<repo>/(blob|tree)/<ref>/<path>
GH_URL_RE = re.compile(r"https://github\.com/([^/]+)/([^/]+)/(?:blob|tree)/[^/]+/(.+?)(?:#.*)?$")


def web_invisible(base, target):
    """Does this link work on disk but 404 on GitHub's web UI?

    Two cases. A symlink anywhere in the path: GitHub renders a symlink as a
    text blob holding the target path, so nothing resolves through or at it.
    A submodule as an intermediate component: the web UI links a submodule
    entry to its own repo, but a deeper path into one 404s. A link whose final
    target IS a submodule directory works, so only strict traversal is flagged.

    This matters because the filesystem check alone passes on all of these --
    which is false confidence for exactly the readers the public ledger story
    is about: people auditing the repo in a browser.
    """
    cur = base
    parts = os.path.normpath(target).split(os.sep)
    for i, part in enumerate(parts):
        cur = os.path.normpath(os.path.join(cur, part))
        if os.path.islink(cur):
            return "crosses a symlink"
        last = i == len(parts) - 1
        if (not last and os.path.isdir(cur) and cur != ROOT
                and os.path.exists(os.path.join(cur, ".git"))):
            return "reaches into a submodule"
    return None


def _origin_slug(path):
    """`org/repo` for a checkout, from its origin remote. None if unknown."""
    url = _git_in(path, "config", "--get", "remote.origin.url")
    if not url:
        return None
    m = re.search(r"github\.com[:/]([^/]+)/(.+?)(?:\.git)?\s*$", url)
    return f"{m.group(1)}/{m.group(2)}" if m else None


def _git_in(cwd, *args):
    import subprocess
    try:
        r = subprocess.run(["git", "-C", cwd, *args],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


_LOCAL_REPOS = None


def local_repos():
    """`{org/repo: local path}` for checkouts this run can actually read.

    Absolute GitHub URLs are the prescribed way to link across a repo boundary
    -- a relative link into a submodule 404s on the web. The cost is that
    check_links skips them entirely (reaching the network would be slow, flaky,
    and useless for a private repo), so the fix for one class of broken link
    created a class nothing checks at all: three renames on 2026-08-24 left six
    stale cross-repo URLs and every run stayed green.

    Where the target repo is on disk -- as a submodule, as the parent of this
    one, or as this repo itself -- the path can be checked without a network
    call. A miss only warns: the local checkout sits at whatever commit its
    pointer names, which is not necessarily the `<ref>` in the URL.
    """
    global _LOCAL_REPOS
    if _LOCAL_REPOS is not None:
        return _LOCAL_REPOS
    repos = {}
    for base in (ROOT, os.path.dirname(ROOT)):
        slug = _origin_slug(base)
        if slug:
            repos.setdefault(slug, base)
        mods = _git_in(base, "config", "--file", os.path.join(base, ".gitmodules"),
                       "--get-regexp", r"^submodule\..*\.path$") or ""
        for line in mods.splitlines():
            key, _, rel = line.partition(" ")
            sub = os.path.join(base, rel)
            if os.path.isdir(sub):
                s = _origin_slug(sub)
                if s:
                    repos.setdefault(s, sub)
    _LOCAL_REPOS = repos
    return repos


def check_cross_repo_url(path, target):
    """An absolute GitHub URL whose repo is on disk must resolve there."""
    m = GH_URL_RE.match(target)
    if not m:
        return
    org, repo, rel = m.group(1), m.group(2), m.group(3)
    base = local_repos().get(f"{org}/{repo}")
    if not base:
        return
    if not os.path.exists(os.path.join(base, rel)):
        warn(path, f"cross-repo link {target} -- {rel} does not exist in the "
                   f"local {org}/{repo} checkout. Renames on the other side of "
                   "a repo boundary are invisible to a link check")


def check_link_text(path, text, target):
    """Does the link text name a different file than the link points at?

    Rewriting a link's target and leaving its text is a silent way to produce a
    citation that names one document and points at another. Three of these
    existed at once on 2026-08-24, from an edit that retargeted anchors into
    freshly extracted records: `[scope.md § The treasury pays direct]` pointing
    at `decisions/2026-08-23-the-treasury-pays-direct.md`.

    Narrow on purpose. It fires only when the text contains something shaped
    like a markdown filename, so ordinary prose text -- "the decision", "docs",
    "here" -- is never a candidate and cannot false-positive.
    """
    named = MD_IN_TEXT_RE.findall(text)
    if not named:
        return
    want = os.path.basename(target.split("#", 1)[0]).lower()
    if want and not any(n.lower() == want for n in named):
        warn(path, f"link text names {named[0]!r} but the link points at "
                   f"{want!r} -- retargeted without retitling?")


def check_links():
    """Every relative markdown link must resolve -- on disk AND on the web UI.

    Navigation without link checking is worse than no navigation, because a link
    that once worked builds trust that a 404 then betrays. The frontmatter graph
    is already validated; this covers the links written in prose, which is where
    a file move quietly breaks things.

    External URLs are skipped -- reaching the network would make the check slow
    and flaky, and a private repo's raw URLs are unreachable from CI anyway.

    Root-level documents (README.md, CLAUDE.md) are scanned as well as docs/:
    the first web-invisible links found in practice were in CLAUDE.md.
    """
    files = []
    for name in sorted(os.listdir(ROOT)):
        if name.endswith(".md"):
            files.append((ROOT, name))
    for dirpath, dirnames, filenames in os.walk(DOCS):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        files += [(dirpath, n) for n in filenames if n.endswith(".md")]

    for dirpath, name in files:
        path = os.path.join(dirpath, name)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for label, target in LINK_TEXT_RE.findall(text):
            if target.startswith(("http://", "https://")):
                check_cross_repo_url(path, target)
                continue
            if target.startswith(("mailto:", "#")):
                continue
            bare = target.split("#", 1)[0]
            resolved = os.path.normpath(os.path.join(dirpath, bare))
            if not os.path.exists(resolved):
                err(path, f"broken link: {target}")
                continue
            why = web_invisible(dirpath, bare)
            if why:
                err(path, f"link {target} {why} -- it resolves on disk but 404s "
                          "on GitHub's web UI; link the target repo's URL instead")
                continue
            check_link_text(path, label, target)


OPEN_STATES = {"draft", "open", "funded", "approved", "building",
               "confirmed", "proposed", "current", None}


def stale_research(data):
    """Current scans past their mode's horizon.

    Detection is deliberately inclusive: every current scan is checked, every
    time, because the cost of missing a stale input is a decision made on a
    number that moved, and the cost of checking is reading a date. Acting on
    what it finds stays explicit -- see the research skill.
    """
    today = date.today()
    out = []
    for rid, (path, fm) in sorted(data["research"].items()):
        if fm.get("status") != "current":
            continue
        mode = fm.get("mode")
        if mode not in RESEARCH_MODES:
            continue
        horizon = RESEARCH_MODES[mode][0]
        conducted = fm.get("conducted")
        if not (isinstance(conducted, str) and ISO_RE.match(conducted)):
            continue
        age = (today - date.fromisoformat(conducted)).days
        if age > horizon:
            out.append((rid, mode, age, horizon, path))
    return out


def open_questions(data, living):
    """Questions declared open and not yet answered by a current scan.

    Two ways a question gets raised. A record says `needs_research: [slug]` --
    something it cannot answer that would change what it says. A research scan
    says `opens: [slug]` -- a gap the scan itself surfaced while looking at
    something else. Either way a scan closes it with `answers: [slug]`.

    `opens` exists because a scan's "what could not be found" section is prose,
    and prose is invisible to a gate. Recording an absence there created no
    obligation to act on it: the absence sat in a paragraph while preflight
    reported clean. That happened once, and it cost a deck's worth of research
    aimed at the wrong audience.

    Prose cannot be scanned for this -- "we should look into X" is not
    matchable -- so the slug is what makes the gate mechanical rather than a
    thing to remember.
    """
    answered = set()
    for _, fm in data["research"].values():
        if fm.get("status") != "superseded":
            for slug in (fm.get("answers") or []):
                answered.add(slug)

    out = []
    # gaps a scan surfaced about itself
    for rid, (path, fm) in sorted(data["research"].items()):
        if fm.get("status") == "superseded":
            continue
        for slug in (fm.get("opens") or []):
            if slug not in answered:
                out.append(("research", rid, slug, path))

    everything = {k: v for k, v in data.items()}
    everything.update(living)
    for kind, records in everything.items():
        for rid, (path, fm) in sorted(records.items()):
            if fm.get("status") not in OPEN_STATES:
                continue
            for slug in (fm.get("needs_research") or []):
                if slug not in answered:
                    out.append((kind, rid, slug, path))
    return out


def check_strays():
    """Files directly under docs/ are living documents -- the founding docs and
    the tree's own README. A dated filename there is an event that missed its
    directory, and nothing else would catch it.

    Directories are the other half, and they used to fall through here silently.
    The taxonomy is ten names; a directory outside it is not merely unvalidated,
    it is *invisible* -- uncounted, unwalked, its links unchecked. That is worse
    than the warning a subdirectory of a known kind already gets, because
    nothing anywhere says the files exist. Found when a registry guide sat in
    docs/guides/ referencing a script that did not exist, and no run complained.

    A warning rather than an error: a tree may carry a directory deliberately,
    and the remedy (move it, or teach the validator the name) is a judgement the
    project makes once. Silence is the defect, not the directory."""
    known = set(EVENTS) | set(LIVING)
    for name in sorted(os.listdir(DOCS)):
        path = os.path.join(DOCS, name)
        if os.path.isdir(path):
            if name in known or name.startswith("."):
                continue
            n = sum(1 for _, _, fs in os.walk(path) for f in fs if f.endswith(".md"))
            warn(path, f"docs/{name}/ is not one of the ten directories -- its {n} markdown "
                       f"file(s) are uncounted and their links unchecked. Move it under "
                       f"{EVENT_DIRS}, a living directory, or outside docs/ if it is not a "
                       f"document")
            continue
        if not os.path.isfile(path) or not name.endswith(".md"):
            continue
        if DATED_PREFIX_RE.match(name):
            err(path, f"dated filename at the docs/ root -- events belong in {EVENT_DIRS}; "
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

    # Every directory README points at docs/README.md as its parent, so a tree
    # without one bootstraps into eight broken links. Created only when absent --
    # this file carries project-specific content once a project has any, and
    # regenerating it would clobber that.
    docs_readme = os.path.join(DOCS, "README.md")
    if not os.path.exists(docs_readme):
        if fix:
            with open(docs_readme, "w", encoding="utf-8") as fh:
                fh.write(nav.starter_docs_readme(EVENTS, LIVING))
        else:
            stale.append(os.path.relpath(docs_readme, ROOT))

    for kind in list(EVENTS) + list(LIVING):
        d = os.path.join(DOCS, kind)
        if not os.path.isdir(d):
            continue

        # Render the README unconditionally, before touching anything else. An
        # empty directory has no files to iterate, so a loop over its contents
        # could never create one -- which left new projects with untracked empty
        # directories (git stores no empty dirs) that failed validation on the
        # first clone. The README is also what makes each directory survive a
        # clone at all.
        readme = os.path.join(d, "README.md")
        if not os.path.exists(readme):
            if fix:
                open(readme, "w", encoding="utf-8").close()
            else:
                stale.append(os.path.relpath(readme, ROOT))
        if os.path.exists(readme):
            block = nav.render_readme(readme, kind, DOCS, data, set(LIVING))
            try:
                if nav.apply_readme(readme, block, fix):
                    stale.append(os.path.relpath(readme, ROOT))
            except nav.ReadmeMarkersMissing:
                # Errors even under --fix. Refusing to rewrite a file we cannot
                # parse is the whole point; "fix" must not mean "overwrite".
                err(readme, "directory README has content but no index markers -- add the "
                            "pair where the generated index belongs:\n"
                            "           <!-- index:begin -->\n"
                            "           <!-- index:end -->\n"
                            "         Everything outside them is preserved. Refusing rather "
                            "than rewriting, because this file's hand-written content would "
                            "be destroyed and nothing would say so.")

        for name in sorted(os.listdir(d)):
            if not name.endswith(".md") or name == "README.md":
                continue
            path = os.path.join(d, name)
            is_readme = False
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


def _git(*args):
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT, *args],
                           capture_output=True, text=True, timeout=20)
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def check_history(base):
    """Rules that only history can see: records must not be deleted, and an
    open proposal's filename must not change.

    Both were documented and unenforceable, which is the worst combination --
    a rule with no check is a rule that erodes quietly, and these two erode in
    ways the tree cannot show afterwards. A deleted record leaves no trace that
    it existed; a renamed proposal orphans the tips attached to its id.
    """
    if _git("rev-parse", "--verify", "--quiet", base) is None:
        warn(os.path.join(ROOT, ".git"),
             f"cannot compare against {base!r} -- history checks skipped")
        return
    diff = _git("diff", "--name-status", "-M", f"{base}...HEAD", "--", "docs/")
    if diff is None:
        # Warns rather than returning quietly, unlike the branch above it,
        # which skips deliberately: no base to compare against is the normal
        # state of a new branch. Reaching here means git resolved the ref and
        # then failed anyway -- an error, a timeout, a missing binary -- and
        # all three history rules stop running. A check that can silently
        # switch itself off is one nobody notices is off.
        warn(os.path.join(ROOT, ".git"),
             f"git diff against {base!r} failed -- history checks skipped")
        return

    event_dirs = tuple(f"docs/{k}/" for k in EVENTS)
    for line in diff.splitlines():
        parts = line.split("\t")
        code = parts[0]
        if code.startswith("D") and len(parts) == 2:
            path = parts[1]
            if path.startswith(event_dirs) and not path.endswith("README.md"):
                err(os.path.join(ROOT, path),
                    "record deleted -- retire with a status instead; deleting erases "
                    "the trail of what was considered and rejected")
        elif (code.startswith("M") and len(parts) == 2) or \
             (code.startswith("R") and len(parts) == 3 and
              parts[1].startswith("docs/rounds/")):
            # Renames are checked too, or a same-commit rename would carry a
            # revised threshold past a check that only reads M rows.
            oldp = parts[1]
            path = parts[-1]
            if not oldp.startswith("docs/rounds/") or path.endswith("README.md"):
                continue
            blob = _git("show", f"{base}:{oldp}")
            if blob is None:
                continue
            was, _ = parse_fm_text(blob)
            if not was or was.get("status") not in ROUND_POSTED:
                continue
            now, _ = parse_frontmatter(os.path.join(ROOT, path))
            if now and now.get("threshold") != was.get("threshold"):
                err(os.path.join(ROOT, path),
                    f"threshold changed after this round reached {was['status']!r}: "
                    f"{was.get('threshold')!r} -> {now.get('threshold')!r}. It is written "
                    "before posting and never revised -- that immutability is the only "
                    "reason a round is an event record rather than a living document")
        elif code.startswith("R") and len(parts) == 3:
            oldp, newp = parts[1], parts[2]
            if not oldp.startswith("docs/proposals/"):
                continue
            blob = _git("show", f"{base}:{oldp}")
            if blob is None:
                continue
            fm, perr = None, None
            status = None
            for ln in blob.split("\n")[1:]:
                if ln.strip() == "---":
                    break
                if ln.startswith("status:"):
                    status = ln.partition(":")[2].strip()
            if status and status != "draft":
                err(os.path.join(ROOT, newp),
                    f"proposal renamed from {os.path.basename(oldp)} while status was "
                    f"{status!r} -- filenames freeze when a proposal leaves draft, because "
                    "people tip an id and renaming orphans the tips")


def check_head_signed():
    """Shipping .allowed_signers declares that signing is expected here, so an
    unsigned HEAD deserves a warning -- a signed history whose newest commits
    are quietly unsigned is worse than an unsigned one, because the signatures
    that are there imply the rest. Presence check only (no verification), so CI
    runners without signing config cannot false-positive; and a warning rather
    than an error, because PR merge refs are synthesized unsigned by GitHub.
    """
    if not os.path.exists(os.path.join(ROOT, ".allowed_signers")):
        return
    try:
        import subprocess
        head = subprocess.run(["git", "-C", ROOT, "cat-file", "commit", "HEAD"],
                              capture_output=True, text=True, timeout=10)
        if head.returncode == 0 and "gpgsig" not in head.stdout:
            warn(os.path.join(ROOT, ".allowed_signers"),
                 "HEAD is unsigned in a repo that ships .allowed_signers -- "
                 "signing config is per-working-copy and does not follow a clone")
    except (OSError, subprocess.TimeoutExpired):
        pass          # no git available; nothing to conclude


def main():
    ap = argparse.ArgumentParser(description="Validate a docs/ tree.")
    ap.add_argument("--fix", action="store_true",
                    help="regenerate stale navigation blocks in place")
    ap.add_argument("--preflight", action="store_true",
                    help="list open research questions and exit non-zero if any remain")
    ap.add_argument("--since", metavar="REF",
                    help="also apply history rules (no deletions, frozen proposal "
                         "filenames) by comparing against REF, e.g. origin/main")
    args = ap.parse_args()

    data = {kind: collect_events(kind) for kind in EVENTS}

    # Regenerate before validating anything, or --fix cannot recover from its own
    # output. A deleted record leaves a dangling link in the generated index; that
    # link fails check_links; and gating regeneration on a clean run means the one
    # command that would repair the index is the one refusing to run. Any generated
    # artifact that is also validated has this shape -- fix first, then check.
    if args.fix:
        check_nav(data, True)

    check_strays()
    check_links()
    check_shared_block(args.fix)
    check_tooling_unpushed()
    check_research_modes_doc()
    check_head_signed()
    if args.since:
        check_history(args.since)
    cross_check(data)
    check_rounds(data, collect_claims())
    living = {kind: collect_living(kind, set(data[LIVING[kind]["cites"][1]]))
              for kind in LIVING}

    questions = open_questions(data, living)
    for kind, rid, slug, path in questions:
        warn(path, f"needs research: {slug!r} -- no current scan answers it")

    stale_scans = stale_research(data)
    for rid, mode, age, horizon, path in stale_scans:
        warn(path, f"{mode} research is {age}d old against a {horizon}d horizon")

    if args.preflight:
        # A gate that passes on a broken tree is no gate. Preflight exists to be
        # the last check before committing to a public position, so validation
        # errors block it too -- otherwise "preflight clean" could be printed
        # over a tree the plain run rejects, and the phrase would mean nothing.
        if errors:
            for e in errors:
                print(f"  ERROR {e}")
            print(f"\npreflight blocked -- {len(errors)} validation error(s) to fix first")
            return 1

        # Staleness warns on ordinary runs and blocks here. A build that breaks
        # because a date passed, with nothing changed, is a bad CI signal -- but
        # committing to a public position on numbers that expired is worse, and
        # this is the gate that stands in front of doing that.
        if questions or stale_scans:
            if questions:
                print(f"\n{len(questions)} open research question(s):\n")
                for kind, rid, slug, path in questions:
                    print(f"  {slug}")
                    print(f"      raised by  docs/{kind}/{rid}")
                print("\nResolve by writing a scan whose `answers:` lists the slug, or by "
                      "dropping\nthe need from the record if it stopped mattering.")
            if stale_scans:
                print(f"\n{len(stale_scans)} stale scan(s):\n")
                for rid, mode, age, horizon, path in stale_scans:
                    print(f"  {rid}")
                    print(f"      {mode}: {age} days old, horizon {horizon}")
                print("\nRe-run each in its mode and supersede, or set status: superseded if "
                      "it no\nlonger bears on anything.")
            return 1
        print("\npreflight clean -- no open questions, no stale research")
        return 0

    stale = [] if errors else check_nav(data, args.fix)
    if stale and not args.fix:
        for f in stale:
            errors.append(f"{f}: navigation block is out of date -- run with --fix")

    counts = " ".join(f"{k}={len(v)}" for k, v in data.items())
    counts += " | " + " ".join(f"{k}={len(v)}" for k, v in living.items())
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
