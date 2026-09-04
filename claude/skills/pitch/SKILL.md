---
name: pitch
description: Produce a round's pitch — the claims ledger, the script, the itemized ask, the narrated video — and post it. Use this skill whenever asked to make a pitch, pitch deck, pitch video, round video, or funding ask for a project, to open or close a turn of the funding loop, or to rebuild or refresh a project's pitch. It derives its own mode (a full extraction from the repository, an incremental turn off the standing ledger, or an elevator card assembled from what is already there) and its own format (markdown and gauge audio always, audience-facing renders on request), runs the research preflight first, and stops if open questions, stale research, or validation errors remain — so reach for it at the start of pitch work rather than after a deck exists. Also use it when asked "what goes in the pitch", "how long should the video be", "what can we honestly claim", or "what should we ask for".
---

# pitch

Three modes over one claims ledger, and a format axis independent of all three.

| | **full** | **turn** | **elevator** |
|---|---|---|---|
| produces | `docs/pitch/`, the ledger and a **~10-minute** script | `docs/rounds/<date>-turn-N.md`, script, ask, threshold, result, and a **<2-minute** script | `docs/pitch/the-room.md`, assembled, **nothing new written** |
| when | init, and when a trigger fires | every other turn | on request, and before Phase 3.5 |
| reader | evaluating the whole project: investor, client, partner, contributor | a stranger deciding whether to tip | someone who just asked what you do |
| can they interrupt | no | no | **yes** |
| success is | a diligence decision | a pledge | **a follow-up question** |
| order | problem → solution → market → traction → business model → team → ask | hook → problem → solution → ask | the one line, then whatever they ask |
| formats | markdown, gauge audio; video and deck on request | markdown, gauge audio; video and deck on request | markdown, and it never renders |
| why that order | researched for partners running diligence, and this is that audience | researched for strangers deciding in seconds, and this is that audience | there is no order to defend once they can interrupt |

**The two orders are both correct, for different readers.** An earlier version of this project
applied the investor order to a ninety-second crowd pitch and filed a high-severity issue about
it. The fix was not "the investor research was wrong" — it studies partners running diligence,
accurately. The fix is that **the order is a function of the audience**, and the two modes have
different ones. Neither order may be used in the other mode.

**Elevator is a third reader, not a third length.** The other two cannot interrupt: one is
running diligence on their own time, the other is scrolling. The elevator listener is in a live
two-way exchange, can stop you mid-sentence, and what counts as success there is not a decision
but a follow-up question. Different shape, not a shorter one. The one-liner is already the short
cut, and a mode that only shortens is a length knob wearing a mode's clothes.

Design and reasoning: [two pitch modes over one claims ledger](https://github.com/geeks-accelerator/code-neon/blob/main/docs/proposals/2026-08-24-pitch-modes-full-and-turn.md).

## The format axis

**Mode is who the reader is. Format is what gets rendered. They are independent, and fusing them
has already cost this project twice.**

| format | when it runs | why |
|---|---|---|
| `markdown` | always, in every mode | the script, the ledger, the ask. The floor, never optional |
| `audio` | **by default**, in both rendering modes | an instrument, not an artifact. It is how duration stops being an assumption ([Step 4b](references/production.md#step-4b--render-the-audio-and-listen-to-it)) |
| `video` | **on request, and not before `reactions.md` has content** | audience-facing |
| `deck` | **on request, and not before `reactions.md` has content** | audience-facing |
| `music` | on request, with video | audience-facing |

**The line is not markdown against rendered. It is instrument against artifact**, and
[Step 4b](references/production.md#step-4b--render-the-audio-and-listen-to-it)
already drew it: the gauge render *"is a gauge, not necessarily the ship take, and the two
jobs are different."* A gauge render is a measurement, it is cached by segment hash, and on run 3 it
is the only reason anyone discovered the inherited 150 wpm constant was 20% wrong. Making it
opt-in would delete the one instrument here that has caught a real error. Audience-facing renders
are the other job entirely.

**Why audience-facing renders are opt-in.** [Phase 11](references/full.md) already says
production runs after [Phase 3.5](references/full.md#phase-35--human-validation)
and never before, because producing before a human has heard the script is polishing something
nobody reacted to. On 2026-08-24 that rule was written down and then broken by the next run:
the N=1 target's `docs/pitch/reactions.md` read `## Status: NOT RUN` while two videos existed,
a 2-minute and a 9.5-minute. Prose naming the failure did not
prevent it, which is the lesson trigger 6 and trigger 7 each arrived at separately. A default
that makes the expensive, irreversible, unreviewed step **opt-in** is the structural version of
a rule that prose did not hold.

**And the modes overlap on format, which one field cannot record.** Turn 1 carries
`pitch_mode: full` over a script its own record describes as the crowd order, because both modes
shipped a video that turn. One value cannot say two things. `mode:` and `format:` as separate
fields can.

**Elevator is what proves the axes are independent**: it has no render at all. A human says it.
Its format set is `markdown`, since the floor is never optional; its **render set** is empty, and
a mode that stays meaningful with nothing rendered is only expressible if format is its own
field.

> **This requires a schema change that has not been made.** `validate.py` constrains `pitch_mode`
> to `["full", "turn"]`, and `schemas.md` documents it as one value meaning *which mode produced
> this round's script*. Until the round record carries `mode:` (three values) and `format:` (a
> list), the frontmatter this file describes will not validate. That change touches every project
> using `neon-docs`, so it is a deliberate migration and not a side effect of this revision.

> **The evidence half is forked from `gitwverse`, N=7 repositories, at commit `cc5f205e`.**
> The production half is ours and is **N=0** — no pitch has been produced, so every step below
> that touches script, video, or posting is derived from research rather than from practice.
> Revise against what actually happens. A step that survives contact unchanged was lucky, not
> proven.

---

# Part 1: The operating core

Used continuously in every mode. Read it first and keep it open; the rationale is in
[`references/rationale.md`](references/rationale.md).

## The four tags

| Tag | Means | What must accompany it |
|---|---|---|
| `EXTRACTED` | The repository **demonstrates** it | A count you can re-run, a commit that happened, a test that exists, a file that is present |
| `RESEARCHED` | True outside the repo, and you looked | A `docs/research/` scan id — not a URL in prose |
| `ASSERTED` | A human said so, or it is your reading | Nothing independent backs it. Stays flagged, permanently |
| `CHECKED` | You verified it yourself, no citable source either side | What you did, and how weak it is |

**The defect this exists to prevent is an `ASSERTED` claim that reads like an `EXTRACTED`
one.** That is where a pitch drifts under pressure to persuade, and the pressure is constant.

## The citation must prove the claim, not locate it

A `file:line` pointing at a document that **states** something proves only that someone wrote
it down. Tagging it `EXTRACTED` because a citation exists is the target defect, reached by
obeying the rules.

**Restate the claim until it matches what the citation proves.**

| The claim you wanted | What the citation proves | Correct form |
|---|---|---|
| The mechanism works | A doc describes it | `EXTRACTED`: *the docs describe a mechanism*. Whether it works is `ASSERTED` |
| A round costs $30 | A doc says $30 | `EXTRACTED`: *the docs state $30*. The figure is `RESEARCHED` against a price list |
| 96 tests pass | The test files exist | `EXTRACTED`: *96 test cases exist*. A result you did not produce is "the repo claims" |

Four routes to an unearned `EXTRACTED`, all found in real runs:

1. **Prose with an address.** The case above.
2. **Third-party testimony in the repo.** A transcript proves they *said* it. Use `CHECKED`.
3. **Your own spot-check.** No citable source either side. Use `CHECKED`.
4. **The genre label doing the work of a citation.** A filename ending `-research.md`, a
   heading reading "Result", a column headed "Measured". These read as instrument output and
   can be projection. **Open the method section before trusting the genre.**

## Restatement is unbounded

Any sentence is one restatement away from `EXTRACTED`, because *the repo states X* is always
true and always citable.

**If a claim is cheaply checkable outside the repository, restating it is evasion.** This
project's tree is confident prose about things nobody has built. Every sentence in it is one
restatement from looking like evidence, which makes the bound load-bearing here rather than
theoretical.

## Split the claim

When a fact is half one tag and half another, **split it into two claims rather than picking
the flattering tag.** A doc stating a threshold while its cited research says something else is
two claims — *the doc states X* and *its source says Y* — and the disagreement is the finding.

One exception: a *composite* built from rows already in the ledger may carry both tags if the
counting convention is declared next to the tally. A **new** fact never gets a dual tag.

## Verify the instrument, not just the number

Every wrong count in the source method's seven runs came from a command that **ran cleanly** —
a glob crossing directories, `grep -c` counting rows *containing* a value rather than rows *in*
it, `git log --reverse -1` returning the newest commit because `-1` applies before the reverse.

- **Find an independent denominator or a known total.** Deriving twice is not enough: two
  derivations can be wrong in the same direction and agree with each other.
- **Read the file list a command matched**, not only its count.
- **A total that exceeds its own denominator is the cheap tell.**
- **When your number disagrees with the document's, suspect your instrument first.** A
  fabricated defect is the more dangerous error, because it *feels* like rigour.
- **Re-derive aggregates last**, then stop at the fixed point — writing the tally changes the
  tally.
- **Numbers in narrative prose are claims too**, and escape both this rule and the ledger
  unless you put them in it.

## The two numbers

**The ratio** of extracted claims, never thresholded — no pass mark has been measured.

**And, in one line: of the three riskiest assumptions, how many are extracted.** This is the
real number. Across seven runs, extracted ratios of 62–81% sat beside riskiest-three scores of
0, 0, 0, 0, 1, 1 and one half. *A pitch can be four-fifths extracted and rest entirely on the
fifth.*

- An assumption is a bet about the future, so read literally the answer is always zero. Read it
  as: **does the repository demonstrate the thing the pitch leans on?** Halves are honest.
- **Audience-facing assumptions are structurally always zero.** A repository cannot demonstrate
  anything about its readers. Say so rather than letting it drag the count down silently.
- `RESEARCHED` splits into independent and self-verifying. Fetching our own live endpoint is
  not market research.

## Disclose what the machine made

**A major reward platform now carries a use-of-AI section by structure**, alongside risks and
environmental commitment — creators name which parts of the work were machine-made. That is a
convention arriving in the genre, not a preference, and it lands on this procedure harder than
on most: the slides are generated or typeset by script, the narration is TTS, and the theme is
model-generated. **A pitch produced this way and silent about it is making the exact kind of
unmarked claim the four tags exist to prevent**, in the one place a reader is least able to
check.

The disclosure is a *line in the pitch*, not a footnote on the page, and it names the parts:
script written by a human or drafted by a model, narration synthetic or recorded, slides
generated or typeset, music generated. Say which, in the index and on the published page.

**For this project the disclosure is the pitch.** The premise is agent-built software. A
reader who discovers the narration is synthetic after being told nothing has learned that the
pitch conceals what the product *is* — the concealment costs more than the fact. That the
convention now exists removes the last argument for being coy about it.

**This is a claim like any other, so it gets a tag.** *The narration is synthetic* is
`EXTRACTED` — a file exists and a script produced it.

## The ledger invariant

**A turn pitch may not make a claim that is not in `docs/pitch/claims.md`.** New claims get
extracted and tagged first, appended second, and only then may the script use them.

Without this, turn mode is a bypass — *"it is just a quick update"* is exactly the pressure
that produces an untagged assertion, and the tags become ceremony performed twice a year while
every claim that reaches a stranger goes out ungated.

---

# Part 2: Derive the mode and the format

**No mode is the default, and only two of the three are derived at all.** Elevator is never
derived — it is asked for, and it can be asked for at any time, because it adds nothing and
ships nothing. Between `full` and `turn`, the state lives in the tree: whether `docs/pitch/`
exists, each round record's `pitch_mode:` (how many turns since the last `full`), its `demoted:`
list (this feeds trigger 3), and `reactions.md` / round results (trigger 2). Read it, decide, and
**say which and why** before doing anything else:

```
turn — no trigger fired; last full 2026-09-14, 3 turns since
full — riskiest assumption `strangers-will-tip` was answered at T=4
```

## Triggers for full

1. **No `docs/pitch/`** — init.
2. **A riskiest-three assumption was answered.** The real trigger: the pitch is organised
   around what is load-bearing and unevidenced, so the moment that question resolves — yes
   **or** no — the pitch is about a different project.
3. **Demotion rate over a third** on this turn's citation re-check. The extraction has drifted
   out from under the narrative.
4. **Six turns elapsed.** A backstop, because (2) and (3) are not trusted to fire. Six is a
   guess; revise it when a rebuild finds the narrative was already stale, or when three
   consecutive rebuilds find nothing.
5. **Pivot** — the code and the docs disagree about *the problem*. Only about the problem;
   disagreements about stack or status are ordinary scan findings.
6. **The procedure changed the artifact.** When a revision to this skill changes *what full
   mode produces* — its length, order, audience, or output shape — the standing pitch was built
   to a procedure that no longer exists, and no amount of ledger freshness fixes that.

7. **The evidence changed.** A new or superseded scan in a mode the pitch cites, and any
   new `regulation`-mode scan regardless of what cites it — what may lawfully be offered
   bounds every ask in the tree. Triggers 1–6 all watch the *project* or the *procedure*;
   none watches the research the pitch is built on, so a scan can land that contradicts a
   live claim while mode derivation reports no trigger.

**Trigger 7 was found the same way trigger 6 was.** On 2026-08-24 an 80-video corpus
produced three scans — `writing-the-ask-practitioner-video`, `non-accredited-offering-pathways`,
`crowdfunding-platform-mechanics` — one of them concluding that a public ask to strangers for
small amounts may be unavailable under either Reg D branch. No trigger fired. Mode derivation
would have said *"turn — no trigger fired"* over research that changes what the pitch may say.

**Trigger 6 was found by needing it.** The re-run that introduced the ~10-minute investor-order
script fired none of triggers 1–5: the tree existed, no assumption had resolved, nothing had
been demoted, no turns had elapsed, and the docs and code did not disagree. Mode derivation
would have said *"turn — no trigger fired"* while the correct answer was plainly a full
rebuild. A trigger list that omits *"the method changed"* silently pins every project to the
procedure in force the day it was first run.

## Deriving the format

**Format is never derived. It is asked for, or it is the default**: markdown plus the gauge
audio render, in both rendering modes, and markdown alone in elevator. Video, deck and music are
named explicitly by a human and are refused while `reactions.md` has no content.

### The render check — and it is deliberately not trigger 8

One check runs on this axis. **It is not numbered into the trigger list, and the reason is the
same argument this revision is built on.** Triggers 1–7 all resolve to one action: rebuild the
pitch. This resolves to a different one: report a divergence. Numbering it 8 would put two
actions behind one sequence, which is precisely the defect that `pitch_mode` holding one value
for two axes already produced. A list, like a field, should say one thing.

**A render no longer matches its script.** `render.py` caches segments by content hash —
`cache.json` records `sha256(model|voice|text)` per segment — and `--check` reads it:

```bash
python3 .claude/skills/pitch/scripts/render.py docs/pitch/two-minute.md \
    --check --voice <the id it was rendered with> --round <the round that rendered it>
```

It reports per segment — matched, `DIVERGED`, `MISSING` (in the script, never rendered), or
`ORPHANED` (rendered, no longer in the script) — spends nothing, and exits 1 on any of the
three, so it works as a gate. **It never re-renders.** When a published audio, video or deck
was rendered from a script that has since moved, that render is stale in exactly the sense a
demoted claim is stale: true when made, unverified now. It goes in the staleness report with
the date it diverged, and it is **not silently re-rendered**, because re-rendering hides that
what a reader saw and what the tree says have come apart.

**Pass `--round`, and know why it is there.** Renders are scoped to the round that produced
them, and an unpinned path resolves to the *newest* round record — so opening turn N+1's
record, before it has rendered anything, moved the check onto an empty directory. A diverged
render published for turn N then reported *"no render to check"* and exited 0: the gate went
quiet at the exact moment the standing render was most likely to be stale. It now names the
rounds that do hold a render and exits 1 rather than passing, but pinning the round is still
how you say which render you meant.

Two more notes on the instrument. The digest covers voice and model as well as text, so a voice
change reads as divergence too — correct for *this render no longer matches*, wider than *the
script moved*, and worth saying which one a report means. And triggers 1–7 all watch the pitch's
content; this is the only check on the format axis, and it was invisible while mode and format
were the same field.

## Step 1 in every mode — preflight, and stop if it fails

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --preflight
python3 .claude/skills/pitch/scripts/scans.py --docs docs --since <last full's SHA>
```

**Non-zero exit means stop.** `validate.py --preflight` blocks on validation errors, open
questions, and research past its mode's horizon. Shipping past any of them means committing
publicly to a position a short search might have corrected, and a pitch is expensive to retract.

**`scans.py` is the second half, and it is a report rather than a gate.** An uncited scan is
not an error — a project may research what it has not pitched — so a clean exit here means
*the list printed*, not *the list was empty*. Gate 9 is the human half: answer every scan it
names. The one thing it does fail on is a `--since` it could not evaluate, because a git
history it cannot read returns the same silence as *no new research*, which is the exact
failure trigger 7 exists to break.

Detection is inclusive by design; **acting on it is not.** Re-run the modes the preflight
*named*, with the [`research`](../research/SKILL.md) skill — a refresh that re-scans everything
on principle buries the finding that mattered.

---

# Part 3: Read the mode you derived

**The procedure lives in one file per mode. Open the one Part 2 selected, and read it before
producing anything** — each is the full step list, and none of them repeats the operating core
above, which applies throughout.

| file | mode | produces |
|---|---|---|
| [`references/full.md`](references/full.md) | **full** | `docs/pitch/` — the scan, the ledger, the ~10-minute script |
| [`references/turn.md`](references/turn.md) | **turn** | `docs/rounds/<date>-turn-N.md` — the round, its ask and its threshold |
| [`references/elevator.md`](references/elevator.md) | **elevator** | `docs/pitch/the-room.md` — assembled, nothing new written |
| [`references/production.md`](references/production.md) | *format* | narration, slides, video, the published page, the update — **shared by both rendering modes**, and the output tree |
| [`references/rationale.md`](references/rationale.md) | — | why the rules are shaped this way, what has actually run, and what would falsify each position |

**Production is its own file because it is not a mode.** Full mode reaches it from Phase 11,
turn mode from Step 5, and elevator never reaches it at all — which is the format axis stated
as a file layout rather than as a paragraph.

**`rationale.md` is not optional reading before a revision.** Almost every rule above was
written against a specific run that broke something, and the record of which run is there. A
rule changed without reading it is a rule changed without knowing what it was for.

---

# Part 4: Gates

1. **Provenance.** Every claim tagged and cited. Untagged is a defect.
2. **Both numbers reported**, neither thresholded.
3. **The problem is a mechanism, not a rival.** Alternatives described accurately, including
   what they do better.
4. **Human validation before done.** [Phase 3.5](references/full.md#phase-35--human-validation)
   in full mode, a measured threshold in turn mode,
   or the index says DRAFT. Elevator mode has no such gate, because it ships nothing and exists
   to feed Phase 3.5 rather than to substitute for it.
5. **`CHECKED` never carries a riskiest assumption and never appears in the one-liner.**
6. **Ledger integrity.** Two halves. The mechanical half is **validator-enforced**: a claim is
   a `| C-NNN |` table row in `claims.md` (row format in
   [schemas](../neon-docs/references/schemas.md)), ids are unique, every row carries exactly one
   tag, and a round's `claims:` list resolves against those ids. The judgement half stays human:
   **does the script's claim list match what the script actually says?** A script can cite C-004
   and then paraphrase it into a stronger sentence, and no parser catches that — in the source
   method this half found three reassigned ids and one claim a script never made.
7. **What the machine made is disclosed**, naming script, narration, slides and music
   separately, in the index and on the published page.
8. **What a pledge buys is written in one sentence** before anything posts, identical in the
   round record and on the page.
9. **Every current scan in a pitch mode either has a consumer or a recorded reason it does
   not.** `scans.py` produces the list; silence is the failure, not absence of a citation.
10. **The threshold precedes the posting.** Validator-enforced three ways: a `posted` round
   without a `threshold:` field is an error, a resolved round without a `result:` is an error,
   and under `--since`, editing the threshold after the round left `draft` is an error — the
   field freezes at posting, like a proposal's filename freezes when it leaves draft.
11. **Format is declared, never implied.** Markdown and the gauge audio render are the default;
   video, deck and music are named by a human. An audience-facing render produced while
   `reactions.md` has no content is Phase 11's ordering violated, and that has already happened
   once. **Declared means named by a human in the request** — this gate is met verbally today and
   becomes *auditable* only when the round record carries `format:`, which is the schema migration
   flagged at the top of this file and not yet made.
12. **A stale render is reported, not refreshed.** When a published render no longer matches the
   script it came from, it goes in the staleness report with the date it diverged. Silently
   re-rendering hides that what a reader saw and what the tree says are different, which is the
   same error as quietly re-extracting a broken claim to a new line number.

## Will not

- **Invent a number.** No market size, projection, conversion rate, or ask figure.
- **Hide a number a human supplied.** The ask is public by default.
- **Write a pure investor deck.** A different pitch from the same evidence.
- **Run without reading.** Phase 0 has no fast path.
- **Persuade past the evidence.** When the evidence is thin, the honest pitch is short.
- **Prosecute the subject.** See below.

## The drift the gates do not catch

Every gate points at persuasion. Real runs report the opposite pull: **prosecution.**

A self-documenting repository hands you its contradictions pre-cited. Extraction makes
assembling them effortless, and the result reads as an audit with a warm closing sentence. That
is worse for this audience, because **a micro-funder cannot fund a verdict.**

The structural fix is upstream, in [Phase 0.5](references/full.md#phase-05--the-affirmative-sweep)
and the bucket order, because a check applied after
the long form arrives too late — by then the evidence base is already tilted. Run the check
anyway, on the long form **and the index**: does a reader know what they would be *for*? If the
answer is only what they would be warned about, the gates held and the genre was lost.

**Fix it by adding what is true and good, never by removing what is true and bad.**

This project is the ideal victim: a docs tree of self-criticism, an issue recording that a plan
was built on the wrong research, and a founding document instructing readers to treat every
number in it as a hypothesis. An honest extraction here produces a devastating and entirely
accurate indictment unless [Phase 0.5](references/full.md#phase-05--the-affirmative-sweep)
runs first.

---

Provenance, status and falsifiers: [`references/rationale.md`](references/rationale.md).

## What to write down afterwards

Whatever surprised you, as an observation with evidence and `n: 1`. Both halves of this
procedure are largely untested in any project; a real run is the only thing that will show
which steps were guesses.
