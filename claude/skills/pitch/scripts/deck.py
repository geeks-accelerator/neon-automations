#!/usr/bin/env python3
"""Render business pitch-deck slides deterministically: SVG -> PNG.

Slides carry headlines and figures, so the text IS the content. Generating it
is the wrong tool twice over:

  - image models hallucinate glyphs. The first FLUX pass garbled the one number
    on the one slide whose entire subject was that number
  - this pitch's thesis is that its figures are exact and checkable. A deck
    about receipts, typeset from approximations, argues against itself

So: a small set of layouts, real fonts, exact strings, rendered at 1920x1080 by
rsvg-convert. No API, no credits, and a re-render is instant -- which matters
more than it sounds, because a deck gets re-cut many times and a paid pipeline
quietly discourages that.

Generated imagery still has a place: an atmospheric background behind a
statement slide, via slides.py. Text and numbers are not that place.

Deck spec is a markdown table in the storyboard: | # | segment | layout | content |
Layouts: statement, stat, list, receipt, quote.
"""
import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

W, H = 1920, 1080
BG, FG, ACCENT, MUTED, RULE = "#0B1220", "#F5F1E8", "#E8A33D", "#7A8699", "#1E2A3E"
FONT = "Helvetica, Arial, sans-serif"
ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*$")


def clean(s):
    """Undo markdown so the slide shows what the author meant.

    A literal pipe inside a markdown table has to be written `\\|` or it ends the
    cell -- but the slide should show `|`, not the escape. Same for emphasis:
    `*is*` is markup in the spec and a pair of asterisks on the slide.
    """
    s = s.replace("\\|", "|")
    s = re.sub(r"(?<!\w)[*_]{1,2}(.+?)[*_]{1,2}(?!\w)", r"\1", s)
    return s.strip()


def esc(s):
    return html.escape(clean(s), quote=False)


def wrap(text, per_line):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > per_line and cur:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def tspans(lines, x, y0, lh, size, weight="400", fill=FG, anchor="start"):
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x}" y="{y0 + i*lh}" font-family="{FONT}" font-size="{size}" '
                   f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
                   f'letter-spacing="-0.5">{esc(ln)}</text>')
    return "\n".join(out)


def chrome(n, total, segment):
    """Slide furniture: a rule, the segment name, and a page number. Small, and
    it is what makes a sequence of images read as one deck."""
    return (f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>'
            f'<rect x="140" y="150" width="120" height="5" fill="{ACCENT}"/>'
            f'<text x="140" y="{H-90}" font-family="{FONT}" font-size="26" fill="{MUTED}" '
            f'letter-spacing="2">{esc(segment.upper())}</text>'
            f'<text x="{W-140}" y="{H-90}" font-family="{FONT}" font-size="26" fill="{MUTED}" '
            f'text-anchor="end">{n} / {total}</text>')


def layout_statement(content, **k):
    lines = wrap(content, 26)
    size = 116 if len(lines) <= 2 else 92
    return tspans(lines, 140, 400, size * 1.18, size, weight="600")


def layout_stat(content, **k):
    """`74% | never deliver ;; 61% | ship late` -- up to three figures."""
    items = [p.strip() for p in content.split(";;") if p.strip()]
    out, x = [], 140
    colw = (W - 280) // max(len(items), 1)
    for it in items:
        num, _, label = it.partition("|")
        out.append(f'<text x="{x}" y="520" font-family="{FONT}" font-size="150" '
                   f'font-weight="700" fill="{ACCENT}" letter-spacing="-4">{esc(num.strip())}</text>')
        out.append(tspans(wrap(label.strip(), 22), x, 610, 46, 38, fill=FG))
        x += colw
    return "\n".join(out)


def layout_list(content, **k):
    head, _, rest = content.partition("::")
    hl = wrap(head.strip(), 30)
    out = [tspans(hl, 140, 360, 88, 74, weight="600")]
    y = 360 + 88 * len(hl) + 70
    for item in [i.strip() for i in rest.split(";;") if i.strip()]:
        out.append(f'<rect x="140" y="{y-30}" width="14" height="14" fill="{ACCENT}"/>')
        ls = wrap(item, 46)
        out.append(tspans(ls, 190, y, 56, 42, fill=FG))
        y += 56 * len(ls) + 30
    return "\n".join(out)


def layout_receipt(content, **k):
    """`Voice + music|22 ;; Images|1 ;; Domain|8 ;; TOTAL|31`

    Row spacing and the headline's own height are both computed, because a
    headline that wraps to two lines used to overprint the first row -- the
    layout assumed one line and said nothing when it got two.
    """
    head, _, rest = content.partition("::")
    hl = wrap(head.strip(), 30)
    out = [tspans(hl, 140, 330, 80, 68, weight="600")]
    rows = [r.strip() for r in rest.split(";;") if r.strip()]
    y = 330 + 80 * len(hl) + 70
    # shrink the row pitch if a long headline plus many rows would overflow
    pitch = 78 if y + 78 * len(rows) < H - 190 else max(56, (H - 190 - y) // max(len(rows), 1))
    for r in rows:
        label, _, amt = r.partition("|")
        total = label.strip().upper().startswith(("TOTAL", "ASK"))
        col = ACCENT if total else FG
        wt = "700" if total else "400"
        if total:
            out.append(f'<rect x="140" y="{y-52}" width="{W-280}" height="3" fill="{RULE}"/>')
            y += 26
        out.append(f'<text x="140" y="{y}" font-family="{FONT}" font-size="46" '
                   f'font-weight="{wt}" fill="{col}">{esc(label.strip())}</text>')
        out.append(f'<text x="{W-140}" y="{y}" font-family="{FONT}" font-size="46" '
                   f'font-weight="{wt}" fill="{col}" text-anchor="end">'
                   f'{esc(amt.strip())}</text>')
        y += pitch
    return "\n".join(out)


def layout_quote(content, **k):
    body, _, attrib = content.partition("::")
    lines = wrap(body.strip(), 30)
    out = [f'<text x="140" y="345" font-family="{FONT}" font-size="150" fill="{RULE}">&#8220;</text>']
    out.append(tspans(lines, 140, 430, 92, 76, weight="500"))
    if attrib.strip():
        out.append(f'<text x="140" y="{430 + 92*len(lines) + 60}" font-family="{FONT}" '
                   f'font-size="34" fill="{MUTED}">{esc(attrib.strip())}</text>')
    return "\n".join(out)


LAYOUTS = {"statement": layout_statement, "stat": layout_stat, "list": layout_list,
           "receipt": layout_receipt, "quote": layout_quote}


def parse_deck(path):
    text = Path(path).read_text(encoding="utf-8")
    fenced, rows = False, []
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced; continue
        if fenced:
            continue
        m = ROW_RE.match(line)
        if m and m.group(1).isdigit():
            rows.append((int(m.group(1)), m.group(2).strip(), m.group(3).strip(),
                         m.group(4).replace("\\|", "|")))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("deck")
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = parse_deck(args.deck)
    if not rows:
        sys.exit(f"no slide rows in {args.deck}")
    bad = [r for r in rows if r[2] not in LAYOUTS]
    if bad:
        sys.exit("unknown layout(s): " + ", ".join(f"#{n}:{lay}" for n, _, lay, _ in bad)
                 + f"\nknown: {', '.join(sorted(LAYOUTS))}")

    print(f"{len(rows)} slides")
    for n, seg, lay, content in rows:
        print(f"  {n:>2}. [{seg:<9}] {lay:<10} {content[:52]}")
    if args.dry_run:
        print("\n  (dry run -- nothing rendered)")
        return 0

    if not subprocess.run(["which", "rsvg-convert"], capture_output=True).returncode == 0:
        sys.exit("rsvg-convert not on PATH (brew install librsvg)")

    out_dir = Path(args.out) if args.out else Path(args.deck).parent / f"{Path(args.deck).stem}-slides"
    out_dir.mkdir(parents=True, exist_ok=True)
    print()
    for n, seg, lay, content in rows:
        body = LAYOUTS[lay](content)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}">{chrome(n, len(rows), seg)}{body}</svg>')
        svg_path = out_dir / f"{n:02d}.svg"
        png_path = out_dir / f"{n:02d}-{lay}.png"
        svg_path.write_text(svg, encoding="utf-8")
        r = subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H),
                            "-o", str(png_path), str(svg_path)],
                           capture_output=True, text=True)
        svg_path.unlink()
        if r.returncode != 0:
            sys.exit(f"rsvg-convert failed on slide {n}: {r.stderr.strip()[:200]}")
        print(f"  {n:>2}. {png_path.name}")
    print(f"\n  {len(rows)} slides -> {out_dir}   cost: $0.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
