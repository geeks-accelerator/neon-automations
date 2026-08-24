---
name: pitch
description: Produce a round's pitch — script, narration, slides, assembled video, and the itemized ask — and post it. Use this skill whenever asked to make a pitch, pitch deck, pitch video, round video, or funding ask for a project, or to open or close a turn of the funding loop. It begins by running the research preflight and stops if open questions remain, so reach for it at the start of pitch work rather than after the deck exists. Also use it when asked "what goes in the pitch", "how long should the video be", or "what should we ask for".
---

# pitch

Produces a round's pitch artifact: a narrated slide deck of ~12–15 slides at ~90 seconds,
with the ask itemized from real costs.

> **Written at N=0.** No pitch has been produced yet, so what follows is derived from
> research and from the project's own documents — not from practice. Revise it against what
> actually happens on the first turn, and treat any step that survives contact unchanged as
> lucky rather than proven.

## Step 1 — preflight, and stop if it fails

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --preflight
```

**Non-zero exit means stop.** It reports two things, and both block:

- **Open questions** — a record has declared something it cannot answer that would change
  what the pitch says.
- **Stale research** — a scan is past its mode's horizon. Pricing expires in 90 days,
  competitive landscape in 180, our own metrics in 7.

Shipping past either means committing publicly to a position that a short search might have
corrected, and a pitch is expensive to retract.

Detection is inclusive by design: every open question and every current scan is checked, every
time, because missing one stale input is a worse failure than an extra check is a cost.
**Acting on it is not.** Re-run the modes the preflight actually named — a pitch refresh that
re-scans everything on principle buries the finding that mattered and costs the time of
everyone reading the result.

Resolve with the [`research`](../research/SKILL.md) skill, or drop a need that stopped
mattering, or supersede a scan that no longer bears on anything. Then re-run.

## Step 2 — derive the ask before writing anything

Itemize from real prices, and **publish the itemization**. The number is small and that is
the interesting part; nobody in this category shows what a round actually costs.

Contributed capacity — agent compute, human hours — never enters a cash ask. It is recorded
in the ledger, not billed to backers.

## Step 3 — script first, slides second

At ~150 words per minute, 90 seconds is **~225 words**. Write and cut the script before
generating anything. Cutting a script is free; cutting finished slides is not.

**The hook goes in the first 15 seconds.** A deck is scanned by someone who chose to open it;
a video competes for someone who did not, and about a third of viewers leave inside 30
seconds. The conventional problem → solution → market → traction → team → ask order buries
the hook, and can only follow it.

**Put who-you-are early.** The team slide draws more attention than any other in funded
decks, and a human carries the story in a way a mechanism does not.

## Step 4 — produce

- **Narration.** A real human voice beats TTS for a first pitch: it removes the
  low-effort-AI association, and it removes a confound — a null result should be
  attributable to the concept, not the voice. A/B TTS in a later turn, one variable at a
  time.
- **Theme.** Generate the music bed **once** and reuse it every round. Cheaper, and a
  recurring show needs a recurring theme; regenerating it each time throws away the sonic
  identity that makes a later episode recognisably the same series.
- **Slides.** Expect ~2 attempts per keeper.
- **Captions throughout**, sans-serif, high contrast, short phrases synced to speech. ~85%
  of video is watched on mute and completion runs far higher with subtitles. This is the
  best-evidenced decision in the whole procedure.

## Step 5 — set the success threshold before posting

A number that would count as **failure**, written down first. A completion rate against a
stated audience size is meaningful; a view count is not.

Set after posting, it cannot fail — and an experiment that cannot fail cannot succeed either.

## Step 6 — post, ask, and open the next turn

File the round's record, then run the full validator so navigation and directory indexes
pick it up:

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --fix
```

## What to write down afterwards

Whatever surprised you, as an observation. This procedure is untested; the first real run is
the only thing that will show which steps were guesses.
