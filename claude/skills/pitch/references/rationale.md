# Why this is shaped the way it is

> Part of the [`pitch`](../SKILL.md) skill. The operating core — the four tags, the
> citation rule, the two numbers, the ledger invariant — and the
> [gates](../SKILL.md#part-4-gates) are in [`SKILL.md`](../SKILL.md), and they apply
> here. This file is the procedure.

Standing argument, provenance and falsifiers. Nothing here is a step; read it when
deciding whether a rule still earns its place, or when a run breaks one.

## Why the honesty gate is a reach argument

A pitch is the highest-sycophancy-surface artifact a repo can produce. What makes the gate
enforceable rather than aspirational is the audience: **the funder is also the user.** An
investor may never touch the product; a micro-funder meets every overclaim on contact, quickly,
and tells people.

The discipline is not *be honest because honesty is good*. It is: **this reader finds out, and
the finding-out is the distribution channel.** That is the argument that survives contact with
someone who wants the pitch punchier.

**There is now a second limb, and it does not depend on anyone finding out.** Regulation
research records that Regulation Crowdfunding carries **strict liability**: if an ask is ever
held to be a securities offering, a material misstatement is enough on its own — no intent, no
knowledge, no reliance required. Whether any given ask is such an offering is a question for
counsel and this skill does not answer it. What follows regardless is the standard one source
gives, which is the ledger's standard stated in a sentence: **never write a claim you could not
answer for if asked *how can you say that*, pointing at a document.**

Nine years in business and nineteen deals closed beats best-in-class and industry-leading, which
a sophisticated reader discounts automatically — so the two limbs agree about the wording as
well as the discipline.

## Status

**The evidence half**: forked from `gitwverse` at `cc5f205e`, 2026-08-24. Seven repositories,
every run revising it, **zero readers** — Phase 3.5 never ran there. Three things held across
all seven and are worth more than any single finding: the ratio consistently misleads and the
riskiest-three number does not; the pull is toward prosecution, not persuasion; and after the
arithmetic rules existed, the errors moved from memory into instruments.

**This skill is project-agnostic and names no tenant.** Runs below are "the N=1 target" because
a public, reusable skill should not carry a private project's name; the traceable record — which
project, which commit, what broke — lives in the registry's `docs/observations/`, which is
public. Provenance belongs there, and the transferable lesson belongs here.

**The extraction half here: N=1.** Full mode ran once, and broke four things the prose had not
anticipated — which is the source method's own pattern continuing:

| run | target | what it broke |
|---|---|---|
| 1 | the N=1 target, 2026-08-24 | **The gate-6 judgement half, both directions at once** — the script's claim list named three ids the script never says and missed four it needs, while the mechanical half passed clean. A word count stated as a measurement was a target (claimed 228, measured 273), and the fixed instrument later broke again by absorbing generated nav. Assembly shipped two arithmetic defects ("six of eight" over a list of five; a $30 ask over an itemization summing to 31). Found and left in place: a silent data-loss defect in the shared tooling, and a docs-vs-world mismatch (the named domain serves a different product) |

**Revised after run 1**, on the founder's call: the two modes now produce different artifacts
for different readers rather than the same artifact at different freshness — a ~10-minute
narrated pitch in the investor order for someone evaluating the project, and a <2-minute video
in the four-part order for the crowd. Narration is TTS in both. That split is **unrun**: every
step below describing full-mode production is N=0 again.

**Run 4 — 2026-08-24, first video.** The slides were the wrong *genre* and the
founder said so on sight: fourteen generated editorial stills, no text, every word pushed into
captions. Rebuilt twice — typeset via `deck.py`, then via the Gamma API — and the lesson is not
about vendors. **A deck's text is its content, so the tool has to be one that renders text
exactly.** Four smaller defects, all free to find: Cloudflare 1010 on a UA-less Replicate call;
the generic `/predictions` endpoint versus `/models/{owner}/{name}/predictions`; an
`Authorization` header sent to an output CDN, which fails *after* billing and reads as a
generation failure; and a zip whose card 10 sorts before card 1, which reorders a deck silently
and still plays.

**Run 3 — 2026-08-24, first narration rendered.** 80.9 seconds measured against 97
estimated: the ~150 wpm constant this procedure inherited is **20% wrong** for a real voice.
Nothing else changed — the script, the parser and the character count were all correct — and
the number was still wrong, because a rate assumption is not a measurement. At the ten-minute
long form the same error is over two minutes. Segment caching worked: a second run rendered
nothing and cost nothing.

**Run 2 — 2026-08-24, the first re-run.** Broke three more things: the trigger list
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

**Revision 2026-08-24b — 80 practitioner videos, and what they moved.** A distillation corpus
of 80 videos produced three scans (`writing-the-ask-practitioner-video`,
`non-accredited-offering-pathways`, `crowdfunding-platform-mechanics`). Reviewing this skill
against them changed nine things, and **none of them came from running the procedure** — this
is research applied to a skill, the same evidence class as everything above it, and it inherits
that weakness.

The structural finding is the one worth keeping: **the skill's own recorded failure recurred
while the skill was describing it.** Three scans landed with no consumer, cited only by each
other, and mode derivation reported no trigger. Trigger 7 and `scans.py` exist because prose
naming a failure did not prevent its second instance — which is the same lesson as trigger 6,
arriving a second time.

What moved: trigger 7 (the evidence changed); `scans.py` and the coverage pass; AI disclosure
as a gate; *what a pledge buys* as a gate; the cheapest-next-step call to action; the founder
story placed last; a close date and the funding-vs-measurement distinction; the update format;
audio ranked over picture. Two prior positions were **not** overturned but now carry falsifiers
that name what would overturn them: the small ask, and the ten-minute length — whose stated
falsifier was **wrong**, since a completion curve cannot see viewers who never press play.

**Revision 2026-08-24c, three modes and a format axis. N=0, and it is a revision by reading, not
by running.** Two defects that had already fired, plus one gap that only became visible once they
were separated:

- **The schema could not record what turn 1 did.** `pitch_mode:` is defined as *which mode
  produced this round's script* and holds one value, while turn 1 shipped artifacts from both
  modes and labelled itself `full` over a crowd-order script.
- **Phase 11's ordering did not hold.** *Production runs after Phase 3.5, never before* was
  written down and broken by the next run: two videos against a `reactions.md` reading
  `Status: NOT RUN`. Making audience-facing renders opt-in is that rule expressed as a default
  rather than as prose, on the evidence that prose did not hold it. The gauge audio render stays
  on by default, because separating instrument from artifact is the distinction Step 4b already
  drew and the gauge is the only instrument here that has caught a real error.
- **Nothing watched the renders.** Triggers 1 to 7 all watch content. The render check exists
  because a script can move out from under a published video, and the staleness machinery, thorough
  about claims, says nothing about renders.

The third mode, elevator, is forked back from `gitwverse`'s Phase 10.5, added there the same day
from the opposite direction. **None of this has run.** Two modes existed and one of them had never
executed; there are now three, and the count of modes that have shipped anything to a reader is
still zero.

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
  it may. **Nothing here evidences ten minutes.**

  **And the completion curve cannot falsify it alone.** A practitioner source names the
  mechanism the curve is blind to: **the displayed runtime is read before play**, so a long
  video *"loses people at second zero, which no amount of front-loading fixes."* Someone who
  never presses play contributes no drop-off point — so a ten-minute pitch could fail exactly
  this way and return a clean completion curve over the few who started. The falsifier has to
  be the **start rate against a shorter control**: the same pitch, same audience, offered at
  two lengths, comparing how many begin. Completion measures the format among people it already
  survived.
- **The third mode.** Elevator is asserted to be a distinct reader: live, two-way, interruptible,
  answered by a question rather than a decision or a pledge. If the card is only ever read
  silently, or if what people ask after hearing it is what the two-minute already answers, then it
  is a length and belongs in the narrative files rather than as a mode.
- **The format axis.** It exists because one field could not record a turn where both modes
  shipped. If no turn ever again produces artifacts in two modes, the axis is bookkeeping for a
  single event. And if the audience-facing formats are requested on every run anyway, the default
  is ceremony and the real default is video.
- **The instrument-against-artifact line.** Gauge audio renders by default and video does not, on
  the argument that one is a measurement and the other is for an audience. If a gauge render is
  ever shipped to a reader unchanged, the line is not where this says it is.
- **The render check.** Never fired. If renders in practice are always regenerated alongside
  the script they came from, nothing goes stale and the check is dead weight.
- **The six-turn backstop.** A guess with no evidence behind it.
- **The threshold numbers.** 30 starts, 40%, 15% — derived from a binomial interval, never
  observed here.
- **The small ask.** Phases 6–7 say resist apologising for a small number, and a practitioner
  who ran both ends now reports against it: effort per contributor is roughly constant, so
  raising his floor made each contributor about five times more valuable. Both can hold — the
  same operator says the money comes from personal connection rather than expected return, which
  is a reason to keep the ask small that has nothing to do with conversion. **What is falsified
  is defending the small number on conversion grounds.** If turns fund at a rate that a larger
  ask would beat on the same effort, the figure is wrong and the itemisation is not the reason
  to keep it.
- **The cheap call to action.** If turns with a reply-or-deposit ask produce no more
  interpretable signal than turns asking straight for a pledge, the cheaper step is costing a
  conversion and buying nothing.

## What to write down afterwards

Whatever surprised you, as an observation with evidence and `n: 1`. Both halves of this
procedure are untested in this project; the first real run is the only thing that will show
which steps were guesses.
