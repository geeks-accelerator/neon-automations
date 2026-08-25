#!/usr/bin/env python3
"""Generate the public pitch site from a private project's pitch tree.

The publishing surface is a TARGET, not a source. Its content is generated from
docs/pitch/ and docs/rounds/; editing it directly is drift, and the generator is
what makes that rule enforceable rather than aspirational.

It extracts *data* -- claim rows, ask lines, the frozen threshold, measured
durations -- and renders a purpose-built page. It deliberately does not dump
markdown through a converter: the private tree contains the workshop, and a
converter would publish whatever happened to be in a file rather than what a
stranger should see.

**It also states what cannot be checked.** A published ledger whose citations
point into a private repository asks the reader to take our word for it. The
tags are honest about what kind of evidence stands behind a claim; whether a
reader can reach it is a separate fact. The page says so, prominently, because
publishing the first without the second claims a verifiability that is not being
offered.

stdlib only. No build step -- the output is a static directory that GitHub Pages
serves as-is.
"""
import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

from paths import build_root

CLAIM_RE = re.compile(r"^\|\s*(C-\d+)\s*\|\s*(.+?)\s*\|\s*`(\w+)`\s*\|\s*(.+?)\s*\|\s*$")
TAG_CLASS = {"EXTRACTED": "ex", "RESEARCHED": "re", "ASSERTED": "as", "CHECKED": "ch"}


def md_inline(s):
    """The small subset that appears in extracted fields. Escape first, so a
    stray angle bracket in a citation cannot become markup."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def read_claims(pitch):
    rows, fenced = [], False
    for line in (pitch / "claims.md").read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = CLAIM_RE.match(line)
        if m:
            rows.append(m.groups())
    return rows


def read_fm(path, key):
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def project_name(proj):
    """The project's own display name, from its README H1.

    Not the directory name: a slug like "some-project" is a path, while the
    README H1 is what the project calls itself, and a published page carries
    the second.
    """
    for candidate in (proj / "README.md", proj / "docs" / "README.md"):
        if candidate.exists():
            m = re.search(r"^#\s+(.+)$", candidate.read_text(encoding="utf-8"), re.M)
            if m:
                return m.group(1).strip()
    return proj.resolve().name


def one_liner(pitch):
    """The page headline is the pitch's own one-liner, not a copy of it.

    It was previously a string literal here that duplicated one-liner.md
    almost-but-not-quite -- two paths to one sentence, which is how they drift.
    """
    f = pitch / "one-liner.md"
    if f.exists():
        body = f.read_text(encoding="utf-8").split("<!-- /nav:parent -->")[-1]
        for para in body.split("\n\n"):
            s = " ".join(para.split()).strip()
            if s and not s.startswith(("#", "<!--", "**Parent:**", "|", "-")):
                return s.strip("*")
    return ""


def duration(audio_dir, unit):
    """Measured seconds from render.py's duration.json, or None.

    Never a fallback figure. A published duration that nobody measured is the
    exact defect this pipeline has hit three times, so when the render has not
    run the page omits the line rather than stating a number.
    """
    f = audio_dir / "duration.json"
    if not f.exists():
        return None
    try:
        secs = json.loads(f.read_text(encoding="utf-8"))["seconds"]
    except (ValueError, KeyError):
        return None
    return f"{secs:.1f}s" if unit == "s" else f"{secs / 60:.1f}"


def read_ask(pitch):
    """The itemized table out of the-ask.md -- the reasonable column."""
    out, seen = [], False
    for line in (pitch / "the-ask.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| line |"):
            seen = True
            continue
        if seen:
            if not line.startswith("|"):
                if out:
                    break
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and not set(cells[0]) <= set("-: "):
                out.append((cells[0], cells[-1]))
    return out


def page(ctx):
    claims = "\n".join(
        f'<tr><td class="id">{c[0]}</td><td>{md_inline(c[1])}</td>'
        f'<td><span class="tag {TAG_CLASS.get(c[2],"as")}">{c[2]}</span></td>'
        f'<td class="cite">{md_inline(c[3])}</td></tr>'
        for c in ctx["claims"])
    ask = "\n".join(f"<tr><td>{md_inline(a)}</td><td class=num>{md_inline(b)}</td></tr>"
                    for a, b in ctx["ask"])
    return f"""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(ctx['title'])}</title>
<style>
:root{{--bg:#fbfaf8;--fg:#14181f;--mut:#5d6570;--line:#e4e0d8;--acc:#b4791f;--card:#fff}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0d1117;--fg:#e9e6e0;--mut:#949daa;--line:#232a35;--acc:#e0a84a;--card:#141b24}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);
font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.wrap{{max-width:820px;margin:0 auto;padding:0 22px 96px}}
header{{padding:72px 0 26px}}
h1{{font-size:clamp(30px,5vw,46px);line-height:1.12;letter-spacing:-.022em;margin:0 0 14px}}
h2{{font-size:26px;letter-spacing:-.015em;margin:56px 0 14px;padding-top:22px;border-top:1px solid var(--line)}}
h3{{font-size:18px;margin:30px 0 8px}}
p{{margin:0 0 15px}} .lead{{font-size:20px;color:var(--mut)}}
video{{width:100%;border-radius:10px;background:#000;display:block;border:1px solid var(--line)}}
table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:15px}}
th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:12px;text-transform:uppercase;letter-spacing:.09em;color:var(--mut);font-weight:600}}
.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.id{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;color:var(--mut);white-space:nowrap}}
.cite{{font-size:13px;color:var(--mut)}}
.tag{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10.5px;letter-spacing:.05em;
padding:2px 7px;border-radius:3px;white-space:nowrap;border:1px solid}}
.ex{{color:#1a7f45;border-color:#1a7f4555;background:#1a7f450f}}
.re{{color:#2563c9;border-color:#2563c955;background:#2563c90f}}
.as{{color:#b4791f;border-color:#b4791f55;background:#b4791f0f}}
.ch{{color:#8a4fbf;border-color:#8a4fbf55;background:#8a4fbf0f}}
@media(prefers-color-scheme:dark){{.ex{{color:#5fd694}}.re{{color:#7aa9ff}}.as{{color:#e0a84a}}.ch{{color:#c69bf0}}}}
.note{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--acc);
border-radius:6px;padding:18px 20px;margin:22px 0}}
.note p:last-child{{margin:0}}
.big{{display:flex;gap:34px;flex-wrap:wrap;margin:18px 0 6px}}
.big div{{flex:1;min-width:130px}}
.big b{{display:block;font-size:38px;line-height:1.1;letter-spacing:-.03em;color:var(--acc);
font-variant-numeric:tabular-nums}}
.big span{{color:var(--mut);font-size:14px}}
a{{color:inherit;text-decoration-color:var(--acc);text-underline-offset:3px}}
code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.88em;
background:var(--card);border:1px solid var(--line);border-radius:3px;padding:1px 5px}}
footer{{margin-top:60px;padding-top:22px;border-top:1px solid var(--line);color:var(--mut);font-size:14px}}
</style>
<div class=wrap>
<header>
<h1>{html.escape(ctx['headline'])}</h1>
<p class=lead>{md_inline(ctx['lead'])}</p>
</header>

<video controls preload="metadata" playsinline poster="media/poster.png">
<source src="media/round.mp4" type="video/mp4">
</video>
<p class=cite>{ctx['cite']}</p>

<h2>What this round costs</h2>
<p>Itemized from public list prices. Not a target — a receipt.</p>
<table><tr><th>Line</th><th class=num>Per round</th></tr>
{ask}
</table>

<h2>The threshold, frozen before this posted</h2>
<div class=note>
<p><strong>{md_inline(ctx['threshold'])}</strong></p>
<p>Written into the round record before anything went out. A validator rejects a posted round
with no threshold, and rejects any later edit to it. If this misses, the number it was meant to
hit stays visible next to the number it got.</p>
</div>

<h2>What is actually built</h2>
<div class=big>
<div><b>0</b><span>lines of product code</span></div>
<div><b>{ctx['n_claims']}</b><span>claims in this ledger</span></div>
<div><b>{ctx['pct']}%</b><span>backed by the repository</span></div>
<div><b>{ctx['risk']}</b><span>of the riskiest {ctx['risk_n']}, extracted</span></div>
</div>
<p>The second number is the real one. Most of what this project leans on is a bet about
readers, and no repository can demonstrate anything about its readers.</p>

<h2>What you cannot check, and why</h2>
<div class=note>
<p>The project repository is <strong>private, and staying private</strong>. Every
<code>EXTRACTED</code> claim below cites a file, a commit, or a re-runnable command — honestly —
and <strong>you cannot follow any of them.</strong></p>
<p>That is worth saying rather than wording around. A tag states what kind of evidence stands
behind a claim; whether a reader can reach it is a separate fact, and publishing the first
without the second would claim a verifiability that is not being offered.</p>
<p>What is open: the <a href="https://github.com/geeks-accelerator/neon-automations">tooling that
produced this pitch</a> is public, so the <em>method</em> is fully checkable even where the
subject is not. Anything cited here can be shown on request.</p>
</div>

<h2>The ledger — {ctx['n_claims']} claims</h2>
<p>Every claim this pitch makes, tagged with the kind of evidence behind it.
<span class="tag ex">EXTRACTED</span> the repository demonstrates it ·
<span class="tag re">RESEARCHED</span> a dated external scan ·
<span class="tag ch">CHECKED</span> verified directly, no citable source ·
<span class="tag as">ASSERTED</span> nothing independent backs it.</p>
<table><tr><th>id</th><th>claim</th><th>tag</th><th>citation</th></tr>
{claims}
</table>

<footer>
<p>Generated from the project's pitch tree by
<a href="https://github.com/geeks-accelerator/neon-automations">neon-automations</a>. This page is
a target, not a source — edits here are drift.</p>
</footer>
</div>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("project", help="path to the private project (contains docs/pitch/)")
    ap.add_argument("--out", required=True, help="publishing directory")
    ap.add_argument("--round", default=None, help="round record (default: newest)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    proj = Path(args.project)
    pitch = proj / "docs" / "pitch"
    if not pitch.is_dir():
        sys.exit(f"no docs/pitch/ under {proj}")
    rounds = sorted((proj / "docs" / "rounds").glob("2*.md"))
    rec = Path(args.round) if args.round else (rounds[-1] if rounds else None)
    if rec is None:
        sys.exit("no round record found")

    claims = read_claims(pitch)
    ex = sum(1 for c in claims if c[2] == "EXTRACTED")
    idx = (pitch / "README.md").read_text(encoding="utf-8")
    rm = re.search(r"riskiest[^:]*:\s*\*?\*?([\d.]+)\s*of\s*(\d+)", idx, re.I)

    turn = read_fm(rec, "turn") or "1"
    ctx = {
        "title": f"{project_name(proj)} — Round {turn}",
        "headline": one_liner(pitch),
        "lead": "Every claim below is tagged with the kind of evidence behind it, "
                "including the ones nothing backs.",
        "claims": claims, "n_claims": len(claims),
        "pct": round(ex / max(len(claims), 1) * 100),
        "risk": rm.group(1) if rm else "?", "risk_n": rm.group(2) if rm else "?",
        "ask": read_ask(pitch),
        "threshold": read_fm(rec, "threshold") or "(no threshold recorded)",
        "turn": turn,
    }
    # Built here rather than interpolated in the template, because each half is
    # a measurement that may not exist yet and "Round 1 - None" is worse than a
    # shorter sentence.
    # Renders live under build/pitch/<round-id>/, scoped to the round being
    # published rather than to whatever ran last -- so republishing turn 1
    # after turn 2 rendered still finds turn 1's video.
    build = build_root(pitch, rec.stem)
    secs = duration(build / "two-minute-audio", "s")
    mins = duration(build / "long-form-audio", "m")
    cite = f"Round {turn}" + (f" &mdash; {secs}" if secs else "")
    if mins and (build / "long-form-video" / "round.mp4").exists():
        cite += f' &middot; the full {mins}-minute version is <a href="media/full.mp4">here</a>.'
    else:
        cite += "."
    ctx["cite"] = cite

    print(f"  {len(claims)} claims, {ex} extracted ({ctx['pct']}%)")
    print(f"  riskiest {ctx['risk']} of {ctx['risk_n']}   ask lines: {len(ctx['ask'])}")
    print(f"  threshold: {ctx['threshold'][:64]}")
    if args.dry_run:
        print("\n  (dry run -- nothing written)")
        return 0

    out = Path(args.out)
    (out / "media").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page(ctx), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")

    for src, dst in [(build / "two-minute-video" / "round.mp4", "media/round.mp4"),
                     (build / "long-form-video" / "round.mp4", "media/full.mp4")]:
        if src.exists():
            shutil.copy2(src, out / dst)
            print(f"  copied {dst}  ({src.stat().st_size/1_048_576:.1f} MB)")
    first = sorted((build / "gamma-slides").glob("01-*.png"))
    if first:
        shutil.copy2(first[0], out / "media" / "poster.png")
        print("  copied media/poster.png")
    print(f"\n  {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
