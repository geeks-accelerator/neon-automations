---
name: pitch
description: Produce a round's pitch — the claims ledger, the script, the itemized ask, the narrated video — and post it. Use this skill whenever asked to make a pitch, pitch deck, pitch video, round video, or funding ask for a project, to open or close a turn of the funding loop, or to rebuild or refresh a project's pitch. It derives its own mode (a full extraction from the repository, or an incremental turn off the standing ledger), runs the research preflight first, and stops if open questions, stale research, or validation errors remain — so reach for it at the start of pitch work rather than after a deck exists. Also use it when asked "what goes in the pitch", "how long should the video be", "what can we honestly claim", or "what should we ask for".
---

# pitch

Two modes over one claims ledger.

| | produces | when |
|---|---|---|
| **full** | `docs/pitch/` — the ledger and the narrative derived from it | init, and when a trigger fires |
| **turn** | `docs/rounds/2026-08-24-turn-N.md` — script, ask, threshold, result | every other turn |

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

10. **Narrative at three lengths. Write the script first**, then the one-liner, then the long
    form. The listed order invites compressing the long form, which inverts the ledger check:
    the script is what the reader meets.

    Two contradictions, both resolved here. The ledger is load-bearing yet the script comes
    first, so: draft the claims *mentally*, write the script, write `claims.md` formally, then
    **back-check the script against it** and move anything that does not survive. And Phase 3.5
    sits earlier but needs this script, so its step 2 is satisfied out of position.

    **The script has two jobs that pull apart.** Phase 3.5 wants something aimed at the weakest
    assumptions, to be falsified; Phase 10 wants something that makes a reader want in. Write
    for the second, *aim* it at the first: end on the question you most need answered.

11. **Materials — deliberately no file.** A deck is a re-cut of the narrative, and producing one
    before a human has heard the script is polishing something nobody reacted to. **Production
    is Part 4, and it runs after Phase 3.5.**

12. **Assembly**: the index, the two numbers, the staleness report. **The index must lead with
    what a reader would be *for*.** It is what gets opened first and it drifts into an audit
    summary faster than the long form does.

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

## Step 4 — script first, everything else second

At ~150 words per minute, 90 seconds is **~225 words**. Write and cut the script before
generating anything. Cutting a script is free; cutting finished slides is not.

### Four parts, not seven slides

| segment | timing |
|---|---|
| **Hook** — the problem, arrestingly | 0–8s |
| **Problem** — why it is worth caring about | 8–30s |
| **Solution** — show it; benefits paired to features | 30–90s |
| **Ask** — what the money buys, itemized | final 10–15s |

**This is not the investor order.** Problem → solution → market → traction → business model →
team → ask is researched for partners running diligence over two minutes. A round's audience is
strangers deciding in ninety seconds, and that order spends slides on market size (irrelevant to
someone giving $10) and on traction and financials, which an early project does not have.
Crowdfunding videos run 60–180 seconds; the most-cited failure is overcomplicating, so viewers
leave before the ask.

### Sell participation, not features

Reward-based backers are primarily driven by **purpose and identification with the mission**;
the reward is secondary. And **participation ranks as the most effective reward category** —
above a physical product, far above a virtual one.

The trap is drifting toward *virtual product* framing — access, credits, downloads — the least
effective category and the first thing most people reach for. What a round sells is naming what
gets built, watching it happen, and holding a claim on the ledger.

### Back-check against the ledger

Every claim the script makes appears in `claims.md`. Move anything that does not survive.
List the claim ids in the round record.

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

- **Narration.** A real human voice beats TTS for a first pitch: it removes the low-effort-AI
  association, and it removes a confound — a null result should be attributable to the concept,
  not the voice. A/B TTS in a later turn, one variable at a time.
- **Put a face on it.** Trust is best built face-to-face, and the segment should read **calm,
  honest, grounded** — no shouting, no overacting. Cheapest version: a face for the founder
  segment, stills for the rest.
- **Theme.** Generate the music bed **once** and reuse it every round. A recurring show needs a
  recurring theme; regenerating it throws away the sonic identity that makes a later episode
  recognisably the same series.
- **Slides.** Expect ~2 attempts per keeper.
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
├── two-minute.md                 the script; doubles as the Phase 3.5 read-aloud
├── long-form.md
├── what-exists-now.md            the five buckets
├── the-ask.md
├── riskiest-assumptions.md
└── reactions.md                  Phase 3.5

docs/rounds/2026-08-24-turn-N.md  event, optional, one per turn
```

† The top of `README.md` is the generated directory index (`--fix` maintains it); the two
numbers and the staleness report are hand-written **below** the generated block, which the
generator preserves.

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

**The production half**: **N=0.** No script has been written, no video produced, nothing posted,
nothing measured. Every timing, threshold, and channel rule is research applied to a situation
it was not gathered in.

**The fork does not receive upstream revisions.** The next run there will break something in it,
on the evidence of the previous seven, and we will not hear. Re-read and diff against the
recorded commit deliberately or not at all.

## Falsifiability

- **The two modes collapse.** If every turn triggers a full rebuild, the split is imaginary.
- **The invariant does not hold.** If turn pitches routinely append claims a full rebuild would
  tag differently, the shared ledger is laundering rather than constraining.
- **The extraction premise.** If a full run finds most of what a pitch needs is not in the
  repository, this is an ordinary pitch skill in an evidence costume — and *that result is worth
  more than the pitch*.
- **The honesty-is-reach claim.** If overclaiming pitches outperform with micro-funders, the
  central argument is wrong.
- **The tri-role reader.** If real readers split into funders-who-do-not-use and
  users-who-do-not-fund, the collapsed persona is a fiction.
- **The prosecution guard.** If a run still produces an audit with a warm closing sentence, the
  guard has to become a gate.
- **The six-turn backstop.** A guess with no evidence behind it.
- **The threshold numbers.** 30 starts, 40%, 15% — derived from a binomial interval, never
  observed here.

## What to write down afterwards

Whatever surprised you, as an observation with evidence and `n: 1`. Both halves of this
procedure are untested in this project; the first real run is the only thing that will show
which steps were guesses.
