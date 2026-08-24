---
name: pitch
description: Produce a round's pitch — the claims ledger, the script, the itemized ask, the narrated video — and post it. Use this skill whenever asked to make a pitch, pitch deck, pitch video, round video, or funding ask for a project, to open or close a turn of the funding loop, or to rebuild or refresh a project's pitch. It derives its own mode (a full extraction from the repository, or an incremental turn off the standing ledger), runs the research preflight first, and stops if open questions, stale research, or validation errors remain — so reach for it at the start of pitch work rather than after a deck exists. Also use it when asked "what goes in the pitch", "how long should the video be", "what can we honestly claim", or "what should we ask for".
---

# pitch

Two modes over one claims ledger.

| | **full** | **turn** |
|---|---|---|
| produces | `docs/pitch/` — the ledger, and a **~10-minute narrated pitch** | `docs/rounds/2026-08-24-turn-N.md` — script, ask, threshold, result, and a **<2-minute video** |
| when | init, and when a trigger fires | every other turn |
| reader | evaluating the whole project — investor, client, partner, contributor | a stranger deciding whether to tip |
| order | problem → solution → market → traction → business model → team → ask | hook → problem → solution → ask |
| why that order | researched for partners running diligence, and this is that audience | researched for strangers deciding in seconds, and this is that audience |
| narration | ElevenLabs TTS | ElevenLabs TTS |

**The two orders are both correct, for different readers.** An earlier version of this project
applied the investor order to a ninety-second crowd pitch and filed a high-severity issue about
it. The fix was not "the investor research was wrong" — it studies partners running diligence,
accurately. The fix is that **the order is a function of the audience**, and the two modes have
different ones. Neither order may be used in the other mode.

Design and reasoning: [two pitch modes over one claims ledger](https://github.com/geeks-accelerator/code-neon/blob/main/docs/proposals/2026-08-24-pitch-modes-full-and-turn.md).

> **The evidence half is forked from `gitwverse`, N=7 repositories, at commit `cc5f205e`.**
> The production half is ours and is **N=0** — no pitch has been produced, so every step below
> that touches script, video, or posting is derived from research rather than from practice.
> Revise against what actually happens. A step that survives contact unchanged was lucky, not
> proven.

---

# Part 1: The operating core

Used continuously in both modes. Read it first and keep it open; the rationale is in Part 5.

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

## The ledger invariant

**A turn pitch may not make a claim that is not in `docs/pitch/claims.md`.** New claims get
extracted and tagged first, appended second, and only then may the script use them.

Without this, turn mode is a bypass — *"it is just a quick update"* is exactly the pressure
that produces an untagged assertion, and the tags become ceremony performed twice a year while
every claim that reaches a stranger goes out ungated.

---

# Part 2: Derive the mode

**Neither mode is the default.** The state lives in the tree: whether `docs/pitch/` exists,
each round record's `pitch_mode:` (how many turns since the last `full`), its `demoted:` list
(this feeds trigger 3), and `reactions.md` / round results (trigger 2). Read it, decide, and
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

**Trigger 6 was found by needing it.** The re-run that introduced the ~10-minute investor-order
script fired none of triggers 1–5: the tree existed, no assumption had resolved, nothing had
been demoted, no turns had elapsed, and the docs and code did not disagree. Mode derivation
would have said *"turn — no trigger fired"* while the correct answer was plainly a full
rebuild. A trigger list that omits *"the method changed"* silently pins every project to the
procedure in force the day it was first run.

## Step 1 in both modes — preflight, and stop if it fails

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --preflight
```

**Non-zero exit means stop.** It blocks on validation errors, open questions, and research past
its mode's horizon. Shipping past any of them means committing publicly to a position a short
search might have corrected, and a pitch is expensive to retract.

Detection is inclusive by design; **acting on it is not.** Re-run the modes the preflight
*named*, with the [`research`](../research/SKILL.md) skill — a refresh that re-scans everything
on principle buries the finding that mattered.

---

# Part 3: full

Produces `docs/pitch/`. The phase numbers are the source method's, kept so a comparison against
it stays a diff rather than an excavation.

## Scope

**Scan the whole *tracked* project, always.** Tracked, not present — one target in the source
runs was 26,265 files on disk and 206 tracked.

- **State the boundary as a partition that sums to the total.** Forcing the arithmetic is what
  makes you discover the directory you would otherwise have lumped into "build stuff".
- **Enumerate top-level ignored directories and ask what their existence proves**, without
  reading contents.
- **At small sizes, exhaustive beats sampled.** A complete negative — *"12 of 208, here are all
  12"* — is categorically stronger, and the whole repo fits in working memory, so cross-document
  contradictions surface unprompted.
- **Running the target's test suite is a WRITE to the target.** Report that tests exist and that
  you did not run them.
- **Submodules have three states**: checked out, pinned but absent, and bypassed by the build.
  Record both the pinned pointer and the checked-out SHA, and say which you cited against.

## Phase 0 — scan

Write `docs/pitch/scan.md` before any other pitch file. Establish, with citations: what the
project claims to be in its own words before yours; what it has shipped and how you can tell;
what it tried and abandoned; where docs and source disagree; age, span, and **gap** as separate
facts; days since the last commit; whether tests exist and separately whether you ran them;
whether the subject has a clock that has run out — grep for **durations and commitments**, not
bare dates; whether this repo is a fragment.

**If the subject is deployed, put its liveness next to the repo's dormancy.** Collected
separately these two facts say much less.

**If there is no executable surface at all, report that as a *category* finding**, not a count
of zero. Every software-shaped claim about that target is then a category error — which is the
live case for a greenfield project whose tree is documents.

## Phase 0.5 — the affirmative sweep

**Its own step, because burying it as a bullet did not work.** Two questions, answered into
their own scan section:

1. **What does the repository enact rather than claim?**
2. **What does it do that is costly, that a persuasive version would have dropped?**

The rest of Phase 0 asks for four kinds of wrong against one kind of right. Skip this and you
will collect prosecution material and then have to reconstruct the reason to say yes from
evidence nobody gathered.

## Phases 1–2 — extract

1. **What this is.** The repo's own account, quoted and cited. Then *separately* your reading of
   whether the source supports it. Two claims, tagged separately.
2. **What problem it solves.** Not the problem you would pitch: the problems the repo
   *documents solving*. Issues, observations, commit messages that name a pain. The richest
   extraction available, usually skipped.

**When the self-description and the shipped code disagree about the problem, follow the code and
say so in the index.** A front page describes what someone wanted to build; the commits describe
what they built. "Code" means shipped artifacts — for a documents-only repo, the commit graph
and the finished outputs are the evidence.

**Ask whose pitch it is.** Owner, the people who did the work, and the entity being pitched are
not always one, and the axis is sometimes scope rather than entity: product, ecosystem, or
company. Decide explicitly and put it in the index.

## The scope note that was left orphaned

A `format` scan in this project carries a **scope note** saying its deck-structure findings
describe investor decks and were misapplied to a crowd pitch. That note was correct and the
correction was **half-finished**: the turn path was fixed and the investor findings were left
behind the note with **no consumer at all** — accurate research, still in the tree, feeding
nothing.

Full mode is that consumer. When a scan gets scope-noted rather than superseded, the note is a
statement that it was applied to the wrong audience — so the question to ask next is *which
audience is it right for, and does anything here serve them?* A scope note with no answer to
that is a scan quietly retired without being marked retired.

## Phases 3–5 — research, by citation

**These get no files here.** Who else has this problem, who the reader is, and what they use
instead are external facts, and external facts live in `docs/research/` with a mode, a horizon,
sources, and supersession. A `RESEARCHED` claim cites a scan id; the validator holds the pitch
tree to it.

Duplicating them inside `docs/pitch/` would create a second copy of every external fact,
expiring on no schedule. **This is the one place we are ahead of the source method** — it has no
staleness machinery and carries these as prose.

One persona, three roles: might fund, will use, is the customer. Do not split them. If the
evidence forces a split, that finding falsifies the premise and belongs in the pitch.

**Doing nothing is almost always the real competitor**, and a rival-scoring table omits it.

## Phase 3.5 — human validation

**Mandatory in full mode.** Needs the script from Phase 10, so in practice step 2 is satisfied
out of position.

1. Name the three riskiest assumptions: **most load-bearing and least evidenced**, not most
   uncertain.
2. Write the script (Phase 10).
3. **Read it to real people who match the reader.** Five is enough to be informative.
4. Apply **Pivot, Persevere, or Pause**, and record which, with the reactions that decided it,
   in `docs/pitch/reactions.md`.

Before anyone hears it, **write into `reactions.md` which reactions would change the pitch
rather than polish it** — pre-register the listening the way the threshold pre-registers the
measurement, or every reaction will be read as wording feedback.

**Our own validation does not satisfy this.** A founder scoring their own assumptions is the
author interviewing themselves with a form in between. Steps 3 and 4 cannot be faked.

This is the only step that can falsify the pitch. Everything else is reasoning about our own
material.

> **Inherited untested.** The source method has never run this step across seven repositories —
> *seven repositories, zero readers*. We can run it: a founder with a contact list is exactly
> what an agent extracting from someone else's repo does not have. Until it runs here, the
> strongest claim available about this skill is that it produced documents.

## Phases 6–7 — the offer

6. **What the money buys.** Micro-funding scopes, not a revenue model. Each names a deliverable
   checkable by the person who paid.
7. **The ask**, itemized from real prices, in `docs/pitch/the-ask.md`.

**Publish the itemization.** The number is small and that is the interesting part; nobody in
this category shows what a round actually costs. High funding goals correlate with failure, and
a detailed allocation breakdown is a documented trust signal — which matters most for a project
with no traction to show. **Resist the urge to apologise for a small number.**

**Usually `ASSERTED`, and the word is usually.** A cost written against a checkable action — a
quoted fee, an invoice, a subscription line — is `EXTRACTED` and belongs in the ask.

**Do not invent a number.** Mark every figure that needs a human and leave it visibly
incomplete. A pitch with an obvious blank is a draft; a pitch with an invented figure is a lie
with a decimal point.

**Do not hide one either.** The ask is **public by default**. The withholding reflex arrives
dressed as prudence, and the tell is that the same worry never attaches to any other claim in
the pitch.

**Contributed capacity — agent compute, human hours — never enters a cash ask.** It is recorded
in the ledger, not billed to backers.

## Phases 8–9

8. **Where this reader already is.** Named rooms, not channel categories. Cites a
   `distribution` scan.
9. **Risk.** A micro-funder is buying delivery risk: what is unfinished, untested, dependent on
   one person. **Defects you find are this evidence. Record them, never fix them** — fixing
   destroys what you are about to cite, and modifying anything outside the pitch directory is
   out of scope.

## Phases 10–12 — derived

10. **Narrative at three lengths.** In full mode the **long form is the script** — a
    ~10-minute narrated pitch in the investor order:

    | segment | carries |
    |---|---|
    | **Problem** | the mechanism the reader is in, never a named rival |
    | **Solution** | shown, benefits paired to features |
    | **Market** | who else has this problem — cites a scan, not a market-size fantasy |
    | **Traction** | what the repository demonstrates. **Often empty, and said plainly** |
    | **Business model** | how it sustains, or that it does not yet |
    | **Team** | the highest-attention slide in funded decks, per the format research |
    | **Ask** | itemized, with what the money buys |

    A `traction` segment with nothing in it is not a reason to skip the segment — it is the
    most informative thing on the slide, and skipping it reads as concealment to exactly the
    reader who checks.

    **Write the ~2-minute version too**, and write it first. It is the Phase 3.5 read-aloud —
    nobody workshops ten minutes with five people — and it is the seed every later turn script
    is cut from. Then the one-liner. Drafting the long form first invites compressing it, which
    inverts the ledger check.

    Two contradictions, both resolved here. The ledger is load-bearing yet the script comes
    first, so: draft the claims *mentally*, write the script, write `claims.md` formally, then
    **back-check the script against it** and move anything that does not survive. And Phase 3.5
    sits earlier but needs this script, so its step 2 is satisfied out of position.

    **The script has two jobs that pull apart.** Phase 3.5 wants something aimed at the weakest
    assumptions, to be falsified; Phase 10 wants something that makes a reader want in. Write
    for the second, *aim* it at the first: end on the question you most need answered.

    **Render the narration here too** — the gauge render is not a turn-mode step, it is how any
    script gets its length measured and heard (Step 4b). Full mode needs it *more*, because
    Phase 3.5 is mandatory and reading a script aloud to five people without having heard it
    once wastes the only sample that can falsify the pitch.

    **Full mode carries its own cost line, and it is not the turn's.** Narration bills about a
    credit per character, and roughly a thousand characters is a minute of speech:

    | | ~2-min turn script | ~10-min full script |
    |---|---|---|
    | characters | ~1,300 | **~10,000** |
| measured seconds | **80.9** *(242 words, ~179 wpm)* | unmeasured — the 150 wpm figure below is an estimate |
    | credits per render | ~1,300 | **~10,000** |
    | renders in a 30,000-credit Starter month | ~23 | **3** |
    | renders in a 100,000-credit Creator month | ~76 | **10** |

    **A ~10-minute pitch does not fit Starter.** Three renders is one draft plus two
    revisions, before any music. Creator is the floor for full mode, and even there ten renders
    a month disappear quickly once a rebuild trigger fires. So: gauge long-form **section by
    section** rather than whole, and re-render only the section that changed. Publish the
    full-mode cost separately from the round's — a reader comparing them should see that the
    standing pitch and the turn are different purchases.

11. **Production — and it runs *after* Phase 3.5, never before.** Full mode does produce a
    narrated artifact, but the ordering principle is unchanged and is the whole reason this
    phase has a number: **producing before a human has heard the script is polishing something
    nobody reacted to.** Three source runs nearly built a deck anyway.

    Slides, narration, captions and assembly follow [Step 6](#step-6--produce), which both
    modes share. At ten minutes expect ~30–40 slides rather than the 10–15 a self-paced deck
    carries — a ten-minute narration over fifteen stills leaves each one on screen for forty
    seconds, which is longer than an image holds attention.

12. **Assembly**: the index, the two numbers, the staleness report — then an **arithmetic
    pass** over the whole tree: re-sum every stated total against its own itemization, re-count
    every enumerated tally against its own list, and re-derive every number that appears in
    more than one file, once, at the end. The first run shipped "six of eight" over a list of
    five and a "thirty dollar" ask over an itemization summing to 31 — in a pitch whose premise
    is that the cost is a receipt. And expect the fixed point to fire: adding the row that
    records a numeric disagreement changes the ratio the index reports.

    **The index must lead with what a reader would be *for*.** It is what gets opened first and
    it drifts into an audit summary faster than the long form does.

## `what-exists-now.md` — five buckets, in this order

The order sets the document's temperature, so run them in it.

1. **Built.**
2. **Built but never claimed.** The costly things nobody advertised. In three source runs this
   was the best material available.
3. **Built unevenly.** *"Eight of sixteen"*, *"3 of 4 gates"*. Often the truest description.
4. **Not built.**
5. **Stated but never built.** The gap between the description and the repository — for this
   audience the single most important thing to be straight about.

**Bucket 5 over-triggers**: something built but not wired up is not an unkept promise. And
**record where the statement appears** — the same sentence is a promise under a product heading
and an invitation under "what you could build".

## Maintenance

A pitch goes stale silently, and **a stale `EXTRACTED` claim is worse than an `ASSERTED` one**
because it carries authority it no longer has.

A re-run **checks its citations before writing anything**: does every cited `file:line` still
exist and still say what the claim says, does every cited commit still exist, do the counts still
hold, how old is each cited scan.

**Whatever fails is demoted, not refreshed.** A claim true when written and now unverified is a
third state; collapsing it to true or false loses information. Demotion goes in the staleness
report with the date it stopped verifying. Quietly re-extracting a broken claim to a new line
number hides that the ground shifted, which is the thing a maintainer needs to know.

On a first run nothing can be demoted, so the report is an *already expected to drift* table
naming which claims will move and why.

**The pitch mutates the tree it describes.** Committing `docs/pitch/` changes the tracked-file
count, the commit count, and "nothing uncommitted" — so tree-shape claims are true at the
scanned SHA and at no commit after. Pin them to the SHA and list them in the first-run
staleness report as breaking on the pitch's own first commit.

---

# Part 4: turn

Produces `docs/rounds/2026-08-24-turn-N.md` and the video. Runs on the standing ledger.
The record's frontmatter shape — `turn`, `pitch_mode`, `claims`, `threshold`, `result`,
`demoted` — is in [schemas](../neon-docs/references/schemas.md); create it as `draft` at
step 1 so there is somewhere to record as you go.

**The record snapshots; the tree stays current.** The script that actually posts is written
into the round record, where event semantics freeze it, while `docs/pitch/two-minute.md`
remains the living script and moves on. When they differ later, that is history working, not
drift — the round shows what turn N's audience saw.

## Step 1 — select and re-verify

Pick the six to ten claims the script needs, and **re-verify those**. Not the whole ledger —
that is the entire efficiency argument for this mode. Demote what fails in the ledger, and
**record the failed ids in the round record's `demoted:` field** — that is where the
full-rebuild trigger reads the rate from, and an empty list is a finding too, saying the
re-check ran and held. Over a third demoted and the next turn is a full rebuild.

## Step 2 — extract what is new, and append it

Work done since the last turn produces new claims. Tag them with the same discipline and append
them to `claims.md` **before** the script uses them. The ledger invariant has no exception for
being in a hurry.

## Step 3 — derive the ask

Itemize from real prices, publish the itemization, and carry over the Phase 6–7 rules above.

**Budget gauge renders separately from ship takes.** They scale with **drafts, not takes** —
the first run's script went through three drafts before it was cut to length, and under this
procedure each of those renders. An ask that budgets "three takes" and then iterates five times
is under-itemized against its own process. Two lines, both published:

| line | scales with |
|---|---|
| gauge renders | number of script drafts |
| ship take | one, plus retries on delivery |

## Step 4 — script first, everything else second

At ~150 words per minute, 90 seconds is **~225 words** — a drafting target, not a
measurement, and **measured once it is wrong by 20%**. A 242-word script estimated at 97s
rendered at 80.9s: ~179 wpm for that voice, not 150. The rate is a property of the voice and
the settings, so it is not a constant to correct — it is a reason not to quote an estimate. **The measurement is the rendered audio's duration** (Step 4b), and it is the
number that gets published.

Word count is a two-step estimate — count the words, assume a rate — and on the first run both
steps failed: the script was published as "~228 words" when it measured 273, and the corrected
instrument then reported 284 because it silently swallowed a generated `<!-- nav -->` block.
The assumed 150 wpm was never checked against a voice at all. **A rendered file has a duration;
it cannot be miscounted, and it settles the rate question by not asking it.**

Write and cut the script before generating slides. Cutting a script is free; cutting finished
slides is not.

### Four parts, not seven slides

| segment | timing |
|---|---|
| **Hook** — the problem, arrestingly | 0–8s |
| **Problem** — why it is worth caring about | 8–30s |
| **Solution** — show it; benefits paired to features | 30–90s |
| **Ask** — what the money buys, itemized | final 10–15s |

**This is not the investor order, and that order is not wrong — it is full mode's.** Problem →
solution → market → traction → business model → team → ask is researched for partners running
diligence over two minutes, and full mode uses it for exactly that reader. A round's audience is
strangers deciding in ninety seconds, where the same order spends slides on market size
(irrelevant to someone giving $10) and on traction and financials an early project does not
have. Crowdfunding videos run 60–180 seconds; the most-cited failure is overcomplicating, so
viewers leave before the ask.

### Sell participation, not features

Reward-based backers are primarily driven by **purpose and identification with the mission**;
the reward is secondary. And **participation ranks as the most effective reward category** —
above a physical product, far above a virtual one.

The trap is drifting toward *virtual product* framing — access, credits, downloads — the least
effective category and the first thing most people reach for. What a round sells is naming what
gets built, watching it happen, and holding a claim on the ledger.

### Step 4b — render the audio, and listen to it

**Every pitch renders narration by default, in both modes.** ElevenLabs, straight from the
script, before any slide exists. This is a **gauge, not necessarily the ship take**, and the
two jobs are different — conflating them is what kept TTS filed as a later A/B experiment when
it was always the cheapest rehearsal available.

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

**TTS ships, in both modes.** Replacing the audio track with a human recording is **out of
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

### Back-check against the ledger

Every claim the script makes appears in `claims.md`. Move anything that does not survive.
List the claim ids in the round record.

**Do it sentence by sentence, in both directions, with the ledger open** — write each spoken
sentence next to the row it needs, then read the claim list against the table. A final glance
is not this check: the first run's list was wrong in both directions at once (three ids the
script never says, three sayings with no id, one claim with no row), and the mechanical half
of gate 6 passed cleanly the whole time.

## Step 5 — the threshold, written before posting

**Two experiments, and one turn can only answer one.**

- **Watchability** — does the artifact hold attention? Needs ~30 video **starts**, any source.
- **Distribution** — can this reach strangers at scale? Needs ranking luck, a warm audience, and
  repetition across turns.

Conflating them is what makes a null result uninterpretable: with no audience you cannot tell an
uninteresting artifact from an empty room. Test watchability per turn; let distribution
accumulate.

**The floor is 30 starts**, because that is where a 95% interval around a 40% completion rate
excludes 15%. Fifty is comfortable; ten tells you nothing. The unit is **starts** — at a 1–3%
link CTR, 30 starts implies 1,000–3,000 impressions.

Default: **≥30 starts with ≥40% completion passes; ≤15% fails; between them is `inconclusive`
and the turn repeats.**

**Write it into the round record's `threshold:` frontmatter field before posting.** A threshold
chosen after seeing the result is not a threshold, and an experiment that cannot fail cannot
succeed either. The record is an event for exactly this reason — and the field is enforced: a
`posted` round without one is a validation error, and editing it after the round leaves `draft`
is a history-rule error under `--since`. When the numbers come back, they land in `result:`.

### Human validation in turn mode

The measured threshold **substitutes** for Phase 3.5. Weaker per instance, but real, repeated,
and quantitative.

**The substitution is not available at T=1**, which has no prior measurement to lean on — the
argument for it is *we already measure this*, and at T=1 that is false. T=1 is an init and gets
the full gate.

## Step 6 — produce

- **Narration.** The gauge render already exists from Step 4b. For the **ship** take at T=1,
  a real human voice: it removes the low-effort-AI association and removes a confound, since a
  null result should be attributable to the concept rather than the voice. A/B the TTS take
  from T=2, one variable at a time.
- **Put a face on it.** Trust is best built face-to-face, and the segment should read **calm,
  honest, grounded** — no shouting, no overacting. Cheapest version: a face for the founder
  segment, stills for the rest.
- **Theme.** Generate the music bed **once** and reuse it every round. A recurring show needs a
  recurring theme; regenerating it throws away the sonic identity that makes a later episode
  recognisably the same series.
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

Set the round's status, append the result when it arrives, then:

```bash
python3 .claude/skills/neon-docs/scripts/validate.py --fix
```

---

# Part 5: Output, gates, and why

## Output shape

```
docs/pitch/                       living, optional, rebuilt by full
├── README.md                     index, the two numbers, staleness report †
├── scan.md                       Phase 0 + the affirmative sweep
├── claims.md                     the ledger — load-bearing
├── one-liner.md
├── two-minute.md                 the ~2-min script: Phase 3.5 read-aloud, and the seed
│                                 every turn script is cut from
├── long-form.md                  the ~10-min full-mode script, investor order, narrated
├── what-exists-now.md            the five buckets
├── the-ask.md
├── riskiest-assumptions.md
├── reactions.md                  Phase 3.5
├── deck-outline.md               gamma.py input — cards, plus a preamble carrying the
│                                 file's title and the segment→timing mapping
└── storyboard.md                 deck.py input — the SAME cards, typeset

**Both deck specs describe one pitch.** Two renderers over one narrative is a feature; two
renderers over two narratives is drift, and it happened — a 14-card storyboard sat beside the
10-card deck that actually shipped, so the fallback would have rendered a pitch nobody
reviewed. When one changes, change the other.

docs/rounds/2026-08-24-turn-N.md  event, optional, one per turn
```

† The top of `README.md` is the generated directory index (`--fix` maintains it); the two
numbers and the staleness report are hand-written **below** the generated block, which the
generator preserves. **Start the file with the empty marker pair** (`<!-- index:begin -->`
`<!-- index:end -->`): a README with no markers is wholly replaced by the next `--fix` — silent
data loss, filed as an open registry issue the first run found by hitting it in a fixture copy.

**Flat, unlike the source method**, which nests under `evidence/`, `narrative/`, `offer/`,
`risk/`, `validation/`. Our validator and navigation generator walk one level, and the filenames
were carrying the grouping anyway. A change to fit the conventions, not to improve the method.

**No `research/` subtree** — Phases 3–5 cite `docs/research/` instead.

Drop a file when the project genuinely has nothing for it, and say so in the index. A stub of
generated filler is the failure that prevents.

## Gates

1. **Provenance.** Every claim tagged and cited. Untagged is a defect.
2. **Both numbers reported**, neither thresholded.
3. **The problem is a mechanism, not a rival.** Alternatives described accurately, including
   what they do better.
4. **Human validation before done.** Phase 3.5 in full mode, a measured threshold in turn mode,
   or the index says DRAFT.
5. **`CHECKED` never carries a riskiest assumption and never appears in the one-liner.**
6. **Ledger integrity.** Two halves. The mechanical half is **validator-enforced**: a claim is
   a `| C-NNN |` table row in `claims.md` (row format in
   [schemas](../neon-docs/references/schemas.md)), ids are unique, every row carries exactly one
   tag, and a round's `claims:` list resolves against those ids. The judgement half stays human:
   **does the script's claim list match what the script actually says?** A script can cite C-004
   and then paraphrase it into a stronger sentence, and no parser catches that — in the source
   method this half found three reassigned ids and one claim a script never made.
7. **The threshold precedes the posting.** Validator-enforced three ways: a `posted` round
   without a `threshold:` field is an error, a resolved round without a `result:` is an error,
   and under `--since`, editing the threshold after the round left `draft` is an error — the
   field freezes at posting, like a proposal's filename freezes when it leaves draft.

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

The structural fix is upstream, in Phase 0.5 and the bucket order, because a check applied after
the long form arrives too late — by then the evidence base is already tilted. Run the check
anyway, on the long form **and the index**: does a reader know what they would be *for*? If the
answer is only what they would be warned about, the gates held and the genre was lost.

**Fix it by adding what is true and good, never by removing what is true and bad.**

This project is the ideal victim: a docs tree of self-criticism, an issue recording that a plan
was built on the wrong research, and a founding document instructing readers to treat every
number in it as a hypothesis. An honest extraction here produces a devastating and entirely
accurate indictment unless Phase 0.5 runs first.

## Why the honesty gate is a reach argument

A pitch is the highest-sycophancy-surface artifact a repo can produce. What makes the gate
enforceable rather than aspirational is the audience: **the funder is also the user.** An
investor may never touch the product; a micro-funder meets every overclaim on contact, quickly,
and tells people.

The discipline is not *be honest because honesty is good*. It is: **this reader finds out, and
the finding-out is the distribution channel.** That is the argument that survives contact with
someone who wants the pitch punchier.

## Status

**The evidence half**: forked from `gitwverse` at `cc5f205e`, 2026-08-24. Seven repositories,
every run revising it, **zero readers** — Phase 3.5 never ran there. Three things held across
all seven and are worth more than any single finding: the ratio consistently misleads and the
riskiest-three number does not; the pull is toward prosecution, not persuasion; and after the
arithmetic rules existed, the errors moved from memory into instruments.

**The extraction half here: N=1.** Full mode ran once, and broke four things the prose had not
anticipated — which is the source method's own pattern continuing:

| run | target | what it broke |
|---|---|---|
| 1 | live-neon, 2026-08-24 | **The gate-6 judgement half, both directions at once** — the script's claim list named three ids the script never says and missed four it needs, while the mechanical half passed clean. A word count stated as a measurement was a target (claimed 228, measured 273), and the fixed instrument later broke again by absorbing generated nav. Assembly shipped two arithmetic defects ("six of eight" over a list of five; a $30 ask over an itemization summing to 31). Found and left in place: a silent data-loss defect in the shared tooling, and a docs-vs-world mismatch (the named domain serves a different product) |

**Revised after run 1**, on the founder's call: the two modes now produce different artifacts
for different readers rather than the same artifact at different freshness — a ~10-minute
narrated pitch in the investor order for someone evaluating the project, and a <2-minute video
in the four-part order for the crowd. Narration is TTS in both. That split is **unrun**: every
step below describing full-mode production is N=0 again.

**Run 4 — live-neon, 2026-08-24, first video.** The slides were the wrong *genre* and the
founder said so on sight: fourteen generated editorial stills, no text, every word pushed into
captions. Rebuilt twice — typeset via `deck.py`, then via the Gamma API — and the lesson is not
about vendors. **A deck's text is its content, so the tool has to be one that renders text
exactly.** Four smaller defects, all free to find: Cloudflare 1010 on a UA-less Replicate call;
the generic `/predictions` endpoint versus `/models/{owner}/{name}/predictions`; an
`Authorization` header sent to an output CDN, which fails *after* billing and reads as a
generation failure; and a zip whose card 10 sorts before card 1, which reorders a deck silently
and still plays.

**Run 3 — live-neon, 2026-08-24, first narration rendered.** 80.9 seconds measured against 97
estimated: the ~150 wpm constant this procedure inherited is **20% wrong** for a real voice.
Nothing else changed — the script, the parser and the character count were all correct — and
the number was still wrong, because a rate assumption is not a measurement. At the ten-minute
long form the same error is over two minutes. Segment caching worked: a second run rendered
nothing and cost nothing.

**Run 2 — live-neon, 2026-08-24, the first re-run.** Broke three more things: the trigger list
had no entry for *the procedure changed* (added as trigger 6, having been found by needing it);
the gate-6 back-check **failed a second time**, exactly as its observation predicted from the
ordering, naming one claim the script never made and missing eight it did; and the
self-referential *"this ledger holds N claims"* row falsified itself on being written — the
documented fixed point, converged by editing in place rather than adding a row. The maintenance
pass demoted one claim (`C-015`) whose count had moved, re-extracted loudly rather than quietly.

What held: the extraction premise (a documents-only repo produced a 27-claim ledger, 74%
extracted), the prosecution guard (the index leads with what a reader would be for; bucket 2
carried the best material), and the two-numbers gap exactly as the source predicted — 74%
extracted beside riskiest-three of 0.5.

**The production half**: **N=0.** A script now exists (244 measured words); no video has been
produced, nothing posted, nothing measured. Every timing, threshold, and channel rule is
research applied to a situation it was not gathered in.

**The fork does not receive upstream revisions.** The next run there will break something in it,
on the evidence of the previous seven, and we will not hear. Re-read and diff against the
recorded commit deliberately or not at all.

## Falsifiability

- **The two modes collapse.** If every turn triggers a full rebuild, the split is imaginary.
- **The invariant does not hold.** If turn pitches routinely append claims a full rebuild would
  tag differently, the shared ledger is laundering rather than constraining.
- **The extraction premise. Held at N=1** — a repository with zero code files still yielded a
  27-row ledger at 74% extracted, because the documents themselves are artifacts. The hook
  stands for repositories with less self-description than this one.
- **The honesty-is-reach claim.** If overclaiming pitches outperform with micro-funders, the
  central argument is wrong.
- **The tri-role reader.** If real readers split into funders-who-do-not-use and
  users-who-do-not-fund, the collapsed persona is a fiction.
- **The prosecution guard.** If a run still produces an audit with a warm closing sentence, the
  guard has to become a gate.
- **The ~10-minute full-mode length.** Decided deliberately, and **against every length finding
  in this tree**: investor first-pass review averages 2 min 14 s, crowdfunding videos lose most
  viewers past 5 minutes, explainers drop sharply past 2. None of those studied a *warm* reader
  who agreed to watch, which is full mode's audience — so the finding may simply not apply, and
  it may. **Nothing here evidences ten minutes.** The falsifier is the first full pitch's
  completion curve: if warm viewers drop at the same place cold ones do, the format is wrong and
  the reader-paced deck is the alternative that was set aside to get here.
- **The six-turn backstop.** A guess with no evidence behind it.
- **The threshold numbers.** 30 starts, 40%, 15% — derived from a binomial interval, never
  observed here.

## What to write down afterwards

Whatever surprised you, as an observation with evidence and `n: 1`. Both halves of this
procedure are untested in this project; the first real run is the only thing that will show
which steps were guesses.
