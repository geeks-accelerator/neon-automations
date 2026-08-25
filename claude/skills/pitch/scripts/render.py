#!/usr/bin/env python3
"""Render a pitch script to narration, and report its MEASURED duration.

Ported from gitwverse/scripts/monologue_audio.py (ElevenLabs + ffmpeg), reduced
to the one job the pitch skill needs: turn a script file into audio and say how
long it actually is.

Why this exists at all, given that the source pitch method is prompt-only and
argues a skill should not grow scripts: that argument is about *extraction* --
reasoning nobody wants automated. Rendering audio is mechanical, and Step 4b of
the skill specifies a render that had nothing to run.

The load-bearing part is not the audio. It is that **the word counter and the
renderer are the same parser**. A script's length was published twice from
ad-hoc counters and was wrong both times -- once by claiming a target as a
measurement, once by silently swallowing a generated <!-- nav --> block. Two
instruments, two failures, one number. Here `--dry-run` and a real render read
the identical text, so the published figure and the rendered file cannot
disagree.

No third-party dependencies -- a tool that needs `pip install` before it runs is
a tool nobody runs. ffmpeg/ffprobe on PATH are needed only to concatenate and
measure; --dry-run needs neither, and needs no API key.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from paths import build_dir

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
DEFAULT_MODEL = "eleven_multilingual_v2"
WPM = 150          # only for the estimate; a real render replaces it

# A spoken segment is a heading carrying a timing, e.g.
#   ## Hook — 0–8s          ## Problem — 0:00–1:30
# Prose sections without one (metadata, "Alternates considered", generated nav)
# are not narrated. This is the whole reason the parser can be shared.
# Separator may be an em-dash, en-dash or hyphen; the timing is anything after
# it that contains a digit ("0-8s", "0:00-1:30", "final 10-15s"). Written this
# loosely on purpose: the first version demanded a digit immediately after the
# separator and silently matched nothing, which reads identically to "this file
# has no script in it".
TIMED_HEADING_RE = re.compile(
    r"^##\s+(?P<name>.+?)\s+[\u2014\u2013-]\s*(?P<timing>[^\u2014]*\d[^\u2014]*?)\s*$")

FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.S)
NAV_RE = re.compile(r"<!--\s*/?nav(?::parent)?\s*-->.*?<!--\s*/nav(?::parent)?\s*-->", re.S)
NAV_LOOSE_RE = re.compile(r"<!--\s*/?nav(?::parent)?\s*-->", re.S)
INDEX_RE = re.compile(r"<!--\s*index:begin\s*-->.*?<!--\s*index:end\s*-->", re.S)


class ElevenLabsError(Exception):
    pass


# --- parsing -----------------------------------------------------------------

def strip_generated(text):
    """Remove frontmatter and every generated block.

    The nav block is removed before anything else counts it. That block is
    appended by the docs validator after the script is written, so any counter
    that runs later sees it -- which is exactly how a 244-word script was once
    reported as 284.
    """
    text = FRONTMATTER_RE.sub("", text)
    text = INDEX_RE.sub("", text)
    text = NAV_RE.sub("", text)
    # A half-open nav block (or one whose partner was edited away) still has to
    # go: from the first nav marker to end of file is never spoken content.
    m = NAV_LOOSE_RE.search(text)
    if m:
        text = text[:m.start()]
    return text


def spoken_text(raw):
    """Strip markdown down to what a voice should say."""
    t = raw
    t = re.sub(r"^\s*>.*$", "", t, flags=re.M)          # blockquotes are notes
    t = re.sub(r"```.*?```", "", t, flags=re.S)          # fenced blocks
    t = re.sub(r"^\s*\|.*$", "", t, flags=re.M)          # tables
    t = re.sub(r"^\s*[-*_]{3,}\s*$", "", t, flags=re.M)  # rules
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)       # links -> text
    t = re.sub(r"[*_`]+", "", t)                          # emphasis, code spans
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def parse_sections(path):
    """Return [(name, text)] for every timed segment, in document order."""
    raw = strip_generated(Path(path).read_text(encoding="utf-8"))
    lines = raw.split("\n")
    sections, cur, buf = [], None, []
    for line in lines:
        m = TIMED_HEADING_RE.match(line)
        if m:
            if cur:
                sections.append((cur, spoken_text("\n".join(buf))))
            cur, buf = m.group("name").strip(), []
        elif line.startswith("## ") and cur:
            sections.append((cur, spoken_text("\n".join(buf))))
            cur, buf = None, []
        elif cur is not None:
            buf.append(line)
    if cur:
        sections.append((cur, spoken_text("\n".join(buf))))
    return [(n, t) for n, t in sections if t]


# --- credentials -------------------------------------------------------------

def get_api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key
    here = Path(__file__).resolve().parent
    # Walk up to the consuming project, so a project's own .env.local is found
    # when the skill is reached through its symlink.
    for base in [here, *here.parents, Path.cwd(), *Path.cwd().parents]:
        for name in (".env.local", ".env"):
            p = base / name
            if not p.exists():
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("ELEVENLABS_API_KEY="):
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
    sys.exit("ELEVENLABS_API_KEY not set. Export it, or put it in .env.local "
             "(which .gitignore covers -- never commit it).")


def elevenlabs_request(endpoint, method="GET", data=None, headers=None):
    hdrs = {"xi-api-key": get_api_key()}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(ELEVENLABS_BASE_URL + endpoint, data=data,
                                 headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        raise ElevenLabsError(f"API {e.code}: {e.read().decode('utf-8', 'replace')[:400]}")
    except urllib.error.URLError as e:
        raise ElevenLabsError(f"connection failed: {e.reason}")


# --- ffmpeg ------------------------------------------------------------------

def have(binary):
    return subprocess.run(["which", binary], capture_output=True).returncode == 0


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    out = r.stdout.strip()
    if r.returncode != 0 or not out:
        raise RuntimeError(f"ffprobe could not read a duration from {path}: "
                           f"{r.stderr.strip() or 'empty output'}")
    return float(out)


def concat(files, out_path):
    listing = out_path.parent / "concat.txt"
    listing.write_text("".join(f"file '{f.resolve()}'\n" for f in files), encoding="utf-8")
    r = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                        "-i", str(listing), "-c", "copy", str(out_path)],
                       capture_output=True, text=True)
    listing.unlink(missing_ok=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed: {r.stderr.strip()[:400]}")


# --- reporting ---------------------------------------------------------------

def report(sections, measured=None):
    chars = sum(len(t) for _, t in sections)
    words = sum(len(t.split()) for _, t in sections)
    print(f"{'segment':<28} {'words':>7} {'chars':>8}")
    print("-" * 46)
    for name, text in sections:
        print(f"{name[:28]:<28} {len(text.split()):>7} {len(text):>8}")
    print("-" * 46)
    print(f"{'TOTAL':<28} {words:>7} {chars:>8}")
    print()
    print(f"  credits (~1/char)   ~{chars:,}")
    print(f"  Starter 30,000/mo   {30000 // max(chars,1)} renders")
    print(f"  Creator 100,000/mo  {100000 // max(chars,1)} renders")
    if measured is None:
        print(f"\n  ESTIMATE at {WPM} wpm: {words / WPM * 60:.0f}s "
              f"({words / WPM:.1f} min) -- an estimate, not a measurement.")
        print("  Render to replace it with a measured duration.")
    else:
        print(f"\n  MEASURED: {measured:.1f}s ({measured / 60:.1f} min)")
        drift = measured - (words / WPM * 60)
        print(f"  the {WPM} wpm estimate was off by {drift:+.0f}s "
              f"({drift / max(measured,1) * 100:+.0f}%)")
        print("\n  Publish the measured number, not the estimate.")
    return words, chars


# --- commands ----------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("script", nargs="?", default=None,
                    help="path to a pitch script (two-minute.md, long-form.md)")
    ap.add_argument("--list-voices", action="store_true",
                    help="print the account's voices and exit; costs nothing")
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and report only; no API key, no ffmpeg, no cost")
    ap.add_argument("--out", default=None, help="output directory (default: alongside the script)")
    ap.add_argument("--voice", default=os.environ.get("ELEVENLABS_VOICE_ID", ""),
                    help="voice id (or ELEVENLABS_VOICE_ID)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--force", action="store_true",
                    help="re-render every section, ignoring the cache")
    args = ap.parse_args()
    if not args.script and not args.list_voices:
        ap.error("a script path is required (or pass --list-voices)")

    if args.list_voices:
        import json as _json
        data, _ = elevenlabs_request("/voices")
        for v in _json.loads(data).get("voices", []):
            lab = v.get("labels") or {}
            bits = ", ".join(f"{k}={val}" for k, val in list(lab.items())[:4])
            print(f"  {v.get('voice_id',''):<24} {v.get('name','')[:22]:<24} {bits[:64]}")
        return 0

    src = Path(args.script)
    if not src.exists():
        sys.exit(f"no such script: {src}")
    sections = parse_sections(src)
    if not sections:
        sys.exit(f"no timed segments found in {src}.\n"
                 "A spoken segment is a heading with a timing, e.g. '## Hook — 0–8s'.")

    if args.dry_run:
        report(sections)
        return 0

    if not args.voice:
        sys.exit("no voice id: pass --voice or set ELEVENLABS_VOICE_ID")
    for b in ("ffmpeg", "ffprobe"):
        if not have(b):
            sys.exit(f"{b} not found on PATH (needed to concatenate and measure)")

    out_dir = Path(args.out) if args.out else build_dir(src, f"{src.stem}-audio")
    seg_dir = out_dir / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    cache_path = out_dir / "cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    files, rendered, reused = [], 0, 0
    prev_text, prev_ids = None, []
    for idx, (name, text) in enumerate(sections, 1):
        digest = hashlib.sha256(f"{args.model}|{args.voice}|{text}".encode()).hexdigest()[:16]
        seg = seg_dir / f"{idx:02d}-{re.sub(r'[^a-z0-9]+', '-', name.lower())[:30]}.mp3"

        # Section-by-section gauging: only what changed costs credits. At ~10
        # minutes a whole re-render is ~10,000 credits, a third of a Starter
        # month, so this is the difference between iterating and not.
        if seg.exists() and cache.get(seg.name) == digest and not args.force:
            files.append(seg)
            reused += 1
            prev_text = text
            print(f"  [{idx}/{len(sections)}] {name}: unchanged, reused")
            continue

        payload = {"text": text, "model_id": args.model}
        if prev_text:
            payload["previous_text"] = prev_text
        if prev_ids:
            payload["previous_request_ids"] = prev_ids[-3:]
        print(f"  [{idx}/{len(sections)}] {name}: rendering {len(text):,} chars...")
        try:
            audio, hdrs = elevenlabs_request(
                f"/text-to-speech/{args.voice}", method="POST",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Accept": "audio/mpeg"})
        except ElevenLabsError as e:
            cache_path.write_text(json.dumps(cache, indent=2))
            sys.exit(f"\nfailed at section {idx} ({name}): {e}\n"
                     "Sections already rendered are cached; re-run to resume.")
        seg.write_bytes(audio)
        cache[seg.name] = digest
        rid = hdrs.get("request-id") or hdrs.get("x-request-id")
        if rid:
            prev_ids.append(rid)
        prev_text = text
        files.append(seg)
        rendered += 1

    cache_path.write_text(json.dumps(cache, indent=2))
    full = out_dir / f"{src.stem}.mp3"
    concat(files, full)
    measured = probe_duration(full)

    # Persist it. A consumer that needs this number and has no path to it gets
    # a hand-typed one -- publish.py carried "80.9s" as a literal for exactly
    # that reason, and a hand-typed measurement on a published page is the
    # failure this script exists to prevent. Writing it here makes the
    # reporting path a mode of the consuming path.
    spoken_words = sum(len(txt.split()) for _, txt in sections)
    (out_dir / "duration.json").write_text(json.dumps({
        "seconds": round(measured, 1),
        "words": spoken_words,
        "wpm": round(spoken_words / (measured / 60)) if measured else None,
        "source": src.name,
    }, indent=2), encoding="utf-8")

    print(f"\n  {rendered} rendered, {reused} reused -> {full}")
    print()
    report(sections, measured=measured)
    return 0


if __name__ == "__main__":
    sys.exit(main())
