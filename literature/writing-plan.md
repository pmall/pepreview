# Writing plan and method

> **SUPERSEDED 2026-11-19 — kept for history, do not follow.** The single
> binding instruction for the prose phase is now `WRITING.md`, which folds in
> the still-binding rules from this file (weight and tier treatment, the four
> moves of a section, placement directives, assembly, xrefs usage). The "Draft
> units" and "Relative weight" tables below and the "no word count" line are
> obsolete: draft units and budgets live in `WRITING.md` and are venue-driven
> (`VENUE.md`, PLOS Computational Biology Review).

> How the review gets written: what the draft units are, how big each one is,
> what shape a section takes, and in what order they are drafted.
>
> `literature/map.md` holds the content: every publication, every fact, every
> claim, structured in reading order — the review minus its prose. This file
> holds everything addressed to whoever writes that prose: sizes, drafting
> order, section shape, and the placement directives below. Neither restates the
> other. **No instruction to the writer belongs in the map.**

## Target

**A review of 49 references, not an exhaustive survey.** There is no word count,
here or anywhere. A draft is as long as what it carries requires; the relative
weights below are the only size constraint, and a section is too long when it
spends prose on material its tier does not warrant, never because it passed a
count.

**Tables A and B are display items**, not main text. Only the paragraph between
them is prose.

______________________________________________________________________

## Weight — the rule that governs every other rule here

A review is read for its **proportions** before it is read for its sentences. A
reader who knows this field arrives with a rough map of what matters in it, and
the fastest way to lose them is to spend three paragraphs on a preprint they
have not heard of and one clause on AlphaFold. The tier system exists to prevent
exactly that, and this section is where it becomes an instruction to the writer.

**Tier determines treatment. It is not a hint.**

| Tier         | Treatment in the prose                                                                               | Test the draft must pass                                                                |
| ------------ | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **backbone** | A passage of its own: mechanism, the numbers that matter, the caveat, and what it is contrasted with | A reader could explain what this system does and why it mattered, from the review alone |
| **meat**     | Named in a sentence or two while a backbone claim is being made; its numbers may be quoted           | Removing it weakens a claim's evidence; it does not leave a hole in the narrative       |
| **mention**  | A clause, or a parenthetical. No mechanism, no numbers in the prose — numbers go to Table A or B     | It can be read past without loss                                                        |

**Nineteen publications carry the review.** They are the backbone set, and they
are the ones a reader should come away able to name:

| Section | Gets a passage                                                    |
| ------- | ----------------------------------------------------------------- |
| §1      | AlphaFold2 · AlphaFold-Multimer · AlphaFold3                      |
| §2      | RoseTTAFold · RFdiffusion · RFantibody · RFpeptides · ProteinMPNN |
| §3      | Boltz-1 · BoltzGen · BoltzProt-1                                  |
| §4      | Chai-2                                                            |
| §5      | BindCraft · Germinal                                              |
| §6      | PXDesign                                                          |
| §7      | ESM-2/ESMFold · ESMC/ESMFold2 · the ESMFold2 binder campaign      |
| §8      | Latent-X1                                                         |
| Primer  | PoseBusters · ipSAE                                               |
| Tables  | FoldBench                                                         |

Everything else in `map.md` — roughly thirty further works — appears in support
of a claim or not at all. **That is not a demotion**; the invariant that every
named publication resolves to a catalog entry is about the catalog's honesty,
not about the prose owing each one a turn.

**Three failure modes, in the order they actually happen.**

1. **The recency inversion.** Recent preprints have long, specific, quotable
   entries because they were read most recently and argue with each other in
   detail. Mastodonts have short entries because their content is assumed. A
   draft written by following entry length will invert the field's weight.
   _Check:_ if a 2026 preprint gets more prose than AlphaFold2, RFdiffusion or
   ProteinMPNN, the draft is wrong regardless of how interesting the preprint
   is.
1. **The interesting-detail trap.** A small paper with an unusual result is more
   fun to write about than a foundational one whose result everybody knows.
   Interest is not weight. A finding earns prose in proportion to what rests on
   it, and `map.md` states what rests on each entry under _Carries_.
1. **Cataloguing under the guise of completeness.** Listing five flow-matching
   papers because the corpus holds five. The background's flow-matching bullet
   says what to do instead: one formalism explained, four named in support.

**Where the map over-supplies, cut rather than expand.** Some entries carry more
material than their tier warrants, because the underlying paper is recent and
detailed. The map records what is true; this file decides what is written. When
the two disagree, tier wins.

## Draft units

Two layers: **drafts**, one per map heading, and the **parts** they collapse
into. A draft is written from one heading and the corpus behind it; a part is
the merge, and merging writes seams and one voice, never a rewrite of a draft.
The background is written a beat at a time — four of them — because the beats
have different sources and merging is where they are made to read as one. The
introduction is a single draft: it opens the review and has one voice from the
start. The three benchmarking units are three drafts rather than one because
they have different sources, timing and positions in the final text. Excluded
works are not a draft unit — they are a record in `candidates.md`, not a part of
the review.

| #   | Draft                                        | File                           | Source                                                  |
| --- | -------------------------------------------- | ------------------------------ | ------------------------------------------------------- |
| 1   | Introduction                                 | `drafts/00-introduction.md`    | The introduction                                        |
| 2   | The founding bet                             | `drafts/01-anatomy.md`         | The anatomy beat                                        |
| 3   | Prediction and generation are one machine    | `drafts/02-identity.md`        | The identity beat                                       |
| 4   | Generator–critic coupling                    | `drafts/03-coupling.md`        | The coupling beat                                       |
| 5   | The disclosure limit                         | `drafts/04-frontier.md`        | The disclosure beat                                     |
| 6   | Metrics primer                               | `drafts/05-metrics-primer.md`  | The metrics primer                                      |
| 7   | §1 AlphaFold and the open co-folding cluster | `drafts/06-alphafold.md`       | §1                                                      |
| 8   | §2 RoseTTAFold → RFdiffusion                 | `drafts/07-rosettafold.md`     | §2                                                      |
| 9   | §3 Boltz                                     | `drafts/08-boltz.md`           | §3                                                      |
| 10  | §4 Chai                                      | `drafts/09-chai.md`            | §4                                                      |
| 11  | §5 Design by backpropagation                 | `drafts/10-inversion.md`       | §5                                                      |
| 12  | §6 Protenix                                  | `drafts/11-protenix.md`        | §6                                                      |
| 13  | §7 ESM                                       | `drafts/12-esm.md`             | §7                                                      |
| 14  | §8 The closed frontier                       | `drafts/13-closed-frontier.md` | §8                                                      |
| 15  | Tables A and B                               | `drafts/14-tables.md`          | Tables A and B — written after §1–§8                    |
| 16  | Conclusion                                   | `drafts/15-conclusion.md`      | The conclusion, gaps subsection included — written last |

The parts they collapse into:

| Part               | File                         | Merges                                                       |
| ------------------ | ---------------------------- | ------------------------------------------------------------ |
| Background         | `drafts/parts/background.md` | drafts 2–5, plus the ordering paragraph that closes the unit |
| The eight sections | `drafts/parts/sections.md`   | drafts 7–14                                                  |

Drafts 1, 6 and 15–16 stand on their own; the introduction opens the review, the
metrics primer renders between the background and §1, and the rest close it.

**The seams between sections are written from the ordering paragraph** that
closes the background: it supplies the two-axis logic, and each section's own
_Why here_ line supplies the seam into it.

**The conclusion is written last, from the finished parts.** §8 is a coda and
the disclosure beat sets up an ending, but the map states which questions the
conclusion gathers, not what it concludes. Its beats and its ending follow from
the other drafts, so they are decided when those exist rather than planned in
advance.

**Its gaps subsection has a hard rule and it is the map's, not this file's:** a
gap enters only when a publication in the catalog states it. There are five for
that reason, and they are not the place to speculate about what comes next. Two
are limits §1–§8 establish and three rest on Tables A and B, which is why the
subsection cannot be drafted before them.

## Relative weight

**Weight follows backbone count, and the count is in the map.** No percentages:
a share to one decimal place is precision the review does not have, and a table
of them gets maintained instead of the argument.

**The one check worth making.** §2 is the heaviest section and §1 next, because
they carry the most backbones; §5, §6 and §8 are the lightest. If a draft comes
back the other way round, the recency inversion has happened, and the fix is to
cut the recent material rather than argue for it. §1–§8 should come to roughly
two thirds of the review, which is right for a review whose argument is the
section order.

## What a section is

A section is a block of argument. It is **not** a list of publications with
commentary on each. Publications appear inside the prose, supporting claims;
they are not headings and they do not each get a turn.

**Its backbones are its subjects; everything else is evidence.** A section with
three backbones has three things to explain properly and a supporting cast.
Prose spent on the cast is prose taken from the subjects — that is the trade,
and it is always the wrong way round when a _mention_ has a sentence to itself.

**Read the entry schema before drafting a section.** `map.md`'s header defines
it: each entry's _Carries_ line is the claim that must survive into the prose,
_Against_ is the comparison the passage should be built around, _Caveat_ travels
with the claim wherever it is cited, and _Collision_ says what this section must
not restate. A backbone passage that states what a system _is_ without stating
what it is **against** has described a paper instead of making an argument.

Every section makes the same four moves, in this order. This is what keeps eight
independently drafted sections reading as one review:

1. **The claim.** What this lineage or technique contributed, stated as a
   proposition. Not a preview of what the section will cover.
1. **The mechanism.** What these models actually do — told once for the whole
   section, from the parsed corpus, rather than restarted for each paper.
1. **The evidence.** Benchmarks and wet-lab campaigns, with the caveat that
   applies to them.
1. **The handoff.** Where the section sits on the coupling spine, and the seam
   into the next section.

**A section draft that could have been written from the map alone has failed.**
The map's own header says what it refuses to hold: _"Method internals, benchmark
numbers, per-paper caveats and quotes are read out of the corpus at writing
time."_ That material is exactly what a section draft is made of, and it comes
from `literature/corpus/`, not from the map entry.

**Collisions are already assigned by the map.** Each draft opens with three
lines — owns / references / must not restate — copied from the map, not
reinvented. The standing assignments: ipTM and pAE definitions to the primer,
ProteinMPNN to §2, AtomWorks to §2 in one line, the trained-critic result to §3,
BoltzDesign1's analysis to §5, mBER's unchosen-targets argument to the identity
beat, the physical-validity thread to §6 and all benchmark caveats to Table A,
and the disclosure argument to §8.

## Using xrefs

`literature/xrefs.md` answers one question: which paper to read when writing
about another. BoltzProt-1 names BoltzGen 57 times — that is §3's central
comparison, and that passage is where the draft's material is. OpenGerminal
names Germinal 45 times, §5's. Latent-X1 names RFdiffusion 50 times, what §8
measures itself against.

A high count means the papers argue with each other; it never means agreement or
benchmarking, which only reading the passage settles. It is not a sizing
instrument, and never sets a tier. Regenerate with
`uv run scripts/build_xrefs.py` before a drafting pass.

## Assembly

Drafts merge into parts, parts into the review. No pass rewrites a draft.

**The eight sections.** §1–4 are ordered by generative formalism, §5–7 by degree
of integration, §8 outside the argument. Assembling them means writing the two
block seams and smoothing the handoffs — not re-editing section bodies.

**The review.** The introduction, the background, then the metrics primer, the
eight sections, the two tables, then the conclusion with its gaps. Scope is
stated in the introduction; the exclusion log stays in `candidates.md` and is
never drafted.

## Placement directives

Decisions about _where_ material lands and _how_ it must be handled, so the map
stays content.

| Directive                                                                                                  | Why                                                                                                                                             |
| ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| The metrics primer renders between the background and §1                                                   | §§1–8 quote pAE, pLDDT, ipTM and PB-valid from the start, and the coupling beat has already raised the question the primer answers              |
| The coupling beat quotes the success criterion without unpacking its units                                 | the primer owns the definitions and follows shortly; unpacking them mid-beat stalls the argument                                                |
| The primer is written around the two families of metric, never as an alphabetical glossary                 | a metric list is dead weight the reader skips; the families do the analytical work                                                              |
| The Latent-X1 / RFpeptides head-to-head lands under Table B, not §8                                        | so it reads as evidence about measurement, not a point scored for Latent Labs                                                                   |
| The conclusion's gaps subsection admits only limits a cataloged publication states                         | otherwise it becomes a wish list, which is the genre's standard filler                                                                          |
| Developability and immunogenicity are the gaps subsection's, not §8's                                      | Latent-X2 is the evidence but the point is about the field, not about Latent Labs                                                               |
| §2 opens by separating RF3 (predictor) from RFdiffusion3 (generator)                                       | the names collide; the lineage's two tracks are unreadable otherwise                                                                            |
| The ordering of §1–§8 closes the background, not the introduction                                          | it is stated in the coupling levels' vocabulary, which the coupling beat defines a few paragraphs earlier                                       |
| AtomWorks gets one line, never a passage                                                                   | it is training infrastructure, not a model or an instrument; its role is that RF3 and RFdiffusion3 both come out of it                          |
| Table B is sorted by designs-tested, never by hit rate                                                     | the denominator is the identity beat's argument; hit-rate order makes it a leaderboard                                                          |
| Table B's hit-definition column is mandatory                                                               | BoltzProt-1's screening-hit / confirmed-binder split means the percentages measure different events                                             |
| No cell enters Table A or B without a stated benchmark, cutoff and measurer                                | the provenance columns are the defence against a leaderboard reading                                                                            |
| Benchmark caveats are stated once in Table A's defect column and pointed at, never relitigated per section | three documented defects, one per prediction instrument, plus Overath's own on the design side                                                  |
| The physical-validity thread is stated once, in §6                                                         | four groups assert four answers and only one pair has been measured against the other; per-section retelling implies more agreement than exists |
