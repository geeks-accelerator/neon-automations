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

from paths import build_dir

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
    ap.add_argument("--audio", default=None, help="rendered narration (default: this round's build dir)")
    ap.add_argument("--slides", default=None, help="slide directory (default: this round's build dir)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--theme", default=None,
                    help="music bed (default: theme.mp3 beside the script; absent = no bed)")
    ap.add_argument("--no-theme", action="store_true", help="skip the bed even if present")
    ap.add_argument("--bed-lufs", type=float, default=-32.0,
                    help="integrated loudness for the music bed. Chosen by measuring, not "
                         "taste: at -32 the bed sits ~16 dB under a -24.5 dB narration, "
                         "audible between sentences and never competing. -36 is nearly "
                         "inaudible, -28 starts to fight the voice")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the slide/timing plan and exit; no ffmpeg, no encode")
    ap.add_argument("--caption-theme", default="dark", choices=["dark", "light"],
                    help="light = dark text on a pale band, for light slide decks")
    args = ap.parse_args()

    script = Path(args.script)
    sb = Path(args.storyboard)
    audio_dir = Path(args.audio) if args.audio else build_dir(script, f"{script.stem}-audio")
    full_audio = audio_dir / f"{script.stem}.mp3"
    slide_dir = Path(args.slides) if args.slides else build_dir(sb, f"{sb.stem}-slides")
    out = Path(args.out) if args.out else build_dir(script, f"{script.stem}-video") / "round.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    if not full_audio.exists():
        sys.exit(f"no narration at {full_audio} -- run render.py first")
    if not args.dry_run:
        for b in ("ffmpeg", "ffprobe"):
            if subprocess.run(["which", b], capture_output=True).returncode != 0:
                sys.exit(f"{b} not found on PATH")
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
    measured_audio = probe(full_audio)

    # The theme is generate-once and lives beside the script. Absent is fine --
    # a round without a bed is a round without a bed, not an error.
    theme = Path(args.theme) if args.theme else script.parent / "theme.mp3"
    theme_loops = 1
    if not theme.exists():
        theme = None
    elif probe(theme) < measured_audio:
        # Loop rather than demand a longer theme. The theme is generate-once by
        # design; regenerating it at full-mode length would cost roughly six
        # times as much AND come back a different piece of music, which defeats
        # the point of having a theme. A 100s bed under a ten-minute pitch is
        # exactly what looping is for.
        import math
        theme_loops = math.ceil(measured_audio / probe(theme))

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
                sys.exit(f"no image for slide {n} in {slide_dir} -- run deck.py or gamma.py")
            if len(matches) > 1:
                # Picking one silently is how a video gets cut from two decks.
                sys.exit(f"slide {n} is ambiguous in {slide_dir}:\n  "
                         + "\n  ".join(m.name for m in matches)
                         + "\nLeftovers from an earlier render. Delete the directory and "
                           "re-run the deck script.")
            plan.append((matches[0], each))

    used = {p.name for p, _ in plan}
    orphans = [f.name for f in sorted(slide_dir.glob("[0-9][0-9]-*.png"))
               if f.name not in used]
    if orphans:
        print(f"  note: {len(orphans)} image(s) in {slide_dir} are not in the deck "
              f"and will be ignored: {', '.join(orphans[:6])}"
              + (" ..." if len(orphans) > 6 else ""))

    if args.no_theme:
        theme = None
    total = sum(d for _, d in plan)
    print(f"{len(plan)} slides over {total:.1f}s of narration"
          + (f"  |  bed: {theme.name}, ducked" if theme else "  |  no music bed"))
    for p, d in plan:
        print(f"  {d:5.1f}s  {p.name}")

    if args.dry_run:
        # The plan is where the mistakes live -- a wrong segment mapping, a
        # missing image, a slide count that does not match the deck. Checking it
        # without ffmpeg means CI can catch those on a runner with no encoder.
        print("\n  (dry run -- nothing encoded)")
        return 0

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
               "-i", str(full_audio)]
        if theme:
            # Sidechain ducking, not a fixed low volume. A bed set quiet enough
            # never to bury a consonant is inaudible in the gaps; ducking lets
            # it breathe between sentences and step back under speech, which is
            # what makes it read as a theme rather than as noise.
            if theme_loops > 1:
                # -stream_loop repeats the input; the atrim below cuts it to
                # length. A hard loop point is audible in isolation and is not
                # at 16 dB under a voice -- worth knowing rather than hiding.
                cmd += ["-stream_loop", str(theme_loops - 1)]
            cmd += ["-i", str(theme)]
            # Loudness-normalise the bed rather than applying a fixed gain.
            # A generated theme has its own dynamics -- a sparse fade-in, then
            # denser passages -- so one gain that suits the middle leaves the
            # opening inaudible. Measured: the first attempt put the theme's
            # opening 30 LU under the narration, which is not "subtle", it is
            # "absent". loudnorm gives the bed one predictable level, and the
            # sidechain then does the only level change that should happen.
            bed_i = args.bed_lufs
            filt = (
                f"[2:a]atrim=0:{measured_audio:.3f},"
                f"loudnorm=I={bed_i}:TP=-2:LRA=7,"
                f"afade=t=in:st=0:d=2.5,"
                f"afade=t=out:st={max(measured_audio - 3.5, 0):.3f}:d=3.5[bed];"
                "[1:a]asplit=2[voice][key];"
                "[bed][key]sidechaincompress=threshold=0.03:ratio=8:attack=10:release=350[ducked];"
                "[voice][ducked]amix=inputs=2:duration=first:normalize=0[a]"
            )
            cmd += ["-filter_complex", filt, "-map", "0:v", "-map", "[a]"]
        # -t, not -shortest. The concat demuxer needs the last image repeated to
        # flush its final frame, and that repeat carries no duration -- so the
        # video stream runs past the audio and -shortest did not reliably cut
        # it back. A 570s narration came out as a 589s file. The measured
        # narration length is the output length, stated rather than inferred.
        cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "medium",
                "-crf", "20", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                "-t", f"{measured_audio:.3f}", "-movflags", "+faststart", str(out)]
        print("\nencoding...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"ffmpeg failed:\n{r.stderr[-1500:]}")

    print(f"\n  {out}  ({out.stat().st_size/1_048_576:.1f} MB, {probe(out):.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
