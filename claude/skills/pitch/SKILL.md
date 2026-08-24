---
name: pitch
description: Produce a round's pitch — script, narration, slides, assembled video, and the itemized ask — and post it. Use this skill whenever asked to make a pitch, pitch deck, pitch video, round video, or funding ask for a project, or to open or close a turn of the funding loop. It begins by running the research preflight and stops if open questions, stale research, or validation errors remain, so reach for it at the start of pitch work rather than after the deck exists. Also use it when asked "what goes in the pitch", "how long should the video be", or "what should we ask for".
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

**Non-zero exit means stop.** It blocks on three things:

- **Validation errors** — a broken tree gates everything else; fix it first.

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

**Two experiments, and one turn can only answer one of them.**

- **Watchability** — does the artifact hold attention? Needs ~30 video **starts**, from any
  source.
- **Distribution** — can this reach strangers at scale? Needs ranking luck, a warm audience,
  and repetition across turns.

Conflating them is what makes a null result uninterpretable: with no audience you cannot tell
an uninteresting artifact from an empty room. Test watchability per turn; let distribution
accumulate.

**The floor is 30 starts**, because that is where a 95% interval around a 40% completion rate
excludes 15%, making *holds attention* and *does not* distinguishable. Fifty is comfortable;
ten tells you nothing. The unit is **starts**, not impressions or views — at a 1–3% link CTR,
30 starts implies 1,000–3,000 impressions.

A workable default: **≥30 starts with ≥40% completion passes; ≤15% fails; between them is
inconclusive and the turn repeats.**

Write it down first. A threshold chosen after seeing the result is not a threshold, and an
experiment that cannot fail cannot succeed either.

## Step 6 — post, ask, and open the next turn

**Take the measurable sample from a direct ask.** Thirty to fifty people reachable
personally who agree to watch. This is not distribution and must not be reported as such —
but it is the only route that guarantees the sample without ranking luck, and the modal cold
launch does not produce one. A median Show HN scores 2 points; most Product Hunt launches get
0–2 upvotes and are not seen.

**Do not spend the one-shot channels on an unproven artifact.** `SHOW IH` is once per
product, Show HN reposts are discouraged, Product Hunt is one real launch. All three are
non-renewable, and all three are worth more spent on something already known to hold
attention — which is exactly what these early turns exist to determine. Hold them for the
launch round.

**Early turns go to repeatable surfaces** — X `#buildinpublic` and similar, which cost
nothing to repeat and compound. Every source on build-in-public says to build the audience
before launching; the cadence *is* that warm-up, so the first turns are building the audience
a later turn will need rather than testing whether one exists.

File the round's record, then run the full validator so navigation and directory indexes
pick it up:

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --fix
```

## What to write down afterwards

Whatever surprised you, as an observation. This procedure is untested; the first real run is
the only thing that will show which steps were guesses.
