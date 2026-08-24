"""Generated navigation for a docs tree -- HATEOAS applied to files.

The principle: every artifact tells you where you can go next, with no external
knowledge required. See obviously-not/docs/guides/hateoas.md.

Everything here is *derived*, never hand-written. The validator already parses
every frontmatter and resolves every cross-reference, so it holds the whole
graph; hand-maintaining navigation would just relocate the drifting-map problem
into the files. Two rules follow from that guide and both are load-bearing:

  Stale links are worse than no links, because they build false trust. So the
  generated block is checked on every run and regenerated with --fix; a file
  whose block is out of date fails.

  No dead ends. Every file gets somewhere to go. Where there genuinely is no
  next action -- a proposal waiting on the crowd, an observation at n=1 -- say
  why rather than inventing one, because a fabricated action is a worse dead
  end than an honest stop.
"""
import os
import re

# Canonical web URL for the skill. Generated READMEs link here rather than to the
# local .claude/skills path: that path resolves on disk but crosses a symlink,
# and GitHub's web UI renders a symlink as a text blob containing the target
# path -- every such link 404s for anyone browsing the repo. A URL into the
# public tooling repo works on the web, in standalone clones, and in CI alike.
SKILL_URL = "https://github.com/geeks-accelerator/neon-automations/blob/main/claude/skills/neon-docs/SKILL.md"

INDEX_BEGIN, INDEX_END = "<!-- index:begin -->", "<!-- index:end -->"
INDEX_RE = re.compile(re.escape(INDEX_BEGIN) + r".*?" + re.escape(INDEX_END), re.S)

# Directory READMEs are signposts, not convention documents. The conventions live
# in SKILL.md, in one place; a README that restates them is a second copy that
# drifts. What a README owes a reader is: what lands here, how to move through it,
# and what is currently in it.
#
# All three are generated, so the duplication that would otherwise accumulate
# across projects cannot happen -- there is one definition and N renderings.
# Anything written below the generated block is preserved, so a project can add
# notes of its own without fighting the tool.
DIRECTORY_DOC = {
    "proposals": ("the tipped backlog",
        "Units of work the community can tip. Tips set the order the agent works in."),
    "plans": ("implementation detail",
        "How an approved proposal gets built. Every plan names the proposal it serves."),
    "issues": ("reported defects",
        "Something is broken or behaves unintendedly. Wanted work is a proposal, not an issue."),
    "observations": ("codified learnings",
        "Things that surprised us or cost debugging time, so the next agent does not repeat them."),
    "decisions": ("the ledger",
        "Non-obvious, hard-to-reverse choices, with what they cost."),
    "research": ("what was true when we looked",
        "External facts a choice turns on, dated so the ground cannot shift under a decision."),
    "architecture": ("the synthesis",
        "How the system works today, derived from the records that produced it."),
    "vision": ("future state",
        "Where this is going. Not commitments."),
}

HOW_TO_READ = {
    "events": ("**Newest first.** Every file is dated and nothing here is rewritten, so an old "
               "record still says what it said. Check `status` before relying on one — "
               "retired records stay in place on purpose, and the trail of what was rejected "
               "is usually the most useful thing here."),
    "research": ("**Newest first, and mind the status.** A `superseded` scan is not wrong, it is "
                 "*expired* — read it when auditing why a past decision looked sensible, never "
                 "when you want current facts. For those, take the newest `current` scan."),
    "decisions": ("**Newest first, then follow `supersedes` backwards.** A superseded decision is "
                  "kept unedited because the reasoning that stopped holding is the part worth "
                  "reading. The chain is the history of how thinking changed."),
    "living": ("**These are rewritten in place, so what you see is what is currently true.** "
               "There are no dates in the filenames for that reason. Git holds what they used "
               "to say."),
}

PARENT_BEGIN, PARENT_END = "<!-- nav:parent -->", "<!-- /nav:parent -->"
NAV_BEGIN, NAV_END = "<!-- nav -->", "<!-- /nav -->"
PARENT_RE = re.compile(re.escape(PARENT_BEGIN) + r".*?" + re.escape(PARENT_END), re.S)
NAV_RE = re.compile(r"\n*" + re.escape(NAV_BEGIN) + r".*?" + re.escape(NAV_END), re.S)
H1_RE = re.compile(r"^(#\s+.*)$", re.M)

MAX_STEPS = 5      # the guide's cap: more than five needs priority signals


def rel(from_path, to_path):
    return os.path.relpath(to_path, os.path.dirname(from_path))


def build_graph(events, living, docs_root, parse):
    """Forward edges are declared in frontmatter. Back edges are the point.

    One-way links are a named anti-pattern: you could get from an issue to the
    observation it produced but never back. Every forward edge here gets its
    reverse computed.
    """
    back = {}     # id -> list of (label, path)

    def add(target_id, kind, label, src_path):
        back.setdefault((kind, target_id), []).append((label, src_path))

    for pid, (path, fm) in events["plans"].items():
        if fm.get("proposal"):
            add(fm["proposal"], "proposals", "Plan", path)
    for iid, (path, fm) in events["issues"].items():
        if fm.get("observation"):
            add(fm["observation"], "observations", "Reported by", path)
    for did, (path, fm) in events["decisions"].items():
        for ref in (fm.get("supersedes") or []):
            add(ref, "decisions", "Superseded by", path)
        for ref in (fm.get("research") or []):
            add(ref, "research", "Informed", path)
    for rid, (path, fm) in events["research"].items():
        for ref in (fm.get("supersedes") or []):
            add(ref, "research", "Superseded by", path)
    for kind, (cite_field, cite_dir) in living.items():
        for path, fm in kind_docs(docs_root, kind, parse):
            refs = fm.get(cite_field) or []
            if isinstance(refs, str):
                refs = [refs]
            for ref in refs:
                add(ref, cite_dir, "Cited by", path)
    return back


def kind_docs(docs_root, kind, parse):
    """Living documents with frontmatter, for back-edge construction."""
    d = os.path.join(docs_root, kind)
    if not os.path.isdir(d):
        return
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md") or name == "README.md":
            continue
        path = os.path.join(d, name)
        fm, err = parse(path)
        if not err:
            yield path, fm


def next_steps(kind, fm, doc_id, path, events, back):
    """State-driven actions with reasons.

    The status vocabularies are already a state machine, so these fall out of
    fields that exist rather than needing a parallel system. Reasons matter more
    than the actions: the guide's point is that consumers, and agents especially,
    act on a why rather than a what.
    """
    status = fm.get("status")
    steps, note = [], None

    if kind == "proposals":
        plans = [p for p, f in events["plans"].values() if f.get("proposal") == doc_id]
        if status == "draft":
            steps.append(("Open it for tipping",
                          "a draft is invisible to the crowd, so nothing can fund it"))
        elif status == "open":
            note = "Waiting on tips. Nothing to do here until it crosses its threshold."
        elif status in ("funded", "approved") and not plans:
            steps.append(("Draft a plan in `docs/plans/` and set its `proposal:` to this id",
                          "money is committed to unspecified work until a plan exists"))
        elif status == "funded":
            steps.append(("Review the plans and set this to `approved`",
                          "funded work with unapproved plans is money sitting idle"))
        elif status == "approved":
            steps.append(("Set this to `building` and start the round",
                          "an approved proposal that never starts is the state projects die in"))
        elif status == "building":
            steps.append(("Tag a release, then set this to `shipped`",
                          "the attestation service reads the tag; without it delivery cannot be proven"))
        elif status == "shipped":
            steps.append(("Write an observation, or record that it taught nothing",
                          "shipping without asking what it taught is how the same cost gets paid twice"))
        elif status in ("declined", "dormant"):
            note = f"Closed as {status}. Left in place so the trail of what was rejected survives."

    elif kind == "plans":
        if status == "draft":
            steps.append(("Get the proposal approved",
                          "a plan cannot start before the work it implements is agreed"))
        elif status in ("approved", "in-progress"):
            steps.append(("Ship it: tagged release, green CI, funded feedback closed",
                          "those three are what the attestation service checks"))
        elif status == "shipped" and not fm.get("release"):
            steps.append(("Add a `release:` tag",
                          "a shipped plan without one cannot be tied to an attestation"))

    elif kind == "issues":
        if status in ("open", "confirmed"):
            steps.append(("Fix it, or open a proposal if the fix is structural",
                          "issues that need funded work belong in the tipped backlog"))
        elif status in ("fixed", "wontfix") and not fm.get("observation"):
            steps.append(("Write an observation, or set `observation:` to record there is none",
                          "closing without asking what it taught is the most common way a team "
                          "pays the same debugging cost twice"))

    elif kind == "observations":
        try:
            n = int(fm.get("n", 1))
        except (TypeError, ValueError):
            n = 1
        if n == 1:
            note = ("N=1. Nothing to do: this is an instance, not a rule. On recurrence, "
                    "increment `n`, update `last_seen`, and append dated evidence.")
        else:
            note = (f"N={n}. Recurrence has earned general language; it may be worth a "
                    "decision or an architecture change.")

    elif kind == "research":
        if status == "superseded":
            note = ("Superseded by newer research. Kept unedited -- decisions were made on "
                    "what it said at the time, and rewriting it would strand their reasoning.")
        else:
            note = ("Current. When the world moves, write a new scan that supersedes this "
                    "one rather than editing it.")

    elif kind == "decisions":
        cited = back.get(("decisions", doc_id), [])
        if status == "accepted" and not any(l == "Cited by" for l, _ in cited):
            steps.append(("Update or add an `architecture/` document citing this",
                          "a decision nothing cites means the synthesis does not yet reflect it"))
        elif status == "accepted":
            note = ("Accepted and reflected in the synthesis. Decisions are never edited -- "
                    "if this stops holding, write a new one that supersedes it.")
        elif status == "superseded":
            note = "Superseded. Kept unedited -- the reasoning that stopped holding is the useful part."

    return steps[:MAX_STEPS], note


def render(path, kind, fm, doc_id, events, back, docs_root, is_readme, living_cites):
    """Return (parent_line, nav_block) for one file."""
    dir_readme = os.path.join(os.path.dirname(path), "README.md")
    crumbs = []
    if not is_readme and os.path.exists(dir_readme):
        crumbs.append(f"[{kind}]({rel(path, dir_readme)})")
    crumbs.append(f"[docs]({rel(path, os.path.join(docs_root, 'README.md'))})")
    parent = f"**Parent:** " + " · ".join(crumbs)

    if is_readme:
        return parent, None

    related = []
    for field, target_kind, label in (("proposal", "proposals", "Implements"),
                                      ("observation", "observations", "Observation")):
        ref = fm.get(field)
        if ref and ref in events.get(target_kind, {}):
            related.append((label, events[target_kind][ref][0]))
    for ref in (fm.get("research") or []):
        if ref in events.get("research", {}):
            related.append(("Based on", events["research"][ref][0]))
    for ref in (fm.get("supersedes") or []):
        if ref in events.get("decisions", {}):
            related.append(("Supersedes", events["decisions"][ref][0]))
    # living documents cite the events that produced them -- render that edge
    # forward as well as backward, or the synthesis links one way only
    if kind in living_cites:
        cite_field, cite_dir = living_cites[kind]
        refs = fm.get(cite_field) or []
        if isinstance(refs, str):
            refs = [refs]
        for ref in refs:
            if ref in events.get(cite_dir, {}):
                related.append(("Derives from", events[cite_dir][ref][0]))
    related += back.get((kind, doc_id), [])

    steps, note = next_steps(kind, fm, doc_id, path, events, back)
    if kind in living_cites and not steps and not note:
        note = ("Living document — rewrite it when the thing it describes changes. "
                "Git holds what it used to say.")

    out = [NAV_BEGIN, ""]
    if related:
        out.append("## Related")
        out.append("")
        seen = set()
        for label, target in related:
            key = (label, target)
            if key in seen:
                continue
            seen.add(key)
            name = os.path.basename(target)[:-3]
            out.append(f"- **{label}:** [{name}]({rel(path, target)})")
        out.append("")
    out.append("## Next")
    out.append("")
    if steps:
        for action, reason in steps:
            out.append(f"1. **{action}** — {reason}.")
    else:
        out.append(note or "Nothing pending.")
    out.append("")
    out.append(NAV_END)
    return parent, "\n".join(out)


def render_readme(path, kind, docs_root, events, living_kinds):
    """Generate a directory README: purpose, how to read it, and a live index."""
    title, purpose = DIRECTORY_DOC[kind]
    how = HOW_TO_READ.get(kind) or HOW_TO_READ["living" if kind in living_kinds else "events"]
    is_living = kind in living_kinds

    out = [INDEX_BEGIN, "", f"# {kind} — {title}", "",
           f"**Parent:** [docs]({rel(path, os.path.join(docs_root, 'README.md'))})", "",
           purpose, "", "## How to read this directory", "", how, "", "## Contents", ""]

    d = os.path.dirname(path)
    names = sorted((n for n in os.listdir(d) if n.endswith(".md") and n != "README.md"),
                   reverse=not is_living)
    if not names:
        out.append("*Empty — nothing filed here yet.*")
    elif is_living:
        out += ["| document | updated |", "|---|---|"]
        for n in names:
            fm = _fm(os.path.join(d, n))
            out.append(f"| [{n[:-3]}]({n}) | {fm.get('updated', '—')} |")
    else:
        col = "n" if kind == "observations" else "status"
        out += [f"| date | record | {col} |", "|---|---|---|"]
        for n in names:
            fm = _fm(os.path.join(d, n))
            date, slug = n[:10], n[11:-3]
            out.append(f"| {date} | [{slug}]({n}) | {fm.get(col, '—')} |")
    out += ["", f"Conventions, schema, and the validator: [neon-docs]({SKILL_URL}).",
            "", INDEX_END]
    return "\n".join(out)


_FM_CACHE = {}


def _fm(path):
    if path not in _FM_CACHE:
        try:
            text = open(path, encoding="utf-8").read()
            data = {}
            if text.startswith("---\n"):
                end = text.find("\n---", 3)
                for line in text[4:end].split("\n"):
                    if ":" in line and not line.startswith((" ", "\t")):
                        k, _, v = line.partition(":")
                        data[k.strip()] = v.strip().strip("'\"")
            _FM_CACHE[path] = data
        except OSError:
            _FM_CACHE[path] = {}
    return _FM_CACHE[path]


def apply_readme(path, block, fix):
    """Replace the generated block; preserve anything a project wrote below it."""
    original = open(path, encoding="utf-8").read()
    m = _find_block(original, INDEX_RE)
    if m:
        text = original[:m.start()] + block + original[m.end():]
    else:
        text = block + "\n"
    if text == original:
        return False
    if fix:
        open(path, "w", encoding="utf-8").write(text)
    return True

CODE_SPAN_RE = re.compile(r"`[^`\n]*`")


def _mask_code_spans(text):
    """Blank out inline code spans so delimiter-matching cannot see them.

    A document that *writes about* the delimiters -- `<!-- nav -->` in a code
    span -- would otherwise have that occurrence treated as a real block opener,
    and everything from there to the closing delimiter deleted. That destroyed
    eleven lines of a committed decision record before anyone noticed.

    Masking rather than skipping, so offsets are preserved and the real block
    can still be located by index.
    """
    return CODE_SPAN_RE.sub(lambda m: " " * len(m.group(0)), text)


def _find_block(text, pattern):
    """Locate a generated block, ignoring any mention inside a code span."""
    return pattern.search(_mask_code_spans(text))


def apply(path, parent, nav, fix):
    """Insert or refresh the generated blocks. Returns True if the file was stale."""
    original = open(path, encoding="utf-8").read()
    text = original

    block = f"{PARENT_BEGIN}\n{parent}\n{PARENT_END}"
    m = _find_block(text, PARENT_RE)
    if m:
        text = text[:m.start()] + block + text[m.end():]
    else:
        m = H1_RE.search(text)
        if m:
            text = text[:m.end()] + "\n\n" + block + text[m.end():]
        else:
            text = block + "\n\n" + text

    if nav:
        m = _find_block(text, NAV_RE)
        if m:
            text = text[:m.start()] + text[m.end():]
        text = text.rstrip() + "\n\n" + nav + "\n"

    if text == original:
        return False
    if fix:
        open(path, "w", encoding="utf-8").write(text)
    return True


def starter_docs_readme(events, living):
    """A minimal docs/README.md for a tree that has none.

    Deliberately thin. This file is a project's own map and accumulates
    project-specific content, so it is written once and never regenerated --
    which means anything put here would be a guess a project has to delete
    rather than a default it can build on.
    """
    ev = " ".join(f"`{k}`" for k in events)
    lv = " ".join(f"`{k}`" for k in living)
    return f"""# docs

## Two kinds of document

| | | naming | how it changes |
|---|---|---|---|
| **Events** | {ev} | `2026-08-23-slug.md` | **accrete** — status advances, notes append, records get superseded |
| **Living** | {lv} | `repo-topology.md` | **overwritten** — what stops being true is deleted |

An event happened on a day; its account of what happened is never rewritten. A living
document describes what currently is, and carries no date because a date implies a snapshot
frozen at that moment.

Everything outside the event directories is a living document, including this file.

## Conventions

Schemas, the validator, and how to file each kind of record:
[neon-docs]({SKILL_URL}).

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --fix
```
"""
