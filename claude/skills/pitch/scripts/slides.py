#!/usr/bin/env python3
"""Generate storyboard slides on Replicate, and report what they cost.

Companion to render.py. Same three properties, for the same reasons:

  - stdlib only, so it runs from a fresh clone with nothing installed
  - content-hash cached, so an unchanged prompt never costs twice
  - --dry-run reports the bill through the SAME parser a real run uses, so the
    published cost and the actual spend cannot drift apart

Replicate, not Leonardo, is the priced line. FLUX is quotable per image, which
is what lets a round's ask stay an itemized receipt; Leonardo bills GPU-load
tokens against a subscription with no published per-model table, so its honest
ask line is "$N/mo, of which this round used an unmeasurable fraction". See the
Leonardo pricing scan.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from paths import build_dir

# Replicate sits behind Cloudflare, which answers a UA-less request with
# HTTP 403 "error code: 1010" -- a browser-integrity block that reads exactly
# like a rejected token. Send a User-Agent and it is a normal API.
USER_AGENT = "neon-pitch/1.0 (+https://github.com/geeks-accelerator/neon-automations)"
API = "https://api.replicate.com/v1"

MODELS = {
    # slug: (owner/name, price per image USD, note)
    "schnell": ("black-forest-labs/flux-schnell", 0.003, "fast, cheapest, good enough for stills"),
    "dev":     ("black-forest-labs/flux-dev",     0.025, "slower, better prompt adherence"),
    "pro":     ("black-forest-labs/flux-1.1-pro", 0.040, "best, and 13x schnell"),
}

ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*$")
STYLE_RE = re.compile(r"^>\s*`(.+?)`\s*$", re.S | re.M)


def parse_storyboard(path):
    """Return (style_token, [(n, segment, title, prompt)]).

    A slide row is a table row whose first cell is a number. The style token is
    the blockquoted code span. Same shape rule as the claims ledger: fix the row
    format and the file becomes machine-readable without ceremony.
    """
    text = Path(path).read_text(encoding="utf-8")
    fenced = False
    style, rows = "", []
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = ROW_RE.match(line)
        if m and m.group(1).isdigit():
            rows.append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
    sm = STYLE_RE.search(text)
    if sm:
        style = " ".join(sm.group(1).split())
    return style, rows


def get_token():
    tok = os.environ.get("REPLICATE_API_TOKEN")
    if tok:
        return tok
    here = Path(__file__).resolve().parent
    for base in [here, *here.parents, Path.cwd(), *Path.cwd().parents]:
        for name in (".env.local", ".env"):
            p = base / name
            if not p.exists():
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("REPLICATE_API_TOKEN="):
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
    sys.exit("REPLICATE_API_TOKEN not set. Export it or put it in .env.local "
             "(gitignored -- never commit it).")


def api(path, method="GET", body=None, token=None, attempts=4):
    """One request, retrying 5xx and 429 with backoff.

    Replicate returns a bare 503 "Internal server error" often enough that a
    single attempt makes a working pipeline look broken. 4xx other than 429 is
    a real client error and fails immediately -- retrying a malformed request
    just spends time discovering it four times.
    """
    last = None
    for i in range(attempts):
        req = urllib.request.Request(
            API + path,
            data=json.dumps(body).encode() if body else None,
            headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT,
                     "Content-Type": "application/json", "Accept": "application/json"},
            method=method)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            last = RuntimeError(f"replicate {e.code}: {detail}")
            if e.code < 500 and e.code != 429:
                raise last
        except urllib.error.URLError as e:
            last = RuntimeError(f"connection failed: {e.reason}")
        if i < attempts - 1:
            time.sleep(2 ** i)
    raise last


def fetch(url, token=None):
    """Download a finished output.

    Deliberately unauthenticated: the output URL is a delivery CDN, not the API,
    and it rejects an Authorization header with a bare 400. That failure lands
    *after* the image has already been generated and billed, so it reads as "the
    generation failed" while actually meaning "the generation worked and the
    download did not" -- and the run's own cost line under-reports, because it
    counts successes.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def generate_with_retry(prompt, model, token, tries=3, unsafe=False):
    """Retry a *prediction-level* failure, which is different from an HTTP one.

    FLUX's safety checker false-positives on ordinary editorial prompts -- a
    blank paper form with a number circled in red pencil tripped it. The error
    itself says to try again, and it is stochastic, so retrying is the vendor's
    own remedy and costs nothing when it works.

    `unsafe` disables the checker. It stays opt-in and off by default: these
    prompts live in a tracked, reviewable storyboard, so a human can see exactly
    what is being asked for, and a flag that silently turns off a safety control
    is not something a pipeline should flip on its own.
    """
    last = None
    for i in range(tries):
        try:
            return generate(prompt, model, token, unsafe=unsafe)
        except RuntimeError as e:
            last = e
            if "NSFW" not in str(e) and "safety" not in str(e).lower():
                raise
            if i < tries - 1:
                time.sleep(1.5 * (i + 1))
    raise last


def generate(prompt, model, token, poll=2.0, timeout=300, unsafe=False):
    owner_name, _, _ = MODELS[model]
    # Official models take POST /models/{owner}/{name}/predictions with only an
    # input body. The generic /predictions endpoint requires a pinned `version`
    # and rejects a `model` field outright -- a 422 that names both problems at
    # once and looks like a malformed request rather than the wrong endpoint.
    pred = api(f"/models/{owner_name}/predictions", "POST", token=token, body={
        "input": {"prompt": prompt, "aspect_ratio": "16:9", "output_format": "png",
                  "num_outputs": 1, "disable_safety_checker": bool(unsafe)},
    })
    started = time.monotonic()
    while pred.get("status") in ("starting", "processing"):
        if time.monotonic() - started > timeout:
            raise RuntimeError(f"timed out after {timeout}s (id {pred.get('id')})")
        time.sleep(poll)
        pred = api(f"/predictions/{pred['id']}", token=token)
    if pred.get("status") != "succeeded":
        raise RuntimeError(f"{pred.get('status')}: {str(pred.get('error'))[:200]}")
    out = pred.get("output")
    url = out[0] if isinstance(out, list) else out
    return fetch(url, token)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("storyboard")
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default="schnell", choices=sorted(MODELS))
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and price only; no token, no network, no cost")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated slide numbers")
    ap.add_argument("--unsafe", action="store_true",
                    help="disable the safety checker. Opt-in, for reviewed storyboard "
                         "prompts that false-positive; never the default")
    args = ap.parse_args()

    sb = Path(args.storyboard)
    style, rows = parse_storyboard(sb)
    if not rows:
        sys.exit(f"no slide rows in {sb} (expected table rows starting with a number)")
    if args.only:
        want = {int(x) for x in args.only.split(",") if x.strip().isdigit()}
        rows = [r for r in rows if r[0] in want]

    _, price, note = MODELS[args.model]
    print(f"{len(rows)} slides, model {args.model} ({note}) at ${price}/image")
    print(f"style: {style[:70]}{'...' if len(style) > 70 else ''}\n")
    for n, seg, title, prompt in rows:
        print(f"  {n:>2}. [{seg.strip():<9}] {title.strip()[:26]:<28} {len(prompt)} chars")
    total = len(rows) * price
    print(f"\n  cost if all generated: ${total:.2f}")

    if args.dry_run:
        print("  (dry run -- nothing generated, nothing spent)")
        return 0

    token = get_token()
    out_dir = Path(args.out) if args.out else build_dir(sb, f"{sb.stem}-slides")
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_path = out_dir / "cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    made = reused = failed = 0
    print()
    for n, seg, title, prompt in rows:
        full = f"{prompt.strip()}, {style}" if style else prompt.strip()
        digest = hashlib.sha256(f"{args.model}|{full}".encode()).hexdigest()[:16]
        dest = out_dir / f"{n:02d}-{re.sub(r'[^a-z0-9]+', '-', title.strip().lower())[:28]}.png"

        # A slide's filename carries its title, so retitling card 3 leaves
        # `03-old-title.png` beside `03-new-title.png` -- and assemble.py globs
        # by number, so it refuses with "slide 3 is ambiguous" until someone
        # deletes the directory by hand. deck.py clears its stale slides for
        # this reason; here the same number can only be held by one file.
        #
        # Rename rather than delete when the image is still right: the digest
        # covers the model and the prompt, not the title, so a retitled card
        # with an unchanged prompt keeps the picture it already paid for.
        for other in sorted(out_dir.glob(f"{n:02d}-*.png")):
            if other == dest:
                continue
            if cache.get(other.name) == digest and not args.force:
                other.replace(dest)
                cache[dest.name] = digest
                print(f"  {n:>2}. retitled, image kept")
            else:
                other.unlink()
            cache.pop(other.name, None)
            cache_path.write_text(json.dumps(cache, indent=2))

        if dest.exists() and cache.get(dest.name) == digest and not args.force:
            print(f"  {n:>2}. unchanged, reused")
            reused += 1
            continue
        print(f"  {n:>2}. generating {title.strip()[:34]}...", end="", flush=True)
        try:
            dest.write_bytes(generate_with_retry(full, args.model, token,
                                                 unsafe=args.unsafe))
            cache[dest.name] = digest
            cache_path.write_text(json.dumps(cache, indent=2))
            print(f" -> {dest.name}")
            made += 1
        except Exception as e:
            print(f" FAILED: {e}")
            failed += 1

    cache_path.write_text(json.dumps(cache, indent=2))
    print(f"\n  {made} generated, {reused} reused, {failed} failed")
    print(f"  spent this run: ~${made * price:.2f}")
    if failed:
        print(f"  re-run to retry the {failed} that failed; cached slides cost nothing again")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
