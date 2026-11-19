# 01 — Introduction (draft, new pass)

Venue format (PLOS Computational Biology Review, see `VENUE.md`): abstract, then
introduction. Budget: ≈250 words abstract, ≈600 words introduction.

## Abstract

Proteins and peptides that bind a chosen target protein underpin much of modern
medicine and laboratory practice, yet they have mostly been found by screening
rather than designed: immunization, or display libraries of a trillion or more
random sequences, one campaign per target, returning whatever the library
happened to contain. Structure prediction changed what can be proposed.
AlphaFold2 resolved a fifty-year-old question at CASP14, and AlphaFold3 extended
the result to arbitrary complexes, so predicting how a sequence folds against a
target became a routine substrate. The open problem moved to design: inventing a
protein or peptide sequence that binds a named site on a named target. This
review surveys the deep-learning systems that now do this. It organizes them by
how tightly the sequence generator is coupled to the structure predictor that
judges its output: generators fine-tuned from a predictor, pipelines that
generate and then filter, and loops that backpropagate the predictor's error
into the sequence itself. It follows each open predictor lineage — AlphaFold,
RoseTTAFold and RFdiffusion, Boltz, Chai, Protenix and ESM — from prediction to
the designs built on it, and treats the closed systems as evidence about the
field's evidence. Across these systems, the number of designs that must be
physically synthesized before one binds has fallen from thousands or millions to
tens, though every campaign chose its own targets and its own definition of a
hit, and the strongest reported results come from systems that publish
benchmarks but not mechanisms. Five gaps remain: nothing optimizes past binding,
protein–protein affinity is not predicted, design against targets without
experimental structures is untested, no two campaigns share a benchmark, and
confidence filters do not discriminate on individual designs.

## Introduction

Blocking, detecting, tagging or drugging a protein each requires a second
molecule that binds it, and for a protein target that molecule is usually itself
a protein or a peptide: an antibody, a nanobody, a minibinder, a macrocyclic
peptide. Molecules of this class carry a large share of modern therapeutics and
of the reagents a working laboratory runs on.

Until recently, obtaining one meant searching rather than designing. Immunize an
animal, or screen a library of a trillion or more random sequences by display
and keep whatever sticks. Both routes work, and both still dominate. They also
commit a wet laboratory from the first step, run once per target, and return
whatever the library happened to contain rather than a molecule proposed on
purpose.

What changed is that structure prediction stopped being the open problem. At
CASP14 in 2020, AlphaFold2 answered a question that had stood open for fifty
years: what structure a given sequence folds into. AlphaFold3 then carried the
result from single chains to arbitrary complexes of proteins, nucleic acids,
ligands and ions. Prediction became a substrate that other work builds on, and
attention moved from folding to binding.

Designing a binder is not the same problem as predicting a structure. A
predictor is handed a known sequence and asked what it folds into, and a solved
experimental structure can say whether the answer was right. A generator is
handed a target and asked to invent a sequence that does something chosen, and
nothing short of a wet laboratory says whether it did. That the two problems
turn out to run on the same machinery is a finding this review arrives at, not a
premise it starts from.

The last two years are an explosion. Several predictor lineages have been
reimplemented openly, design systems have been stacked on every one of them, and
results are published faster than anyone compares them. The models are also run:
commercial providers shipped optimized inference kernels for most of these
systems within a single week of September 2026, reporting two- to fourfold
throughput gains.

The problem this review addresses is one: given a target protein, design a new
protein or peptide that binds it. Antibodies, nanobodies, minibinders and
macrocyclic peptides are treated as a single object, because to every model
surveyed here they are the same thing: a chain of amino acids judged by how it
folds against the target. Small molecules are the other half of binder discovery
and are out of scope. A small molecule is a variable-size graph under hard
valence rules, not a chain drawn from a fixed alphabet of twenty, so generating
one takes different machinery and is judged on different benchmarks.

The main text first explains what a co-folding model is, why prediction and
generation run on one machinery, and how tightly a generator can be coupled to
its critic. It then follows the open lineages, from each predictor to the
designs built on it, and closes on the systems that publish results without
mechanisms and on what the field has not yet shown. One number threads all of
it: how many designs must be physically made before one binds. Screening-era
campaigns needed thousands to millions of candidates per target; current systems
report tens. The measure of progress in this field is how few designs are needed
to get a binder.
