# Generative Methods for De Novo Binder Design: Architectural Trade-offs and Experimental Reality

*Draft Review Manuscript prepared for PLOS Computational Biology. Authors,
affiliations, and required journal statements to be finalized prior to
submission.*

## Abstract

Advances in protein structure prediction and biomolecular co-folding have
enabled computational de novo binder design against specific protein targets.
Generative models conditioned on target structures now narrow experimental
testing from massive empirical libraries to tens of candidates for peptides,
minibinders, and antibodies. This review examines how multi-chain structure
predictors are turned into binder-design workflows, focusing on two core
mechanistic trade-offs: supplying evolutionary information through multiple
sequence alignments or protein language models, and generating atomic
coordinates through regression, diffusion, or flow matching. We trace how these
architectural choices give rise to generate-and-filter pipelines, unified
all-atom diffusion models, and gradient-based sequence optimization. We then
assess why structural confidence filters remain an imperfect guide to candidate
selection and why experimental differences prevent treating published wet-lab
hit rates as direct comparisons. Finally, we outline the main technical and
translational bottlenecks separating in vitro binding hits from developable drug
leads.

## Introduction

Artificial intelligence transformed structural biology by bringing protein
structure prediction to near-experimental accuracy. AlphaFold2 marked this
turning point at CASP14, using coevolutionary signals in multiple sequence
alignments (MSAs) to predict single-chain folds to a median Cα root-mean-square
deviation (RMSD) of 0.96 Å at 95% residue coverage [@alphafold2]. AlphaFold3
subsequently extended this framework to complexes containing proteins, nucleic
acids, small-molecule ligands, and ions, establishing biomolecular co-folding as
a general modeling paradigm [@alphafold3]. With reliable complex prediction in
hand, the field has moved quickly to the inverse challenge: repurposing these
neural architectures to generate de novo binders against specific targets.

Moving from complex prediction to binder generation draws on the same core
architecture. Supplying the sequences of all interacting chains asks the network
to predict the three-dimensional complex, whereas leaving the binder chain
masked or initialized as noise asks the same model to generate a complementary
partner [@rfdiffusion; @boltzgen]. What differs sharply in practice is search
and validation. Evaluating a structure predictor starts from a given natural
sequence whose predicted geometry can be scored purely in silico against a
held-out crystal or cryo-electron microscopy structure in the Protein Data Bank
(PDB). In de novo design, the sequence itself is unknown and must be discovered
from a combinatorial space of $20^L$ possibilities for a chain of length *L*
without evolutionary alignments or a pre-existing experimental reference.
Confirming binding therefore requires synthesizing and assaying candidates in a
wet laboratory.

Many therapeutically relevant protein targets present broad, flat surfaces that
lack the deep pockets required by small-molecule drugs. Engaging these surfaces
calls for peptides, compact de novo proteins (minibinders), or antibody formats
such as nanobodies (VHHs), single-chain variable fragments (scFvs), and
monoclonal antibodies (mAbs). Conventional discovery obtains these binders by
screening vast random display libraries or immunizing animals, a process that
must be repeated for each new target and offers limited control over the binding
site. Generative and filtering pipelines instead propose candidate sequences
against a chosen structure, reducing experimental testing from thousands or
millions of variants in empirical screens and early computational campaigns
[@chai2; @rfantibody] to tens of synthesized designs per target \[@chai2;
@rfpeptides; @boltzgen; @protenix_v2\].

Written from a drug-discovery and protein-engineering perspective, this review
examines de novo protein- and peptide-design methods, emphasizing underlying
mechanisms and architectural trade-offs rather than ranking models. We first
describe how structure-prediction trunks and coordinate-generation modules work,
then trace how those components give rise to distinct binder-design workflows,
evaluate computational filtering limits alongside wet-lab campaign evidence, and
conclude with the translational and technical bottlenecks separating in vitro
binding hits from viable drug leads. Small-molecule drug design, which operates
on variable chemical graphs governed by valence rules, requires separate
architectures and benchmarks, placing it outside the scope of this review.

## 1. Co-folding Architectures and Mechanistic Trade-offs

### The two-stage co-folding pipeline

Modern protein structure prediction rests on the principle that correlated
mutations between positions in an MSA reflect spatial proximity in the folded
protein [@alphafold2]. Most contemporary co-folding models build on this
principle through a two-stage pipeline (Fig 1). In the first stage, a deep
sequence-to-pairwise reasoning trunk transforms sequence and evolutionary inputs
into single-residue and pairwise representations. Examples include the Evoformer
in AlphaFold2 [@alphafold2], the simplified Pairformer shared by AlphaFold3,
Boltz, Chai-1, Protenix, and RoseTTAFold3 \[@alphafold3; @boltz1; @chai1;
@protenix_v1; @rosettafold3\], and the recurrent folding trunk in ESMFold and
ESMFold2 [@esm2; @esmc]. A linear projection on the pairwise representation
predicts a distogram, giving a probability distribution over binned physical
distances for every residue pair, typically 2 to 22 Å in 64 bins. For binder
design, the entire trunk is differentiable and executes in a single forward pass
for a given complex [@boltz1], so the distogram can serve both as a training
loss and as a smooth surrogate objective during sequence optimization
[@alphafold2; @boltzdesign1; @esmc]. In the second stage, a dedicated coordinate
module converts these learned representations into explicit atomic positions.
This two-stage layout contrasts with notable alternative architectures. Early
RoseTTAFold propagated parallel one-dimensional sequence, two-dimensional
pairwise distance, and three-dimensional coordinate tracks throughout the
network, allowing spatial motifs and target geometry to be supplied as input
coordinates [@rosettafold; @rosettafold2]. ESM3 takes a different route,
encoding sequence, structure, and function as discrete tokens within a
multimodal masked language model so that any track can be prompted or generated
jointly [@esm3].

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

How evolutionary information enters the trunk creates a central mechanistic
divide in binder design. Standard MSA-based co-folders, including AlphaFold2,
AlphaFold3, RoseTTAFold3, Boltz, and Protenix, retrieve homologous sequences
from large databases at inference time \[@alphafold2; @alphafold3;
@rosettafold3; @boltz1; @protenix_v1\]. Database retrieval is discrete,
non-differentiable, and undefined for a synthetic binder sequence with no
natural homologs. Consequently, whenever an MSA-trained model evaluates or
optimizes a de novo binder chain, that chain must run in single-sequence mode
(without an MSA), even if the target protein carries a deep alignment. Both the
AlphaFold2 and AlphaFold3 studies report that shallow-MSA and single-sequence
inputs represent their weakest accuracy regime [@alphafold2; @alphafold3].

Replacing database lookups with a protein language model (PLM) embeds
evolutionary statistics into network weights learned from billions of natural
sequences. ESM-2 and ESMFold established that single-sequence structure
prediction without MSAs or templates is feasible, initially trading lower
accuracy than AlphaFold2 for substantially faster inference [@esm2]. Recent
scaling of this approach has closed much of that gap for complex interfaces.
ESMC is a PLM trained on roughly 2.8 billion sequences, whose frozen
6-billion-parameter representations drive ESMFold2 through 48 recurrent
pair-state folding layers (24 in ESMFold2-Fast) and a sliding-window
atom-attention diffusion transformer [@esmc]. In single-sequence mode, ESMFold2
matches MSA-enabled AlphaFold3 on antibody–antigen structure prediction, a
parity confirmed by independent AtlasFold benchmarks [@atlasfold], while
retaining an optional detachable MSA encoder for unusually high-perplexity
sequences [@esmc]. For binder design, this architecture provides a clear
advantage: because a PLM expects single sequences natively, gradients from the
folding trunk and distogram can propagate all the way back through the PLM into
the input sequence representation without pushing the designed chain outside its
training distribution [@esmc].

Hybrid architectures bridge these two input modes. Chai-1 incorporates both an
MSA track and a PLM track that can operate independently or jointly, alongside
optional experimental contact or pocket restraints [@chai1]. On antibody–protein
interfaces, where natural cross-chain coevolution is weak, single-sequence
Chai-1 matches its MSA-enabled mode and outperforms MSA-driven
AlphaFold-Multimer v2.3 [@chai1]. Taken together, these results explain why
single-sequence PLM trunks are particularly well suited to designed peptides,
minibinders, and antibody loops whose sequences lack paired evolutionary
alignments.

### Coordinate-generation strategies and physical stereochemistry

The second major architectural choice governs how trunk representations become
atomic coordinates, trading off inference speed, chemical generality, and
end-to-end differentiability. Single-pass coordinate regression, introduced in
AlphaFold2's Invariant Point Attention (IPA) structure module and adopted in
ESMFold, updates rigid residue frames in one forward pass [@alphafold2; @esm2].
Because coordinates are regressed through a shallow, deterministic module rather
than over hundreds of iterative steps, gradients from three-dimensional
geometric and confidence losses propagate cleanly back to the input sequence
[@alphafold2; @bindcraft]. However, frame-based IPA modules are tailored to
canonical amino-acid backbones and do not naturally generalize to arbitrary
non-protein atoms or unusual covalent chemistries.

To unify proteins, nucleic acids, small molecules, ions, and modified or
cyclized peptides within one coordinate head, AlphaFold3 replaced IPA with an
iterative all-atom diffusion module that transforms Gaussian noise into atomic
coordinates along a stochastic differential equation trajectory [@alphafold3].
Subsequent all-atom co-folders, including Boltz, Chai-1, Protenix, RoseTTAFold3,
and ESMFold2, adopted variants of this diffusion formalism \[@boltz1; @chai1;
@protenix_v1; @rosettafold3; @esmc\]. Unlike single-pass regression, stochastic
diffusion samples a distribution of plausible structures instead of outputting
one deterministic pose. In practice, co-folders run multiple model seeds and
draw a batch of diffusion samples per trunk pass before using an internal
confidence head to select a top-ranked prediction, for example five seeds with
five samples each in standard AlphaFold3 inference [@alphafold3]. These gains in
chemical generality come at two practical costs for binder design. First,
iterative denoising is slow, often requiring hundreds to roughly 1,000 forward
passes per generated structure [@frameflow]. Second, unrolling those denoising
steps to compute sequence gradients is computationally impractical, breaking the
simple end-to-end backpropagation path available in IPA regression models
[@boltzdesign1].

Flow matching addresses the sampling bottleneck by formulating coordinate
generation as an ordinary differential equation (ODE) with straighter transport
trajectories requiring far fewer integration steps. On unconditional protein
monomers, FrameFlow recast frame diffusion as flow matching and reported twofold
higher designability at five times fewer timesteps [@frameflow].
Target-conditioned flow models, including PPIFlow, OriginFlow, AtomFlow, and
D-Flow, extend these faster trajectories to protein–protein interfaces
[@ppiflow; @originflow; @atomflow; @dflow]. Beyond faster sampling, few-step ODE
decoders can restore end-to-end differentiability through all-atom coordinates
[@pxdesign].

Predicting free three-dimensional coordinates in all-atom diffusion models also
introduces physical-validity errors that rigid amino-acid frames largely
avoided. Because bond geometry and handedness are learned from data rather than
fixed by residue templates, AlphaFold3 reported occasional steric clashes and a
4.4% chirality violation rate on the PoseBusters physical-plausibility benchmark
[@posebusters] for protein–ligand complexes, despite penalizing such violations
when ranking its sampled structures [@alphafold3]. Two strategies address this
limitation. Boltz-1x applies explicit steering potentials during denoising to
suppress clashes and inverted stereocenters [@boltz1]. RoseTTAFold3 instead
encodes stereochemistry during training to avoid perturbing inference
trajectories, achieving 1.74 Å mean backbone RMSD on mixed L/D peptides compared
with 1.88 Å for AlphaFold3 and 2.24 Å for Boltz-1x [@rosettafold3].

## 2. Design Workflows: Turning Predictors into Binder Generators

Structure predictors evaluate one candidate at a time, making blind exploration
of sequence space impractical. Binder-design systems therefore repurpose these
networks through three primary workflows (Fig 1B). The first generates a
three-dimensional binder geometry against the target, assigns a compatible
sequence with a separate inverse-folding model, and refolds the complex to
filter candidates. The second trains a single all-atom diffusion network to
generate atomic coordinates and amino-acid identities simultaneously,
eliminating the inverse-folding handoff before refolding-based filtering. The
third keeps a trained structure predictor fixed and optimizes the binder
sequence by gradient descent until the network produces a high-confidence
complex. Table 1 summarizes representative open and commercial systems from
these three families, comparing their trunk inputs, coordinate formalisms,
supported modalities, and methodological openness.

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
condition on its structure [@rfdiffusion]. Because the model outputs only a
sequence-free backbone, an inverse-folding network such as ProteinMPNN next
assigns compatible amino-acid sequences to the generated geometry
[@proteinmpnn]. Candidates are then refolded in complex with the target using
AlphaFold-Multimer or chain-break-adapted AlphaFold2 and triaged on confidence
and self-consistency thresholds [@rfdiffusion]. AlphaProteo illustrates typical
cutoffs by requiring an interchain predicted aligned error (iPAE) below 10 Å, a
binder-aligned RMSD below 1 Å, and a per-residue confidence (pLDDT) above 80
[@alphaproteo]. Clearing these computational filters does not guarantee wet-lab
success. As the ProteinMPNN authors noted, high native sequence recovery on
offline fixed-backbone benchmarks does not necessarily predict whether a
designed sequence will fold accurately [@proteinmpnn]. Likewise, the in silico
success rates frequently quoted for backbone generators measure self-consistency
with a refolding predictor, not experimental target engagement [@rfdiffusion].

Targeted architectural modifications extend this decoupled workflow to new
modalities and scales. RFdiffusion3 moved away from fine-tuning a RoseTTAFold
predictor altogether, instead pre-training a compact 168-million-parameter
all-atom transformer U-Net modeled on AlphaFold3's diffusion module using PDB
structures and AlphaFold2-predicted models [@rfdiffusion3]. By trimming its
Pairformer trunk from 48 to 2 layers and sampling in 100 steps, RFdiffusion3
runs roughly an order of magnitude faster than earlier releases and pairs with
LigandMPNN in place of ProteinMPNN whenever non-protein atoms such as ligands,
nucleic acids, or metal ions are present [@rfdiffusion3; @ligandmpnn]. For
specialized topologies like head-to-tail macrocycles, RFpeptides adds a cyclic
relative positional encoding to RFdiffusion and RoseTTAFold2 [@rfpeptides].
After inverse folding and filtering with cyclic AlphaFold2 (AfCycDesign)
[@afcycdesign], RFpeptides yielded binders against all four targets from fewer
than 20 synthesized peptides per target, supported by experimental crystal
structures [@rfpeptides]. Related variants in Table 1 explore alternative
inverse-folding architectures in AlphaDesign [@alphadesign], adapt backbone
generation for antibody loops in RFantibody [@rfantibody], replace frame
representations with Cartesian diffusion transformers in PXDesign-d [@pxdesign],
or accelerate sampling through ODE flow matching in PPIFlow and AtomFlow
[@ppiflow; @atomflow].

### Unified prediction-and-design all-atom models

A second workflow eliminates the handoff between geometry generators and
inverse-folding models by training a single all-atom diffusion network jointly
for structure prediction and de novo sequence–structure generation. BoltzGen
exemplifies this unified approach under a fully reproducible MIT release
providing model weights, training code, and datasets [@boltzgen]. Conditioned on
a target, BoltzGen simultaneously generates atomic coordinates and amino-acid
identities for masked binder chains, covering peptides, minibinders, and
nanobodies, though full antibodies were excluded from training [@boltzgen]. It
matches the structure-prediction accuracy of Boltz-2 on the same benchmark test
set, yet its design pipeline relies on Boltz-2 to refold and filter generated
candidates [@boltzgen]. Commercial systems such as Chai-2 and Latent-X may use
related co-design strategies internally, but their generative architectures
remain undisclosed [@chai2; @latentx1; @latentx2]. BoltzGen therefore stands as
the clearest open representative of this class, while its successor BoltzProt-1
is offered through a commercial API [@boltzprot1].

Joint all-atom training also exposes how generative diffusion models memorize
biases in the Protein Data Bank. The BoltzGen authors documented that at
designed binder lengths between 73 and 76 residues, structural diversity
collapses as the model overwhelmingly samples ubiquitin, an artifact traced to
more than 900 ubiquitin entries in the PDB [@boltzgen]. More broadly, the
authors caution that even unified all-atom design is neither "zero-shot" nor
"plug-and-play" in practice, recommending manual inspection and iterative reruns
over unexamined automated selection [@boltzgen].

### Gradient-based sequence optimization

The third workflow turns a frozen structure predictor into a generator via
gradient descent, often termed hallucination or model inversion. Because
discrete residue identities cannot be differentiated, the binder sequence is
relaxed into a continuous probability distribution over the 20 amino acids at
each of *L* positions, represented as an *L* × 20 weight matrix. At each
optimization step, this soft sequence is passed alongside the target through the
differentiable predictor to compute a design loss favoring confident folding and
tight interchain contacts. Gradients of that loss flow backward through the
network to update the sequence weights, nudging each position toward amino acids
that improve the predicted complex. To obtain a discrete sequence, a
temperature-annealing schedule gradually sharpens these distributions over
iterations until each position commits to a one-hot residue, a strategy
popularized by ColabDesign [@colabdesign].

When the predictor uses a single-pass IPA regression module, gradients propagate
cleanly from predicted three-dimensional coordinates and confidence heads back
to the input sequence [@alphafold2]. BindCraft exploits this full-network
differentiability in AlphaFold-Multimer, cycling randomly among its five
independently trained models between iterations to curb overfitting
[@bindcraft]. It sharpens the binder sequence over four stages, annealing
continuous amino-acid weights into discrete residues with a straight-through
step that sends one-hot sequences forward and continuous gradients backward,
before a final mutation-refinement step [@bindcraft]. A ProteinMPNN variant then
redesigns non-interface residues to improve stability and solubility
[@bindcraft]. A notable mechanistic feature of BindCraft is that it repredicts
the target structure at every optimization step, permitting induced-fit
rearrangements ranging from 0.5 to 5.5 Å Cα RMSD [@bindcraft]. For cyclic
peptides, AfCycDesign applies a cyclic relative positional offset to
AlphaFold2's peptide chain while keeping the target linear, yielding eight
monomer crystal structures within 1.0 Å of design, though its MDM2 and Keap1
binders relied on motif grafting rather than de novo hallucination
[@afcycdesign]. However, both BindCraft and AfCycDesign rely on MSA-trained
AlphaFold2 models for invented binder chains that lack evolutionary alignments,
forcing optimization into the predictor's weakest, MSA-free regime
\[@alphafold2; @bindcraft; @afcycdesign\].

Adapting gradient optimization to diffusion-based co-folders requires
circumventing the cost of differentiating through hundreds of denoising steps
[@boltzdesign1]. Two solutions have proved effective. The first computes
gradients exclusively from the differentiable trunk's distogram and confidence
heads while placing a stop-gradient on the diffusion module to block
backpropagation through iterative denoising. BoltzDesign1 applies this strategy
to Boltz-1's 64-bin Pairformer distogram, optimizing the pairwise distance
distribution from which diffusion samples; on 212 BindCraft binders, Pairformer
contacts matched diffusion-sampled contacts on 76% of designs [@boltzdesign1].
ESMFold2 applies the same distogram-gradient strategy through its native
single-sequence PLM trunk, invoking the diffusion and confidence modules only at
the end to score interface predicted TM-score (ipTM) [@esmc]. The second
solution preserves coordinate-level backpropagation by replacing iterative
diffusion with a few-step deterministic decoder. Built on the open
AlphaFold3-style predictor Protenix, PXDesign-h substitutes a differentiable
two-step ODE sampler for its 200-step diffusion module and optimizes against
five ensemble models resampled at each step [@pxdesign].

Optimizing a sequence solely for high predicted confidence can produce unnatural
amino-acid compositions that exploit a single predictor's blind spots rather
than genuinely folding and binding. To prevent such adversarial designs, recent
gradient methods add language-model priors or restrict search to discrete
mutations. Native PLM trunks such as ESMC guide designed sequences toward
natural protein statistics during backpropagation [@esmc]. For MSA-based
predictors, external language models can provide a similar guardrail: Germinal
combines live gradients from an antibody language model (IgLM) and
AlphaFold-Multimer [@germinal], whereas mBER incorporates fixed sequence
preferences from ESM-2 [@mber]. Taking a complementary route, RFOptimization
avoids continuous sequence relaxation altogether [@rfoptimization]. It keeps
sequences strictly discrete, using RoseTTAFold3 gradients only to propose
single-point mutations that are accepted or rejected iteratively. To curb
predictor-specific overfitting, it interleaves Boltz refolding with LigandMPNN
resampling while holding out AlphaFold3 as an independent check
[@rfoptimization].

## 3. Candidate Selection and Experimental Evidence

### Candidate selection and filtering limits

Evaluating a structure predictor against an experimentally solved reference uses
external accuracy metrics, such as DockQ interface scores [@dockq] and atomic
RMSD [@kabsch]. As de novo binders lack an experimental structure, every design
workflow relies on internal self-consistency checks and model-estimated
confidence scores to select the small subset of candidates ordered for wet-lab
testing. Standard filters combine self-consistency RMSD between generated and
refolded coordinates with pLDDT [@alphafold2], ipTM, and iPAE
[@alphafold_multimer]. Recent pipelines increasingly adopt ipSAE, which
restricts ipTM to interchain residue pairs below a fixed PAE threshold so that
disordered tails or arbitrary chain trimming do not dilute interface scores
[@ipsae]. Yet structure-prediction confidence heads are trained on solved bound
complexes to estimate coordinate error, not to distinguish binders from
nonbinders or predict affinity. High structural confidence therefore does not
guarantee wet-lab binding on unseen designs. Three lines of evidence show why
these scores fall short for candidate selection.

As described in Section 1, co-folding predictors sample a pool of candidate
structures for each input and rely on internal confidence scores to pick a top
prediction, but even on known complexes those heads routinely fail to rank the
most accurate pose first. Evaluating seven predictors on FoldBench, a benchmark
of experimentally solved complexes [@foldbench], AtlasFold compared each model's
top-ranked prediction against the best structure generated in the same run and
found a consistent selection gap [@atlasfold]. Specifically, confidence ranking
missed an acceptable pose (DockQ > 0.23) already present among the generated
samples on 11 to 21% of antibody–antigen complexes (4.5% for Boltz-1) and 3 to
8% of general protein–protein interfaces [@atlasfold]. The FoldBench study
itself documented a closely related failure mode for antibodies: a predictor can
model the key CDR-H3 binding loop accurately while docking the antibody at the
wrong site, and per-sample confidence scores do not reliably distinguish
near-native poses from misdocked decoys [@foldbench].

Although confidence filters raise hit rates in large candidate pools [@mber],
their accuracy in predicting wet-lab binding fluctuates sharply between targets.
Overath et al. illustrated this variability by re-scoring 3,766 experimentally
tested designs against 15 targets from six published campaigns through a uniform
pipeline [@overath_meta]. AlphaFold3 ipSAE emerged as the strongest overall
predictor of binding, with its average precision spanning 0.1 to 1.0 depending
on the target, partly reflecting heterogeneous source assays and older design
models in the pooled dataset [@overath_meta]. In the Germinal antibody campaign,
many nonbinders cleared the same ipSAE threshold as validated binders
[@germinal]. Evaluating refolding filters on a shared experimental benchmark,
PXDesign found that Protenix and AlphaFold2 selected largely different subsets
of true binders and that no single cutoff maximized accuracy on all targets
simultaneously [@pxdesign].

Replacing structure-prediction confidence with classifiers trained on wet-lab
binding outcomes can also substantially improve hit rates on identical candidate
pools. In a controlled comparison on 10 low-homology targets, BoltzProt-1 kept
the BoltzGen generator and a fixed budget of 15 designs per target, swapping
BoltzGen's confidence scores for BoltzPPI, a classifier trained on experimental
binding data [@boltzprot1]. This change alone more than doubled confirmed
binders from 3.3% (5/150) to 8.0% (12/150), expanding confirmed hits from 2 to 4
of the 10 targets [@boltzprot1]. Candidate ranking therefore shapes experimental
yield independently of the generative architecture.

### Reading wet-lab campaigns critically

Recent experimental campaigns spanning compact minibinders, nanobodies,
antibodies, and cyclic peptides have shown that computational de novo design can
routinely produce nanomolar and occasionally picomolar binders from modest
synthesis budgets. Table 2 compiles representative studies grouped by modality
alongside their target scope, number of designs tested, binding criteria, and
key caveats. Because no two de novo campaigns share a common target panel, assay
format, or positivity threshold, headline hit rates should be read as
context-dependent demonstrations rather than head-to-head rankings.

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
call binders from a permissive primary screen alone, such as a qualitative
surface plasmon resonance (SPR) signal without a numeric cutoff \[@bindcraft;
@rfpeptides; @latentx1\] or a small single-point biolayer interferometry (BLI)
shift of 0.05 to 0.1 nm above background [@protenix_v2; @pxdesign; @chai2].
Other campaigns add orthogonal confirmation in a second, independent assay,
which reduces the final validated hit count relative to single-screen calls. For
example, BoltzProt-1 separates initial screening hits from validated binders
confirmed by reversing sensor orientation and external vendor re-testing
[@boltzprot1], and Germinal similarly verified antigen-binding fragment (Fab)
hits with both SPR and BLI [@germinal]. Multivalent avidity also overstates
apparent affinities when binders are tested as dimeric Fc fusions or under dense
sensor-immobilization setups that allow simultaneous multi-site engagement, a
caveat flagged on reported picomolar and sub-nanomolar hits in Protenix-v2,
BindCraft, and Chai-2 [@protenix_v2; @bindcraft; @chai2]. Finally, excluding
constructs that fail chemical synthesis or protein expression shrinks the
hit-rate denominator and inflates reported success rates. In practice,
cyclic-peptide campaigns such as RFpeptides and Latent-X1 often assayed only
about half of the sequences selected for synthesis [@rfpeptides; @latentx1], and
PXDesign showed on PD-L1 that omitting six poorly expressing designs raised its
hit rate from 47.1% of ordered constructs to 72.7% of those tested [@pxdesign].

Target and epitope selection biases are equally consequential. Most published
campaigns test a handful of targets and epitopes selected by the authors, yet
binding difficulty varies sharply between sites on a single protein: two
epitopes on the same antigen (AMBP) in Protenix-v2 produced 4% and 48% hit rates
[@protenix_v2]. The scale of this selection effect was quantified by mBER, which
designed more than 1.15 million unique VHHs against 436 human cell-surface
proteins (145 assayed by phage display without affinity measurement), aiming at
randomly sampled exposed hotspots [@mber]. On uncurated hotspots, mBER's median
per-design hit rate was roughly 0.4%, two orders of magnitude below curated
small-panel reports, while its best individual sites reached 7.5% overall and
38% (8/21) within an ipTM-filtered bin [@mber].

Even when identical molecules are re-tested in different laboratories, assay
conditions shift measured performance. In one example, AlphaProteo resynthesized
RFdiffusion's full published panels (including nonbinders) for yeast display at
10- to 20-fold lower target concentrations, and hit rates fell from 33% to 16%
on IL-7Rα and from 6% to 0% on TrkA [@alphaproteo; @rfdiffusion]. Similarly,
when Latent-X1 resynthesized RFpeptides' two best macrocycles and re-tested them
in its own SPR assay, the same peptides measured 4.4- to 5-fold weaker than
originally reported, shifting from 1.90 to 8.38 µM on MDM2 and from 2.0 to 10.0
µM on MCL-1 [@latentx1; @rfpeptides]. Alongside these experimental confounders,
several commercial systems keep their architectures, weights, and selection
pipelines undisclosed, placing their wet-lab claims outside independent
verification [@bender_perspective]. These include AlphaProteo, Chai-2, Latent-X1
and Latent-X2, and API-only BoltzProt-1 \[@alphaproteo; @chai2; @latentx1;
@latentx2; @boltzprot1\], as well as unpublished models such as IsoDDE, which is
known from third-party scaling plots alone [@opendde].

## 4. From In Vitro Binding Hits to Drug Leads

### The translational gap

Nearly every de novo binder-design study frames its work around therapeutic
discovery, whether accelerating drug development, engineering species
cross-reactivity, or blocking clinically relevant interactions \[@boltzgen;
@chai2; @bindcraft; @latentx2; @mber\]. Reviewing a decade of artificial
intelligence in pharmaceutical research, Bender et al. draw a useful distinction
between model validation and process validation [@bender_perspective]. Model
validation measures performance on an isolated task, such as accurately
predicting complex structures or identifying nanomolar in vitro hits, whereas
process validation asks the harder translational question of whether those
outputs improve downstream drug-discovery decisions and reduce clinical failure
[@bender_perspective]. Public databases already contain more than $10^6$
bioactive small molecules compared with roughly $10^3$ marketed drugs, a
reminder that confirming target binding in a biophysical assay is only the first
step toward a viable peptide or protein therapeutic [@bender_perspective].

Clinical viability simultaneously demands high expression, solubility, thermal
stability, low self-association, minimal immunogenicity, suitable
pharmacokinetics, and the intended functional modulation beyond passive binding
[@bender_perspective; @latentx2]. The blinded AIntibody challenge offered a
concrete illustration of this trade-off: on its out-of-library engineering task,
30.4% of computational designs did not bind, and the highest-affinity binder in
the competition (2.9 pM) failed to elute from a hydrophobic interaction
chromatography (HIC) column, indicating poor developability [@aintibody].
Despite these requirements, nearly all open generative frameworks optimize and
filter exclusively for predicted binding geometry, leaving developability and
immunogenicity to downstream screening. Early results from closed platforms
suggest that joint optimization of binding and drug-like properties is
achievable. For example, Latent-X2 reports de novo macrocycles and antibodies
whose developability and low-immunogenicity profiles match or exceed approved
therapeutics, including binders on 9 of 18 antibody targets down to 26.2 pM
[@latentx2]. Yet because its architecture is withheld, independent researchers
cannot examine how those competing objectives are balanced [@latentx2].

### Quantitative protein–protein affinity prediction

Once a campaign identifies an initial binder, optimizing its potency lacks
reliable computational guidance because quantitative affinity ($K_D$) prediction
for protein–protein complexes remains unsolved. Current co-folding confidence
scores behave mainly as binary indicators of whether a complex forms rather than
calibrated free-energy estimators, so they cannot distinguish weak micromolar
hits from nanomolar leads or guide affinity-maturing mutations. BindCraft notes
that AlphaFold2 ipTM separates binders from nonbinders without predicting how
tightly they bind [@bindcraft]. The same bottleneck appeared among computational
methods in the blinded AIntibody challenge, where only 1 of 26 participating
groups outperformed random selection when ranking closely related antibody
clones sharing the same CDR-H3 loop by binding strength [@aintibody]. Dedicated
affinity-prediction modules added onto co-folding models, such as Boltz-2's
affinity head, have so far succeeded on small-molecule free-energy benchmarks,
but they are trained exclusively on single-protein ligand assays and do not
apply to multimeric protein–protein interactions [@boltz2]. Consequently,
potency ranking and affinity maturation continue to depend on experimental
kinetics after design.

### Targets without experimental structures and conformational dynamics

Current design workflows depend heavily on static, experimentally solved target
structures and struggle with flexible, uncharacterized, or intrinsically
disordered proteins. Nearly all successful wet-lab campaigns so far have started
from an experimental crystal or cryo-electron microscopy structure of the target
protein, or from a well-folded predicted domain \[@rfdiffusion; @bindcraft;
@rfpeptides; @latentx1\]. When no experimental structure is available, how
reliably binder design works from predicted target coordinates is largely
untested, a caveat Germinal raised after designing against AlphaFold3 models
[@germinal]. Flexible loops and intrinsically disordered regions pose a deeper
challenge because they lack a single fixed conformation in solution, whereas
PDB-trained co-folders produce static snapshots and can hallucinate artificial
secondary structure in unstructured stretches unless mitigated during training
[@alphafold3]. Recent campaigns have begun targeting flexible extracellular
loops on G protein-coupled receptors (GPCRs) [@protenix_v2] and disordered
regions of proteins such as NPM1. On NPM1, BoltzGen observed live-cell nucleolar
co-localization for 1 of 5 designed peptides, which does not confirm direct
binding to the disordered region [@boltzgen]. Overall, reliable design against
dynamic or structurally uncharacterized proteins remains an open problem.

### Blinded prospective benchmarks for de novo design

Beyond these technical challenges, the field still lacks a standardized, blinded
prospective wet-lab benchmark for target-conditioned de novo binder design.
Structure prediction matured rapidly around shared blind assessments such as
CASP and unified benchmark suites like FoldBench [@foldbench], where models are
scored under common protocols on held-out experimental structures. De novo
binder evaluation is harder to standardize because every proposed sequence must
be synthesized, expressed, and assayed physically, leaving the field dependent
on disconnected, self-selected campaigns. Independent replication of entire
campaigns is rare, with AlphaProteo's re-testing of RFdiffusion's full panels as
a notable exception [@alphaproteo; @rfdiffusion], and retrospective
meta-analyses such as Overath et al. standardize computational scoring without
removing assay heterogeneity among source studies [@overath_meta]. The blinded
AIntibody challenge proved that unified wet-lab benchmarking involving 29
organizations is feasible, combining uniform affinity kinetics with a five-assay
developability panel [@aintibody]. However, that benchmark was narrow in scope,
testing library-conditioned antibody optimization against the well-characterized
SARS-CoV-2 receptor-binding domain rather than target-conditioned de novo design
spanning diverse modalities [@aintibody]. Extending multi-group blinded
prospective evaluation to novel targets and uncurated epitopes for peptides,
minibinders, and antibodies, with full reporting of ordered constructs,
independent binding confirmation, and developability profiling, will be
essential for fair head-to-head comparison of design methods.

## Conclusions

Within a few years, protein structure prediction and biomolecular co-folding
have matured into reliable tools for modeling macromolecular complexes. Design
pipelines built on these predictors have begun shifting binder discovery away
from massive empirical library screening toward targeted computational
generation. On well-characterized targets, such workflows can already deliver
nanomolar binders in peptide, minibinder, and antibody formats from only tens of
synthesized candidates. This progress does not rest on a single strategy:
tracing current systems from their underlying components reveals distinct
architectural approaches to exploring sequence space, each striking a different
balance between differentiability, sampling speed, and all-atom chemical
generality.

Generating plausible binders is no longer the limiting step; the primary
bottleneck is identifying which candidates to test experimentally. Most
pipelines still filter designs using structural confidence scores from
co-folding models trained to minimize three-dimensional coordinate error on
bound complexes, not to distinguish binders from nonbinders. Those metrics vary
widely in predictive accuracy between targets and can be outperformed by
classifiers trained on wet-lab binding data. Published campaigns also resist
direct comparison, as differences in assay rigor, multivalent avidity, construct
attrition, and target curation strongly shape reported hit rates. Beyond initial
hit discovery, quantitative protein–protein affinity prediction and design
against flexible or structurally uncharacterized targets are unresolved modeling
challenges. Translating in vitro binding hits into developable, functionally
active drug leads will depend on overcoming these limitations and evaluating
progress through transparent methods and shared, blinded prospective benchmarks.

## Acknowledgments

Acknowledgments, author contributions, financial disclosures, competing
interests, data availability, and AI-assistance disclosures required by *PLOS
Computational Biology* will be completed prior to submission.

## References

All inline citations use verified Pandoc keys resolving to the repository BibTeX
catalog for compilation into numbered Vancouver-style references upon manuscript
submission.
