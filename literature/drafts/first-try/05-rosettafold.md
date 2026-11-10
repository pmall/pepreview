# §2 — RoseTTAFold → RFdiffusion

This lineage's two current models share a name and nothing else, and the first
job is to keep them apart. RoseTTAFold3 (RF3) is a **predictor**: handed a
sequence, it diffuses coordinates toward the structure that sequence folds into.
RFdiffusion3 (RFD3) is a **generator**: its diffusion runs with the sequence
unknown, inventing a backbone that ProteinMPNN writes a sequence onto afterwards
— which is why the generator has a ProteinMPNN step and the predictor does not.
The two are siblings, not revisions of one model, and both are trained on
AtomWorks, the shared data-and-training framework this lineage now builds its
models on. Between them they hold the section's organizing fact: this is the
only lineage in the review still shipping both tracks. As a generator the line
is what the design literature cites, and as a predictor it has never stopped
shipping — RF3 is current, benchmarked directly against AlphaFold3, Boltz-2 and
Chai-1, and is what the gradient optimizer of §5 takes its losses from.

## The predictors

The line starts where AlphaFold was still a black box. RoseTTAFold (RF1) is the
one architecture in this review not derived from AlphaFold, and the paper keeps
the receipts: in the wake of the CASP14 talks, the lab worked
`in the absence of a published method` and built a three-track network — a 1D
sequence track, a 2D distance-map track and a 3D coordinate track, information
passing back and forth between all three — with accuracies
`approaching those of DeepMind in CASP14`. The complex result arrived as a side
effect: memory limits had forced training on crops of two discontinuous sequence
segments, the network turned out to handle the chain breaks between them
seamlessly, and so feeding it two sequences handed back a protein–protein
complex directly from sequence, short-circuiting the fold-each-unit-then-dock
pipeline. Set against AlphaFold2, contemporaneously and on the same problem,
that establishes two independent routes to the same destination — the reason the
review has two lineage origins to place rather than one. As a predictor RF1 is
an ancestor — no post-2024 paper in the corpus benchmarks against it — and its
role is the network RFdiffusion fine-tunes from.

RoseTTAFold2 (RF2) is the test of what the accuracy actually needed. Once the
AF2 method was public, the lab rebuilt its own network adding AlphaFold2's ideas
one at a time: FAPE loss, recycling, distillation on AF2's own predictions and
network depth all proved essential, while AF2's two signature modules —
invariant point attention and triangle attention — proved replaceable, an
architecture reaching AlphaFold2's accuracy on monomers and
AlphaFold2-Multimer's on complexes without either, and scaling past 1,000
residues. The conclusion is the sentence this section stands on:
`excellent performance can be achieved with a broader class of models` than the
one nearly every other predictor re-uses. Its one caveat is publication: a
preprint, never peer-reviewed, three years on.

RoseTTAFold All-Atom (RFAA) widens the line beyond proteins: RF2's protein and
nucleic-acid chains kept, and an atom-bond graph added for everything else —
small molecules, metals, covalent modifications. Its history predates the
field's shared history: published online on 7 March 2024, two months before
AlphaFold3, built from the Baker lab's own RF2 rather than on DeepMind's method
— the date that makes the two origins a fact rather than a framing. Chai-1's
late-2024 benchmark is the last place in the corpus it still appears as a
comparator.

RF3 is where the predictor track has arrived. It is all-atom, with a diffusion
structure stage, trained on AtomWorks, and released permissively (BSD) with
code, data and weights, benchmarked directly against AF3, Boltz-2 and Chai-1.
Where it leads is the physical validity of the small molecules it predicts, and
here the lineage answers the question AF3's successors raise by design choice:
RF3 encodes chirality as features the network learns — a per-chiral-centre error
signal, reinforced by training on inverted-chirality examples as data
augmentation — and predicts 88% of ligand chiral centres correctly, against 84%
for AF3 and 76% for Boltz-2 running without inference-time guidance. The paper
is careful with its own headline: the RF3–AF3 difference is not significant (p =
0.064). The mechanism is the point, because it is the lineage's answer to
inference-time steering, Boltz-1x's approach to the same problem — steering, per
this paper, `may shift the network outside the training distribution`, while a
learned feature cannot.

## The generators

RFdiffusion is the turn. It trains the predictor to output structure from
corruption rather than from information, and the reversal is one sentence in the
paper:
`in RFdiffusion, the primary input is the noised coordinates from the previous step`.
Everything else is deliberately unchanged — a direct fine-tune of the
RoseTTAFold weights, trained to denoise, with the MSE loss the ablations show is
needed for unconditional generation, and self-conditioning in which each
denoising step conditions on its own previous prediction, the AF2 recycling idea
re-used. The historical proof the generative-turn beat rests on is the paper's
own ablation: fine-tuning from the pretrained predictor outperforms training an
equivalent network from untrained weights for the same amount of training, so
the claim that a predictor was fine-tuned into a generator with nothing else
changed is this paper's own evidence rather than a narrative gloss. What the
trick bought, measured by single-point BLI on five protein targets with 95
designs per target, is an experimental binder success rate of 19% — a rate the
paper calls a conservative estimate —
`roughly two orders of magnitude over our previous Rosetta-based method on the same targets`.
The paper splits its own credit: one order of magnitude to the generator, the
second to the AF2 filter that sifted designs before synthesis. The lift, in
other words, was never generator-only.

One bias to read its numbers with: what the paper terms `in silico success` is a
confidence-metric filter — a design counts if AF2, fed the ProteinMPNN sequence,
refolds the backbone within 2 Å at a predicted alignment error below 5 — so the
paper's in silico success rates are rates of passing a filter, not of binding;
the 19% above is the experimental exception. The comparison this paper wins in
the lineage's own house is over unconditional monomers: RFdiffusion holds up
past 100 residues where the Baker lab's own gradient technique — hallucination
through RoseTTAFold, the method §5 runs on stronger predictors — deteriorates.

RFdiffusion2 pushes the diffusion's conditioning granularity from residues to
atoms: it generates scaffolds around the functional-group positions of an enzyme
active site without being told which residues those groups belong to, the model
inferring rotamer and sequence index itself.

RFdiffusion3 is the sibling's answer to the successor problem, and it is where
the lineage's own recipe breaks. RFD3 is not a fine-tune of anything: its
account begins from a transformer U-Net over atoms in the image of AlphaFold3's
diffusion module — AF3's Pairformer shrunk from 48 layers to 2, roughly 168M
parameters against AF3's ~350M — and it is trained on PDB complexes and AF2
distillation; nothing in it is initialized from a predictor. The identity claim
is weakest, in other words, in the lineage that established it. What it buys is
all-atom design: backbone and sidechain atoms diffuse together, in the context
of ligands, nucleic acids and atom-level constraints — hydrogen-bond donor or
acceptor status for chosen atoms, solvent-exposure labels, relative position of
the binding partner. It runs an order of magnitude faster than its predecessors,
outperforms RFD1 on four of five binder targets in silico with far more unique
solutions per problem, and moved to the lab: DNA-binding proteins designed for
DNA sequences withheld from training and cysteine hydrolases, both
experimentally characterized. The ProteinMPNN step survives even here, because
the diffusion trajectory still ends at a backbone rather than a committed
sequence.

**ProteinMPNN** writes the sequence. Generating geometry and generating sequence
are two problems, and inverse folding is the bridge. ProteinMPNN is a
message-passing network trained autoregressively to recover native sequences
from fixed backbones, with an order-agnostic decoding scheme: the order residues
are decided in is sampled, so one model accepts fixed regions anywhere in the
chain, skips them, or couples chains by symmetry. Against Rosetta's
fixed-backbone design on a monomer test set it recovers 52.4% of native residues
to Rosetta's 32.9%, and it trains on backbone noise so its sequences survive the
near-misses a generator produces rather than demanding crystallographic
geometry. Its own caveat is the honesty that matters: native sequence recovery,
the metric it is scored on, is sensitive to crystallographic resolution and
`may not correlate with proper folding`. It is nevertheless the one piece of
machinery this review's sections share — run across §2–§6, by nine labs, at both
coupling levels — and outside it the corpus holds a single substitute,
AlphaDesign's own diffusion sequence designer benchmarked as comparable:
evidence that the field's dependence is adoption rather than necessity.
LigandMPNN is the same network conditioned on ligand and nucleic-acid context,
the all-atom extension of the stage and the variant this section's arms reach
for once a target carries small molecules.

## The arms

RFantibody is the antibody arm, and it exists because the base model could not
serve it:
`the original ('vanilla') RFdiffusion network is unable to design antibodies de novo`,
because the interfaces it favours are built of regular secondary structure —
helices and strands laid against the epitope — and antibody interfaces are made
of loops jutting from a framework. The fine-tune conditions RFdiffusion on
epitope hotspot residues and selected framework templates, producing VHHs, scFvs
and full antibodies aimed at a chosen site, with ProteinMPNN writing the CDR
sequences and RoseTTAFold2 judging self-consistency. What this entry carries is
that the screen remains: the high-throughput arm of the experiments puts 9,000
designs per target through yeast display, and across the paper's targets the
success rates run from 0% to 2% — the paper's own word for the design success
rate is `quite low` — so display screening is, in its words,
`currently necessary`. OrthoRep's continuous in vivo hypermutation lifts the
initial tens-to-hundreds-of-nanomolar affinities roughly two orders of
magnitude, to single-digit nanomolar, without moving the designed pose. This is
the baseline the falling-designs figures of the later sections are read against:
the lineage that made epitopes aimable did not abolish the screening era, and
§3, §4 and §5 cite RFantibody precisely when they report their pipelines doing
without it.

RFpeptides is the macrocycle arm: the same recipe, one geometrical change. A
cyclic relative positional encoding added to both RF2 and RFdiffusion encodes
the head-to-tail closure a macrocycle requires, so the chain reads as a closed
ring rather than a protein with an appended link. ProteinMPNN sequences the
backbones; filtering stays Level 1 — refolding in AfCycDesign, AlphaFold2 given
the cyclic offset that makes a chain read as closed, the same trick where §5's
cyclic thread starts, then Rosetta interface metrics. The budget this entry
carries sits at the low end of the identity beat: twenty or fewer tested designs
against each of four targets, binders to all four, and X-ray structures for
three complexes matching the design models at under 1.5 Å. Its strongest case
was designed against a structure the pipeline itself supplied — no experimental
structure of Rhombotarget A existed, only an AF2 and RF2 prediction the
designers trusted enough to aim hotspots at — and the best macrocycle, RBB_D10,
bound at 9.4 nM by SPR, with the subsequent crystal structure confirming both
the predicted target fold and the designed pose.

RFOptimization (§5) closes the stack: training-free refinement of finished
designs, with gradients taken from RF3 above and a cycling move through
ProteinMPNN and LigandMPNN beside them — predict, generate, inverse-fold,
optimize and filter from one group. Its caveat is the ceiling on how far the
review leans on it: in silico only, no wet-lab validation, no designs-tested
denominator. And the gradient move it runs is the Baker lab returning, on its
own AF3-class predictor, to the technique RFdiffusion displaced.

Where this lineage had to build a generator by surgery — fine-tune a predictor,
add a sequence stage, retrain per modality — the next one starts with the
machinery installed: as §3 argues outright, a diffusion predictor's weights
already are a generator, the moment nothing tells them which sequence to fill.
