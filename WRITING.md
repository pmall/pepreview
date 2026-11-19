# How the review gets written

> Single binding instruction file for the prose phase: the field, the goal and
> register, the test every claim is weighed against, the target venue, the
> budgets, what a section draft is, and the style rules distilled from the
> critique of the first completed pass ("Style: describe, don't prove" at the
> end). `literature/writing-plan.md` is superseded and kept for history only;
> `VENUE.md` holds the target venue's extracted author guidelines.

## The field

Deep-learning models that predict protein structure and design proteins or
peptides binding a target protein — the co-folding predictors and the design
systems built on them.

**In scope** = generates a protein or peptide sequence — peptide, minibinder,
macrocycle, nanobody, antibody, any chain from the 20-letter amino-acid alphabet
— that binds a named target, or predicts the structure such a system designs
against. **Out of scope** = the small-molecule modality: a ligand is a
variable-size graph under hard valence rules, not a chain from a fixed alphabet,
so it takes different machinery and different benchmarks. Also out: sequence
generation with no target conditioning. The field moves fast — explosive in 2026
— so references dated before 2025 are generally out of scope, except where they
belong to an active lineage whose full history is kept for understanding (ESM,
RoseTTAFold).

## The goal

Show a curious newcomer that landscape and give them the keys to understand it.
The review is not a record of isolated claims, and not a log of disputes between
approaches and lineages.

## Target venue

**PLOS Computational Biology, article type Review** — extracted author
guidelines in `VENUE.md` (checked 2026-11-19). The operative constraints: main
text 3,000–6,000 words; two or three display items; structure Title / Abstract /
Introduction / Main Text (at most three heading levels) / Conclusions /
Acknowledgments / References; references numbered in order of appearance, cited
in square brackets; AI assistance disclosed at submission. The venue asks a
Review for "a critique with new points of view" — the review's point of view is
the coupling-level taxonomy of generator–critic architectures plus the
disclosure limit on the field's evidence; the families-and-concepts exposition
is the vehicle that carries it, not a summary of the field.

## The register

**The review explains principles and documents what has been published. It has
nothing to prove.** There is no thesis, no case against anyone, and no verdict
to reach about a lab, a paper or a lineage.

Commentary is allowed, and it is commentary: it helps a reader read what is in
front of them. The line is simple — **state the conditions a number was measured
under, never grade the people who measured it.** That a benchmark counts 172
targets, that one paper averages per sequence cluster and another per interface,
that a hit threshold was 0.1 nm, that 15 designs were tested per target: all of
this is information a reader needs to interpret a figure, and it is stated
flatly. That a paper overclaims, that a literature is unaccountable, that one
group did the more disciplined experiment: none of this belongs anywhere in the
review.

The recurring failure here is **inventing a point to argue and then building a
unit to win it** — most often by assembling real facts into an indictment no
source makes. Facts stay facts. If a passage reads as prosecution, it is wrong
in register even when every number in it is correct.

## The test

Weigh every claim against the weight of presenting AlphaFold, RoseTTAFold,
ESMFold and how their approaches differ. Minuscule beside that means cut, or one
line. Being legitimate and well-evidenced earns nothing on its own.

The recurring failure is clinging to a detail that is true, interesting and far
too light for this review.

## What follows from it

- **A unit's size matches its job.** The metrics primer explains vocabulary, so
  it gets vocabulary-sized space, not a thesis.
- **Definitions sit beside the thing defined**, never in a section about
  definitions. Such a section invites missing the obvious members and drifts
  into argument.
- **Weak points and disputes go to the discussion**, where they compete with the
  other gaps. That placement is the filter: a theme that cannot hold its own
  there was never heavy enough to carry through the review.
- **A unit arguing for its own existence is already too big.**

## What is being written

**One continuous review article, drafted one section at a time.** Thirteen
drafts, one per `#` heading in `literature/map.md`, in reading order, written
into `literature/drafts/NN-slug.md`:

| #   | Draft                   | Map unit                                    | Prose words |
| --- | ----------------------- | ------------------------------------------- | ----------: |
| 01  | `01-introduction.md`    | The introduction (+ ~250-word abstract)     |         600 |
| 02  | `02-background.md`      | Background, four beats                      |       1,100 |
| 03  | `03-metrics-primer.md`  | The metrics primer — vocabulary source only |         250 |
| 04  | `04-alphafold.md`       | §1 AlphaFold and the open cluster           |         550 |
| 05  | `05-rosettafold.md`     | §2 RoseTTAFold → RFdiffusion                |         750 |
| 06  | `06-boltz.md`           | §3 Boltz                                    |         500 |
| 07  | `07-chai.md`            | §4 Chai                                     |         200 |
| 08  | `08-backpropagation.md` | §5 Design by backpropagation                |         400 |
| 09  | `09-protenix.md`        | §6 Protenix                                 |         350 |
| 10  | `10-esm.md`             | §7 ESM                                      |         450 |
| 11  | `11-closed-frontier.md` | §8 The closed frontier                      |         150 |
| 12  | `12-the-numbers.md`     | The numbers — 2–3 display items, not prose  |           0 |
| 13  | `13-conclusion.md`      | The conclusion                              |         450 |

Completed passes are archived in subfolders of `literature/drafts/`, named for
the attempt (`drafts/first-try/`); a new pass writes to the paths above.

**The budget is set before writing, never after.** It is venue-driven:
`VENUE.md` targets a PLOS Computational Biology Review — 3,000–6,000 words of
main text and two or three display items — so the units above sum to ≈5,750
words of main text plus an abstract of ≈250 drafted with unit 01. §1–§8 carry
≈3,750 words (two thirds of the main text), weighted by backbone count, with a
floor of 150 for a coda to make its move at all; the numbers unit spends its
budget on display items, not prose. A draft written to length reads; a long
draft cut to length does not, because cutting removes connective prose and
leaves the facts, which is the wrong half.

**Display items do not count.** Their conditions belong in columns, not in
sentences.

**A number in the budget is a target, not a ceiling to fill.** A section that
says what it has to say in less is finished.

## Weight, section shape, and placement

Folded in from `literature/writing-plan.md` (now superseded); the plan's "Draft
units" table and its "no word count" line are the parts that died — budgets and
units live here and are venue-driven.

**Tier determines treatment, and the map's tier wins over entry length.**
**backbone** → a passage of its own: mechanism, the numbers that matter, the
caveat, what it is contrasted with. **meat** → a sentence or two while a
backbone claim is being made; its numbers may be quoted. **mention** → a clause,
readable past without loss. Three failure modes, in the order they happen: the
recency inversion (a 2026 preprint out-prosed against AlphaFold2), the
interesting-detail trap, and cataloguing under the guise of completeness. Where
the map over-supplies, cut rather than expand.

**Every section makes the same four moves, in order:** the claim (what this
lineage or technique contributed, as a proposition); the mechanism (told once
per section, from the parsed corpus); the evidence (benchmarks and wet-lab
campaigns, with the caveat that applies); the handoff (where the section sits on
the coupling spine, and the seam into the next). A backbone passage that says
what a system is without what it is **against** has described a paper, not made
the argument.

**Placement directives** (standing assignments):

- Metric definitions ship beside the thing defined at first use; the primer
  draft is the vocabulary source, not a rendered section.
- The Latent-X1 / RFpeptides head-to-head lands under the numbers unit, not §8.
- The conclusion's gaps admit only limits a cataloged publication states.
- Developability and immunogenicity belong to the conclusion, not §8.
- §2 opens by separating RF3 (predictor) from RFdiffusion3 (generator).
- Display-item cells carry benchmark, cutoff and measurer, or they do not enter;
  the campaigns table is ordered by designs tested, never by hit rate, and its
  hit-definition column is mandatory.
- Benchmark caveats are stated once in the display items' scope note and pointed
  at, never relitigated per section; the physical-validity thread is stated
  once, in §6.
- ProteinMPNN is owned by §2; the trained-critic result by §3; BoltzDesign1's
  analysis by §5; mBER's unchosen-targets argument by the identity beat.

**`xrefs.md` answers one question only:** which paper to read when writing about
another. It never sizes anything and never sets a tier.

**Assembly:** introduction → background → §1–§8 → display items → conclusion.
Seams are written from the ordering paragraph that closes the background and
each unit's own _Why here_ line; no pass rewrites a draft body.

## A section is prose in one article

The reader arrives having just read the previous section and will read the next
one. Write for that reader.

- **No preamble.** No owns / references / must-not-restate block, no statement
  of scope, no note on provenance. That is process residue: it serves the writer
  and the assembly pass, and a reader skips it. Collisions are resolved by *not
  writing* the material, which needs no annotation.
- **No invented headings.** A `##` beat in `map.md` is layout for the map. A
  section gets its title and nothing else unless the map's unit is long enough
  that the final article will carry subheads — the background and §2 are the
  only candidates. Never head a paragraph "What was measured" or "The AF2 pole".
- **No section throat-clearing.** Not "this section covers", not "So:", not a
  closing paragraph that summarizes the section to the reader who just read it.
  The handoff is a clause, usually the last one.
- **No per-section recap of shared material.** The co-folding architecture, the
  coupling vocabulary and the metric definitions are each explained once, in the
  unit that owns them. Later sections use them as known.

## Numbers

**The exhibits carry the figures. The prose carries the argument.**

- Quote a figure in prose only when the sentence is *about* that figure — the
  result a backbone claim rests on, or a comparison the section is built around.
  Two or three per section is normal.
- A figure that stays in prose keeps the conditions that make it readable:
  benchmark, subset, denominator, measurer, hit definition, cutoff. If it will
  not fit with them, it goes to the exhibit and the prose points there.
- Never write a paragraph that is a sequence of measurements. If a passage reads
  as a results table in sentences, its figures belong in an exhibit.
- A figure that exists only inside an unparseable image is recorded as
  unavailable. It is never approximated, and never reconstructed from a
  neighbouring number.

## Where the material comes from

- **`literature/map.md` says what the review asserts.** It is the content and
  the structure: the claim under _Carries_, the comparison under _Against_, the
  limit under _Caveat_, the material to leave alone under _Collision_.
- **`literature/corpus/` says what proves it.** Mechanism, quotes, conditions
  and caveats are read out of the parsed paper at writing time. Resolve a bib
  key to its DOI in `literature/refs.bib`; the corpus file is the DOI with `/`
  written `__`.
- **A draft that could have been written from the map alone has failed.**
- **`literature/xrefs.md` answers one question only:** which paper to read when
  writing about another. It never sizes anything and never sets a tier.

## Verification

Every claim is checked against the parsed source before it is written. Claims
taken from the map are provisional until confirmed, and they fail most often in
the details a review depends on — what a metric measures, what a method identity
is, what a denominator counts, whether a difference was significant.

Where the map and the paper disagree, **the paper wins and the prose is written
correctly.** The writer does not edit `map.md`, `refs.bib` or `candidates.md`:
corrections are reported and applied outside the writing pass, so that parallel
writers never contend for those files.

## Formatting

Never hand-wrap. After editing any `.md`, run
`uv run mdformat --wrap 80 <files>`. Formatter output is never a review finding.

## How this phase fails

Observed, not hypothetical:

1. **No budget set up front**, so thirteen writers each size their own section
   and the review comes out three times over.
1. **A long draft cut to length**, which keeps the facts and drops the prose
   that made them mean something.
1. **Scaffolding in the prose** — preambles, invented subheads, per-section
   openings and closings — so thirteen sections read as thirteen documents
   rather than one article.
1. **Condition inventories**: every figure kept with every condition attached,
   until a paragraph is a methods section.
1. **The recency inversion**: a 2026 preprint outweighing AlphaFold2 or
   RFdiffusion because its map entry is longer. Where the map over-supplies, cut
   rather than expand. Tier wins over entry length.

## Style: describe, don't prove

Distilled from the critique of the first completed pass. The facts, the
structure and the verification were right; the surface was not. Five rules and
the observed failures they fix.

### 1. No references to the review's own chapters

A sentence states its fact. It does not point at where another section stores
that fact. The reader of a review article does not know what "§5" is, and does
not want to be told "§6 makes the levels" or "the argument §2 makes" or "the
identity beat's". A display item in the same section may be referenced normally
("Exhibit 3 reports…"); another chapter may never be.

Observed in the first pass, all to be rewritten as statements:

- "what §2–§8 do is reproduce it openly, vary the attachment point — the
  property §5 depends on entirely"
- "the design systems of §5 do not invert" → name the systems (BindCraft,
  Germinal, …) and state what they do not do.
- "the MSA-depth dependence is the same as AlphaFold-Multimer's, the dependence
  §7 removes" → state the mechanism of the removal; the section number adds
  nothing.
- "Every co-folder is two stages … — the anatomy the rest of the review reads
  through" → meta-commentary about the review, delete.

If a statement feels true but only as a pointer to somewhere else, the content
is missing here: write the content or cut the sentence.

### 2. An em dash marks a badly structured sentence

The first pass used an em dash roughly every six sentences (44 alone in the
background). The dash is not a punctuation preference to swap out; it is a
symptom. A writer reaches for one when the sentence carries more ideas than its
structure can hold, and the dash papers over the overload.

- **Do not repair a dashed sentence by replacing the dash.** A comma, a colon or
  a parenthesis in the dash's place keeps the very problem the dash exposed: a
  sentence whose structure cannot hold its ideas. Punctuation substitution is
  cosmetic; the sentence still fails on one read.
- **Repair it by restructuring.** Decide the sentence's one idea, put subject
  and verb on it, and move the remainder into neighbouring sentences. A
  correctly built sentence needs no dash to be readable in the first place.

Before (from the background's opening, dashed):

> Design needed prediction first, and prediction was solved on a single wager:
> that coevolution between two positions in a multiple sequence alignment is a
> usable proxy for the two residues being close in space. AlphaFold2 cashed it —
> median 0.96 Å backbone accuracy on CASP14, against 2.8 Å for the next best
> method — and AlphaFold3 carried the result to arbitrary complexes.

After (restructured, not repunctuated):

> Prediction had to come first, and prediction succeeded on a stated assumption:
> coevolution between two positions in a multiple sequence alignment is a usable
> proxy for two residues being close in space. The assumption held. AlphaFold2
> reached a median backbone accuracy of 0.96 Å on CASP14, and the next best
> method reached 2.8 Å. AlphaFold3 later carried the result to arbitrary
> complexes.

The dashes disappear because the ideas have separated. Replacing them with
commas would have kept one overloaded sentence: a fourteen-word subject, a
nine-word tail and two interpolated figures still competing for the same clause.
The bad structure survives any punctuation.

### 3. Describe; do not argue

The review describes what was published. Sentences that stage a contest, or
score one, are wrong even when their facts are right. Banned moves, all observed
in the first pass:

- **Aphorisms**: "Nobody spends that on software nobody runs"; "the same
  designs, a different judge". State the underlying fact instead: vendors
  published optimized inference kernels; the critic swap moved the rate from
  3.3% to 8.0%.
- **Drama framing**: "the real test comes from the system that filled the loop
  out"; "the diffusion wall gets a third answer". Say what the test was and who
  set it; say the third answer exists and what it does.
- **Pseudo-etymology of stakes**: "cashed the wager", "the bet that made it
  work". Report what the authors assumed and what they achieved.
- **Rhetorical enumeration for rhythm** ("a bet, a wall, an answer…"): the
  reader should never feel the sentence was composed for effect.
- **"Which is why", "that is why", "so" as argument joints.** Give the
  mechanism, or nothing.

### 4. Sentences a scientist can parse on one read

One idea per sentence, normal subject–verb–object order, one level of
subordination. The subject of a scientific sentence is a system, a paper, a
metric or a number; if the subject of a sentence is "the review", "the prose" or
"the reader", the sentence is about the writing, not the field, and should not
exist.

- **No stacked clauses.** If a sentence holds two em dashes, a colon and a
  parenthesis, it is three sentences.
- **Define at first use, then use.** The same quantity must be named the same
  way every time ("DockQ success rate" does not become "interface recovery
  success" three sentences later).
- **Plain verbs over picturesque ones**: not "cashes", "lands", "carries the
  wall", "collapses the budget"; say "achieves", "reports", "reduces",
  "introduces".

### 5. Nothing stolen from the register's shadow

The register forbids grading people; the first pass smuggled judgment in by
grading artifacts ("the corpus's most direct statement that the screen has been
removed", "the claim RFantibody does not make"). A comparison between two
published statements is a fact and may be stated: "RFantibody reports design
success rates without the assay it depends on; Chai-2 ran the assay and reports
the result." One clause of context, no verdict.
