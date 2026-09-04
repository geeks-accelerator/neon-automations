# Production — steps 6 to 7b

> Part of the [`pitch`](../SKILL.md) skill. The operating core — the four tags, the
> citation rule, the two numbers, the ledger invariant — and the
> [gates](../SKILL.md#part-4-gates) are in [`SKILL.md`](../SKILL.md), and they apply
> here. This file is the procedure.

Shared by both rendering modes. **Step 4b runs early in both** — it is the gauge, and it is
how a script's duration stops being an assumption. Everything from Step 6 on is
audience-facing: full mode reaches it from Phase 11 and never before Phase 3.5, turn mode
from Step 5, and elevator never reaches it at all.

## Step 4b — render the audio, and listen to it

**Every pitch renders narration by default, in both rendering modes.** This is the `audio`
format, and it is the one render that does not wait for Phase 3.5, because it is an instrument
rather than an artifact. ElevenLabs, straight from the script, before any slide exists. This is
a **gauge, not necessarily the ship take**, and the two jobs are different — conflating them is
what kept TTS filed as a later A/B experiment when it was always the cheapest rehearsal
available.

What the render is for:

- **The real duration.** Replaces the assumed rate with a measured fact. Publish this number.
- **Hearing what silent reading hides** — sentences too long for one breath, tongue-twisters,
  and figures that are hard to *hear*. "Thirty-one dollars" and "$31" read identically and
  land differently.
- **Rehearsal before Phase 3.5.** Reading a script to five people without having heard it once
  is a wasted sample; the render is the cheapest possible dry run.

```bash
# free: parse, count, and estimate. No API key, no ffmpeg, no cost.
python3 .claude/skills/pitch/scripts/render.py docs/pitch/two-minute.md --dry-run

# render: caches each segment by content hash, concatenates, and probes duration
python3 .claude/skills/pitch/scripts/render.py docs/pitch/long-form.md --voice <id>
```

A **spoken segment is a heading carrying a timing** — `## Hook — 0–8s`,
`## Problem — 0:00–1:30`. Headings without one are not narrated, which is what keeps metadata,
"Alternates considered", and generated navigation out of the audio.

**`--dry-run` and a real render share one parser, deliberately.** This script's length was
published wrong three times from three different ad-hoc counters: `~228` when it was 273, then
284 when a generated `<!-- nav -->` block was swallowed, then 244 because a `split("## Hook")`
left `— 0–8s` in the body where the heading-strip could not match it. **A number derived by a
different code path than the one that consumes it will drift, and every drift reads as a fact.**
The counter is now the renderer.

Re-render on every draft — the cache means only a changed segment costs credits, which is what
makes iterating on a ten-minute script affordable at all.

**TTS ships, in both rendering modes.** Replacing the audio track with a human recording is **out of
scope for now** and is a reasonable future feature; nothing in the procedure prevents it, and
the script and slide timings do not change if it happens.

At ten minutes this is not really a choice — a human take that must be re-recorded on every
rebuild is not a repeatable artifact, and TTS is what makes a long-form pitch cheap enough to
regenerate when a claim gets demoted.

**One measurement caveat, recorded rather than resolved.** The turn threshold measures whether
the artifact holds attention, and a synthetic voice is a variable inside it. If turns fail at
the low end, "the voice" and "the concept" are not separable from the number alone — so a null
result reads as *this artifact did not hold attention*, never as *the idea is wrong*. The clean
A/B is a human take against the TTS one, one variable at a time, whenever the human-voice
feature lands.

---

## Step 6 — produce

- **Narration.** The gauge render already exists from Step 4b. For the **ship** take at T=1,
  a real human voice: it removes the low-effort-AI association and removes a confound, since a
  null result should be attributable to the concept rather than the voice. A/B the TTS take
  from T=2, one variable at a time.
- **Put a face on it.** Trust is best built face-to-face, and the segment should read **calm,
  honest, grounded** — no shouting, no overacting. Cheapest version: a face for the founder
  segment, stills for the rest. **Not the opening** — see the trust ladder above.
- **Audio over picture, and it is the one line with no cheaper substitute.** Three independent
  sources rank it that way. It costs nothing while narration is TTS, and it becomes a real ask
  line the moment Step 6's human ship take happens — a microphone is the purchase, not a
  camera. Itemised benchmarks from the same sources, for sanity-checking an ask rather than
  for copying: do-it-yourself $100–500, freelancer $1,000–5,000, agency $5,000–15,000. What
  drives that number up is **explanation** — anything the audience must be taught.
- **Theme.** `music.py` generates the bed **once**; `assemble.py` mixes it. A recurring show
  needs a recurring theme, and regenerating it throws away the sonic identity that makes a
  later episode recognisably the same series.

  **So the theme is a source asset, not a build artifact** — it stays in `docs/pitch/` and is
  committed, unlike the audio, slides and video, which go to `build/pitch/<round-id>/`.
  Everything else in the pipeline is reproducible from tracked text; a theme regenerated from
  the same prompt comes back *different*, so treating it as derived would silently change the
  show on a fresh clone. The prompt is stored beside it.

  **Set the bed level by measuring, not by ear-guessing a gain.** A fixed `volume=` multiplier
  strands a generated theme's sparse opening — the first attempt put it 30 LU under the
  narration, which is not subtle but absent. `loudnorm` to a target gives one predictable
  level; the sidechain then does the only level change that should happen. At `-32` LUFS the
  bed sits ~16 dB under a `-24.5` dB narration: audible between sentences, never competing.
  Ducking moves it ~1.6 dB there, which is correct rather than weak — a bed already 16 dB down
  does not need much, and heavy ducking would erase it.
- **Slides — and the first question is which kind of slide.** A pitch deck carries headlines
  and figures: **the text is the content.** A first run generated moody editorial stills under
  an explicit *no text* rule and pushed every word into captions, which is music-video grammar
  and was rejected on sight. Three routes, in the order to reach for them:

  | route | script | cost | when |
  |---|---|---|---|
  | **Gamma** | `gamma.py` | subscription, Pro+ | the default. Real deck design, PNG export, ~40s |
  | **Typeset** | `deck.py` | **$0.00** | no Gamma access, or full layout control. SVG → `rsvg-convert` |
  | **Generated** | `slides.py` | ~$0.003–0.04/image | atmosphere behind a statement slide. **Never for a number** |

  **Never generate text as an image.** Models hallucinate glyphs — the first run garbled the
  one number on the one slide whose whole subject was that number. And a pitch claiming its
  figures are exact, typeset from approximations, argues against itself.

  With Gamma, **`textMode: preserve`, not `generate`.** Expansion writes prose the ledger does
  not back, which is the failure the ledger exists to prevent. Supply finished, claim-checked
  copy and buy the design. `generate` is available and owes a line-by-line back-check.

  Everything before the first `---` in an outline is **preamble** and is not sent — that is
  where the file's own title and its segment→timing mapping live.

**The produce commands, in order.** Every one takes `--out`; the defaults resolve to
`build/pitch/<round-id>/` via `paths.py`, so pass it only to override. Three of these five had
no invocation written down anywhere until now, which made the skill readable and not runnable.

```bash
# theme — once per project, then never again
python3 .claude/skills/pitch/scripts/music.py --dry-run

# slides — pick one route
python3 .claude/skills/pitch/scripts/gamma.py  docs/pitch/deck-outline.md --dry-run
python3 .claude/skills/pitch/scripts/deck.py   docs/pitch/storyboard.md   --dry-run
python3 .claude/skills/pitch/scripts/slides.py docs/pitch/storyboard.md   --dry-run

# assemble — slides timed from the measured audio, not the storyboard's targets
python3 .claude/skills/pitch/scripts/assemble.py \
    docs/pitch/two-minute.md docs/pitch/storyboard.md --dry-run

# ...and for a Gamma deck, whose slides are elsewhere and carry their own text
python3 .claude/skills/pitch/scripts/assemble.py \
    docs/pitch/two-minute.md docs/pitch/storyboard.md --no-captions \
    --slides build/pitch/<round-id>/deck-outline-slides --dry-run
```

Drop `--dry-run` to spend money and write files. `music.py` and `slides.py` also take
`--force`, which is the only way past their "already exists" guard.

**The second argument names the storyboard, and the storyboard picks the slide directory.**
That is the seam to watch: `assemble.py` derives its slides from the file it is handed, so
passing `storyboard.md` looks in `storyboard-slides/` — `deck.py`'s output — no matter which
route actually rendered. `--no-captions` is the Gamma advice and the storyboard argument is
the typeset route, so the two together are a deck nobody rendered; the Gamma line above pairs
the flag with the directory it belongs to. The storyboard still has to be passed either way,
because it carries the segment→slide mapping the timing is computed from.

**Binary dependencies.** The scripts are stdlib-only in Python, but three shell out:
`deck.py` needs **`rsvg-convert`** (`brew install librsvg` / `apt install librsvg2-bin`), and
`render.py` and `assemble.py` need **`ffmpeg`** and **`ffprobe`**. Every `--dry-run` path is
free of all three, which is what lets CI check the parsers on a bare runner — `assemble.py`
prints its plan with the timings marked absent rather than guessed, since the mapping, the
image lookup and the counts are what a dry run is for and none of them need a duration.
`scans.py` needs neither — it reads the tree, and shells out to `git` only for `--since`.

- **Assembly.** `assemble.py` times slides from the **measured** per-segment audio, never the
  storyboard's targets. Captions burn in for image-only decks; a Gamma deck already carries its
  text, so captions there duplicate the slide and collide with it — use `--no-captions`.

  **Prefer a provider that can be priced per unit, and say why when you do not.** FLUX via
  Replicate/OpenRouter is quotable per image; Leonardo bills GPU-load tokens against a
  subscription with **no published per-model table**, so its honest ask line is *"$X/mo, of
  which this round used an unmeasurable fraction"* — a floor, not a receipt. A pitch whose
  differentiator is that the ask is itemized should notice when a tooling choice quietly
  removes that.

  This is the general shape, not a verdict on one vendor: **a subscription-priced input cannot
  appear as a per-round line.** Disclose it separately as a fixed monthly cost, the way an
  apportioned domain share is disclosed, and never divide it into an invented per-image
  figure.
- **Captions throughout**, sans-serif, high contrast, short phrases synced to speech. ~85% of
  video is watched on mute and completion runs far higher with subtitles. This is the
  best-evidenced decision in the whole procedure.

## Step 6b — publish

`publish.py` generates a static site from `docs/pitch/` and the round record: the video, the
itemized ask, the frozen threshold, and the full claims ledger — plus a **prototype**, if the
round carries one.

```bash
# citations point into a private repo — the page says so
python3 .claude/skills/pitch/scripts/publish.py <project> --out <publishing-repo> \
    --round <round-id>

# citations a reader can follow
python3 .claude/skills/pitch/scripts/publish.py <project> --out <publishing-repo> \
    --round <round-id> --repo-url https://github.com/<owner>/<repo>
```

**Visibility is an input, not an assumption.** The verifiability section used to assert the
repository is private, as a fixed paragraph — true for the tenant it was written against and
false for any other consumer, published as fact on the one page arguing that unbacked claims
get tagged. Omitting `--repo-url` keeps the private wording, because understating what a
reader can verify costs them nothing and overstating it is the failure being avoided.

**A round may carry a prototype, and most will not.** Drop a self-contained static page at
`build/pitch/<round-id>/prototype/index.html` and `publish.py` copies the directory and links it
under the video. It is optional by construction: a round that ships code against an existing
product has screenshots, not drawings, and has nothing to put here. A round funding something
that **does not exist yet** does — and a drawing is the cheapest way to let a backer argue with
the thing before it is written rather than after.

Two rules make it worth having. **Self-contained**: no external scripts, fonts or hosts. A
round's artifacts have to be readable by a stranger with a browser and nothing else, so a link
to an editor or a design tool behind a login is not a prototype, it is a promise. And **build it
from the same tokens the page uses** — if the drawings and the round page disagree about what
the product looks like, the drawings are the ones a reader will believe.

**The publishing surface is a target, not a source.** It is generated; editing it is drift. It
extracts *data* — claim rows, ask lines, the threshold — rather than converting markdown,
because the private tree holds the workshop and a converter would publish whatever happened to
be in a file.

**And it states what cannot be checked.** A published ledger whose citations point into a
private repository asks the reader to take your word for it. The tags are honest about what kind
of evidence stands behind a claim; whether a reader can reach it is a **separate fact**, and
publishing the first without the second claims a verifiability that is not being offered. The
generated page says so above the ledger, not in a footnote.

## Step 7 — post, and open the next turn

**Take the measurable sample from a direct ask.** Thirty to fifty people reachable personally
who agree to watch. This is not distribution and must not be reported as such — but it is the
only route that guarantees the sample without ranking luck, and the modal cold launch does not
produce one. A median Show HN scores 2 points; most Product Hunt launches get 0–2 upvotes.

**Do not spend the one-shot channels on an unproven artifact.** `SHOW IH` is once per product,
Show HN reposts are discouraged, Product Hunt is one real launch. All three are non-renewable
and worth more spent on something already known to hold attention — which is what these early
turns exist to determine. Hold them for the launch round.

**Early turns go to repeatable surfaces** — X `#buildinpublic` and similar, which cost nothing to
repeat and compound. Every source on build-in-public says to build the audience before
launching; the cadence *is* that warm-up.

## Step 7b — the update, which is the same document every time

A round ends; the backers do not. The update between turns is a **fixed shape, not an
occasion** — not a `format:` in the axis sense — and its consistency is what makes movement
visible:

- **Bottom line up front, including the lowlights, quantified.** One page.
- **Monthly or quarterly.** Weekly is too often to have anything to say, and is reported as the
  fastest route to unsubscribes.
- **Identical structure every time.**
- **Repeat the elevator pitch.** Small backers forget what they backed. This is
  `the-room.md`, unchanged — which is the point of its being assembled rather than written.
- **End with two or three specific asks.** An update with no ask trains people not to reply.

The common founder error here is reported as **over-secrecy, not over-disclosure** — and honest
disclosure early is what makes a bad month reportable later rather than a confession. This is
free to adopt now and expensive to retrofit once backers have seen three different shapes.

**The update is not a round record.** The record is an event and freezes; the update is
correspondence. Where a project keeps them is its own call, but a threshold, a claim list, and a
frozen script do not belong in a mailout, and a mailout does not get a `threshold:` field.

Set the round's status, append the result when it arrives, then:

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --fix
```

---

## Output shape

```
docs/pitch/                       living, optional, rebuilt by full
├── README.md                     index, the two numbers, staleness report, the
│                                 AI disclosure, and the scan-coverage answers †
├── scan.md                       Phase 0 + the affirmative sweep
├── claims.md                     the ledger — load-bearing
├── one-liner.md
├── two-minute.md                 the ~2-min script: Phase 3.5 read-aloud, and the seed
│                                 every turn script is cut from
├── long-form.md                  the ~10-min full-mode script, investor order, narrated
├── what-exists-now.md            the five buckets
├── the-ask.md                    itemized, milestone-shaped, and what a pledge buys
├── riskiest-assumptions.md       the three — and, when several pitches are live, the
│                                 possibilities table they fall out of
├── the-room.md                   elevator mode, assembled from this tree, adds no claims
├── reactions.md                  Phase 3.5
├── deck-outline.md               gamma.py input — cards, plus a preamble carrying the
│                                 file's title and the segment→timing mapping
└── storyboard.md                 deck.py input — the SAME cards, typeset

docs/rounds/<date>-turn-N.md      event, optional, one per turn

build/pitch/<date>-turn-N/        generated output. gitignored, regenerable
├── two-minute-audio/             render.py -- segments, duration.json
├── long-form-audio/
├── gamma-slides/ full-slides/    gamma.py
├── storyboard-slides/            deck.py
└── two-minute-video/ long-form-video/   assemble.py -- round.mp4
```

**Both deck specs describe one pitch.** Two renderers over one narrative is a feature; two
renderers over two narratives is drift, and it happened — a 14-card storyboard sat beside the
10-card deck that actually shipped, so the fallback would have rendered a pitch nobody
reviewed. When one changes, change the other.

**Nothing generated goes in `docs/`.** `docs/pitch/` holds what a person writes and one source
asset (`theme.mp3`); everything a script produces goes to `build/pitch/<round-id>/`, and every
script takes `--out` if you want it elsewhere.

**The round id in that path is the round record's own id**, not a parallel date-slug, and that
is the whole point of scoping it. A round record is dated and permanent; it used to cite
`docs/pitch/long-form-video/round.mp4`, a path the *next* turn overwrites. The record survived
and the thing it attested to did not — a ledger whose citations are silently replaced. Renders
now sit under the id of the round that produced them, so republishing turn 1 after turn 2 has
rendered still finds turn 1's video.

`build/` rather than `artifacts/` because `artifacts/` already means committed prose in these
repos — side quests, observations, creative works. A directory name that means both derived
output and kept writing means neither.

† The top of `README.md` is the generated directory index (`--fix` maintains it); the two
numbers and the staleness report are hand-written **below** the generated block, which the
generator preserves. **Start the file with the empty marker pair** (`<!-- index:begin -->`
`<!-- index:end -->`): a README with no markers is wholly replaced by the next `--fix` — silent
data loss, filed as an open registry issue the first run found by hitting it in a fixture copy.

**Flat, unlike the source method**, which nests under `evidence/`, `narrative/`, `offer/`,
`risk/`, `validation/`. Our validator and navigation generator walk one level, and the filenames
were carrying the grouping anyway. A change to fit the conventions, not to improve the method.

**No `research/` subtree** — Phases 3–5 cite `docs/research/` instead.

**Render output sits beside the scripts**, one directory per script per format
(`two-minute-audio`, `long-form-video`, `deck-slides`). An audio directory carries
`cache.json` (segment digests) and `duration.json` (the measured seconds, spoken word count and
the resulting wpm). **`duration.json` is where any consumer reads a duration from** — the
published page did once carry a hand-typed `80.9s`, because the number was measured, printed,
and never written down, leaving every downstream reader to retype it. A render directory whose script has
moved since it was produced is what the render check reports.

Drop a file when the project genuinely has nothing for it, and say so in the index. A stub of
generated filler is the failure that prevents.
