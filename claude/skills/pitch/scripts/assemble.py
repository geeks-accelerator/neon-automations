#!/usr/bin/env python3
"""Assemble narration + slides + burned-in captions into the round video.

Third of the three production scripts, and the only one that spends nothing:
ffmpeg locally, no API, no credits. Reruns are free, so iterate here rather than
regenerating upstream.

Slide timing comes from the MEASURED per-segment audio durations, not from the
storyboard's target timings. The targets are what we aimed at; the audio is what
happened, and they differed by 20% on the first render because the inherited
~150 wpm constant is wrong for a real voice.

Captions are burned in, not a sidecar track: ~85% of video is watched on mute
and completion runs far higher with subtitles, which is the best-evidenced
decision in the whole procedure. Burned-in also means they are under our control
rather than a player's.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render as R          # one parser for the script, shared with the renderer
import slides as S          # one parser for the storyboard, shared with the generator


def probe(path):
    return R.probe_duration(path)


def wrap(text, width=42):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def srt_time(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):06.3f}".replace(".", ",")


def sentences(text):
    parts = re.split(r"(?<=[.?!])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def build_srt(segments, seg_durations, out_path):
    """One cue per sentence, each sentence given a share of its segment's
    measured duration proportional to its length. Crude, and good enough:
    a caption a little early reads as anticipation, a little late reads as a
    bug, so the bias is toward starting on time."""
    cues, t, idx = [], 0.0, 1
    for (name, text), dur in zip(segments, seg_durations):
        sents = sentences(text) or [text]
        total = sum(len(s) for s in sents) or 1
        for s in sents:
            share = dur * (len(s) / total)
            cues.append(f"{idx}\n{srt_time(t)} --> {srt_time(t + share)}\n"
                        + "\n".join(wrap(s)) + "\n")
            t += share
            idx += 1
    out_path.write_text("\n".join(cues), encoding="utf-8")
    return idx - 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("script", help="the pitch script (two-minute.md)")
    ap.add_argument("storyboard")
    ap.add_argument("--audio", default=None, help="rendered narration (default: alongside script)")
    ap.add_argument("--slides", default=None, help="slide directory (default: alongside storyboard)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--caption-theme", default="dark", choices=["dark", "light"],
                    help="light = dark text on a pale band, for light slide decks")
    args = ap.parse_args()

    script = Path(args.script)
    sb = Path(args.storyboard)
    audio_dir = Path(args.audio) if args.audio else script.parent / f"{script.stem}-audio"
    full_audio = audio_dir / f"{script.stem}.mp3"
    slide_dir = Path(args.slides) if args.slides else sb.parent / f"{sb.stem}-slides"
    out = Path(args.out) if args.out else script.parent / f"{script.stem}-video" / "round.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    if not full_audio.exists():
        sys.exit(f"no narration at {full_audio} -- run render.py first")
    segments = R.parse_sections(script)
    _, rows = S.parse_storyboard(sb)
    if not rows:
        sys.exit(f"no slide rows in {sb}")

    # measured per-segment durations, from the rendered segment files
    seg_files = sorted((audio_dir / "segments").glob("*.mp3"))
    if len(seg_files) != len(segments):
        sys.exit(f"{len(seg_files)} audio segments but {len(segments)} script segments -- "
                 "re-render; they must correspond one to one")
    seg_dur = [probe(f) for f in seg_files]

    # slides grouped by the segment named in their storyboard row
    by_seg = {}
    for n, seg, title, _ in rows:
        by_seg.setdefault(seg.strip().lower(), []).append(n)

    plan = []
    for (name, _), dur in zip(segments, seg_dur):
        nums = by_seg.get(name.strip().lower(), [])
        if not nums:
            sys.exit(f"storyboard has no slides for segment {name!r}")
        each = dur / len(nums)
        for n in nums:
            matches = sorted(slide_dir.glob(f"{n:02d}-*.png"))
            if not matches:
                sys.exit(f"no image for slide {n} in {slide_dir} -- run slides.py")
            plan.append((matches[0], each))

    total = sum(d for _, d in plan)
    print(f"{len(plan)} slides over {total:.1f}s of narration")
    for p, d in plan:
        print(f"  {d:5.1f}s  {p.name}")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        listing = td / "slides.txt"
        lines = []
        for p, d in plan:
            lines.append(f"file '{p.resolve()}'\nduration {d:.3f}\n")
        lines.append(f"file '{plan[-1][0].resolve()}'\n")   # concat demuxer needs the last twice
        listing.write_text("".join(lines), encoding="utf-8")

        vf = ("scale=1920:1080:force_original_aspect_ratio=increase,"
              "crop=1920:1080,format=yuv420p")
        if not args.no_captions:
            srt = td / "captions.srt"
            n = build_srt(segments, seg_dur, srt)
            print(f"\n{n} caption cues burned in")
            # Legibility over an unknown background is the whole problem. An
            # outline tuned for dark slides vanished on Gamma's white ones --
            # white text, grey halo, on white. BorderStyle=4 paints a fully
            # opaque box, which is legible over anything and stops the caption
            # competing with whatever the slide has in that corner.
            if args.caption_theme == "light":
                prim, back = "&H00101010", "&H00F2F2F2"   # near-black on near-white
            else:
                prim, back = "&H00FFFFFF", "&H00101010"   # near-white on near-black
            style = (f"FontName=Helvetica,FontSize=16,PrimaryColour={prim},"
                     f"BackColour={back},BorderStyle=4,Outline=0,Shadow=0,"
                     f"Alignment=2,MarginV=28")
            vf += f",subtitles='{srt}':force_style='{style}'"

        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
               "-i", str(full_audio), "-vf", vf, "-c:v", "libx264", "-preset", "medium",
               "-crf", "20", "-r", "30", "-c:a", "aac", "-b:a", "192k",
               "-shortest", "-movflags", "+faststart", str(out)]
        print("\nencoding...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"ffmpeg failed:\n{r.stderr[-1500:]}")

    print(f"\n  {out}  ({out.stat().st_size/1_048_576:.1f} MB, {probe(out):.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
