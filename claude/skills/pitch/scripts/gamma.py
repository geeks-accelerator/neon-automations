#!/usr/bin/env python3
"""Generate deck slides with the Gamma Generate API and download them as PNGs.

Gamma does layout and visual design well, which is the half `deck.py` does
plainly and the half a generated-image model does not do at all. The API
exports PNG directly, so the slides drop straight into assemble.py -- nothing
here scrapes or reverse-engineers anything.

  POST https://public-api.gamma.app/v1.0/generations   (X-API-KEY header)
  GET  /v1.0/generations/{id}                          poll ~5s until completed
  -> gammaUrl (editable deck) + exportUrl (the PNGs)

API access starts at the Pro tier. On paid plans credits burn only on API
calls, Agent edits and Ultra models -- roughly 1-3 per card plus 2-15 per
standard image, so a 14-card illustrated deck is ~40-250 of Pro's 4,000/month.
The subscription is the cost; the per-round marginal is noise.

**textMode defaults to `preserve`, not `generate`.** That is deliberate and it
is the one setting worth arguing about. `generate` writes new prose from an
outline, which is what makes Gamma pleasant to use -- and it would let text
into this deck that no row in claims.md backs, which is the exact failure the
ledger exists to prevent. So: we supply finished, claim-checked copy and buy
Gamma's *design*, not its copywriting. Pass --text-mode generate if you want
expansion, and back-check every produced line against the ledger afterwards.
"""
import argparse
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://public-api.gamma.app/v1.0"
UA = "neon-pitch/1.0 (+https://github.com/geeks-accelerator/neon-automations)"


def get_key():
    k = os.environ.get("GAMMA_API_KEY")
    if k:
        return k
    here = Path(__file__).resolve().parent
    for base in [here, *here.parents, Path.cwd(), *Path.cwd().parents]:
        for name in (".env.local", ".env"):
            p = base / name
            if not p.exists():
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("GAMMA_API_KEY="):
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
    sys.exit("GAMMA_API_KEY not set. Create one at gamma.app (Pro or above), then put it "
             "in .env.local -- which .gitignore covers. Never commit it.")


def api(path, method="GET", body=None, key=None, attempts=4):
    last = None
    for i in range(attempts):
        req = urllib.request.Request(
            BASE + path,
            data=json.dumps(body).encode() if body else None,
            headers={"X-API-KEY": key, "User-Agent": UA,
                     "Content-Type": "application/json", "Accept": "application/json"},
            method=method)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            last = RuntimeError(f"gamma {e.code}: {detail}")
            if e.code < 500 and e.code != 429:
                raise last
        except urllib.error.URLError as e:
            last = RuntimeError(f"connection failed: {e.reason}")
        if i < attempts - 1:
            time.sleep(2 ** i)
    raise last


def outline_body(text):
    """Frontmatter and preamble out; cards only.

    **Everything before the first `---` separator is preamble and is not sent.**
    An outline file is also a tracked document with a title and a note about why
    it exists, and without this rule that prose becomes card one -- an eleven
    card deck whose opening slide explains the deck. Predictable beats clever:
    if you want a card first, start the file with a separator.
    """
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    parts = re.split(r"^---\s*$", text, flags=re.M)
    return "\n---\n".join(p for p in parts[1:] if p.strip()) if len(parts) > 1 else text


def download(url, dest_dir, prefix="slide"):
    """Fetch the export. PNG exports arrive as a zip of one file per card;
    a single-image export arrives as the image itself."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        blob = r.read()
    dest_dir.mkdir(parents=True, exist_ok=True)
    # Same hazard deck.py has: a re-run producing fewer cards leaves orphans
    # under numbers the assembler globs by, and it would cut a video from two
    # decks without failing.
    for f in sorted(dest_dir.glob("[0-9][0-9]-*.png")):
        f.unlink()
    if blob[:2] == b"PK":
        names = []

        def card_order(m):
            """Gamma names members `<card>_<slug>.png`. Sorting those as strings
            puts card 10 before card 1, which silently reorders the deck -- and
            a reordered deck still assembles, still plays, and is wrong."""
            mm = re.match(r"^(\d+)", Path(m).name)
            return (int(mm.group(1)) if mm else 10**6, m)

        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            members = sorted((m for m in z.namelist() if m.lower().endswith(".png")),
                             key=card_order)
            for i, m in enumerate(members, 1):
                out = dest_dir / f"{i:02d}-{Path(m).stem[:28]}.png"
                out.write_bytes(z.read(m))
                names.append(out)
        return names
    out = dest_dir / f"{prefix}.png"
    out.write_bytes(blob)
    return [out]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("outline", help="markdown outline; --- separates cards")
    ap.add_argument("--out", default=None)
    ap.add_argument("--text-mode", default="preserve",
                    choices=["preserve", "condense", "generate"],
                    help="preserve (default) keeps our claim-checked copy; generate writes new prose")
    ap.add_argument("--amount", default="detailed",
                    choices=["brief", "medium", "detailed", "extensive"])
    ap.add_argument("--images", default="pictographic",
                    choices=["pictographic", "aiGenerated", "themeAccent", "placeholder",
                             "noImages", "webFreeToUseCommercially"],
                    help="pictographic = Gamma's illustrations")
    ap.add_argument("--image-style", default="", help="free-text style for aiGenerated")
    ap.add_argument("--theme", default="", help="themeId from your workspace")
    ap.add_argument("--cards", type=int, default=0, help="0 = let cardSplit decide")
    ap.add_argument("--tone", default="calm, honest, grounded, understated")
    ap.add_argument("--audience", default="a stranger deciding in ninety seconds whether to back an idea")
    ap.add_argument("--export", default="png", choices=["png", "pdf", "pptx"])
    ap.add_argument("--dry-run", action="store_true", help="show the request; no key, no call")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    src = Path(args.outline)
    text = outline_body(src.read_text(encoding="utf-8"))
    cards = len([c for c in re.split(r"^---\s*$", text, flags=re.M) if c.strip()])

    payload = {
        "inputText": text,
        "textMode": args.text_mode,
        "format": "presentation",
        "cardSplit": "inputTextBreaks",
        "exportAs": args.export,
        "textOptions": {"amount": args.amount, "tone": args.tone, "audience": args.audience},
        "imageOptions": {"source": args.images},
        "cardOptions": {"dimensions": "16x9"},
    }
    if args.cards:
        payload["numCards"] = args.cards
        payload["cardSplit"] = "auto"
    if args.image_style:
        payload["imageOptions"]["style"] = args.image_style
    if args.theme:
        payload["themeId"] = args.theme

    print(f"{cards} cards from {src.name}  ({len(text):,} chars)")
    print(f"  textMode={args.text_mode}  amount={args.amount}  images={args.images}  "
          f"export={args.export}")
    if args.text_mode == "generate":
        print("  ! generate writes new prose -- back-check every line against claims.md")
    if args.dry_run:
        print("\n" + json.dumps({**payload, "inputText": f"<{len(text)} chars>"}, indent=2))
        print("\n  (dry run -- nothing sent)")
        return 0

    key = get_key()
    started = api("/generations", "POST", body=payload, key=key)
    gid = started.get("generationId") or started.get("id")
    if not gid:
        sys.exit(f"no generationId in response: {json.dumps(started)[:300]}")
    print(f"\n  generationId {gid}\n  polling...", end="", flush=True)

    t0 = time.monotonic()
    while True:
        if time.monotonic() - t0 > args.timeout:
            sys.exit(f"\n  timed out after {args.timeout}s. The generation may still finish; "
                     f"check status with generationId {gid}")
        time.sleep(5)
        st = api(f"/generations/{gid}", key=key)
        status = st.get("status")
        print(".", end="", flush=True)
        if status in ("completed", "failed", "error"):
            break
    print()
    if status != "completed":
        sys.exit(f"  generation {status}: {json.dumps(st)[:300]}")

    print(f"  deck: {st.get('gammaUrl', '(no url)')}")
    export_url = st.get("exportUrl") or st.get("exportUrls")
    if not export_url:
        sys.exit("  completed, but no exportUrl -- open the deck and export by hand")
    if isinstance(export_url, list):
        export_url = export_url[0]

    out_dir = Path(args.out) if args.out else src.parent / f"{src.stem}-slides"
    files = download(export_url, out_dir)
    print(f"\n  {len(files)} file(s) -> {out_dir}")
    for f in files:
        print(f"    {f.name}")
    print(f"\n  elapsed {time.monotonic() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
