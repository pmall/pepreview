# 02 — Background (draft, new pass)

Budget: ≈1,100 words of prose; the two tables are display items and do not
count. The four map beats, in reading order.

## The founding assumption, and how a co-folding model is built

Design needed prediction first. Prediction succeeded on a single assumption:
coevolution between two positions in a multiple sequence alignment (MSA) is a
usable proxy for the two residues being close in space. AlphaFold2 confirmed the
assumption at CASP14, reaching a median backbone accuracy of 0.96 Å on the
competition domains against 2.8 Å for the next best method. AlphaFold3 then
generalized the result from single chains to arbitrary complexes of proteins,
nucleic acids, ligands and ions.

Every co-folding model has two stages, and the stages do different jobs. Stage 1
is the trunk: sequences go in, pairwise reasoning comes out. Its principal
output is a distogram, a probability distribution over the distance between each
pair of residues. The trunk is where the coevolution signal enters, and it is
differentiable throughout. What feeds the trunk divides the field. Most models
retrieve an MSA from sequence databases at inference time, so evolutionary depth
is looked up on demand; AlphaFold2 and AlphaFold3, RoseTTAFold, Boltz and
Protenix are built this way. A protein language model instead holds the same
statistics in its weights, so a single sequence is enough; ESM2 with ESMFold and
ESMC with ESMFold2 are built this way. The divide is not a wall: Chai-1 carries
both tracks and can run on either.

Stage 2 is the structure stage: pairwise reasoning goes in, atomic coordinates
come out. The variation here is the generative formalism, and it decides how
many forward passes one sample costs. AlphaFold2 uses a single regression pass,
trained end to end, and gradients traverse the whole network. AlphaFold3 and the
models built in its image use diffusion: coordinates are sampled along a long
stochastic denoising trajectory, which costs roughly a thousand forward passes
per high-quality sample. Flow matching replaces the stochastic trajectory with a
deterministic one and buys the same sample quality in far fewer steps; FrameFlow
reports twice the designability at five times fewer sampling steps on
unconditional monomers. Four target-conditioned binder generators in the
literature are built on flow matching (PPIFlow, OriginFlow, AtomFlow, D-Flow).
Both formalisms are borrowed from image generation. What differs is only what
gets noised: where an image model denoises pixels, these modules are trained to
receive noised atomic coordinates and predict the true ones.

## Prediction and generation run on the same machinery

What separates a predictor from a generator is only which sequences are held
fixed. Give a co-folding model every chain in a complex and it predicts a
structure. Leave the binder chain blank and ask for a chain that folds against
the rest, and the same model generates. RFdiffusion reached this place by
fine-tuning RoseTTAFold, a predictor, into a generator of backbones. BoltzGen
states the same fact as a design principle: one all-atom diffusion model
performs both structure prediction and protein design.

A predictor alone was not enough. It answers a question that must already have
been asked: how does this sequence fold against the target? It cannot say which
sequence to try, and there are twenty choices at every position of a chain tens
of residues long. The established workaround was a library: immunize an animal,
or screen a trillion or more random sequences by display and keep whatever
sticks. RFantibody states the limit plainly: no method designs novel
epitope-specific antibodies entirely in silico, so discovery relies on
immunization, random library screening, or antibodies isolated from patients. A
library also returns binders to whichever part of the target happens to be
accessible; it cannot be aimed at a chosen site.

What generation bought is measured in one number: how many designs must be
physically made before one binds.

| Era                                             | Designs tested per target                                                                                | Source                                  |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Screening-based, and early computational design | "thousands to millions of designs to reliably identify hits"                                             | Chai-2's characterization of prior work |
| Current generative systems with filtering       | 16–30 (Protenix-v2), ≤20 (Chai-2), ≤20 (RFpeptides), 30–100 (Latent-X), 43–101 (Germinal), 84 (ESMFold2) | each system's own campaign              |

The hit rates in the same campaigns sharpen the picture: 16% for Chai-2 on de
novo antibodies, 2–48% BLI-confirmed for Protenix-v2's VHH-Fc designs and 16–88%
on four GPCRs, 70% for ESMFold2's minibinders. Not all of these percentages
count the same event. BoltzProt-1 separates screening hits from confirmed
binders and notes that screening hits are what prior binder-design literature
typically reports as binders; its own confirmed-binder rate is 8.0%. And every
number above comes from a campaign whose targets and epitopes its authors
selected. The exception is mBER, a million-scale VHH campaign against hundreds
of cell-surface proteins with hotspots drawn at random; its median per-design
hit rate sits two orders of magnitude below the headline numbers, and on one
target epitope choice alone moves the rate from 0.4% overall to 7.5% at its best
hotspot.

Image generation has no AlphaFold. Nothing scores whether a generated image is
correct, so image models are judged by human preference. Protein design can
close a loop on its own objective, because a predictor grades the output. How
tightly that loop is closed separates the design approaches that follow.

## How tightly the generator is coupled to its critic

Every system here pairs something that proposes sequences with something that
judges them. What separates the systems is how tightly the two are bound.

| Coupling                                 | What is optimized                                                | Where the critic sits | Examples                                                                                   |
| ---------------------------------------- | ---------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------ |
| Level 0: the generator is a predictor    | the model's own sampling                                         | inside the model      | BoltzGen; RFdiffusion, fine-tuned from RoseTTAFold                                         |
| Level 1: generate, then filter           | nothing; designs are sampled and filtered                        | after the fact        | RFdiffusion, then ProteinMPNN, then AlphaFold2 judges; RFpeptides, PXDesign-d, Protenix-v2 |
| Level 2: backpropagate into the sequence | an L×20 simplex of amino-acid probabilities, annealed to one-hot | inside the loss       | BindCraft, Germinal, BoltzDesign1, PXDesign-h, ESMFold2                                    |

Level 1 is the field's default, and it produced the standard success criterion,
quoted here whole: interchain AlphaFold2 pAE below 10, binder-aligned RMSD below
1 Å, pLDDT above 80. Level 1 has two forms. The default filter is the
predictor's own confidence scores. The alternative is a critic trained to answer
whether a design binds: BoltzPPI, swapped into BoltzGen with the candidate pool
untouched, raises the confirmed-binder rate from 3.3% to 8.0%, and PXDesign
finds that Protenix and AF2-IG filters retain different true positives.
RFOptimization is the one system that keeps the sequence as real amino acids
throughout and uses the gradient only to rank point mutations.

Level 2 is possible because a sequence being designed can relax: it is held as a
probability distribution over the twenty amino acids at each of L positions, and
every point in that space is still a valid input to a structure predictor. A
design loop can hand the predictor a blurred sequence, read how wrong the
resulting structure is, and step downhill. This is what BindCraft does through
AlphaFold2, Germinal over antibody CDR loops, and ESMFold2 through a language
model and a folding head at once.

One precondition makes Level 2 possible at all: MSA emancipation. An MSA is a
database lookup on a sequence that does not exist yet. It is neither
differentiable nor defined for a binder still being invented, so any Level-2
loop must run its predictor single-sequence on the designed chain. That is the
regime AlphaFold2's own paper documents as its weakest, and it is why ESMFold2,
which is natively single-sequence, can backpropagate through a
six-billion-parameter language model without leaving its training distribution.
The anatomy of the structure stage decides where the gradient can attach.
AlphaFold2 is differentiable end to end. AlphaFold3-class models replaced the
structure module with diffusion, and unrolling a thousand denoising steps for a
gradient is impossible, so design loops read the loss from the trunk's distogram
or the confidence heads instead. Those attachment choices are what the design
systems differ over.

## The disclosure limit

The strongest claimed results increasingly come from systems that publish
benchmarks but withhold mechanisms: AlphaProteo, Latent-X, the generator behind
Chai-2, and IsoDDE, which has no publication at all and appears only as the top
point on a competitor's scaling curve. The sharpest case is Boltz: Boltz-1,
Boltz-2 and BoltzGen are released under MIT licenses with weights, while
BoltzProt-1 is API-only. Because every campaign chose its own targets, assay and
hit definition, a hit rate is self-reported by the party whose method cannot be
inspected, and the papers that disclose most are not the ones reporting the
highest numbers. The closed systems are read here as evidence about the field's
evidence, not as its strongest results.
