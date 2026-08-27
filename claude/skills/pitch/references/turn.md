# turn mode

> Part of the [`pitch`](../SKILL.md) skill. The operating core — the four tags, the
> citation rule, the two numbers, the ledger invariant — and the
> [gates](../SKILL.md#part-4-gates) are in [`SKILL.md`](../SKILL.md), and they apply
> here. This file is the procedure.

Produces `docs/rounds/<date>-turn-N.md` and the round's artifacts, off the standing
ledger. Steps 6 onward — produce, publish, post, update — are in
[`production.md`](production.md), because full mode shares them.

Produces `docs/rounds/<date>-turn-N.md` and the video. Runs on the standing ledger.
The record's frontmatter shape — `turn`, `pitch_mode`, `claims`, `threshold`, `result`,
`demoted` — is in [schemas](../../neon-docs/references/schemas.md); create it as `draft` at
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

**A milestone and a period, never a round label.** *"We're raising a seed round"* communicates
nothing; the split is read as a statement of priorities, and a milestone-shaped ask can be
reported against where a round-sized one cannot. The procedure that follows from it inverts
which number is fixed: cost the milestone, sum what the reachable network could plausibly
give, and **if the second is not comfortably larger, choose a cheaper milestone.** The plan is
the variable, not the ask.

**Say what a pledge buys, in one sentence, before anyone pledges.** Gift, purchase,
contribution, or a claim on future value — the same words to every backer, written down before
money moves. Ownership confusion is reported as real, arriving at any amount, and almost
entirely preventable at this cost. It is also the boundary the regulation research turns on: a
pledge buying participation resembles a reward or a gratuity, while a pledge buying a claim on
future value switches on every securities constraint. **The sentence goes in the round record
and on the published page**, not only in the mechanism doc.

**Not legal advice, and the skill does not decide this.** It requires that the answer be
written down and identical everywhere, which is the part that is free now and expensive after
three rounds have each implied something different.

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

| segment | share of the whole | at a 90s target |
|---|---|---|
| **Hook** — the problem, arrestingly | ~10% | 0–9s |
| **Problem** — why it is worth caring about | ~15% | 9–22s |
| **Solution** — show it; benefits paired to features | ~60% | 22–76s |
| **Ask** — one-sentence backstory, then what the money buys, itemized, then the cheapest next step | ~15% | final 14s |

**Shares, because the total is a measurement and not a setting.** These were absolute seconds
running 0–8 / 8–30 / 30–90 with a *"final 10–15s"* Ask — which does not close: a Solution
ending at 90 leaves nothing before it. The first real script came in at **80.8s** measured
(8.3 / 11.9 / 44.3 / 16.3), close to these proportions and nowhere near those seconds, because
a render lands where the voice lands. Cut against the shares and check the measurement.

**This is not the investor order, and that order is not wrong — it is full mode's.** Problem →
solution → market → traction → business model → team → ask is researched for partners running
diligence over two minutes, and full mode uses it for exactly that reader. A round's audience is
strangers deciding in ninety seconds, where the same order spends slides on market size
(irrelevant to someone giving $10) and on traction and financials an early project does not
have. Crowdfunding videos run 60–180 seconds; the most-cited failure is overcomplicating, so
viewers leave before the ask.

### The call to action is the cheapest next step, not the pledge

The four-part order ends on the ask, and the reflex is to make that ask the pledge — the most
expensive thing available. Practitioner sources converge the other way from two directions:
the goal of a cold ask is **a reply, not a meeting**, and asking for the expensive thing first
is named as *arguably the biggest mistake*; the substitute is a question that lets the reader
choose the cheaper option.

**This is not softening the ask. It is the fix for a measurement problem this procedure already
has.** Step 5 records that with no audience you cannot tell an uninteresting artifact from an
empty room — a null pledge count is uninterpretable. A cheap action produces signal in exactly
that case, because people who will not pledge will still reply, reserve, or deposit.

The cheapest real-money version is a **refundable one-dollar deposit**. One agency reports 20–40%
of a deposit list converting at launch, and the mechanism is corroborated from an unrelated
domain — a B2B pre-sell method whose core claim is that **payment changes the counterparty's
behaviour**, at any size. Its equity-side analogue is legally sanctioned: *testing the waters*
collects non-binding indications of interest and needs no platform.

**Both deposit figures come from one interested source, so treat the rate as unmeasured here.**
What transfers is the ordering — a cheap paid step before an expensive one — not the numbers.

**And the buying signal is unsolicited advice.** When someone starts telling you how to improve
the thing, they are committed; nobody advises a project they do not care about. That is a
better read on a turn's comments than the pledge count.

### Sell participation, not features

Reward-based backers are primarily driven by **purpose and identification with the mission**;
the reward is secondary. And **participation ranks as the most effective reward category** —
above a physical product, far above a virtual one.

The trap is drifting toward *virtual product* framing — access, credits, downloads — the least
effective category and the first thing most people reach for. What a round sells is naming what
gets built, watching it happen, and holding a claim on the ledger.

### The founder story goes last, and the video does not open on your face

The trust ladder is ranked so each rung substitutes for the one above: an undeniable clip,
progress photos, an uncut workflow video, testimonials, domain authority, PR, past delivery,
occupational authority. **A project with none of them still has the bottom rung — the story**,
in three parts: you had the problem, you searched and each attempt failed, and here is what you
committed. It does not prove delivery; it makes you a person with something at stake.

**It goes last, after someone already wants the thing** — and the same finding says **do not
open on your own face**: *"you are not at first the most enticing thing about your project."*
Step 6's *put a face on it* is right about the founder segment and silent about its position;
the position is the end.

**Where it goes is an open conflict, not a solved one.** The Ask segment is 10–15 seconds and
a three-part story does not fit in it — so the story either takes ~20s from **Solution**, or
the turn video runs longer than 90s, or the story is cut to one sentence. The sources do not
settle this: they say *last*, and they were describing campaign pages and longer videos, not a
90-second cut.

The reading recorded here: **at 90 seconds, one sentence at the top of the Ask** — *I had this
problem, I tried X, here is what I committed* — and the full three-part version belongs on the
page and in full mode's script, which has room for it. That is a judgement, not a finding, and
the falsifier is a turn that reads the one-sentence version to no effect while a longer cut
lands.

### Step 4b — render the audio, and listen to it

**Moved, because it is shared.** The gauge render is not a turn-mode step — it is how *any*
script gets its length measured and heard, in both rendering modes — so it lives with the rest
of production: [`production.md`](production.md#step-4b--render-the-audio-and-listen-to-it).
Run it here, before the back-check, and before anything is cut to length.

### Back-check against the ledger

Every claim the script makes appears in `claims.md`. Move anything that does not survive.
List the claim ids in the round record.

**Do it sentence by sentence, in both directions, with the ledger open** — write each spoken
sentence next to the row it needs, then read the claim list against the table. A final glance
is not this check: the first run's list was wrong in both directions at once (three ids the
script never says, three sayings with no id, one claim with no row), and the mechanical half
of [gate 6](../SKILL.md#part-4-gates) passed cleanly the whole time.

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

**A turn needs a close, not only a threshold.** Funding is U-shaped — an opening spike, a
dead middle, a closing spike — and **an open-ended ask has no closing spike because there is
nothing to remind anyone about.** Reward campaigns run ~30 days. Write the close date into the
round record with the threshold, and treat the final reminder as a planned step rather than an
afterthought.

**The measurement threshold and a funding threshold are different objects.** `threshold:`
above is the *experiment* — does the artifact hold attention. A minimum-goal-or-refund is a
*funding* rule, and its logic only holds under all-or-nothing: a round that keeps whatever it
raises inverts the incentive the minimum was there to create. Decide which this round is and
say so; do not let the two words share a field.

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
