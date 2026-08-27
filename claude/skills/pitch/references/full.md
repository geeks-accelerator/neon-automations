# full mode

> Part of the [`pitch`](../SKILL.md) skill. The operating core — the four tags, the
> citation rule, the two numbers, the ledger invariant — and the
> [gates](../SKILL.md#part-4-gates) are in [`SKILL.md`](../SKILL.md), and they apply
> here. This file is the procedure.

Produces `docs/pitch/` — the standing pitch, rebuilt when a trigger fires. Read
[`production.md`](production.md) for Phase 11's rendering, which both rendering modes share.

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

**And it recurred, so the check is now mechanical.** `scans.py` walks every `current` scan and
reports what outside `docs/research/` actually names it:

```bash
python3 .claude/skills/pitch/scripts/scans.py --docs docs
```

Two rules in it were each found by getting them wrong first.

- **A scan's own `Cited by:` line is not evidence.** It is a hand-maintained backlink and it
  drifts in both directions — on the tree this was written against, three scans with real
  consumers carried no backlink at all. Read the tree, not the claim about the tree.
- **A sibling scan is not a consumer.** Scans cross-reference each other, so a batch published
  together cites itself into apparent coverage. Three scans landed on 2026-08-24 citing only
  each other, and a backlink check called them consumed. The question is whether research
  reaches the *pitch*; a citation that never leaves `docs/research/` has not.

An uncited scan is **not an error** — a project may research what it has not pitched. Not
knowing is the error. Answer each one: cite it, or write the *not applicable, because …* line
in the index.

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

### Step 1 has a plural form, and it is the one that survives disagreement

Naming the three riskiest assumptions asks what is shakiest about **the pitch you already
wrote**. When more than one pitch is genuinely available — a different buyer, a different
thing sold, a different scope — that question arrives too late, because the choice has already
been made by whoever drafted first.

**So when several pitches are live, write the possibilities down before judging any of them,
and for each one ask what would have to be true for it to be the *best* choice.** One row per
possibility, in `riskiest-assumptions.md`, and **no row may be argued against until every row
is written** — that ordering is the whole mechanism, and it is the first thing dropped under
time pressure.

| possibility | who is buying | what would have to be true | weakest condition | evidence |
|---|---|---|---|---|
| … | … | three or four conditions, each falsifiable | the one to test first | a tag and a citation |

The riskiest three then fall out of the table rather than being nominated: they are the
weakest load-bearing conditions across the possibilities still standing.

**Tag conditions with the same four tags, and do not put them in the ledger yet.** A condition
is not a new kind of object, so it gets no fifth tag and no private vocabulary — but it is also
not something the pitch says, and `claims.md` holds what the pitch says. A condition enters the
ledger only when the script actually makes it, and it arrives carrying the tag it already had.
The ledger invariant has no exception here and does not need one.

**Why phrase it as a condition rather than an opinion.** *"Enterprise is the real business"*
puts a person behind a position, and every later discussion becomes evidence-gathering for
whoever said it loudest. *"For enterprise to be the best choice, audit value would have to
exceed retention liability"* puts a measurable condition on the table that nobody owns. When
it fails, nothing has to be conceded — the condition simply did not hold. That is the point of
the form, not a side effect of it.

**And the question does not close when the choice is made.** The conditions behind the chosen
possibility keep being asked — *are they still true?* — which is the same object as a demoted
claim: true when relied on, unverified now. Put them in the staleness report with the ledger,
not in a separate list that nothing re-checks.

**One possibility is always "do nothing different"**, for the same reason Phases 3–5 say doing
nothing is usually the real competitor. A table without it is a menu, not a comparison.

> **This is `WWHTBT`, and it is imported, not derived from a run here.** Attribution and
> mechanics were checked; the claim that it depersonalises disagreement in practice was not,
> and is `ASSERTED`. See
> [the framework scan](https://github.com/geeks-accelerator/code-neon/blob/main/docs/research/2026-08-27-venture-planning-frameworks.md).
> Skip the table when only one pitch is available — a single-row possibilities table is
> ceremony, and step 1 alone is the right instrument there.

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

    **Render the narration here too** —
    [Step 4b](production.md#step-4b--render-the-audio-and-listen-to-it)
    is not a turn-mode step, it is how any
    script gets its length measured and heard (Step 4b). Full mode needs it *more*, because
    Phase 3.5 is mandatory and reading a script aloud to five people without having heard it
    once wastes the only sample that can falsify the pitch.

    **Full mode carries its own cost line, and it is not the turn's.** Narration bills about a
    credit per character, and roughly a thousand characters is a minute of speech:

    | | ~2-min turn script | ~10-min full script |
    |---|---|---|
    | characters | ~1,300 | **~10,000** |
    | measured seconds | **80.9** *(242 words, ~179 wpm)* | **570.0** *(1,568 words, ~165 wpm)* |
    | credits per render | ~1,300 | **~10,000** |
    | renders in a 30,000-credit Starter month | ~23 | **3** |
    | renders in a 100,000-credit Creator month | ~76 | **10** |

    **The rate is not a constant with a better value.** The same voice read the round script
    at 179 wpm and the long form at 165 — it depends on the prose as well as the speaker, so
    150 wpm was wrong by 20% in one direction and 10% in the other. Render, then publish what
    it measured.

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

    Slides, narration, captions and assembly follow
    [Step 6](production.md#step-6--produce), which both modes share. At ten minutes expect ~30–40 slides rather than the 10–15 a self-paced deck
    carries — a ten-minute narration over fifteen stills leaves each one on screen for forty
    seconds, which is longer than an image holds attention.

12. **Assembly**: the index, the two numbers, the staleness report — then an **arithmetic
    pass** over the whole tree: re-sum every stated total against its own itemization, re-count
    every enumerated tally against its own list, and re-derive every number that appears in
    more than one file, once, at the end. The first run shipped "six of eight" over a list of
    five and a "thirty dollar" ask over an itemization summing to 31 — in a pitch whose premise
    is that the cost is a receipt. And expect the fixed point to fire: adding the row that
    records a numeric disagreement changes the ratio the index reports.

    **Then the coverage pass, which is the arithmetic pass's mirror.** The arithmetic pass
    asks whether every number the pitch states is supported. This asks the reverse: whether
    every scan the tree holds reached the pitch. Run `scans.py`, and for each scan it names,
    either cite it or record why it does not apply. Both passes exist because the tree can be
    internally consistent and still be wrong about the world it was built from.

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

**Demoting a claim is not finished until the prose that states it moves too.** A count also
appears in `scan.md` and `what-exists-now.md`, and *those* copies are narrative — outside the
ledger, so nothing re-checks them. Demote `C-003` three times and the ledger walks away from
two documents still asserting the first value as current fact.

Observed: live-neon on 2026-08-24 carried three live values for one measurement — narratives
at 27 markdown, `C-003` at 140 after two demotions, and `git ls-files` at 147. So on every
demotion of a counting claim, **grep the narrative documents for the old value before writing
the report**, and re-extract each one that still states it. The arithmetic-discipline rule
above already says numbers in prose are claims; this is the step that acts on it.
