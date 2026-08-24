#!/usr/bin/env python3
"""Generate the show's music bed -- once -- and reuse it every round.

This is the one production asset that is deliberately NOT regenerated per
round. Two reasons, and the second is the real one:

  - music costs more credits than narration. A 90s bed runs ~2,700 against
    ~3,900 for three takes of a 90s script, and it would recur every round
  - a recurring show needs a recurring theme. Regenerating it each episode
    throws away the sonic identity that makes episode seven recognisably the
    same series as episode two

So the output is a **source asset, not a build artifact**, and it is committed
rather than gitignored. Everything else in the pipeline is derived from a
tracked text file and reproducible from it; a theme regenerated from the same
prompt comes back different, so treating it as derived would quietly change the
show's identity on any fresh clone.

Generate long enough to cover a round with headroom; assemble.py trims and
fades to the narration's measured length.
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render as R

BASE = "https://api.elevenlabs.io/v1"

DEFAULT_PROMPT = (
    "Sparse, restrained instrumental bed for a serious documentary segment. "
    "Low sustained strings and soft piano, slow, unhurried, no percussion build, "
    "no drums, no swell, no resolution. Quiet and understated -- it sits far "
    "under a spoken voice and never competes with it. Neutral and honest in "
    "tone, not uplifting, not corporate, not tense."
)


def compose(prompt, ms, key):
    body = json.dumps({"prompt": prompt, "music_length_ms": ms}).encode()
    req = urllib.request.Request(
        BASE + "/music", data=body, method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json",
                 "Accept": "audio/mpeg"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"elevenlabs {e.code}: {e.read().decode('utf-8','replace')[:300]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="docs/pitch/theme.mp3",
                    help="where the theme lives; committed, not gitignored")
    ap.add_argument("--seconds", type=int, default=100,
                    help="cover the longest round with headroom; assembly trims")
    ap.add_argument("--prompt", default=DEFAULT_PROMPT)
    ap.add_argument("--force", action="store_true",
                    help="regenerate over an existing theme -- changes the show's identity")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    ms = args.seconds * 1000
    # ~900 credits per minute per variant, two variants by default
    est = int(args.seconds / 60 * 900 * 2)

    print(f"theme: {args.seconds}s -> {out}")
    print(f"  estimated ~{est:,} credits (music bills more than narration)")
    print(f"  prompt: {args.prompt[:72]}...")

    if out.exists() and not args.force:
        try:
            dur = R.probe_duration(out)
            print(f"\n  already exists: {dur:.1f}s, {out.stat().st_size/1024:.0f} KB")
        except Exception:
            print(f"\n  already exists: {out.stat().st_size/1024:.0f} KB")
        print("  Not regenerating. This asset is generate-once by design -- a new one "
              "would be a different theme,\n  and the point of a theme is that it does not "
              "change. Pass --force if that is what you want.")
        return 0

    if args.dry_run:
        print("\n  (dry run -- nothing generated, nothing spent)")
        return 0

    key = R.get_api_key()
    print("\n  composing...", end="", flush=True)
    audio = compose(args.prompt, ms, key)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(audio)
    print(f" done")
    meta = out.with_suffix(".json")
    meta.write_text(json.dumps({
        "prompt": args.prompt, "seconds": args.seconds,
        "prompt_sha256": hashlib.sha256(args.prompt.encode()).hexdigest()[:16],
    }, indent=2), encoding="utf-8")
    try:
        print(f"  {out}  {R.probe_duration(out):.1f}s, {out.stat().st_size/1024:.0f} KB")
    except Exception:
        print(f"  {out}  {out.stat().st_size/1024:.0f} KB")
    print(f"  prompt recorded in {meta.name} -- so a later regeneration is a deliberate "
          f"change, not an accident")
    return 0


if __name__ == "__main__":
    sys.exit(main())
