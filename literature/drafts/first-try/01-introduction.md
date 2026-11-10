# The introduction

Binders are how biology is acted on. Blocking a protein, detecting it, tagging
it, drugging it — each of these means having a second molecule that binds the
first, and for a protein target that second molecule is usually itself a protein
or a peptide: an antibody, a nanobody, a minibinder, a macrocyclic peptide. Such
molecules carry a large share of modern medicine. By 2022, monoclonal antibodies
accounted for more than half of all biopharmaceutical approvals in the United
States and Europe, up from about 20% two decades earlier. They and their
fragments also fill the racks of reagents a working biologist runs on.

Getting one has meant searching rather than designing. Immunize an animal, or
screen huge libraries of random or semi-random sequences by display and keep
whatever sticks: that is still how most binders are found. It also commits a wet
lab from the first step, runs once per target, and returns whatever the library
happened to contain rather than a molecule proposed on purpose. The route has no
way of being aimed except through what was stocked into it. The ambition behind
everything in this review is to propose instead: candidates for a named target,
computed, in whatever number the designer chooses.

What changed is that structure prediction stopped being the open problem. At
CASP14 in 2020, AlphaFold2 answered a question that had stood open for more than
fifty years — what structure a sequence folds into — and AlphaFold3 then carried
the result from single chains to complexes containing nearly all of the
molecular types in the Protein Data Bank, ligands, nucleic acids and ions among
them. Prediction is now built on rather than argued over, and the field's
attention moved from folding to binding.

Designing a binder is not the same problem as predicting a structure. A
predictor is handed a known sequence and asked what it does; a generator is
handed a target and asked to invent a sequence that does something chosen. A
prediction can be checked against a solved structure. For a designed binder,
nothing but a wet lab says whether it binds. Whether the two problems turn out
to run on one machinery is something this review arrives at rather than starts
from.

It is timely to ask, because the last two years are an explosion. Several
predictor lineages have been reimplemented openly, design systems have been
stacked on every one of them, and results are published faster than anyone
compares them. The models are also run: within one week of September 2026,
NVIDIA and Anthropic each shipped accelerated inference paths for these exact
models — Boltz-2, Chai-1, Protenix, OpenFold3, RoseTTAFold3 and ESMFold2 among
them — reporting, each on its own benchmarks, a 2.9-fold throughput gain for
NVIDIA's runtime on a matched 1,000-dimer folding panel, and a 4.1-fold average
speedup for Anthropic's kits across thirteen predictors on their fastest mode,
or 1.6-fold with outputs unchanged. Nobody spends that kind of engineering on
software nobody runs. A newcomer cannot see the shape of any of this from the
papers alone.

This review is about one problem: given a target protein, design a new protein
or peptide that binds it. Antibodies, nanobodies, VHHs, scFvs, minibinders and
macrocyclic peptides are one object here, because that is what they are to every
model in the review: a chain of amino acids, judged by how it folds against the
target. Small molecules are the other half of binder discovery and are out of
scope — a molecule is a variable-size graph under hard valence rules, not a
chain drawn from a fixed alphabet of twenty, so generating one takes different
machinery and is judged on different benchmarks. Sequence generation with no
target conditioning is outside the review for the same reason.

The models are followed lineage by lineage, from each predictor to the designs
built on it: AlphaFold, then RoseTTAFold, Boltz, Chai, Protenix and ESM, so each
architecture is met once and then traced to what it produces, results and
caveats together. What comes before them is preparation: what a co-folder is,
why prediction and generation turn out to be one machinery, how tightly a
generator can couple to its critic, what the field's disclosure limit does to
its evidence, and the vocabulary its numbers are quoted in. A closing coda steps
outside the open lineages to systems that publish benchmarks and withhold
mechanisms, read there as evidence about the field's evidence rather than as its
strongest results.

And through it all runs one number: how many designs must be physically made
before one of them binds. Screening-era work measured its patience in thousands
of candidates per target; the systems collected here report tens. The measure of
progress in this field is how few designs buy a binder, and the sections that
follow are, read one way, a history of that number falling.
