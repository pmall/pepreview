# Generative Methods for De Novo Binder Design: Architectural Trade-offs and Experimental Reality

*Draft Review Manuscript prepared for PLOS Computational Biology. Authors,
affiliations, and required journal statements to be finalized prior to
submission.*

## Abstract

Advances in protein structure prediction and biomolecular co-folding have
enabled computational de novo binder design against specific protein targets.
Generative models conditioned on target structures now narrow experimental
testing from massive empirical libraries to tens of candidates per target across
peptides, minibinders, and antibodies. This review examines how multi-chain
structure predictors are turned into binder-design workflows, focusing on two
core mechanistic trade-offs: how evolutionary information enters the network and
how atomic coordinates are generated. In particular, we discuss how replacing
multiple sequence alignments with protein language models enables native
single-sequence optimization, and how coordinate-generation choices balance
speed, differentiability, and chemical generality. We also examine why
structural confidence filters remain an imperfect guide to candidate selection
and why experimental differences prevent treating published wet-lab hit rates as
direct comparisons. Finally, we outline the main technical and translational
bottlenecks that still separate in vitro binding hits from developable drug
leads.

## Introduction

Artificial intelligence transformed structural biology by bringing protein
structure prediction to near-experimental accuracy. AlphaFold2 marked this
turning point in the CASP14 assessment, showing that coevolutionary signals in
multiple sequence alignments (MSAs) can recover single-chain folds to a median
backbone accuracy of 0.96 Å r.m.s.d.95, compared with 2.8 Å for the next best
method [@alphafold2]. AlphaFold3 subsequently generalized this framework to
complexes containing proteins, nucleic acids, small-molecule ligands, and ions,
establishing biomolecular co-folding as a general modeling paradigm
[@alphafold3]. With accurate complex prediction in hand, the field has moved
quickly to the inverse challenge: repurposing these neural architectures not
merely to fold known proteins, but to generate de novo binders against specific
protein targets.

Moving from complex prediction to binder generation draws on the same core
architecture. Supplying the sequences of all interacting chains asks the network
to predict the three-dimensional complex, whereas leaving the binder chain
masked or initialized as noise asks the same model to generate a complementary
partner [@rfdiffusion; @boltzgen]. What differs sharply in practice is search
and validation. During training and benchmarking, a structure predictor
evaluates a fixed natural sequence whose predicted geometry can be scored
directly against a held-out crystal or cryo-electron microscopy structure in the
Protein Data Bank (PDB). By contrast, de novo design must search a combinatorial
space of $20^L$ sequences for a chain of length *L*, lacks natural evolutionary
alignments for the invented binder, and has no pre-existing structural
reference, so binding can only be confirmed by synthesizing and assaying
candidates in a wet laboratory.

Many therapeutically relevant protein targets present broad, flat surfaces that
lack the deep pockets required by small-molecule drugs. Engaging these surfaces
calls for peptides, compact de novo proteins (minibinders), or antibody formats
such as nanobodies (VHHs), single-chain variable fragments (scFvs), and
monoclonal antibodies (mAbs). Conventional discovery obtains such binders by
screening vast random display libraries or immunizing animals, a process that
must be repeated for each new target and offers limited control over the binding
site. Generative and filtering pipelines instead propose candidate sequences
directly against a chosen target structure, narrowing experimental synthesis
budgets from thousands or millions of variants in display libraries and early
computational campaigns [@chai2; @rfantibody] down to tens of tested designs per
target [@chai2; @rfpeptides; @boltzgen; @protenix_v2].

Written from a drug-discovery and protein-engineering perspective, this review
examines these protein- and peptide-design methods, emphasizing underlying
mechanisms and architectural trade-offs rather than ranking models. We first
examine how structure-prediction trunks and coordinate-generation modules
operate, then trace how those components give rise to distinct binder-design
workflows, evaluate computational filtering limits alongside wet-lab campaign
evidence, and conclude with the translational and technical bottlenecks
separating in vitro binding hits from viable drug leads. Small-molecule drug
design, which operates on variable chemical graphs governed by valence rules,
requires separate architectures and benchmarks and therefore lies outside the
scope of this review.

## 1. Co-folding Architectures and Mechanistic Trade-offs

### The two-stage co-folding pipeline

Modern protein structure prediction rests on the principle that correlated
mutations across positions in an MSA reflect spatial proximity in the folded
three-dimensional structure [@alphafold2]. Whereas early RoseTTAFold
architectures propagated information through parallel one-dimensional sequence,
two-dimensional pairwise distance, and three-dimensional coordinate tracks from
input to output, allowing spatial motifs and target geometry to be supplied
directly as coordinates [@rosettafold; @rosettafold2], most contemporary
co-folding models adopt a two-stage pipeline (Fig 1). In the first stage, a deep
sequence-to-pairwise reasoning trunk transforms sequence and evolutionary inputs
into single-residue and pairwise residue representations. Examples include the
Evoformer in AlphaFold2 [@alphafold2], the simplified Pairformer shared across
AlphaFold3, Boltz, Chai-1, Protenix, and RoseTTAFold3 \[@alphafold3; @boltz1;
@chai1; @protenix_v1; @rosettafold3\], and the recurrent folding trunk in
ESMFold and ESMFold2 [@esm2; @esmc]. A linear projection on the pairwise
representation predicts a distogram, giving a probability distribution over
binned physical three-dimensional distances (typically 2 to 22 Å across 64 bins)
for every residue pair. Crucially for design, the entire trunk is differentiable
and executes in a single forward pass for a given protein complex [@boltz1],
allowing the distogram to serve both as a training loss and as a smooth
surrogate objective during sequence optimization \[@alphafold2; @boltzdesign1;
@esmc\]. In the second stage, a dedicated coordinate module converts these
learned trunk representations into explicit three-dimensional atomic positions.

**Fig 1. Co-folding architectural trade-offs and binder-design workflows.** (A)
Two-stage co-folding architectures separate a differentiable
sequence-to-pairwise reasoning trunk from a three-dimensional coordinate module.
Evolutionary information enters the trunk via database multiple sequence
alignment (MSA) retrieval, which is non-differentiable and undefined for
invented sequences, via a pre-trained protein language model (PLM) trunk such as
ESMC/ESMFold2 that supports native single-sequence inference and end-to-end
gradient backpropagation to input sequences, or via a hybrid dual-track trunk
such as Chai-1. The trunk outputs single and pair representations along with a
differentiable distogram head, feeding either a single-pass differentiable
regression module (Invariant Point Attention) or an iterative all-atom diffusion
or few-step flow/ODE coordinate generator. (B) These architectural choices map
onto three practical binder-design workflows. Generate-and-filter pipelines
decouple backbone or all-atom generation from inverse folding and post-hoc
refolding filters or binding classifiers. Unified all-atom diffusion models
train a single network jointly for structure prediction and design.
Gradient-based sequence optimization backpropagates through regression modules,
trunk distogram or confidence heads that bypass diffusion, or few-step ODE
decoders, optionally regularized by language-model priors or discrete mutation
proposals.

### Evolutionary inputs: multiple sequence alignments versus protein language models

How evolutionary information enters the trunk creates one of the deepest
mechanistic divides in binder design. Standard MSA-based co-folders, including
AlphaFold2, AlphaFold3, RoseTTAFold3, Boltz, and Protenix, retrieve homologous
sequences from large sequence databases at inference time \[@alphafold2;
@alphafold3; @rosettafold3; @boltz1; @protenix_v1\]. Database retrieval is
inherently discrete and non-differentiable, and it is undefined for a synthetic
binder sequence that has no natural homologs. Consequently, whenever an
MSA-trained model evaluates or optimizes a de novo binder chain, that chain must
run in single-sequence mode (without an MSA), even if the target protein carries
a deep alignment. Both the AlphaFold2 and AlphaFold3 publications document that
shallow-MSA and single-sequence inputs represent their weakest accuracy regime
[@alphafold2; @alphafold3].

Replacing database lookups with a protein language model embeds evolutionary
statistics directly into network weights learned across billions of natural
sequences. ESM-2 and ESMFold established that single-sequence structure
prediction without MSAs or templates is feasible, initially trading lower
accuracy than AlphaFold2 for substantially faster inference [@esm2]. Recent
scaling of this paradigm has closed much of that gap for complex interfaces.
ESMC is a protein language model trained on roughly 2.8 billion sequences, whose
frozen 6-billion-parameter representations drive ESMFold2 through 48 recurrent
pair-state folding layers (24 in ESMFold2-Fast) and a sliding-window
atom-attention diffusion transformer [@esmc]. Without MSAs, ESMFold2 matches
MSA-enabled AlphaFold3 on antibody–antigen structure prediction, a parity
confirmed by independent AtlasFold benchmarks [@esmc; @atlasfold], while
retaining an optional detachable MSA encoder for unusually high-perplexity
sequences [@esmc]. For binder design, the architectural payoff is direct:
because a protein language model trunk expects single sequences natively,
gradients from the folding trunk and distogram can propagate all the way back
through the language model into the input sequence representation without
pushing the designed chain outside the model's training distribution [@esmc].

Hybrid architectures bridge these two regimes. Chai-1 incorporates both an MSA
track and a protein language model track that can operate independently or
jointly, alongside optional experimental contact or pocket restraints [@chai1].
On antibody–protein interfaces, where natural cross-chain coevolution is weak,
single-sequence Chai-1 matches MSA-enabled Chai-1 and outperforms MSA-driven
AlphaFold-Multimer v2.3 [@chai1]. Together, these results highlight why
single-sequence language-model trunks are particularly well suited to designed
peptides, minibinders, and antibody loops whose sequences lack paired natural
alignments.

### Coordinate-generation strategies and physical stereochemistry

The second major architectural choice governs how trunk representations become
atomic coordinates, trading off inference speed, chemical generality, and
end-to-end differentiability. Single-pass coordinate regression, introduced in
AlphaFold2's Invariant Point Attention (IPA) structure module and adopted in
ESMFold, updates rigid residue frames directly in a single forward pass
[@alphafold2; @esm2]. Because coordinates are regressed in one shallow,
deterministic pass rather than across hundreds of iterative steps, gradients
from three-dimensional coordinate and confidence losses propagate cleanly all
the way back to the input sequence [@alphafold2; @bindcraft]. However,
frame-based IPA modules are tailored to canonical amino-acid backbones and do
not naturally generalize to arbitrary non-protein atoms or unusual covalent
chemistries.

To unify proteins, nucleic acids, small molecules, ions, and modified or
cyclized peptides within one coordinate head, AlphaFold3 replaced IPA with an
iterative all-atom diffusion module that transforms Gaussian noise into atomic
coordinates along a stochastic differential equation trajectory [@alphafold3].
Subsequent all-atom co-folders, including Boltz, Chai, Protenix, RoseTTAFold3,
and ESMFold2, adopted variants of this diffusion formalism \[@boltz1; @chai1;
@protenix_v1; @rosettafold3; @esmc\]. Unlike single-pass regression, stochastic
diffusion samples from a distribution of plausible structures rather than
outputting one deterministic pose. In practice, co-folders generate a pool of
candidate structures for a given complex by running multiple random seeds of the
overall network and drawing a batch of diffusion samples per trunk pass (five
model seeds of five diffusion samples each in standard AlphaFold3 inference),
then use an internal confidence head to select one top-ranked prediction
[@alphafold3]. Diffusion brings broad chemical generality at two costs relevant
to design. First, iterative denoising is slow, with protein diffusion generators
often requiring hundreds to roughly 1,000 forward passes per sample
[@frameflow]. Second, unrolling hundreds of stochastic denoising steps to
compute sequence gradients is computationally impractical, breaking the simple
end-to-end backpropagation path enjoyed by IPA regression models
[@boltzdesign1].

Flow matching addresses the sampling bottleneck by formulating coordinate
generation as an ordinary differential equation (ODE) with straighter transport
trajectories requiring far fewer integration steps. On unconditional protein
monomers, FrameFlow recast frame diffusion as flow matching and reported twofold
higher designability at five times fewer timesteps [@frameflow].
Target-conditioned flow-matching generators, including PPIFlow, OriginFlow,
AtomFlow, and D-Flow, extend these faster trajectories to protein–protein
interfaces [@ppiflow; @originflow; @atomflow; @dflow], and few-step ODE decoders
can additionally restore end-to-end differentiability through all-atom
coordinates [@pxdesign].

Predicting free three-dimensional positions for every atom in all-atom diffusion
models also introduces physical-validity errors that rigid amino-acid frames
largely avoided. Because bond geometry and handedness are learned from data
rather than fixed by residue templates, AlphaFold3 still reported occasional
steric clashes and a 4.4% chirality violation rate on the PoseBusters benchmark
despite ranking penalties [@alphafold3]. Two strategies address this limitation.
Boltz-1x applies explicit steering penalties during denoising to suppress
clashes and inverted stereocenters [@boltz1]. RoseTTAFold3 instead encodes
stereochemistry during training to avoid perturbing inference trajectories,
achieving 1.74 Å mean backbone RMSD on mixed L/D peptides compared with 1.88 Å
for AlphaFold3 and 2.24 Å for Boltz-1x [@rosettafold3].

## 2. Design Workflows: Turning Predictors into Binder Generators

Because structure predictors evaluate a fixed sequence rather than searching
sequence space directly, practical binder-design systems repurpose them through
three primary workflows (Fig 1B). The first generates a three-dimensional binder
geometry (either a backbone alone or an all-atom structure including side
chains) against the target, assigns a compatible sequence with a separate
inverse-folding model, and refolds the complex to filter candidates. The second
trains a single all-atom diffusion network to generate atomic coordinates and
amino-acid identities simultaneously, eliminating the inverse-folding handoff
before refolding-based filtering. The third keeps a pre-trained structure
predictor fixed and optimizes the binder sequence directly by gradient descent
until the network predicts a high-confidence complex. Table 1 summarizes
representative open and commercial systems across these three paradigms,
highlighting how trunk inputs, coordinate formalisms, supported modalities, and
methodological openness vary across the field.

**Table 1. Representative Co-folding and Binder-Design Systems.**

| System                                                                             | Input trunk                                                 | Coordinate formalism                                    | Design workflow                                                                                            | Modalities                                                           | Openness                                    |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------- |
| RFdiffusion + ProteinMPNN [@rfdiffusion; @proteinmpnn]                             | MSA (RoseTTAFold fine-tuned)                                | SE(3) frame diffusion                                   | Generate-and-filter (backbone diffusion, inverse folding, AF2 filter)                                      | Minibinders, protein scaffolds                                       | Open code and weights                       |
| RFdiffusion3 + LigandMPNN [@rfdiffusion3; @ligandmpnn]                             | Pre-trained 2-layer Pairformer (no RF predictor init)       | All-atom U-Net diffusion (100 steps)                    | Generate-and-filter (all-atom diffusion, inverse folding; AlphaDesign [@alphadesign] alternative)          | Minibinders, peptides, enzymes, ligand binders                       | Published architecture                      |
| RFantibody [@rfantibody]                                                           | MSA (RoseTTAFold fine-tuned)                                | SE(3) frame diffusion                                   | Generate-and-filter (epitope-conditioned CDR diffusion, ProteinMPNN)                                       | VHHs, scFvs, mAbs                                                    | Published architecture                      |
| RFpeptides [@rfpeptides]                                                           | MSA (RF2 with cyclic positional offset)                     | SE(3) frame diffusion                                   | Generate-and-filter (cyclic diffusion, ProteinMPNN, AfCycDesign filter)                                    | Macrocyclic peptides                                                 | Published architecture                      |
| PPIFlow / AtomFlow [@ppiflow; @atomflow]                                           | Structure-conditioned flow networks                         | ODE flow matching                                       | Generate-and-filter (few-step flow generation, inverse folding)                                            | Protein–protein binders, all-atom complexes                          | Published architecture                      |
| PXDesign-d / PXDesign-h [@pxdesign]                                                | MSA (Protenix Pairformer)                                   | DiT Cartesian diffusion (d) / 2-step ODE (h)            | Generate-and-filter (d) or end-to-end backpropagation (h)                                                  | Minibinders                                                          | Open Protenix platform                      |
| Protenix-v2 [@protenix_v2]                                                         | MSA (Pairformer)                                            | All-atom diffusion                                      | Generate-and-filter (diffusion generation, confidence ranking)                                             | Minibinders, VHHs, Fv, mAbs                                          | Open Protenix platform                      |
| BoltzGen [@boltzgen]                                                               | MSA (Pairformer)                                            | All-atom diffusion                                      | Unified joint prediction and design with Boltz-2 refolding filter                                          | Minibinders, peptides, VHHs (excludes full mAbs)                     | Open weights, training code, and data (MIT) |
| BoltzProt-1 [@boltzprot1]                                                          | MSA (Pairformer)                                            | All-atom diffusion                                      | Refined BoltzGen generator ranked by BoltzPPI binding classifier                                           | VHHs, protein binders                                                | Commercial API only (weights closed)        |
| BindCraft / AfCycDesign [@bindcraft; @afcycdesign]                                 | MSA trunk (AF2 / AF2-Multimer, single-seq binder)           | Single-pass IPA regression                              | Full-network backpropagation (BindCraft adds ProteinMPNN surface redesign; AfCycDesign adds cyclic offset) | Minibinders (BindCraft); macrocycles (AfCycDesign)                   | Open code (ColabDesign / AF2 weights)       |
| BoltzDesign1 / RFOptimization [@boltzdesign1; @rfoptimization]                     | MSA (Boltz-1 or RF3 Pairformer)                             | Diffusion bypassed (distogram and confidence gradients) | Continuous sequence relaxation (BoltzDesign1) or discrete mutation search (RFOptimization)                 | Minibinders, cyclic peptides, ligand binders                         | Open code on MIT/BSD predictor weights      |
| Germinal / mBER [@germinal; @mber]                                                 | MSA trunk (AF2-Multimer) + IgLM or ESM-2 prior              | Single-pass IPA regression                              | Backpropagation regularized by live IgLM (Germinal) or static ESM-2 (mBER) priors                          | scFvs and VHHs (Germinal; OpenGerminal [@opengerminal]); VHHs (mBER) | Open code (OpenGerminal Apache-2.0)         |
| ESMC / ESMFold2 [@esmc]                                                            | PLM trunk (6B ESMC, optional MSA)                           | Sliding-window atom-attention diffusion                 | Native single-sequence backpropagation through PLM and folding trunk distogram                             | Minibinders, scFvs                                                   | Biohub / EvolutionaryScale release          |
| AlphaProteo / Chai-2 / Latent-X1 & X2 [@alphaproteo; @chai2; @latentx1; @latentx2] | Undisclosed (Chai-2 folding module resembles hybrid Chai-1) | Undisclosed generative architectures                    | Published wet-lab campaigns with confidence and self-consistency filtering                                 | Minibinders, macrocycles, VHHs, scFvs                                | Undisclosed generative architectures        |

### Structure generation with inverse folding

The most widely adopted binder-design pipeline decouples geometry generation
from sequence assignment, operating without backpropagation during design.
RFdiffusion popularized this generate-and-filter workflow by fine-tuning
RoseTTAFold predictor weights to denoise three-dimensional residue frames
against a fixed target protein, relying on RoseTTAFold's coordinate track to
condition directly on target geometry [@rfdiffusion]. RFdiffusion outputs only a
sequence-free backbone, so an inverse-folding network, most commonly
ProteinMPNN, next assigns compatible amino-acid sequences to the generated
geometry [@proteinmpnn]. Candidates are then refolded in complex with the target
by a structure predictor such as AlphaFold2 (adapted for complexes via
chain-break offsets or AlphaFold-Multimer) and triaged on confidence and
self-consistency thresholds, exemplified by AlphaProteo's widely referenced
cutoffs of interchain PAE below 10 Å, binder-aligned RMSD below 1 Å, and pLDDT
above 80 [@rfdiffusion; @alphaproteo]. Two caveats apply throughout this
workflow. First, as the ProteinMPNN authors noted, high native sequence recovery
on offline fixed-backbone benchmarks does not necessarily predict whether a
designed sequence will fold accurately [@proteinmpnn]. Second, the "in silico
success" rates frequently quoted for backbone generators measure
self-consistency with a refolding predictor rather than experimental target
engagement [@rfdiffusion].

Targeted architectural modifications extend this decoupled paradigm across
modalities and scales. RFdiffusion3 moved away from fine-tuning a RoseTTAFold
predictor altogether, instead pre-training a compact 168-million-parameter
all-atom transformer U-Net modeled on AlphaFold3's diffusion module directly on
PDB and AlphaFold2 distillation structures [@rfdiffusion3]. By trimming its
Pairformer trunk from 48 to 2 layers and sampling in 100 steps, RFdiffusion3
runs roughly an order of magnitude faster than earlier releases, using
LigandMPNN in place of ProteinMPNN whenever non-protein atoms such as ligands,
nucleic acids, or metal ions are present [@rfdiffusion3; @ligandmpnn]. For
specialized topologies such as head-to-tail macrocycles, RFpeptides adds a
cyclic relative positional encoding to RFdiffusion and RoseTTAFold2
[@rfpeptides]. After inverse folding and cyclic AlphaFold2 (AfCycDesign)
filtering, it produced crystal-structure-verified binders across four targets
from fewer than 20 synthesized peptides each [@rfpeptides; @afcycdesign].
Related variants in Table 1 explore autoregressive diffusion for inverse folding
in AlphaDesign [@alphadesign], fine-tune diffusion for antibody loops in
RFantibody [@rfantibody], replace frame representations with Cartesian diffusion
transformers in PXDesign-d [@pxdesign], or accelerate sampling through ODE flow
matching in PPIFlow and AtomFlow [@ppiflow; @atomflow].

### Unified prediction-and-design all-atom models

A second workflow eliminates the handoff between separate geometry generators
and inverse-folding models by training a single all-atom diffusion network
jointly for structure prediction and de novo sequence–structure generation.
BoltzGen exemplifies this unified approach under a fully reproducible MIT
release providing model weights, training code, and training datasets
[@boltzgen]. Conditioned on a target, BoltzGen simultaneously generates atomic
coordinates and amino-acid identities for masked binder chains across peptides,
minibinders, and nanobodies (full antibodies were excluded from training)
[@boltzgen]. It matches the structure-prediction accuracy of Boltz-2 on the same
benchmark test set, yet the design pipeline still relies on that predictor to
refold and filter generated candidates [@boltzgen]. While commercial systems
such as Chai-2 and Latent-X may use related co-design strategies internally,
their generative architectures remain undisclosed \[@chai2; @latentx1;
@latentx2\], leaving BoltzGen (and its API-only follow-up BoltzProt-1
[@boltzprot1]) as the clearest open representative of this paradigm.

Joint all-atom training also exposes how generative diffusion models memorize
biases in the Protein Data Bank. The BoltzGen authors transparently documented
that at designed binder lengths between 73 and 76 residues, structural diversity
collapses as the model overwhelmingly samples ubiquitin, an artifact traced to
the presence of more than 900 ubiquitin entries in the PDB [@boltzgen]. More
broadly, the authors caution that even unified all-atom design is neither
zero-shot nor plug-and-play in practice, recommending manual structural
inspection and iterative reruns rather than unexamined automated selection
[@boltzgen].

### Gradient-based sequence optimization

The third workflow turns a pre-trained structure predictor directly into a
generator via gradient descent, often termed hallucination or model inversion.
Because discrete amino-acid identities cannot be differentiated directly, the
binder sequence is relaxed into a continuous probability distribution over the
20 amino acids at each of *L* positions (an *L* × 20 matrix of amino-acid
weights). At each optimization step, this soft sequence is passed alongside the
target through the differentiable predictor to compute a design loss favoring
confident folding and tight interchain contacts. Gradients of that loss flow
backward through the network to update the underlying sequence weights, nudging
each position toward amino acids that improve the predicted complex. Because a
real protein must have a single amino acid at every position, a
temperature-annealing schedule gradually sharpens these distributions over
iterations until each position commits to a discrete one-hot residue, a workflow
popularized by ColabDesign [@colabdesign].

When the predictor uses a single-pass IPA regression module, gradients propagate
cleanly from predicted three-dimensional coordinates and confidence heads back
to the input sequence [@alphafold2]. BindCraft leverages this full-network
differentiability across AlphaFold-Multimer, cycling randomly among all five
trained parameter sets between iterations to curb overfitting [@bindcraft]. It
sharpens the binder sequence over four stages, progressing from continuous
amino-acid weights to discrete residues (feeding discrete sequences forward
while keeping continuous gradients backward) and final single-mutation
refinement, after which a soluble ProteinMPNN variant redesigns non-interface
residues to improve stability and solubility [@bindcraft]. A notable mechanistic
feature of BindCraft is that it repredicts the target structure at every
optimization step, permitting induced-fit target rearrangements ranging from 0.5
to 5.5 Å Cα RMSD across designs [@bindcraft]. For cyclic peptides, AfCycDesign
applies a cyclic relative positional offset to AlphaFold2's peptide chain while
keeping the target linear, yielding eight monomer crystal structures within 1.0
Å of design, though its MDM2 and Keap1 binders relied on motif grafting rather
than direct de novo hallucination [@afcycdesign]. However, because both
BindCraft and AfCycDesign rely on MSA-trained AlphaFold2 models while the
invented binder chain has no evolutionary alignment, optimization necessarily
operates in the predictor's weakest, MSA-free regime [@alphafold2; @bindcraft].

Adapting gradient optimization to diffusion-based co-folders requires
circumventing the cost of differentiating through hundreds of denoising steps
[@boltzdesign1]. Two solutions have proved effective. The first computes
gradients exclusively from the differentiable trunk's distogram and confidence
heads while placing a stop-gradient on the diffusion module, preventing
gradients from flowing back through the iterative denoising steps. BoltzDesign1
applies this strategy to Boltz-1's 64-bin Pairformer distogram, optimizing the
underlying distance distribution from which diffusion samples; on 212 BindCraft
binders, Pairformer contacts matched diffusion-sampled contacts on 76% of
designs, whereas nucleic-acid targets required confidence-head losses to
maintain correlation [@boltzdesign1]. ESMFold2 pairs this distogram-gradient
strategy with its native single-sequence language-model trunk, running
single-stage continuous optimization directly through both the
6-billion-parameter ESMC language model and two ESMFold2 trunk replicates before
invoking the diffusion and confidence modules only in final steps to score ipTM
[@esmc]. The second solution preserves coordinate-level backpropagation by
replacing the iterative diffusion sampler with a few-step deterministic decoder:
built on the open AlphaFold3-style predictor Protenix, PXDesign-h substitutes a
differentiable two-step ODE sampler for Protenix's 200-step diffusion module and
optimizes against an ensemble of five resampled models [@pxdesign].

Optimizing a sequence solely for high predicted confidence can produce unnatural
amino-acid compositions that exploit a single predictor's blind spots rather
than genuinely folding and binding. To prevent such adversarial designs, recent
gradient methods add language-model priors or restrict search to discrete
mutations. Native language-model trunks such as ESMC guide designed sequences
toward natural protein statistics intrinsically during backpropagation [@esmc].
For MSA-based predictors, external language models can provide a similar
guardrail: Germinal merges live gradients from an antibody language model (IgLM)
with AlphaFold-Multimer confidence gradients [@germinal], whereas mBER
incorporates fixed sequence preferences from ESM-2 [@mber]. Taking a
complementary route, RFOptimization avoids continuous sequence relaxation
altogether [@rfoptimization]. It keeps sequences strictly discrete, using
RoseTTAFold3 gradients only to propose single-point mutations that are accepted
or rejected iteratively. To curb overfitting to any single predictor, it
interleaves Boltz refolding with LigandMPNN resampling while holding out
AlphaFold3 as an independent check [@rfoptimization].

## 3. Candidate Selection and Experimental Evidence

### Candidate selection and filtering limits

Evaluating a structure predictor against an experimentally solved reference uses
external geometric metrics, including DockQ interface accuracy [@dockq] and
atomic RMSD [@kabsch]. As de novo binders lack an experimental structure, every
design workflow relies on internal self-consistency checks and model-estimated
confidence scores to select the small subset of candidates ordered for wet-lab
testing. Standard filters combine self-consistency RMSD between generated and
refolded coordinates, per-residue confidence (pLDDT) [@alphafold2], interface
predicted TM-score (ipTM), and interchain predicted aligned error (iPAE)
[@alphafold_multimer]. More recent pipelines also adopt ipSAE, which restricts
ipTM to interchain residue pairs below a fixed PAE threshold so that disordered
tails or arbitrary chain trimming do not dilute interface scores [@ipsae]. Yet
structure-prediction confidence heads are trained on experimentally solved bound
complexes to estimate coordinate error rather than on nonbinders or binding
thermodynamics, so high structural confidence does not guarantee wet-lab binding
on unseen designs. Three lines of evidence show why structural confidence
remains an imperfect guide to candidate selection.

As noted in Section 1, co-folding predictors generate a pool of candidate
structures for each complex and rely on internal confidence scores to select a
top prediction, yet even on known complexes those confidence heads routinely
fail to rank the most accurate binding pose first. Across seven predictors
evaluated on FoldBench, a benchmark of experimentally solved complexes
[@foldbench], comparing each model's confidence-ranked top prediction against
the best structure actually generated in the same run revealed a consistent
ranking loss [@atlasfold]. Specifically, confidence ranking missed an acceptable
interface (DockQ > 0.23) already present among the generated samples on 11 to
21% of antibody–antigen complexes (4.5% for Boltz-1) and 3 to 8% of general
protein–protein interfaces [@atlasfold]. The FoldBench study itself noted a
closely related failure mode for antibodies: even when a predictor models the
key CDR-H3 binding loop accurately, it can still dock the antibody at the wrong
site, and per-sample confidence scores do not reliably separate near-native
poses from misdocked decoys [@foldbench].

While confidence filters raise hit rates across large candidate pools [@mber],
their accuracy in predicting wet-lab binding fluctuates sharply from one target
to another. Overath et al. illustrated this variability by re-scoring 3,766
experimentally tested designs across 15 targets from six published campaigns
through a uniform pipeline [@overath_meta]. AlphaFold3 ipSAE emerged as the
strongest single predictor of binding overall, yet its average precision spanned
0.1 to 1.0 depending on the target (bearing in mind that the pooled set retains
heterogeneous source assays and earlier-generation generators) [@overath_meta].
In the Germinal antibody campaign, many experimental nonbinders cleared the
exact same ipSAE threshold as validated binders [@germinal]. Evaluating
refolding filters on a shared experimental benchmark, PXDesign found that
Protenix and AlphaFold2 selected largely different subsets of true binders and
that no single cutoff maximized accuracy across all targets simultaneously
[@pxdesign].

Replacing structure-prediction confidence with classifiers trained directly on
wet-lab binding outcomes can also substantially improve hit rates on identical
candidate pools. In a controlled comparison across 10 low-homology targets (150
designs total), BoltzProt-1 kept the BoltzGen generator and 15-design-per-target
testing budget fixed and replaced BoltzGen's confidence scores with BoltzPPI, a
classifier trained on experimental binding data [@boltzprot1]. This change alone
more than doubled confirmed binders from 3.3% (5/150, yielding hits on 2 of 10
targets) to 8.0% (12/150, yielding hits on 4 of 10 targets) [@boltzprot1].
Candidate ranking therefore shapes experimental yield independently of the
underlying generative architecture.

### Reading wet-lab campaigns critically

Over the past three years, experimental campaigns across compact minibinders,
nanobodies, antibodies, and cyclic peptides have demonstrated that computational
de novo design can routinely recover nanomolar and occasionally picomolar
binders from modest synthesis budgets. Table 2 compiles representative campaigns
grouped by modality alongside their target scope, testing budgets, binding
criteria, and experimental caveats. Because no two de novo campaigns share a
common target panel, assay format, or positivity threshold, headline hit rates
should be read as context-dependent demonstrations rather than direct
head-to-head rankings.

**Table 2. Representative Wet-Lab De Novo Binder Campaigns and Assay Context.**

| System                                                     | Target scope and selection                                                            | Designs tested per target                          | Assay and hit criterion                                                                                                                                | Key caveats                                                                                                               |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| **Minibinders**                                            |                                                                                       |                                                    |                                                                                                                                                        |                                                                                                                           |
| RFdiffusion [@rfdiffusion]                                 | 5 author-selected targets                                                             | 95/target (475 pooled)                             | Single-point BLI at 10 µM ≥ 50% positive control; 19% pooled, best 28 nM (influenza HA)                                                                | Single assay; AlphaProteo yeast-display re-test recovered lower rates at 10–20× lower target concentration [@alphaproteo] |
| AlphaProteo [@alphaproteo]                                 | 8 author-selected targets                                                             | 54–172/target                                      | Yeast-display flow cytometry > 0.2 (1.3 for IL-17A); 9–88% on 7 targets, 0/54 TNFα, best 82 pM (IL-7Rα)                                                | Undisclosed generative architecture; single display format for hit calls                                                  |
| BindCraft [@bindcraft]                                     | 12 author-selected targets                                                            | 6–53/target                                        | SPR binding observed (no numeric cutoff); 10–100% (mean 46.3%), best < 1 nM (PD-1), 5 nM (CbAgo)                                                       | PD-1 sub-nM hit measured as bivalent Fc fusion (avidity); single assay format                                             |
| PXDesign (PXDesign-d) [@pxdesign]                          | 6 author-selected targets                                                             | 9–17/target                                        | BLI > 0.06 nm at 1 µM then $K_D$ < 1,000 nM; 20–73% on 5 targets, 0/16 TNFα                                                                            | Expression attrition shifts rates (PD-L1: 72.7% tested vs. 47.1% sent); wet-lab tested diffusion mode only                |
| ESMFold2 campaign [@esmc]                                  | 5 author-selected targets (minibinders and scFvs)                                     | 84/cohort                                          | BLI stringent (0.25–0.4 nm) and inclusive (> 0.1 nm); mean 70.0% minibinders (best 68 pM), 21.0% scFvs                                                 | Author-selected targets; cutoff shading image-only; best-hit target not stated in text                                    |
| **Nanobodies and antibodies**                              |                                                                                       |                                                    |                                                                                                                                                        |                                                                                                                           |
| RFantibody [@rfantibody]                                   | 4 targets (yeast display); 3 targets (SPR)                                            | 9,000/target (display); 95/target (SPR)            | Yeast display or single-concentration SPR; 0–2% confirmed hit rate, best 78 nM (HA), 1.4 µM (RSV site III)                                             | Authors note library screening remains necessary given current success rates                                              |
| BoltzGen / BoltzProt-1 [@boltzgen; @boltzprot1]            | 9 novel targets (\<30% PDB identity, BoltzGen); 10 low-homology targets (BoltzProt-1) | 15/target                                          | BoltzGen: sensorgram or ≥ 300% control (6/9 targets, best 6.1 nM VHH); BoltzProt-1: flipped orientation + vendor confirmation (8.0% vs. 3.3% BoltzGen) | BoltzProt-1 separates orthogonal confirmation from screening hits; API-only (weights closed)                              |
| Chai-2 [@chai2]                                            | 52 novel targets (scFv/VHH); 5 targets (minibinders)                                  | ≤ 20/target/format (Ab); 20–25 (minibinders)       | BLI > 0.1 nm and > 300% background; 16% combined Ab (26/52 targets), 68% minibinders (best 18.3 pM)                                                    | Undisclosed generative architecture; avidity flagged on EFNA5 scFv and 4/10 minibinder affinities                         |
| Protenix-v2 [@protenix_v2]                                 | Novelty-filtered soluble panel + 4 GPCRs                                              | 16–30/target (GPCRs); figure-only (soluble)        | BLI > background + 0.05 nm; binders on all soluble targets (2–48%), GPCR VHH-Fc 16–88%, mAb 0–50%                                                      | Manually chosen in-stock targets and epitopes; bivalent VHH-Fc avidity (including 112 pM GPRC5D)                          |
| Germinal / mBER [@germinal; @mber]                         | 4 VHH + 2 scFv targets (Germinal); 145 of 436 targets, random hotspots (mBER)         | 43–101 ordered (Germinal); 1,153,241 pooled (mBER) | Germinal: split-luciferase + BLI (or SPR + BLI for Fab, best 170 nM VHH); mBER: phage enrichment (median ~0.4%, up to 38% ipTM-filtered)               | Germinal VHH rates use BLI sub-denominators; mBER reports phage enrichment without affinity quantification                |
| **Macrocyclic peptides**                                   |                                                                                       |                                                    |                                                                                                                                                        |                                                                                                                           |
| RFpeptides [@rfpeptides]                                   | 4 author-selected targets                                                             | 6–14 tested (of 11–27 selected)                    | SPR single-cycle kinetics at 100 µM (no numeric cutoff); 2–4 hits/target, best 6 nM (GABARAP), crystal structures                                      | Synthesis attrition (14/27 MCL-1, 11/26 RbtA tested); single assay format                                                 |
| Latent-X1 / Latent-X2 (macrocycles) [@latentx1; @latentx2] | 3 RFpeptides-matched targets (X1); 2 targets (X2)                                     | 11–17 of 30 submitted (X1); 10/target (X2)         | SPR measurable signal (X1: 91–100%, best 5.35 µM); BLI > 0.1 nm and kinetics (X2: 9/10 PHD2, 8/10 K-Ras G12D, best 1.54 nM)                            | Undisclosed architecture; synthesis attrition in X1; single assay format                                                  |

Three experimental factors explain much of the apparent spread in published hit
rates and affinities. Hit definitions and assay rigor vary widely: some studies
call binders from a single permissive screen, such as a qualitative surface
plasmon resonance (SPR) signal without a numeric cutoff \[@bindcraft;
@rfpeptides; @latentx1\] or a small single-point biolayer interferometry (BLI)
shift of 0.05 to 0.1 nm above background [@protenix_v2; @pxdesign; @chai2],
whereas others verify candidates in a second, independent assay that eliminates
many initial hits. For example, BoltzProt-1 separates initial screening hits
(comparable to what earlier campaigns typically report as binders) from
confirmed binders verified by reversing sensor immobilization orientation and
independent vendor re-testing [@boltzprot1], and Germinal similarly confirmed
Fab hits across both SPR and BLI [@germinal]. Multivalent avidity also inflates
apparent affinities when binders are tested as dimeric Fc fusions or under dense
sensor-immobilization setups that allow simultaneous multi-site engagement, a
caveat flagged on headline picomolar and sub-nanomolar hits in Protenix-v2,
BindCraft, and Chai-2 [@protenix_v2; @bindcraft; @chai2]. Finally, excluding
constructs that fail chemical synthesis or protein expression shrinks the
hit-rate denominator: cyclic-peptide campaigns such as RFpeptides and Latent-X1
often assayed only about half of the sequences selected for synthesis
[@rfpeptides; @latentx1], and PXDesign showed on PD-L1 that omitting six poorly
expressing designs raised its reported hit rate from 47.1% of ordered constructs
to 72.7% of tested constructs [@pxdesign].

Target and epitope selection biases are equally consequential. Most published
campaigns test a handful of targets and epitopes selected by the authors, yet
binding difficulty varies sharply even across sites on a single protein: two
epitopes on the same antigen (AMBP) in Protenix-v2 yielded 4% and 48% hit rates
[@protenix_v2]. The scale of this selection effect was quantified by mBER, which
designed more than 1.15 million unique VHHs across 436 human cell-surface
targets (145 assayed by phage display without affinity measurement) targeting
randomly sampled exposed surface hotspots [@mber]. Across uncurated hotspots,
mBER's median per-design hit rate was roughly 0.4%, two orders of magnitude
below curated small-panel headlines, whereas its best individual hotspots
reached 7.5% overall and 38% (8/21) within an ipTM-filtered bin [@mber]. Even
when identical molecules are re-tested across laboratories, assay conditions
shift measured performance. When AlphaProteo resynthesized RFdiffusion's full
published panels (including nonbinders) for yeast display at 10- to 20-fold
lower target concentrations, hit rates fell from 33% to 16% on IL-7Rα and from
6% to 0% on TrkA [@alphaproteo; @rfdiffusion]. Similarly, when Latent-X1
resynthesized RFpeptides' two best macrocycles and re-tested them in its own SPR
assay, the exact same peptides measured 4.4- to 5-fold weaker than originally
published, shifting from 1.90 to 8.38 µM on MDM2 and from 2.0 to 10.0 µM on
MCL-1 [@latentx1; @rfpeptides]. Given how strongly assay choices, target
curation, and post-hoc filtering shape reported hit rates, wet-lab claims from
closed commercial systems cannot be independently verified or reproduced when
their architectures, weights, and filtering pipelines remain undisclosed
[@bender_perspective]. This limitation applies to AlphaProteo [@alphaproteo],
Chai-2 [@chai2], Latent-X1 and Latent-X2 [@latentx1; @latentx2], API-only
BoltzProt-1 [@boltzprot1], and unpublished models such as IsoDDE, which is known
publicly only from third-party scaling plots [@opendde].

## 4. From In Vitro Binding Hits to Drug Leads

### The translational gap

Nearly every de novo binder-design study frames its work around therapeutic
discovery, from accelerating biologic drug development to engineering species
cross-reactivity or blocking clinically relevant interactions \[@boltzgen;
@chai2; @bindcraft; @latentx2; @mber\]. Reviewing a decade of artificial
intelligence in pharmaceutical research, Bender et al. draw a useful distinction
between model validation and process validation [@bender_perspective]. Model
validation measures performance on an isolated task, such as predicting accurate
complex structures or recovering nanomolar in vitro hits, whereas process
validation asks the harder translational question of whether those outputs
actually improve downstream drug-discovery decisions and reduce clinical failure
[@bender_perspective]. Public databases already contain more than $10^6$
bioactive small molecules compared with roughly $10^3$ marketed drugs, a
reminder that confirming target binding in a biophysical assay is only the first
step toward a viable peptide or protein drug [@bender_perspective].

Clinical viability simultaneously demands high expression, solubility, thermal
stability, low self-association, minimal immunogenicity, suitable
pharmacokinetics, and the intended functional modulation rather than passive
binding [@bender_perspective; @latentx2]. The blinded AIntibody challenge
offered a stark empirical illustration of this trade-off: on its out-of-library
engineering task, 30.4% of computational designs failed to bind, and the
highest-affinity binder in the entire competition (2.9 pM) failed to elute from
a hydrophobic interaction chromatography (HIC) developability column
[@aintibody]. Despite these requirements, nearly all open generative frameworks
still optimize and filter exclusively for predicted binding geometry, leaving
developability and immunogenicity to downstream screening. Closed platforms
suggest that multi-parameter design is feasible: Latent-X2 reports de novo
macrocycles and antibodies with developability and low-immunogenicity profiles
matching or exceeding approved therapeutics, including binders on 9 of 18
antibody targets down to 26.2 pM [@latentx2]. Yet its undisclosed architecture
prevents independent analysis of how those competing properties are balanced
[@latentx2].

### Quantitative protein–protein affinity prediction

Even once a campaign identifies an initial binder, optimizing its potency still
lacks reliable computational guidance, as predicting quantitative binding
affinity ($K_D$) for protein–protein complexes remains unsolved. Current
co-folding confidence scores behave mainly as binary indicators of whether a
complex forms rather than calibrated free-energy estimators, so they cannot
distinguish weak micromolar hits from nanomolar leads or guide affinity-maturing
mutations. BindCraft explicitly notes that AlphaFold2 ipTM separates binders
from nonbinders without predicting how tightly they bind [@bindcraft]. The same
bottleneck appeared across computational methods in the blinded AIntibody
challenge, where only 1 of 26 participating groups outperformed random selection
when ranking closely related antibody clones (sharing the same HCDR3 loop) by
binding strength [@aintibody]. Dedicated affinity-prediction heads added onto
co-folding models, such as Boltz-2's binding-affinity head, have so far achieved
strong accuracy only on small-molecule free-energy benchmarks, because they are
trained exclusively on single-protein ligand assays and do not apply to
multimeric protein–protein interactions [@boltz2]. Consequently, potency ranking
and affinity maturation continue to depend on experimental kinetics after
design.

### Targets without experimental structures and conformational dynamics

Current design workflows remain heavily tied to static, experimentally solved
target structures and struggle with flexible, uncharacterized, or intrinsically
disordered proteins. Nearly all successful wet-lab campaigns so far have started
from an experimental crystal or cryo-electron microscopy structure of the target
protein, or from a well-folded predicted domain \[@rfdiffusion; @bindcraft;
@rfpeptides; @latentx1\]. For structurally uncharacterized targets without a
solved structure, how reliably binder design works when starting solely from a
predicted target model remains largely untested, a caveat Germinal explicitly
noted after running designs against AlphaFold3-predicted targets [@germinal].
Flexible loops and intrinsically disordered regions pose an even deeper
challenge because they lack a single fixed conformation in solution, whereas
PDB-trained co-folders produce static snapshots and can hallucinate artificial
secondary structure across disordered stretches unless explicitly mitigated
during training [@alphafold3]. Recent campaigns have begun targeting flexible
extracellular loops on GPCRs [@protenix_v2] and probing disordered proteins such
as NPM1, where BoltzGen observed live-cell nucleolar co-localization for 1 of 5
designed peptides without yet confirming direct binding to the disordered region
[@boltzgen]. Overall, reliable design against dynamic or structurally
uncharacterized proteins remains an open problem.

### Blinded prospective benchmarks for de novo design

Beyond these technical challenges, the field still lacks a standardized, blinded
prospective wet-lab benchmark for target-conditioned de novo binder design.
Structure prediction matured rapidly around shared blind assessments such as
CASP and unified benchmark suites like FoldBench [@foldbench], where models are
scored under common protocols on held-out experimental structures. De novo
binder evaluation is harder to standardize because every proposed sequence must
be synthesized, expressed, and assayed physically, leaving the field dependent
on disconnected, self-selected campaigns. Full-campaign independent replication
remains rare, with AlphaProteo's re-testing of RFdiffusion's full panels as a
notable exception [@alphaproteo; @rfdiffusion], and retrospective meta-analyses
such as Overath et al. standardize computational scoring without removing assay
heterogeneity across source studies [@overath_meta]. The blinded AIntibody
challenge showed that unified wet-lab benchmarking across 29 organizations is
feasible, combining independent affinity kinetics with a five-assay
developability panel, yet it tested library-conditioned antibody optimization
against a single well-characterized antigen (SARS-CoV-2 RBD) rather than
target-conditioned de novo design across diverse modalities [@aintibody].
Extending blinded, multi-group prospective evaluation to novel targets and
uncurated epitopes across peptides, minibinders, and antibodies, with full
reporting of ordered constructs, independent binding confirmation, and
developability profiling, will be necessary to measure genuine progress cleanly.

## Conclusions

Within a few years, biomolecular co-folding models have transformed de novo
binder design from massive empirical library screening into targeted
computational sequence generation. Across peptides, minibinders, and antibody
formats, workflows built on either MSA-based or single-sequence language-model
trunks can now yield nanomolar binders from tens of tested candidates on
well-characterized targets. Tracing these systems from their underlying
components shows that no single architecture dominates every setting, as each
approach carries distinct strengths and limitations in single-sequence
differentiability, sampling speed, all-atom chemical generality, and
stereochemical fidelity. At the same time, rapid generative progress has shifted
the primary bottleneck away from proposing plausible folds and toward selecting
real binders. Structure-prediction confidence heads estimate coordinate error on
solved complexes rather than binding thermodynamics, so they still misrank
accurate poses, fluctuate across targets, and can be outperformed by classifiers
trained directly on wet-lab outcomes. Comparing published campaigns further
requires looking past headline hit rates to assay rigor, multivalent avidity
effects, construct attrition, and target curation, while quantitative
protein–protein affinity prediction and flexible or uncharacterized targets
remain open technical frontiers. Turning in vitro binding hits into developable,
functionally active drug leads, and testing genuine progress through transparent
methods and shared, blinded prospective benchmarks, will define the next stage
of computational binder design.

## Acknowledgments

Acknowledgments, author contributions, financial disclosures, competing
interests, data availability, and AI-assistance disclosures required by *PLOS
Computational Biology* will be completed prior to submission.

## References

All inline citations use verified Pandoc keys resolving to the repository BibTeX
catalog for compilation into numbered Vancouver-style references upon manuscript
submission.
