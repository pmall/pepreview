# §7 — ESM

The divide the review has followed since AlphaFold — evolutionary statistics
retrieved from a database at inference time, or carried in a language model's
weights — closes here, and it closes for the carried answer: on the
antibody–antigen class every design section from §3 onward runs against,
single-sequence accuracy no longer pays for the retrieval step. The coupling
ladder tops out at the same moment. §6 assembled a design loop around a
predictor its own platform shipped; the ESM line arrives one step further, with
the language model, the folding head and the design loop as one system — what
its paper describes as a search run by gradient descent through a model that
both knows what a plausible protein is and folds candidate sequences against a
target.

The mechanism is one scaling story told twice. A protein language model is
trained only to predict masked-out amino acids, and its attention patterns come
to reproduce the residue–residue contacts the coevolution bet recovered from
alignments: as the ESM-2 family is scaled from 8 million to 15 billion
parameters, atomic-resolution structure becomes projectable from the
representations alone. ESMFold puts a folding head over the frozen language
model — sequence in, all-atom structure out, no database search and no templates
at inference. Its 2023 form paid for that independence: a mean TM-score of 0.83
on CAMEO against AlphaFold2's 0.88 with its MSAs and templates, and 0.68 against
0.85 on CASP14. The paper's own account of the gap is perplexity — the language
model's estimate of how expected a sequence is — and on the 18 CASP14 targets
where perplexity falls below 7, ESMFold matches AlphaFold2. That trade was real,
and it was the standing objection to single-sequence prediction for the three
years this section spans.

ESM-3 is the generative turn of the same lineage: sequence, structure and
function as three tracks of discrete tokens in one masked-token model, so any
track can be prompted and any track generated. The background's argument that a
predictor and a generator are one machinery appears here as the PLM instance —
one set of weights does both, with no design head bolted on — and the accuracy
trade is already closing before the lineage's next model arrives: at 98 billion
parameters, single-sequence prediction beats ESMFold at 0.880 against 0.861 LDDT
on the CAMEO test set. The same paper carries the corpus's one wet-lab-confirmed
de novo protein whose function is not binding: esmGFP, prompted from six
chromophore residues, 58% sequence identity to the nearest known fluorescent
protein, bright on the plate reader.

The version that settles the thread is ESMC and ESMFold2, one release: a masked
language model at 6 billion parameters trained on close to 2.8 billion sequences
— the metagenomic expansion that keeps its representations improving with scale
— and a folding head that consumes them. ESMFold2 pools representations from all
layers of the frozen language model into a two-dimensional pair state, refines
it through 48 folding layers whose recurrent update is run for further loops at
inference and is computed with a stabilized recursion the model was trained to
backpropagate through, then decodes coordinates with a diffusion transformer on
a truncated schedule. The MSA track is not absent but optional, and it earns its
keep almost exactly where the language model is weakest: it contributes little
at low pseudo-perplexity and markedly improves harder, higher-pseudo-perplexity
sequences.

On prediction, the claim is parity rather than victory. On the FoldBench
antibody–antigen subset, under one protocol — five seeds, five diffusion samples
per seed, confidence-ranked — ESMFold2 reaches a DockQ pass rate of 50% ± 2 from
a single sequence, against AlphaFold3's 47% ± 2 with an MSA; on protein–protein
complexes the comparison runs the other way unless both models are given the
MSA. The margin is inside the stated error bars, and AtlasFold — a second group,
independent of this one, that reaches single-sequence folding from a metagenomic
language model of its own — re-runs the same benchmark with AlphaFold3 at 49.3%
and ESMFold2 at 48.6%. What survives both runs is the word "matching": the
search for related sequences is no longer the price of accuracy on the class
this review designs for, which is the claim that matters, not "exceeding".
AtlasFold also releases its whole path — training code, training data, stage
checkpoints and weights under an MIT licence — so the route is not one lab's
private road.

The design half then follows from the prediction half without new machinery. A
design is a sheet of logits over the amino acids of the binder chain, updated by
gradient descent through both networks: three losses read off ESMFold2's
distogram — low entropy inside the binder, low entropy across the binder–target
contacts, a packing-radius penalty — and one from the language model's own
amino-acid logits, the sequence prior, which in §5's composed systems had to be
added as a second model and a second gradient. The distributions sharpen to
discrete sequences over a short annealed search, designs are ranked by the
average ipTM of an ensemble of ESMFold2 replicas, and nothing is bolted together
from someone else's parts. The off-distribution problem the coupling beat raised
— every §5 loop running a predictor single-sequence against its training regime
— does not arise, because single-sequence is this system's native regime; the
precondition had been argued in the background as settled, and this is the
ceiling it named.

The wet-lab campaign takes that loop to five targets the authors chose — PDGFRβ,
EGFR, PD-L1, CD45 and CTLA-4 — in two modalities: de novo minibinders and scFvs
whose frameworks come from therapeutic antibodies, only the CDRs designed. Each
target–modality–compute cohort was trimmed to a plate's worth of designs for
testing. Under the paper's stringent BLI signal cutoffs, the higher-compute
cohorts hit 36–88% for minibinders across the five targets and 15–29% for scFvs;
expanding the candidate pool and the ranking ensemble improved results in nine
of ten target–modality pairs. Affinities of purified designs range from 68 pM to
70 nM, cryo-EM of an EGFR–minibinder complex at 3.8 Å returns a 1.204 Å r.m.s.d.
against the computational model — inside the reconstruction's uncertainty — and
epitope-competition assays, live-cell staining and homolog testing support
binding at the intended sites on the intended targets. The hit rate here is also
the corpus's highest outside §8, from targets and an assay the same authors
selected, so the provenance columns of Exhibit 4 attach to it as to every
campaign in this review; and the benchmark comparisons above read under Exhibit
1's defect note too, since this paper is the one that flagged the temporal
leakage in Boltz-2's FoldBench numbers. With the loop inside the model, the
escalation §5 traced has nowhere further to climb, and what comes next in the
review is not another rung: §8, where the systems cannot be opened the way this
one just was.
