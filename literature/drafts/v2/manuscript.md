# Deep-Learning Methods for Protein and Peptide Binder Generation

## Abstract

Binding a specific target protein is a central mechanism in therapeutics,
diagnostics, and laboratory reagents, typically carried out by protein or
peptide modalities such as antibodies, nanobodies, single-chain variable
fragments, minibinders, and macrocyclic peptides. Historically, discovering such
binders has relied on experimental search through animal immunization or
combinatorial display libraries containing trillions of random sequences, an
approach that is labor-intensive per target and difficult to direct toward a
chosen epitope. Recent advances in deep-learning structure prediction and
biomolecular co-folding have enabled computational binder generation, shifting
discovery from screening vast random pools toward testing tens of designed
sequences per target. Unlike small-molecule generation over variable chemical
graphs, protein and peptide binder design searches sequences drawn from the
20-amino-acid alphabet evaluated by how they fold against a target surface.
Across the rapidly expanding landscape of open and proprietary systems,
architectures vary along three primary axes: how evolutionary information enters
the sequence trunk (multiple sequence alignment retrieval, protein language
models, or both), how three-dimensional coordinates are produced (single-pass
coordinate regression, iterative stochastic diffusion, or straighter-trajectory
flow matching), and how structure predictors drive sequence design (joint or
fine-tuned predictor-generators, generate-and-filter pipelines with inverse
folding and learned scorers, or gradient-based sequence optimization). Despite
rapid gains in experimental hit rates, reported numbers depend heavily on
testing budgets, assay confirmation criteria, target and epitope selection, and
method disclosure. Major open challenges remain in predicting quantitative
protein–protein binding affinity, optimizing developability and immunogenicity
alongside binding, building shared prospective benchmarks, and addressing the
limits of per-design confidence filtering.

# Introduction and Conceptual Background

## Why protein binders matter and how discovery shifted from search to design

Binding a target protein selectively is the physical basis for blocking a
signaling pathway, detecting an analyte, tagging a cellular structure, or
modulating enzymatic activity. When the target itself is a protein, the binding
partner is often another protein or a peptide. Major modalities include
full-length antibodies, single-domain nanobodies (VHHs), single-chain variable
fragments (scFvs), compact de novo minibinders, and head-to-tail macrocyclic
peptides. Together, these molecules form a large share of modern biologics and
research reagents because extended protein–protein interfaces can recognize flat
or shallow surfaces that are difficult to engage with small chemical compounds.

Historically, obtaining a protein binder has been an experimental search problem
rather than a design problem. Standard workflows rely on immunizing animals,
isolating clones from patients, or panning combinatorial phage or yeast display
libraries containing $10^{12}$ or more random sequences. These experimental
platforms are effective and remain workhorses in academia and industry, yet they
carry structural constraints: screening must begin in the wet lab and be
repeated from scratch for every new target, and selection tends to recover
binders against whichever regions happen to be immunogenic or sterically
accessible rather than a site chosen by the investigator [@rfantibody].
Computational binder generation seeks to invert this workflow by proposing
candidate amino-acid sequences directly for a user-specified target protein and
epitope.

Focusing on protein and peptide binders defines a clean technical boundary
distinct from small-molecule generation. Whether a system designs a macrocyclic
peptide, a minibinder, or the complementarity-determining regions (CDRs) of a
nanobody, the generated object is a linear or cyclized chain drawn from the
fixed 20-letter amino-acid alphabet, evaluated by how that chain folds against
the target surface. Small-molecule generation instead operates over
variable-size chemical graphs constrained by atomic valence rules, bond orders,
and synthetic accessibility, requiring different neural architectures and
evaluation benchmarks.

Direct computational binder design became practical once deep-learning models
reached experimental accuracy on protein structure prediction. AlphaFold2 solved
single-chain structure prediction at CASP14 [@alphafold2], and AlphaFold3
extended the framework to complexes containing proteins, nucleic acids,
small-molecule ligands, and ions [@alphafold3]. Even so, generating a binder
differs fundamentally from predicting a structure. A structure predictor maps a
known amino-acid sequence to its three-dimensional fold, and its accuracy can be
checked directly against an experimentally determined crystal or cryo-electron
microscopy structure. A binder generator must invent a new sequence out of
$20^L$ possible sequences for a chain of length $L$ such that the resulting
molecule folds stably and binds the intended target; that outcome can only be
confirmed experimentally in a wet lab.

Between 2024 and 2026, the field expanded rapidly across multiple predictor
lineages, open-source reproductions, and generative design stacks. Active
deployment is also reflected in engineering investments aimed at inference
speed: in September 2026, teams from NVIDIA, Anthropic, and ESM released
optimized inference kernels for Boltz, Chai-1, Protenix, OpenFold, RoseTTAFold3,
RFdiffusion, BindCraft, PXDesign, and ESMFold2, reporting 2–4× throughput gains
in public engineering blog posts and code repositories.

## How co-folding predictors are built

Modern protein structure prediction rests on the principle that correlated
mutations (coevolution) between pairs of positions in a multiple sequence
alignment (MSA) indicate spatial proximity in the folded three-dimensional
protein. AlphaFold2 demonstrated how accurately deep networks can extract this
signal at CASP14, reaching a median backbone accuracy of 0.96 Å r.m.s.d.95 (Cα
RMSD at 95% residue coverage; 95% confidence interval 0.85–1.16 Å) compared with
2.8 Å r.m.s.d.95 for the next best method [@alphafold2]. AlphaFold3 generalized
this setup from single chains to multi-component biomolecular complexes, an
approach commonly referred to as co-folding [@alphafold3].

While early RoseTTAFold 1 and 2 architectures processed 1D sequence, 2D
pairwise, and 3D coordinate tracks in parallel from input to output
[@rosettafold; @rosettafold2], most current co-folding predictors organize
computation into two sequential stages: a differentiable trunk that reasons over
sequence and evolutionary context, followed by a structure or diffusion module
that converts internal representations into explicit atomic coordinates.

The first stage, the trunk, is instantiated as the Evoformer in AlphaFold2
[@alphafold2], the Pairformer in AlphaFold3, Boltz, Chai, Protenix, and
RoseTTAFold3 [@alphafold3; @boltz1; @chai1; @protenix_v1; @rosettafold3], or the
folding trunk in ESMFold and ESMFold2 [@esm2; @esmc]. It transforms sequence and
evolutionary inputs into single-residue and pairwise residue representations. A
linear head attached to the pair representation predicts a distogram, which is a
probability distribution over inter-residue distances for every residue pair.
The distogram serves both as a training supervision signal and, in several
design methods, as a differentiable geometric surrogate \[@alphafold2;
@boltzdesign1; @esmc\]. The trunk is differentiable throughout and typically
runs once per complex or random seed [@boltz1]. Predictor families differ
primarily in how evolutionary signal enters this trunk. MSA-based systems
retrieve homologous sequences from sequence databases at inference time, as in
AlphaFold2 [@alphafold2], AlphaFold3 [@alphafold3], RoseTTAFold \[@rosettafold;
@rosettafold3\], Boltz [@boltz1], and Protenix [@protenix_v1]. Protein language
model (PLM)-based systems instead absorb evolutionary statistics into their
weights during large-scale pre-training, permitting single-sequence inference
without database searches, as in ESM-2/ESMFold [@esm2], ESMC/ESMFold2 [@esmc],
and AtlasFold [@atlasfold]. Hybrid systems such as Chai-1 incorporate both an
MSA track and a protein language model track and can operate with either
[@chai1].

The second stage converts the trunk's single and pair representations into 3D
atomic coordinates, and its mathematical formalism governs both inference speed
and differentiability. AlphaFold2 and ESMFold rely on single-pass coordinate
regression through an end-to-end differentiable structure module built on
Invariant Point Attention (IPA) [@alphafold2; @esm2]; ablations in AlphaFold2
showed that removing end-to-end structural gradients reduces prediction accuracy
[@alphafold2]. AlphaFold3 and subsequent AF3-class co-folders, including Boltz,
Chai, Protenix, RoseTTAFold3, and ESMFold2, replaced the IPA module with a
diffusion module for structure prediction itself, independent of generative
design [@alphafold3; @boltz1; @chai1; @protenix_v1; @rosettafold3; @esmc].
Adapted from image generation by replacing noised pixels with noised atomic
coordinates, diffusion generates structures iteratively by denoising Gaussian
noise along a stochastic differential equation (SDE) trajectory \[@alphafold3;
@frameflow\]. High-quality diffusion sampling in protein generation often
requires hundreds or roughly 1,000 forward passes [@frameflow]. Flow matching
addresses this sampling cost by formulating coordinate transport as an ordinary
differential equation (ODE) with straighter trajectories that need fewer
timesteps. FrameFlow recast the earlier FrameDiff generator using flow matching
and reported twofold better designability at five times fewer sampling steps on
unconditional protein monomers [@frameflow]. Target-conditioned binder
generators built on flow matching include PPIFlow [@ppiflow], OriginFlow
[@originflow], AtomFlow [@atomflow], and D-Flow [@dflow]. A key difference from
image generation is that protein outputs do not depend on subjective human
judgment during computation: candidate folds and interfaces can be automatically
scored by structure predictors.

## Turning structure predictors into binder generators

Structure prediction and binder generation can run on the exact same neural
network simply by changing which inputs are held fixed. Supplying sequences for
all chains asks the network to predict the bound complex; holding the target
chain fixed while leaving the binder chain unspecified or corrupted with noise
asks the network to construct a partner that folds against the target. BoltzGen
implements this duality directly as a single all-atom diffusion model trained to
perform both structure prediction and protein design [@boltzgen]. RFdiffusion
reached a related duality by fine-tuning the RoseTTAFold structure predictor
into a backbone generator, leveraging RoseTTAFold's 3D coordinate track running
from input to output so that target structures or active-site motifs could be
provided directly as coordinates rather than solely as pairwise distances
[@rosettafold2; @rfdiffusion].

Across the literature, design pipelines combine sequence and structure
generation with structure predictors in three main ways (**Figure 1**). First,
joint or fine-tuned predictor-generators reuse prediction weights directly to
denoise unknown binder structures, either by fine-tuning a predictor into a
backbone generator (RFdiffusion and RFdiffusion2 from RoseTTAFold
\[@rfdiffusion; @rfdiffusion2\]) or by training one all-atom diffusion model
jointly on prediction and design tasks (BoltzGen [@boltzgen]). Second,
generate-and-filter pipelines separate generation from evaluation without
passing gradients through the predictor during sampling. A generator proposes
candidate backbones, an inverse-folding model (most commonly ProteinMPNN
[@proteinmpnn]) designs sequences compatible with those backbones, and a
downstream scorer ranks candidates before synthesis. Filtering most often relies
on refolding confidence metrics, as in RFdiffusion followed by ProteinMPNN and
AlphaFold2 [@rfdiffusion], RFpeptides [@rfpeptides], BoltzGen [@boltzgen],
PXDesign-d [@pxdesign], and Protenix-v2 [@protenix_v2]; a widely cited filter
stated in AlphaProteo requires interchain AlphaFold2 PAE < 10 Å, binder-aligned
binder RMSD < 1 Å, and pLDDT > 80 [@alphaproteo]. Alternatively, confidence
scores can be replaced by a classifier trained directly on experimental binding
outcomes, as in BoltzProt-1's BoltzPPI scorer [@boltzprot1]. Third,
gradient-based sequence optimization (often called hallucination or
backpropagation) represents a binder of length $L$ as a continuous probability
distribution over the 20 amino acids at each position (an $L \\times 20$
simplex), passes this relaxed sequence into a differentiable predictor, and
descends gradients of structural confidence or distogram losses while annealing
toward discrete one-hot amino acids, as in BindCraft [@bindcraft], Germinal
[@germinal], BoltzDesign1 [@boltzdesign1], PXDesign-h [@pxdesign], and ESMFold2
[@esmc]. One variant, RFOptimization, keeps sequences strictly discrete and uses
predictor gradients solely to rank single-point mutations [@rfoptimization].

**Figure 1. Co-folding predictor architectures and binder-design workflows.**
(A) Two-stage co-folding predictor architecture. Sequence and evolutionary
information enters the differentiable trunk (Evoformer, Pairformer, or folding
trunk) via MSA retrieval, protein language model (PLM) embeddings, or both,
producing single representations, pairwise representations, and a linear
distogram head. Coordinates are generated by single-pass Invariant Point
Attention (IPA) regression (AlphaFold2, ESMFold), iterative stochastic
differential equation (SDE) diffusion (AlphaFold3, Boltz, Chai, Protenix,
RoseTTAFold3, ESMFold2), or straighter-trajectory ordinary differential equation
(ODE) flow matching (FrameFlow and binder extensions PPIFlow, OriginFlow,
AtomFlow, D-Flow). (B) Three workflows for turning structure predictors into
binder generators: (1) joint or fine-tuned predictor-generators that denoise an
unspecified binder chain against a fixed target (RFdiffusion, RFdiffusion2,
BoltzGen); (2) generate-and-filter pipelines linking backbone generation,
inverse folding (ProteinMPNN), and post-hoc filtering via confidence metrics or
a trained experimental-binding classifier (BoltzPPI); and (3) gradient-based
sequence optimization over a continuous $L \\times 20$ sequence relaxation
annealed to one-hot amino acids, differentiating end-to-end through a regression
module (BindCraft, Germinal), through trunk distograms and confidence heads
while stopping gradients before diffusion (BoltzDesign1, ESMFold2, and discrete
gradient-ranked mutations in RFOptimization), or through a differentiable 2-step
ODE sampler (PXDesign-h).

*Illustrator specification for Figure 1 (remove prior to submission):* Two
horizontally stacked panels (Panel A on top, Panel B below). Panel A flows
left-to-right across three boxed columns: (1) Input sources (stacked branches
for MSA database lookup, PLM embeddings, and hybrid dual tracks) feeding into
(2) a central Trunk block labeled with single/pair representations and an
outgoing distogram head, feeding into (3) three parallel coordinate-module
branches illustrating single-pass IPA regression (1 step), curved noisy SDE
diffusion (200–1,000 steps), and straighter ODE flow-matching trajectories (few
steps). Panel B shows three stacked horizontal workflow lanes: Lane 1 depicts a
shared diffusion network with fixed target coordinates and noised binder
coordinates entering and a designed binder complex exiting; Lane 2 depicts a
sequential pipeline (Backbone Generator → Inverse Folding [ProteinMPNN] →
Predictor Confidence Filter or Learned Classifier [BoltzPPI]); Lane 3 depicts a
closed feedback loop from an $L \\times 20$ relaxed sequence matrix through the
predictor with three color-coded gradient return paths (full end-to-end through
IPA regression; trunk distogram/confidence shortcut with a stop-gradient icon
before diffusion; and a 2-step ODE decoder loop).

Three practical engineering constraints shape how these workflows behave in
practice. The first is the single-sequence requirement of gradient-based
optimization. Retrieving an MSA requires searching a sequence database for an
existing sequence, which is neither defined for a newly invented binder nor
differentiable. Gradient optimization must therefore run the binder chain in
single-sequence mode. For MSA-trained predictors such as AlphaFold2 (inverted by
BindCraft [@bindcraft]), shallow-MSA and single-sequence inputs are documented
as their weakest accuracy regime [@alphafold2]. Protein language models such as
ESMC and ESMFold2 are natively single-sequence, allowing gradients to flow
through a 6-billion-parameter language model and folding trunk without leaving
the model's training distribution [@esmc].

The second constraint is differentiating through multi-step diffusion modules.
Whereas AlphaFold2's regression-based IPA structure module supports
straightforward end-to-end backpropagation [@alphafold2; @bindcraft], unrolling
hundreds or roughly 1,000 denoising steps in an AF3-class diffusion predictor to
compute sequence gradients is computationally impractical \[@frameflow;
@boltzdesign1\]. Design methods handle this obstacle in two ways. BoltzDesign1
[@boltzdesign1], RFOptimization [@rfoptimization], and ESMFold2 [@esmc] compute
gradients directly from the trunk's distogram and confidence heads without
backpropagating through the diffusion module (ESMFold2 optimizes
distogram-entropy and ESMC losses and runs its diffusion and confidence modules
only in final steps to score ipTM [@esmc]). PXDesign-h instead replaces the
200-step diffusion decoder with a differentiable 2-step ODE sampler so gradients
can pass through coordinate generation [@pxdesign].

The third constraint is that post-generation filtering strongly affects
experimental yield independently of the generator itself. In BoltzProt-1,
holding the BoltzGen candidate pool fixed and replacing standard
confidence-score ranking with the trained BoltzPPI classifier increased
confirmed-binder rates from 3.3% to 8.0% and raised confirmed target coverage
from 2/10 to 4/10 [@boltzprot1]. Similarly, PXDesign observed that Protenix and
AlphaFold2-Initial-Guess (AF2-IG) filters select largely non-overlapping subsets
of true-positive binders [@pxdesign]. To reduce overfitting to any single
predictor's biases during optimization, RFOptimization interleaves RoseTTAFold3
and Boltz inside the design loop while holding out AlphaFold3 as an independent
evaluation check [@rfoptimization].

## Reading reported numbers: testing budgets, hit definitions, and disclosure

A practical indicator of progress in binder generation is how many candidate
sequences must be physically synthesized and tested per target to obtain a
working binder. Earlier display-based and computational pipelines often required
screening thousands to millions of designs to reliably identify hits \[@chai2;
@rfantibody\]. Recent generative and filtering campaigns routinely test tens of
designs per target: 16 to 30 in Protenix-v2 [@protenix_v2], at most 20 per
target and format in Chai-2 [@chai2], at most 20 in RFpeptides [@rfpeptides], 30
to 100 in Latent-X1 [@latentx1], 43 to 101 in Germinal [@germinal], and 84 per
cohort in ESMFold2 [@esmc]. Reported wet-lab hit rates in such small panels
include 16% overall for Chai-2 de novo antibodies [@chai2], 2–48% on soluble
targets and 16–88% on GPCRs for Protenix-v2 VHH-Fc designs [@protenix_v2], and a
70.0% mean hit rate for ESMFold2 minibinders [@esmc].

Raw hit rates, however, cannot be compared at face value across studies because
two experimental choices strongly influence the reported percentages. First, hit
definitions vary substantially. BoltzProt-1 explicitly distinguishes initial
screening hits (noting that these correspond to what prior binder-design papers
typically report as binders) from confirmed binders validated in follow-up
assays, reporting an 8.0% confirmed-binder rate alongside a higher initial
screening-hit rate [@boltzprot1]. Second, target and epitope selection can shift
success rates by orders of magnitude. Most campaigns evaluate targets and
binding sites chosen by the authors. In contrast, mBER tested 1,153,241 unique
VHH designs across 436 human cell-surface proteins (145 assayed) directed at
randomly selected surface hotspots, using phage display enrichment without
individual affinity confirmation [@mber]. Its median per-design hit rate of
roughly 0.4% was about two orders of magnitude lower than headline figures from
small targeted campaigns, yet its best individual hotspots achieved hit rates up
to 38% under strict filtering, overlapping the rates reported in smaller studies
[@mber].

Interpreting published performance also requires tracking the spectrum of method
openness and disclosure across the field. Systems fall into four categories of
availability: fully reproducible releases providing model weights, training
code, and training datasets (OpenFold3 [@openfold3], AtlasFold [@atlasfold],
BoltzGen [@boltzgen]); open-weights releases under permissive licenses such as
MIT, Apache-2.0, or BSD (Boltz-1 [@boltz1], Boltz-2 [@boltz2], Protenix
[@protenix_v1], RoseTTAFold3 [@rosettafold3], OpenDDE [@opendde], OpenGerminal
[@opengerminal]) or non-commercial licenses (Chai-1 [@chai1], ESM3-open
[@esm3]); papers reporting wet-lab or benchmark outcomes whose generative
architectures are undisclosed (AlphaProteo [@alphaproteo], Latent-X1
[@latentx1], Latent-X2 [@latentx2], Chai-2's generator [@chai2]) or restricted
to API-only commercial access without released weights (BoltzProt-1
[@boltzprot1], ESM3-98B [@esm3]); and unpublished commercial or private systems
known publicly only through web platforms or third-party benchmark points
(IsoDDE [@opendde], Chai-3, SeedFold [@opendde]). Openness has also changed
within individual lineages: Boltz-1, Boltz-2, and BoltzGen provide MIT-licensed
weights [@boltz1; @boltz2; @boltzgen], whereas BoltzProt-1 publishes a paper and
wet-lab dataset while offering API-only commercial access [@boltzprot1];
likewise, AlphaFold3 was co-authored by Google DeepMind and Isomorphic Labs
[@alphafold3], whereas Isomorphic Labs' subsequent IsoDDE model has no
accompanying publication [@opendde; @bender_perspective]. Because wet-lab
campaigns evaluate author-selected targets, assays, and hit thresholds, results
from closed-weight or undisclosed systems cannot be independently audited or
reproduced from the published papers alone [@bender_perspective].

Finally, reading computational benchmarks alongside design campaigns requires
separating external accuracy and physical-validity metrics from model
self-estimates (**Box 1**). External metrics evaluate a predicted structure
against an experimental reference or physical chemistry rules, whereas internal
confidence metrics are estimated by the predictor itself without any
experimental ground truth. Because de novo designed binders have no experimental
structure prior to synthesis, design pipelines depend on these internal
self-estimates and on self-consistency RMSD (comparing a generated backbone
against a predicted refolding of its own designed sequence) to select candidates
for wet-lab testing.

### Box 1: Core Evaluation Metrics

| Category                     | Metric                               | Reference                           | What it measures and how it is used                                                                                                                                                                                                                                                                                                                                                                                                                 | Source                |
| ---------------------------- | ------------------------------------ | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| External accuracy / validity | **lDDT**                             | Experimental structure              | Local Distance Difference Test; compares local interatomic distances without global superposition, so a correctly folded domain in the wrong relative orientation still scores high.                                                                                                                                                                                                                                                                | [@lddt]               |
| External accuracy / validity | **TM-score**                         | Experimental structure              | Length-normalized global fold similarity to an experimental reference structure.                                                                                                                                                                                                                                                                                                                                                                    | [@tm_score]           |
| External accuracy / validity | **RMSD** (and self-consistency RMSD) | Experimental or predicted structure | Root-mean-square deviation (Å) after optimal superposition via Kabsch's algorithm. Measures accuracy against an experimental structure; in design pipelines, self-consistency RMSD compares a generated backbone to a predicted refolding of its own designed sequence (no experimental structure involved).                                                                                                                                        | [@kabsch]             |
| External accuracy / validity | **DockQ**                            | Experimental structure              | Combines protein–protein interface accuracy measures onto a 0–1 scale, with DockQ ≥ 0.23 commonly used as the acceptable-interface threshold.                                                                                                                                                                                                                                                                                                       | [@dockq]              |
| External accuracy / validity | **PoseBusters / PB-valid**           | Physical chemistry rules            | Pass/fail physical plausibility check for chemical validity, bond geometry, stereochemistry/chirality, steric clashes, and internal energy, paired with a protein–ligand benchmark set (308 complexes plus 85 Astex Diverse complexes in the original benchmark [@posebusters]; 428 complexes as evaluated by AlphaFold3 [@alphafold3]; reported across AlphaFold3 [@alphafold3], Chai-1 [@chai1], Boltz-1 [@boltz1], and Protenix [@protenix_v1]). | [@posebusters]        |
| Model self-estimate          | **pLDDT**                            | Model self-estimate                 | Per-residue predicted lDDT on a 0–100 scale, empirically calibrated against ground-truth lDDT.                                                                                                                                                                                                                                                                                                                                                      | [@alphafold2]         |
| Model self-estimate          | **pTM**                              | Model self-estimate                 | Predicted global TM-score for the overall structure.                                                                                                                                                                                                                                                                                                                                                                                                | [@alphafold2]         |
| Model self-estimate          | **PAE**                              | Model self-estimate                 | Predicted Aligned Error; residue-by-residue matrix estimating positional error (Å) between pairs of residues.                                                                                                                                                                                                                                                                                                                                       | [@alphafold2]         |
| Model self-estimate          | **ipTM**                             | Model self-estimate                 | Interface predicted TM-score computed over interchain residue pairs only.                                                                                                                                                                                                                                                                                                                                                                           | [@alphafold_multimer] |
| Model self-estimate          | **iPAE** (interchain PAE)            | Model self-estimate                 | PAE restricted to interchain residue pairs (e.g., AlphaProteo applies an interchain PAE < 10 Å filter [@alphaproteo]; the ipSAE study suggests 10 or 15 Å cutoffs [@ipsae]).                                                                                                                                                                                                                                                                        | [@alphafold_multimer] |
| Model self-estimate          | **ipSAE**                            | Model self-estimate                 | Restricts ipTM calculation to well-predicted interchain residue pairs below a PAE cutoff (such as 10 or 15 Å), removing sensitivity to how disordered or non-interacting regions are trimmed (used in Germinal [@germinal] and Overath et al. [@overath_meta]).                                                                                                                                                                                     | [@ipsae]              |

# Model Families: From Predictors to Design Systems

Tracing each model family from structure prediction to binder generation shows
how architectural choices, training data, and release policies shape downstream
design workflows. **Table 1** compares the major open and proprietary lineages
side by side before each family is examined in detail.

**Table 1. Overview of major structure predictors and binder-design systems.**

| System / Lineage                                     | Primary Role                                                   | Evolutionary Input                                      | Coordinate Stage                                                      | Target / Binder Modalities                                                        | Design or Filtering Mechanism                                                                          | Openness / License                                           | Reference                                              |
| ---------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------ |
| AlphaFold2 / AF-Multimer                             | Structure predictor (monomer & multimer)                       | MSA                                                     | Single-pass IPA regression                                            | Protein chains and multimers                                                      | Refolding filter (pLDDT, ipTM, iPAE); inverted by backpropagation pipelines                            | Open code & weights                                          | [@alphafold2; @alphafold_multimer]                     |
| OpenFold                                             | Structure predictor (AF2 reproduction)                         | MSA                                                     | Single-pass IPA regression                                            | Protein chains                                                                    | Open retraining and structural distillation dataset                                                    | Open source (code, weights, data)                            | [@openfold]                                            |
| AlphaFold3                                           | All-atom co-folding predictor                                  | MSA                                                     | All-atom SDE diffusion                                                | Proteins, nucleic acids, ligands, ions (incl. Ab–Ag)                              | Refolding / ranking filter (up to 1,000 seeds for Ab–Ag)                                               | Closed / restricted weights                                  | [@alphafold3]                                          |
| OpenFold3                                            | All-atom co-folding predictor (AF3 reproduction)               | MSA                                                     | All-atom SDE diffusion                                                | Proteins, nucleic acids, ligands, ions                                            | Open retraining (13M-sequence distillation set)                                                        | Apache-2.0 (weights, code, data)                             | [@openfold3]                                           |
| RoseTTAFold 1 / 2 / RFAA                             | Structure predictors (protein & all-atom)                      | MSA                                                     | Parallel 3-track (1D/2D/3D) regression                                | Proteins; RFAA adds nucleic acids, ligands, metals                                | Base architectures for RFdiffusion and RFpeptides                                                      | Open code & weights                                          | [@rosettafold; @rosettafold2; @rosettafold_all_atom]   |
| RoseTTAFold3 (RF3)                                   | All-atom co-folding predictor                                  | MSA                                                     | All-atom SDE diffusion (learned chirality)                            | Biomolecular complexes, mixed L/D peptides, ligands                               | Supplies distogram/confidence gradients for RFOptimization                                             | BSD                                                          | [@rosettafold3]                                        |
| RFdiffusion 1 / 2 / 3                                | Backbone & all-atom structure generators                       | Target structure conditioned (no MSA on binder)         | Equivariant frame diffusion (RFD1/2); all-atom U-Net diffusion (RFD3) | Minibinders, active-site scaffolds (RFD2), all-atom binders (RFD3)                | Generate-and-filter (RFD1/2 fine-tuned from RF; RFD3 pre-trained) + MPNN + refolding                   | Open code & weights                                          | [@rfdiffusion; @rfdiffusion2; @rfdiffusion3]           |
| ProteinMPNN / LigandMPNN / AlphaDesign               | Inverse folding (sequence design)                              | None (fixed-backbone conditioned)                       | Fixed backbone input (autoregressive MPNN / ADM)                      | Protein backbones; LigandMPNN adds ligands, nucleic acids, metals                 | Assigns or redesigns sequences onto generated backbones                                                | Open code & weights                                          | [@proteinmpnn; @ligandmpnn; @alphadesign]              |
| RFantibody                                           | Antibody structure generator                                   | Target structure + framework                            | Fine-tuned RFdiffusion                                                | VHHs, scFvs, full antibodies (epitope-specific)                                   | Backbone diffusion + inverse folding + refolding + display/SPR screening                               | Open code & weights                                          | [@rfantibody]                                          |
| RFpeptides                                           | Macrocyclic peptide generator                                  | Target structure                                        | Cyclic-encoding RFdiffusion / RF2                                     | Head-to-tail macrocyclic peptides                                                 | Cyclic diffusion + ProteinMPNN + AfCycDesign & Rosetta filtering                                       | Open code & weights                                          | [@rfpeptides]                                          |
| FrameFlow / PPIFlow / OriginFlow / AtomFlow / D-Flow | Flow-matching structure generators                             | Target structure (binder variants)                      | ODE flow matching                                                     | Unconditional monomers (FrameFlow); target-conditioned protein binders            | Straighter ODE coordinate trajectories + sequence design / filtering                                   | Research publications                                        | [@frameflow; @ppiflow; @originflow; @atomflow; @dflow] |
| Boltz-1 / Boltz-1x / Boltz-2                         | All-atom co-folding predictors (+ ligand affinity in Boltz-2)  | MSA                                                     | All-atom SDE diffusion (FK steering in Boltz-1x)                      | Biomolecular complexes; small-molecule affinity (Boltz-2)                         | Refolding filter for BoltzGen/BoltzProt-1; inverted by BoltzDesign1                                    | MIT (weights, code)                                          | [@boltz1; @boltz2]                                     |
| BoltzGen                                             | Joint co-folding predictor & binder generator                  | MSA (prediction) / target conditioned (design)          | Unified all-atom SDE diffusion                                        | Proteins, peptides, VHHs (full mAbs excluded); disordered & ligand targets        | Joint prediction/design diffusion + Boltz-2 refolding filter                                           | MIT (weights, code, data)                                    | [@boltzgen]                                            |
| BoltzProt-1 (with BoltzPPI)                          | Binder generator & trained binding classifier                  | MSA / target conditioned                                | Refined BoltzGen diffusion                                            | VHHs and protein binders                                                          | BoltzGen-derived generator + BoltzPPI experimental-binding classifier                                  | Commercial API-only (weights closed)                         | [@boltzprot1]                                          |
| Chai-1                                               | All-atom co-folding predictor                                  | Hybrid (MSA and/or PLM track)                           | All-atom SDE diffusion (+ experimental restraints)                    | Biomolecular complexes, antibodies                                                | Complex prediction and refolding (single-sequence parity on antibodies)                                | Non-commercial weights; commercial web server                | [@chai1]                                               |
| Chai-2 (and Chai-3)                                  | De novo binder generator (Chai-3: foundation model)            | Undisclosed (Chai-2f resembles Chai-1)                  | Undisclosed                                                           | scFvs, VHHs, minibinders                                                          | Zero-shot design + Chai-2f folding filter (generator undisclosed)                                      | Closed weights & architecture (Chai-3: unpublished platform) | [@chai2]                                               |
| ColabDesign / AfCycDesign                            | Backpropagation library / cyclic peptide designer              | Single-sequence on binder                               | AF2 IPA regression (cyclic offset in AfCycDesign)                     | Proteins; head-to-tail macrocyclic peptides (AfCycDesign)                         | 3-stage continuous-to-one-hot AF2 backpropagation (motif grafting + MPNN/Rosetta for binders)          | Open-source library / code                                   | [@colabdesign; @afcycdesign]                           |
| BindCraft (and BindCraft2)                           | Gradient-based binder designer                                 | Single-sequence on binder (AF-Multimer)                 | Full AF-Multimer IPA regression (induced-fit target)                  | Minibinders (BindCraft2 adds cyclic peptides, VHHs, scFv/Fab, repeats, glues)     | 4-stage continuous-to-discrete backpropagation (5-model swap) + ProteinMPNN + AF2/Rosetta filter       | Open code (BindCraft2 code released, unpublished)            | [@bindcraft]                                           |
| BoltzDesign1                                         | Gradient-based binder designer                                 | Single-sequence on binder (Boltz-1 trunk)               | Stop-gradient on Boltz-1 diffusion (distogram/confidence heads)       | Protein and nucleic-acid-binding designs                                          | 4-stage continuous relaxation on 64-bin Pairformer distogram + optional LigandMPNN                     | Open code (in-silico evaluated)                              | [@boltzdesign1]                                        |
| RFOptimization (RFO)                                 | Discrete gradient-guided design refiner                        | Single-sequence / predictor trunk                       | Bypasses RF3 diffusion (distogram/confidence heads)                   | Protein–protein, cyclic peptide, small-molecule binders                           | Discrete Metropolis–Hastings mutations from RF3 gradients + 50% Boltz/LigandMPNN cycling               | Preprint method (in-silico evaluated)                        | [@rfoptimization]                                      |
| Germinal / OpenGerminal                              | Gradient-based antibody CDR designer                           | Single-sequence + antibody LM (IgLM / AbLang1)          | Full AF-Multimer IPA regression + masked framework template           | Antibody CDR loops (VHH, scFv/Fab)                                                | Live AF-Multimer + LM gradient merging (PSSM + STE) + AbMPNN + co-folding/ipSAE filter                 | Open code; OpenGerminal Apache-2.0                           | [@germinal; @opengerminal]                             |
| mBER (and mBER-2)                                    | Template- and PLM-biased VHH designer                          | Single-sequence + static ESM-2 prior                    | AF-Multimer IPA regression + NanoBodyBuilder2 template                | VHHs (mBER-2 extends to microbinders)                                             | ColabDesign 3-stage loop with fixed ESM-2 logit bias + held-out AF-Multimer ipTM filter                | Open code (mBER-2 technical report)                          | [@mber]                                                |
| Protenix-v1 / Protenix-v2                            | All-atom co-folding predictors & antibody/binder designer (v2) | MSA                                                     | All-atom SDE diffusion                                                | Biomolecular complexes; v2 designs miniproteins, VHH, Fv, full mAbs (incl. GPCRs) | Co-folding + epitope-specific/site-agnostic design & ranking (paired with PXMeter)                     | Protenix-v1 open weights & code; Protenix-v2 preprint        | [@protenix_v1; @protenix_v2; @pxmeter]                 |
| PXDesign (PXDesign-d / -h)                           | Dual-mode binder designer                                      | Target conditioned / single-sequence (PXDesign-h)       | DiT Cartesian diffusion (-d); 2-step ODE sampler (-h)                 | Minibinders                                                                       | Diffusion + inverse folding (-d) or end-to-end 2-step ODE hallucination (-h) + Protenix/AF2-IG filters | Open benchmark & web server (built on Protenix)              | [@pxdesign]                                            |
| ESM-2 / ESMFold                                      | PLM & single-sequence monomer folder                           | PLM (single-sequence, no MSA)                           | Single-pass IPA regression                                            | Monomeric proteins                                                                | Single-sequence structure prediction; ESM-2 also used as static prior (mBER)                           | Open weights & code                                          | [@esm2]                                                |
| ESM-3                                                | Multimodal generative protein LM                               | Multimodal discrete tokens (no MSA)                     | Discrete 3D structure tokens                                          | Sequence, structure, and function generation (e.g., esmGFP)                       | Masked-token multimodal prompting and generation (1.4B, 7B, 98B)                                       | 1.4B academic-only; 98B API-only                             | [@esm3]                                                |
| ESMC / ESMFold2                                      | PLM, all-atom co-folder, & binder designer                     | PLM (6B ESMC, single-sequence; optional detachable MSA) | 48-layer recurrent trunk + sliding-window diffusion transformer       | Biomolecular complexes, Ab–Ag; minibinders & scFvs                                | 150-step single-stage gradient optimization via ESMC + distogram + final ipTM ranking                  | Preprint (Biohub / EvolutionaryScale)                        | [@esmc]                                                |
| AtlasFold                                            | Single-sequence PLM structure predictor                        | PLM (single-sequence, no MSA)                           | 48-block Pairformer + all-atom diffusion                              | Protein monomers and complexes (AtlasFold-M)                                      | Independent single-sequence co-folding + rank vs. oracle benchmarking                                  | MIT (weights, code, checkpoints, data)                       | [@atlasfold]                                           |
| OpenDDE                                              | Scaled all-atom co-folding predictor                           | MSA                                                     | Atom-level refiner + all-atom diffusion (3× wider Pairformer)         | Biomolecular complexes, Ab–Ag (joint design on roadmap)                           | Scaled Pairformer (128 to 384) co-folding + third-party Ab–Ag scaling benchmarks                       | Apache-2.0                                                   | [@opendde]                                             |
| AlphaProteo                                          | De novo minibinder designer                                    | Undisclosed (AF2 used for filtering)                    | Undisclosed                                                           | Minibinders                                                                       | Undisclosed generator + disclosed AF2 PAE/RMSD/pLDDT filter                                            | Closed weights & undisclosed architecture                    | [@alphaproteo]                                         |
| Latent-X1 / Latent-X2                                | All-atom binder & antibody designer                            | Undisclosed                                             | Undisclosed (all-atom)                                                | Macrocycles, minibinders (X1); drug-like VHH/scFv & macrocycles (X2)              | Undisclosed generator + ipTM/PAE and self-consistency filtering                                        | Closed weights & undisclosed architecture                    | [@latentx1; @latentx2]                                 |
| IsoDDE / SeedFold                                    | Unpublished structure predictors                               | Undisclosed                                             | Undisclosed                                                           | Biomolecular complexes, Ab–Ag                                                     | Known publicly only via third-party scaling-curve points in OpenDDE                                    | Closed / unpublished                                         | [@opendde; @bender_perspective]                        |

## AlphaFold and open reproductions

AlphaFold2 [@alphafold2] demonstrated experimental-level single-chain structure
prediction at CASP14 (median 0.96 Å r.m.s.d.95, 95% CI 0.85–1.16 Å, versus 2.8 Å
for the next best method) by combining an MSA-driven Evoformer trunk and
distogram head with an end-to-end differentiable Invariant Point Attention (IPA)
structure module. Because coordinates emerge from a single differentiable
regression pass, AlphaFold2 served both as a standard post-hoc refolding filter
[@rfdiffusion; @alphaproteo] and as a substrate for gradient-based sequence
design [@bindcraft]. Its documented weakness is a sharp accuracy drop when MSA
depth shrinks, making single-sequence input its weakest regime [@alphafold2].
AlphaFold-Multimer [@alphafold_multimer], released as a bioRxiv preprint without
peer review, retrained the network on protein complexes and introduced
interchain confidence scores (ipTM and interchain PAE) that became standard
design filters; gradient-based complex design tools such as BindCraft
[@bindcraft], Germinal [@germinal], and mBER [@mber] invert AlphaFold-Multimer
rather than the monomer model. OpenFold [@openfold] provided an open-source
retraining of AlphaFold2 alongside a structural distillation dataset later used
to train Boltz-1 [@boltz1].

AlphaFold3 [@alphafold3] generalized co-folding to complexes of proteins,
nucleic acids, small-molecule ligands, and ions by replacing the Evoformer with
a simplified Pairformer trunk and substituting an all-atom diffusion module for
IPA. On the 428-structure PoseBusters benchmark, it outperformed AutoDock Vina
and RoseTTAFold All-Atom without requiring solved pocket coordinates
[@alphafold3]. For antibody–antigen complexes, however, reported accuracy relied
on selecting the top-ranked sample across 1,000 random seeds rather than the
five seeds used for other classes, with accuracy still improving at 1,000 seeds
[@alphafold3]. Multi-step diffusion also prevents direct end-to-end
backpropagation through coordinates and introduces documented physical-validity
artifacts: a 4.4% chirality violation rate on PoseBusters despite a chirality
ranking penalty, residual steric clashes, and hallucinated secondary structure
in intrinsically disordered regions (mitigated via cross-distillation from
AlphaFold-Multimer v2.3) [@alphafold3]. Predictions remain static PDB-like
structures rather than conformational ensembles, and shallow MSAs still degrade
accuracy [@alphafold3].

AlphaFold3's restricted weights prompted open reproductions including Boltz-1
[@boltz1], Protenix [@protenix_v1], and OpenFold3 [@openfold3]. OpenFold3
distributes Apache-2.0 weights, training code, and its full training corpus,
including a reproduction of AlphaFold3's 13-million-sequence MGnify distillation
set, enabling retraining from scratch [@openfold3]. As a software release rather
than a peer-reviewed paper, OpenFold3 relies on self-reported benchmarks, and
its technical report evaluates superseded `preview2` weights rather than the
newer `OpenBind-0` default [@openfold3].

## RoseTTAFold, RFdiffusion, and inverse folding

Developed independently of AlphaFold at the Baker Lab and the Institute for
Protein Design, this family spans structure predictors, diffusion generators,
inverse folding models, and modality-specific tools. Two similarly named recent
releases serve opposite roles: RoseTTAFold3 (RF3) [@rosettafold3] is an all-atom
structure predictor that denoises coordinates for a known sequence, whereas
RFdiffusion3 (RFD3) [@rfdiffusion3] is a generative model that denoises
coordinates with sequence unknown before inverse folding.

The predictor branch began with RoseTTAFold (RF1) [@rosettafold], a three-track
(1D sequence, 2D pairwise distance, 3D coordinate) network contemporaneous with
AlphaFold2 in which complex prediction emerged via discontinuous two-segment
cropping without dedicated multimer training; superseded as a predictor, RF1
supplied the weights fine-tuned into RFdiffusion [@rfdiffusion]. RoseTTAFold2
(RF2), an unreviewed bioRxiv preprint, ablated AlphaFold2 and showed that FAPE
loss, recycling, distillation, and depth drove accuracy while IPA and triangle
attention were unnecessary: RF2 matched AlphaFold2 on monomers and
AlphaFold-Multimer on complexes without either module, scaled better past 1,000
residues, and kept an input-to-output 3D coordinate track suited to spatial
design constraints [@rosettafold2]. Built on RF2, RoseTTAFold All-Atom (RFAA)
added nucleic acids, small molecules, and metals two months before AlphaFold3
[@rosettafold_all_atom]. RoseTTAFold3 (RF3) subsequently adopted a BSD-licensed
all-atom diffusion architecture that learns ligand chirality from geometric
features rather than inference-time guidance, predicting 88% of ligand chiral
centers correctly versus 84% for AlphaFold3 and 76% for Boltz-2 without
guidance, and achieving 1.74 Å mean backbone RMSD on mixed L/D peptides versus
1.88 Å for AlphaFold3 and 2.24 Å for Boltz-1x [@rosettafold3]. Its authors
caution that inference-time modifications may shift diffusion networks outside
their training distribution [@rosettafold3].

On the generative side, RFdiffusion (RFD1) fine-tuned RF1 for equivariant frame
diffusion over each residue's Cα position and N–Cα–C frame orientation,
outperforming earlier RoseTTAFold hallucination and establishing the backbone
diffusion, ProteinMPNN, and AlphaFold2 refolding workflow [@rfdiffusion]. Its
authors note that reported in silico success measures agreement with AlphaFold2
confidence and self-consistency RMSD filters rather than experimental binding
[@rfdiffusion]. RFdiffusion2 (RFD2), also fine-tuned from RoseTTAFold, enabled
sequence-agnostic, atom-level enzyme active-site scaffolding from
functional-group coordinates [@rfdiffusion2]. RFdiffusion3 (RFD3) departed from
predictor initialization by pre-training an all-atom transformer U-Net modeled
on AlphaFold3's diffusion module directly on PDB structures and AlphaFold2
distillation data; reducing the Pairformer from 48 to 2 layers (168 million
trainable parameters) with 100-step sampling makes RFD3 roughly an order of
magnitude faster than earlier versions [@rfdiffusion3].

Because backbone generators omit amino-acid identities, inverse folding models
assign sequences. ProteinMPNN [@proteinmpnn], an autoregressive message-passing
neural network for fixed backbones, became the standard sequence-design
component across RFdiffusion [@rfdiffusion], RFpeptides [@rfpeptides], BindCraft
surface redesign [@bindcraft], and PXDesign [@pxdesign], though its authors
caution that native sequence recovery does not necessarily correlate with
accurate folding [@proteinmpnn]. LigandMPNN [@ligandmpnn] conditions sequence
design on non-protein context including small molecules, nucleic acids, and
metal ions, while AlphaDesign's Autoregressive Diffusion Model (ADM)
[@alphadesign] benchmarks comparably to ProteinMPNN with complementary
structural preferences.

Two modality extensions adapted this framework to antibodies and cyclic
peptides. RFantibody [@rfantibody] fine-tuned RFdiffusion for epitope-specific
VHH, scFv, and antibody design, testing 9,000 designs per target by yeast
display (four targets) and 95 per target by *E. coli* expression with surface
plasmon resonance (SPR; three targets); confirmed hit rates of 0–2% (best SPR
affinities 78 nM on influenza hemagglutinin and 1.4 µM on RSV site III) led the
authors to note that experimental library screening remains necessary
[@rfantibody]. RFpeptides [@rfpeptides] added a cyclic relative positional
encoding to RFdiffusion and RF2 for head-to-tail macrocycles, pairing
ProteinMPNN with AfCycDesign [@afcycdesign] and Rosetta interface filtering to
obtain crystal-structure-verified binders across all four targets from fewer
than 20 synthesized designs each. A separate tool in this family, RFOptimization
[@rfoptimization], uses RF3 gradients for training-free discrete refinement and
is covered under gradient-based design.

## Boltz

Boltz-1 [@boltz1], the first MIT-licensed AF3-class all-atom co-folder, was
trained partly on OpenFold distillation structures [@openfold] and supported
external design tools such as BoltzDesign1 [@boltzdesign1] (covered under
gradient-based design). Boltz-1x added Boltz-steering, using Feynman-Kac
steering potentials at inference time to reduce chirality violations and steric
clashes [@boltz1]. Boltz-2 [@boltz2] maintained essentially unchanged
structure-prediction accuracy while adding conditioning controls and a
small-molecule affinity module. That module achieved a mean Pearson correlation
of 0.66 on the four-target FEP+ subset at over 1,000-fold lower compute than
free-energy perturbation and exceeded 0.55 on three of eight blinded industrial
assays (weaker on the other five), but because it is trained on single-protein
ligand assays, it does not predict protein–protein binding affinity [@boltz2].
Its June 1, 2023 training cutoff also overlaps the standard FoldBench window
(January 13, 2023 to November 1, 2024), causing temporal leakage noted in later
benchmarks [@protenix_v1; @protenix_v2; @esmc].

BoltzGen [@boltzgen] introduced an MIT-licensed (weights, training code, and
data) all-atom diffusion model trained jointly for structure prediction
(matching Boltz-2 on its test set) and de novo binder design across proteins,
peptides, and nanobodies against targets from disordered proteins to small
molecules, excluding full antibodies from training and filtering candidates with
Boltz-2 refolding. Across eight wet-lab campaigns covering 26 targets, testing
at most 15 designs per target yielded nanomolar binders on 6 of 9 novel targets
(\<30% PDB sequence identity in a bound context) in both nanobody and
miniprotein formats, and 15–20 designs per target yielded binders on 4 of 5
benchmark targets in each format (down to 0.81 nM on PDGFR) [@boltzgen].
Disclosed caveats include diversity collapse into ubiquitin at binder lengths
73–76 (attributed to more than 900 PDB ubiquitin entries) and a `BoltzGenv0`
refolding bug that mis-assigned fixed binder residues to the target chain
(yielding 0/7 hits on two targets versus 1/7 and 7/7 once fixed); the authors
caution that binder design is not plug-and-play and advise manual structural
inspection and reruns [@boltzgen].

BoltzProt-1 [@boltzprot1] paired a refined BoltzGen generator with BoltzPPI, a
classifier trained directly on experimental binding outcomes rather than
structure-confidence heads. Across 10 low-homology targets using identical
candidate pools and 15 designs per target (150 total), switching from BoltzGen's
confidence ranking to BoltzPPI raised confirmed binders from 3.3% (5/150; 2/10
targets) to 8.0% (12/150; 4/10 targets) [@boltzprot1]. The study separated
initial screening hits from confirmed binders verified by flipped assay
orientations and independent vendor re-testing [@boltzprot1]. Unlike earlier
MIT-licensed Boltz releases, BoltzProt-1 is offered only via commercial API and
platform access without released weights [@boltzprot1].

## Chai

Chai-1 [@chai1] is an AF3-class diffusion co-folder with both an MSA track and a
protein language model track usable independently or together, plus optional
experimental restraints (pocket, contact, or docking) that deliver double-digit
accuracy gains. It matched AlphaFold3 on PoseBusters (77% versus 76% ligand RMSD
success), and on antibody–protein interfaces, single-sequence Chai-1 matched
MSA-enabled Chai-1 while both outperformed AlphaFold-Multimer v2.3 with MSAs,
which the authors attribute to weak evolutionary signal in antibodies [@chai1].
Model weights carry a non-commercial license (commercial use via web server),
and commercial use restrictions prevented benchmarking against AlphaFold3 or
ESM-3, confining comparison to AlphaFold-Multimer v2.3 on CASP15 [@chai1].

Chai-2 [@chai2] built on Chai-1 (via an intermediate `Chai-1d` prototype) for
zero-shot scFv, VHH, and minibinder design without library screening or affinity
maturation. Testing at most 20 designs per target per format across 52 novel
targets produced 13.7% scFv (68/496) and 20.0% VHH (41/205) hit rates (16%
combined; binders on 26/52 targets), while five minibinder targets (20–25
designs each) achieved a 68% hit rate (75/111; best affinity 18.3 pM on IL-7Rα)
[@chai2]. The paper describes only the folding submodule (`Chai-2f`, similar in
architecture to Chai-1) and withholds the generative architecture [@chai2]. A
commercial successor, Chai-3 (2026), runs via Chai Discovery's web platform
without an accompanying publication.

## Gradient-based design by backpropagation

Gradient-based design inverts a pretrained structure predictor, updating a
sequence so predicted complexes satisfy structural confidence or contact losses.
These methods differ in gradient path (full coordinate regression versus trunk
distograms and confidence heads), sequence representation (continuous relaxation
versus discrete mutations), and language-model priors (live gradients versus
static logit biases). Because AlphaFold2's Invariant Point Attention module
predicts coordinates in one differentiable pass, gradients propagate end-to-end
to the input sequence [@alphafold2]. ColabDesign supplies the open-source
AlphaFold2 backpropagation library and three-stage annealing schedule
(`design_3stage`) used by AfCycDesign, BindCraft, Germinal, and mBER
[@colabdesign]. AfCycDesign applies a cyclic relative positional encoding to the
peptide while keeping the target linear, yielding eight monomeric macrocycle
crystal structures within 1.0 Å of design models, although its MDM2 and Keap1
binders grafted known motifs onto hallucinated scaffolds before ProteinMPNN and
Rosetta redesign rather than hallucinating binders directly [@afcycdesign].
BindCraft backpropagates confidence losses through AlphaFold-Multimer into an $L
\\times 20$ sequence matrix, randomly swapping five weight sets and repredicting
the target each step for induced fit (0.5–5.5 Å target Cα RMSD) [@bindcraft]. A
four-stage schedule anneals logits to softmax probabilities, straight-through
estimation (one-hot forward, softmax backward), and discrete mutation search,
followed by soluble-weight ProteinMPNN surface redesign (>4 Å from the
interface), single-sequence AlphaFold2 refolding, and Rosetta scoring, achieving
10–100% hit rates (mean 46.3%) across 12 targets (6–53 designs/target)
[@bindcraft]. Optimizing single-sequence binders operates outside AlphaFold2's
MSA training regime, and ipTM predicts binding rather than affinity
[@alphafold2; @bindcraft]. A successor code release, BindCraft2, extends this
loop to cyclic peptides, VHHs, scFv/Fab fragments, ankyrin repeats, multidomain
binders, disordered motifs, and molecular glues without published benchmarks
yet.

Because unrolling multi-step diffusion denoising is impractical, BoltzDesign1
and RFOptimization backpropagate from Pairformer distogram and confidence heads
while diverging in sequence representation. BoltzDesign1 adapts BindCraft's
continuous schedule to Boltz-1 (adding a softmax warm-up), places a
stop-gradient on diffusion, and minimizes contact losses on the 64-bin
Pairformer distogram, optionally using the confidence head (needed for
nucleic-acid targets) and LigandMPNN surface redesign \[@boltzdesign1; @boltz1;
@ligandmpnn\]. RFOptimization refines existing designs strictly in discrete
space to avoid continuous-relaxation artifacts, proposing single-point
substitutions from negative normalized gradients of RoseTTAFold3's distogram and
confidence heads via annealed Metropolis–Hastings [@rfoptimization;
@rosettafold3]. On half of its steps, it runs a Boltz folding and LigandMPNN
resampling cycle while holding AlphaFold3 out, raising AF3-refolded success
(iPAE < 2.5, ipTM > 0.8) across protein–protein interfaces (6.73% to 22.31%),
cyclic peptides (1.25% to 12.57%), and small-molecule binders (5.62% to 24.91%)
[@rfoptimization]. Both systems are evaluated in silico only [@boltzdesign1;
@rfoptimization].

To enforce natural antibody sequences, Germinal and mBER add language-model
priors to AlphaFold-Multimer differently. Germinal designs CDR loops on a
CDR-masked framework template by merging live AlphaFold-Multimer and IgLM
gradients (via weighted sum, MGDA, or PCGrad), feeding a continuous
position-specific scoring matrix to AlphaFold-Multimer and straight-through
discrete tokens to IgLM, followed by semigreedy steps and AbMPNN redesign
(43–101 designs/antigen) [@germinal]. Nonbinders cleared the same ipSAE
threshold as binders, and dependence on AlphaFold3-predicted antigen accuracy
remains open [@germinal]; OpenGerminal reimplements the pipeline under
Apache-2.0 with open-source scoring and AbLang1 [@opengerminal]. By contrast,
mBER runs ESM-2 once over a NanoBodyBuilder2-templated VHH framework (templated
separately from the target hotspot, without MSAs) and adds fixed logits as a
static bias throughout `design_3stage`, with ablations showing both template and
prior are required [@mber]. Across 1,153,241 VHHs for 436 targets (145 assayed)
with random hotspots, phage enrichment spanned 0.4% overall to 7.5% at a single
target's best hotspot and 38% (8/21) in an ipTM-filtered bin without affinity
quantification [@mber]; mBER-2 (a company technical report) extends to
microbinders at roughly tenfold higher hit rates without stating whether
hotspots were randomized.

## Protenix

ByteDance Seed's Protenix family combines open-weights co-folding, dual-mode
binder design, antibody generation, and benchmarking tools. Protenix-v1
reproduces AlphaFold3 under open weights; under matched training cutoff, scale,
and inference budget, it outperforms AlphaFold3 on protein–protein and
antibody–antigen interfaces and trails on protein–ligand and protein–DNA
complexes, while its recommended `Protenix-v1-20250630` checkpoint trains past
that strict cutoff [@protenix_v1]. DockQ success scales roughly log-linearly
with sampling budget (36.01% at 1 seed to 47.68% at 80 seeds; 95% bootstrap CI
49.3–56.3% for one 5×5 run) [@protenix_v1]. On FoldBench [@foldbench],
Protenix-v1 showed that model-specific inference failures evaluate models on
unequal subsets (e.g., Boltz-1 on 252 interfaces vs. Chai-1 on 251, sharing 237)
and restricting to the common intersection reverses which model leads
[@protenix_v1]. Built on Protenix, PXDesign offers two modes: PXDesign-d uses a
Diffusion Transformer (DiT) over Cartesian coordinates, whereas PXDesign-h
replaces 200-step diffusion with a 2-step ODE sampler for end-to-end gradient
hallucination across five resampled Protenix models [@pxdesign]. All six wet-lab
campaigns used PXDesign-d (20–73% nanomolar hit rates on 5/6 targets; 0/16 on
TNFα), while filtering analysis showed that Protenix and AF2-IG retain largely
distinct true positives with target-dependent thresholds [@pxdesign].

Protenix-v2 improves antibody–antigen DockQ > 0.23 success by 9–13 percentage
points over Protenix-v1 across PXMeter-AB, FoldBench-AB, and AF3-AB, with 5
seeds outperforming Protenix-v1 at 1,000 seeds [@protenix_v2]. It expands design
to VHH, Fv, and full mAbs in epitope-specific and site-agnostic modes. On a
novelty-controlled soluble panel (applying BoltzGen's 30%-identity and Chai-2's
SAbDab filters), biolayer interferometry (BLI)-confirmed VHH-Fc binders were
found for every antigen (100% target-level success; 2–48% hit rates); on four
GPCRs with small, flexible extracellular epitopes, testing 16–30 designs per
target yielded 16–88% VHH-Fc and 0–50% mAb hit rates [@protenix_v2]. Two AMBP
epitopes produced 4% versus 48% hit rates, prompting prioritization of native
ligand-binding interfaces; caveats include manual epitope selection on in-stock
targets and no direct Chai-2 head-to-head because overlapping targets differed
in format [@protenix_v2]. ByteDance Seed's open PXMeter benchmark toolkit
[@pxmeter] added sp2-planarity, amide-planarity, and sp3-non-planarity checks in
v1.1.0 (introduced with Protenix-v2 and used as PXMeter-AB by OpenDDE) after
observing twisted amides and flat sp3 centers passing PoseBusters
\[@protenix_v2; @opendde; @posebusters\].

## ESM

The ESM lineage replaces inference-time MSA searches with protein language
models trained on billions of sequences. ESM-2 and ESMFold showed that a masked
language model paired with a folding trunk and IPA structure module predicts 3D
structures from single sequences without MSAs or templates, trading lower
accuracy than AlphaFold2 for much faster inference across the ESM Metagenomic
Atlas [@esm2]. ESM-3 scaled to a multimodal discrete-token transformer covering
sequence, structure, and function across 2.78 billion proteins (1.4B, 7B, and
98B parameters), improving CAMEO single-sequence lDDT over ESMFold (0.880 vs.
0.861) and generating functional `esmGFP` at 58% sequence identity to natural
fluorescent proteins; `ESM3-open` (1.4B) is academic-only while the 98B model is
API-only [@esm3].

ESMC and ESMFold2 extend single-sequence language modeling to all-atom complexes
and binder design [@esmc]. Frozen 6B-parameter ESMC representations (~2.8
billion sequences) feed 48 recurrent pair-state folding layers (24 in
ESMFold2-Fast) and a sliding-window diffusion transformer, with an optional
detachable MSA encoder [@esmc]. Single-sequence ESMFold2 matches MSA-enabled
AlphaFold3 on antibody–antigen interfaces within error bars across independent
AtlasFold runs [@esmc; @atlasfold]. Because single-sequence input is native,
binder optimization backpropagates directly through ESMC and the folding trunk's
distogram for 150 single-stage steps (annealed to temperature 0.01 across two
replicates), running diffusion and confidence heads only in final steps to rank
by ensemble ipTM or distogram-entropy proxy (plus pI ≤ 6.0 for minibinders)
[@esmc]. Testing 84 designs per cohort across five author-selected targets
yielded 36–88% hit rates (mean 70.0% at higher compute; best 68 pM) for
minibinders and 15–29% (mean 21.0%) for scFvs [@esmc]. Independently, AtlasFold
released an MIT-licensed single-sequence language-model folder (weights, code,
data, and checkpoints) alongside a seven-model FoldBench rank-versus-oracle
benchmark [@atlasfold].

## Closed and undisclosed systems

Several binder-design systems publish wet-lab outcomes while withholding
generative architectures or weights. Google DeepMind's AlphaProteo tested 54–172
minibinders across eight targets, achieving 9% (TrkA) to 88% (BHRF1) hit rates
(0/54 on TNFα; best 82 pM on IL-7Rα) and resynthesizing RFdiffusion designs for
yeast-display comparison; it discloses its AF2 filter (`interchain PAE < 10`,
`binder-aligned binder RMSD < 1 Å`, `pLDDT > 80`) but describes the generator
only as trained on PDB and AlphaFold distillation data [@alphaproteo]. Latent
Labs' Latent-X1 and Latent-X2 describe only a proprietary all-atom architecture
filtered by ipTM, PAE, and self-consistency [@latentx1; @latentx2]. Latent-X1
reported 10–64% minibinder hit rates (five targets; best < 0.01 nM) and 91–100%
on macrocycles (three targets; 11–17 peptides tested), resynthesizing
RFpeptides' two top binders for affinity comparison while leaving hit rates
across distinct assays [@latentx1; @rfpeptides]; Latent-X2 reported macrocycles
on two targets (best 1.54 nM) and VHH/scFv binders on 9/18 targets (best 26.2
pM) with drug-like developability and low immunogenicity [@latentx2]. Within
their own lineages, Chai-2 likewise withholds its generator beyond `Chai-2f`
[@chai2] and BoltzProt-1 limits access to a commercial API [@boltzprot1].

Other systems have no primary publications and appear only via platforms or
external benchmarks. OpenDDE, an Apache-2.0 co-folder built on Protenix-v1 and
OpenFold3, triples Pairformer hidden width from 128 to 384 (~3× parameters, ~9×
compute), adds an atom-level refiner before diffusion, and lists joint design on
its roadmap [@opendde]. Alongside third-party antibody–antigen comparisons,
OpenDDE supplies the only public scaling-curve points for unpublished IsoDDE
(also noted as lacking public verification by Bender et al.
[@bender_perspective]) and SeedFold [@opendde], alongside the commercial web
platform Chai-3.

# Quantitative Landscape and Evaluation Pitfalls

Interpreting structure-prediction and binder-design benchmarks requires reading
every metric alongside its evaluation protocol. On the common target
intersection of FoldBench (1,522 assemblies across nine tasks scored by lDDT,
DockQ, and RMSD), monomer accuracy across seven AF3-class predictors has
converged into a tight 0.85–0.89 lDDT band and general protein–protein DockQ
success spans roughly 7 percentage points (65.4–72.7%), whereas antibody–antigen
success spans more than a factor of two (23.1–52.3%; **Table 2A**) \[@foldbench;
@protenix_v1\]. Even on a shared target set, training cutoffs constrain who can
be compared: Boltz-2 is excluded from FoldBench common-intersection tables
because its 2023-06-01 cutoff overlaps the 2023-01-13 to 2024-11-01 benchmark
window [@boltz2; @protenix_v1; @protenix_v2; @esmc].

Identical metric names also shift when target filtering, averaging units, or MSA
pipelines change. Because models fail on different inputs (out-of-memory errors,
unsupported glycans, or token limits), restricting FoldBench protein–protein
pairs to the common completed set ($n = 237$) reverses Boltz-1 (68.4% vs. 68.3%
published) and Chai-1 (67.5% vs. 68.5% published), while AlphaFold3's FoldBench
antibody–antigen score varies modestly across unfiltered (47.90%),
intersection-filtered (48.75%), and independently re-run (48.8%) evaluations
[@foldbench; @protenix_v1; @opendde]. Averaging units cause far larger swings:
Chai-1 reports 52.9% antibody DockQ success over 40%-identity interface clusters
[@chai1], whereas FoldBench evaluates per interface and obtains 25.2% for the
same model [@foldbench]. Boltz-1 uses a third convention, averaging per
interface within each complex before averaging across complexes [@boltz1], and
external FoldBench runs of OpenFold3 shifted from 70.79% to 69.29% under a
different MSA pipeline [@openfold3; @protenix_v2].

A distinct bottleneck separates generating a near-native complex from
recognizing it with internal confidence scores. Across seven predictors
evaluated template-free by AtlasFold (**Table 2A**), selecting the top sample by
confidence loses 11–21 percentage points relative to oracle selection against
the experimental structure on antibody–antigen interfaces (4.5 points for
Boltz-1) and 3–8 percentage points on general protein–protein interfaces
[@atlasfold]. FoldBench similarly observed that an accurately modeled CDR-H3
loop is necessary but not sufficient for correct antibody–antigen docking
because confidence scores do not reliably identify near-native poses
[@foldbench]. This ranking gap drives large inference-time seed budgets:
AlphaFold3 ranked antibody–antigen poses over 1,000 seeds [@alphafold3],
Protenix-v1 climbed from 36.01% (1 seed) to 47.68% (80 seeds) [@protenix_v1],
and OpenDDE reported oracle antibody–antigen success rising from roughly 66% to
over 90% at several hundred seeds [@opendde].

**Table 2A. Shared structure-prediction benchmarks (FoldBench common
intersection) and confidence-ranking versus oracle selection gaps (AtlasFold).**

| Model                                  | FoldBench Monomer (lDDT, $n = 287$) | FoldBench Prot–Prot (%, $n = 237$) | FoldBench Ab–Ag (%, $n = 160$) | FoldBench Prot–Lig (%, $n = 441$) | AtlasFold Ab–Ag Rank / Oracle (%, $n = 172$) | AtlasFold Prot–Prot Rank / Oracle (%, $n = 278$) |
| -------------------------------------- | ----------------------------------: | ---------------------------------: | -----------------------------: | --------------------------------: | -------------------------------------------: | -----------------------------------------------: |
| Protenix-v1 [@protenix_v1]             |                              0.8857 |                              72.70 |                          52.31 |                             62.54 |                              44.945 / 65.818 |                                  74.445 / 81.572 |
| AlphaFold3 [@alphafold3]               |                              0.8803 |                              71.73 |                          48.75 |                             62.59 |                              49.285 / 66.168 |                                  73.006 / 78.028 |
| Boltz-1 [@boltz1]                      |                              0.8664 |                              68.35 |                          34.38 |                             54.65 |                              34.967 / 39.505 |                                  71.120 / 76.632 |
| Protenix-v0.5.0 [@protenix_v1]         |                              0.8717 |                              68.06 |                          43.94 |                             58.49 |                                          n/a |                                              n/a |
| Protenix-v0.2.0 [@protenix_v1]         |                              0.8622 |                              66.24 |                          35.62 |                             51.02 |                                          n/a |                                              n/a |
| HelixFold3 (via [@protenix_v1])        |                              0.8547 |                              65.40 |                          28.75 |                             52.38 |                                          n/a |                                              n/a |
| Chai-1 [@chai1]                        |                              0.8639 |                              67.51 |                          23.12 |                             50.79 |                                          n/a |                                              n/a |
| ESMFold2 (MSA) [@esmc]                 |                                 n/a |                                n/a |                            n/a |                               n/a |                              52.270 / 63.427 |                                  73.230 / 77.237 |
| ESMFold2 (seq only) [@esmc]            |                                 n/a |                                n/a |                            n/a |                               n/a |                              48.602 / 61.489 |                                  69.216 / 74.071 |
| AtlasFold-M (seq only) [@atlasfold]    |                                 n/a |                                n/a |                            n/a |                               n/a |                              46.955 / 64.733 |                                  63.358 / 71.560 |
| AF-Multimer v2.3 [@alphafold_multimer] |                                 n/a |                                n/a |                            n/a |                               n/a |                              40.924 / 52.921 |                                  65.206 / 68.615 |

*Notes for Table 2A:* FoldBench common-intersection columns report PDB entries
released 2023-01-13 to 2024-11-01 (homology-reduced against a reproduction of
AlphaFold3's 2021-09-30 training set) under 5 seeds × 5 diffusion samples, 10
recycles, top-ranked prediction [@foldbench; @protenix_v1]. Monomer is mean
lDDT; Prot–Prot and Ab–Ag are DockQ success rate (DockQ ≥ 0.23, %); Prot–Lig is
joint success rate (ligand RMSD < 2 Å and lDDT-PLI > 0.8, %). AlphaFold3,
Boltz-1, Chai-1, HelixFold3, and Protenix-v0.2.0 rows were recomputed by the
Protenix-v1 authors from published per-instance logs with the
common-intersection filter applied; Protenix-v0.5.0 and Protenix-v1 are the
authors' own runs (Protenix-v1 bootstrapped over 5-seed draws from 20 seeds)
[@protenix_v1]. On the same common set, nucleic-acid subsets span 50.00–68.46%
(Prot–RNA, $n = 46$), 49.27–75.91% (Prot–DNA, $n = 274$), 0.2909–0.5693 lDDT
(DNA, $n = 14$), and 0.4416–0.6547 lDDT (RNA, $n = 15$) [@protenix_v1]. Boltz-2
[@boltz2] is excluded because its 2023-06-01 training cutoff overlaps the
FoldBench window [@protenix_v1; @protenix_v2; @esmc]. AtlasFold columns report
mean DockQ > 0.23 (%) across 252 five-seed subsets drawn from 10 seeds,
template-free throughout, computed with OpenStructure 2.9.1; AlphaFold3,
Boltz-1, Protenix-v1, and ESMFold2 (MSA) used AlphaFold3-pipeline MSAs, whereas
ESMFold2 (seq only) and AtlasFold-M ran without MSAs [@atlasfold]. Per-class
headline tables in AlphaFold3 (Extended Data Table 1 / Fig. 1c) [@alphafold3],
Boltz-1 [@boltz1], Boltz-2 [@boltz2], and RoseTTAFold2 [@rosettafold2] are
published as figure-only images rather than extractable text.

Wet-lab binder campaigns are even less directly comparable because no two de
novo studies share a target panel, assay format, or binding threshold. Grouping
campaigns by confirmation rigor (**Table 2B**) exposes four recurring
confounders. First, several headline affinities reflect bivalent Fc fusions or
avidity-affected formats rather than monovalent affinity, including
Protenix-v2's VHH-Fc constructs (except VEGF-A) [@protenix_v2], four of Chai-2's
ten quoted miniproteins plus its EFNA5 scFv [@chai2], and BindCraft's bivalent
Fc PD-1 construct [@bindcraft]. Second, synthesis and expression attrition
alters denominators, as documented in RFpeptides [@rfpeptides], Latent-X1
macrocycles [@latentx1], and PXDesign's PD-L1 campaign (72.7% of tested designs
vs. 47.1% sent for expression) [@pxdesign]. Third, some studies report
target-level success (BoltzGen, Protenix-v2, Latent-X2) \[@boltzgen;
@protenix_v2; @latentx2\] while others report per-design hit rates (Chai-2,
PXDesign, BindCraft, ESMFold2) [@chai2; @pxdesign; @bindcraft; @esmc].

Fourth, operational binding criteria range from unthresholded qualitative SPR
responses [@bindcraft; @rfpeptides; @latentx1] and single-point BLI cutoffs
spanning 0.05–0.4 nm [@protenix_v2; @pxdesign; @chai2; @esmc; @latentx2] to
BoltzProt-1's separation of initial screening hits (including ambiguous
sensorgrams) from confirmed binders verified by capture-level variation,
concentration series, inverted assay orientation, and independent vendor
re-testing [@boltzprot1]. Three cross-lab resynthesis experiments illustrate how
strongly assay protocols shift reported outcomes. When AlphaProteo re-tested
RFdiffusion's published designs (including nonbinders) by yeast display at
10–20× lower target concentrations, hit rates fell from 33% to 16% on IL-7Rα and
from 6% to 0% on TrkA [@alphaproteo; @rfdiffusion]. When Latent-X1 resynthesized
RFpeptides' two top macrocycles, measured affinities were 4.4× and 5× weaker
than published, with Latent-X1 leading on MDM2 and trailing on MCL-1
\[@latentx1; @rfpeptides\]. Latent-X2 likewise resynthesized two RaPID
macrocycles under a different cyclization chemistry than its own designs
[@latentx2]. **Table 2B** therefore summarizes performance within each study's
own experimental regime rather than on a common scale.

**Table 2B. Representative wet-lab and in-silico binder design campaigns grouped
by experimental validation format.**

| System                                                        | Modality & Targets                                                  |                            Designs Tested | Reported Outcome / Hit Rate                                                                                                                       | Best Affinity                                      | Key Assay Criterion & Caveats                                                                                                                                                          |
| ------------------------------------------------------------- | ------------------------------------------------------------------- | ----------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Binding confirmed across two assay formats**                |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| BoltzProt-1 [@boltzprot1]                                     | VHH, 10 low-homology targets                                        |                           15/target (150) | 12 confirmed binders (8.0%; 4/10 targets); BoltzGen on same pools and budget: 5 (3.3%; 2/10 targets)                                              | Not reported                                       | Clean sensorgram verified by flipped assay orientation and independent vendor re-testing; separate from initial screening hits (see footnote) [@boltzprot1].                           |
| Germinal [@germinal]                                          | scFv (tested as Fab), 2 targets                                     |                                 48/target | 3/48 PD-L1 and 1/48 IL-3 confirmed on both SPR and BLI                                                                                            | 360 nM (SPR) / 650 nM (BLI)                        | Dual SPR and BLI confirmation [@germinal].                                                                                                                                             |
| Latent-X1 [@latentx1]                                         | Minibinders, 5 targets                                              | 100/target (HT-BLI), 88/target (mDisplay) | 10–64% per target (platforms correlate at Pearson $r = 0.68$–$0.79$)                                                                              | < 0.01 nM (IL-7Rα, SC2RBD)                         | Robust mammalian-display dynamic range on 3 of 5 targets; proprietary architecture undisclosed [@latentx1].                                                                            |
| Germinal [@germinal]                                          | VHH, 4 targets                                                      |                101 / 46 / 43 / 52 ordered | 7 / 2 / 4 / 5 confirmed by BLI after split-luciferase screen                                                                                      | 170 nM (PD-L1); 42 nM after Legobody rescaffolding | Expression luminescence > 150,000 RLU and rising binding ratio between two timepoints, then detectable BLI; quoted fractions use BLI sub-denominators (25 / 11 / 11 / 20) [@germinal]. |
| **Single assay format**                                       |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| Latent-X2 [@latentx2]                                         | Macrocycles, 2 targets                                              |                                 10/target | 9/10 (PHD2), 8/10 (K-Ras G12D)                                                                                                                    | 1.54 nM (PHD2)                                     | Reference-subtracted single-point BLI > 0.1 nm advancing to kinetics (global fit $R^2 > 0.95$); architecture undisclosed [@latentx2].                                                  |
| RFpeptides [@rfpeptides]                                      | Macrocycles, 4 targets                                              |           6–14 tested (of 11–27 selected) | 2–4 hits per target                                                                                                                               | 6 nM (GABARAP)                                     | SPR single-cycle kinetics at 100 µM (no numeric threshold stated); synthesis attrition (14/27 MCL-1, 11/26 RbtA); crystal structures solved [@rfpeptides].                             |
| BoltzGen [@boltzgen]                                          | VHH and proteins, 9 novel targets                                   |                                 15/target | Binders on 6/9 targets, both modalities                                                                                                           | 6.1 nM VHH (PMVK); 9.8 nM protein (MZB1)           | Quantifiable sensorgram, or association ≥ 300% of negative control where fitting failed; target-level rate reported [@boltzgen].                                                       |
| PXDesign [@pxdesign]                                          | Minibinders, 6 targets                                              |                               9–17/target | 20–73% on 5 targets; 0/16 on TNFα                                                                                                                 | "Multiple nanomolar" (no exact value in text)      | BLI > 0.06 nm at 1 µM then $K_D < 1,000$ nM; PD-L1 attrition: 72.7% of tested vs. 47.1% sent for expression (6 excluded) [@pxdesign].                                                  |
| Latent-X1 [@latentx1]                                         | Macrocycles, 3 targets                                              |                              11–17/target | 91 / 100 / 94%                                                                                                                                    | 5.35 µM (MDM2)                                     | Measurable SPR signal (no numeric threshold stated); 11–17 synthesized of 30 submitted (700 generated); architecture undisclosed [@latentx1].                                          |
| Chai-2 [@chai2]                                               | scFv and VHH, 52 novel targets                                      |                        ≤ 20/target/format | 13.7% scFv (68/496), 20.0% VHH (41/205); 26/52 targets                                                                                            | < 1 nM (EFNA5 scFv, avidity-flagged)               | Binding-positive curve > 0.1 nm and > 300% of background; EFNA5 scFv avidity-flagged; generator undisclosed [@chai2].                                                                  |
| BoltzGen [@boltzgen]                                          | VHH and proteins, 5 benchmark targets                               |                              15–20/target | Binders on 4/5 targets                                                                                                                            | 0.81 nM (PDGFR)                                    | Same sensorgram / ≥ 300% negative-control criterion; target-level rate reported [@boltzgen].                                                                                           |
| Latent-X2 [@latentx2]                                         | VHH and scFv, 18 targets                                            |                        4–24/target/format | Binders on 9/18 targets; up to 25% of designs                                                                                                     | 26.2 pM (HDAC8 scFv)                               | Single-point BLI > 0.1 nm advancing to kinetics (global fit $R^2 > 0.95$; $R^2 > 0.90$ with visual review for AHSP); architecture undisclosed [@latentx2].                             |
| Chai-2 [@chai2]                                               | Minibinders, 5 targets                                              |                              20–25/target | 68% (75/111); binders on 5/5 targets                                                                                                              | 18.3 pM (IL-7Rα)                                   | Same > 0.1 nm and > 300% background criterion; 4 of 10 quoted miniprotein affinities avidity-affected [@chai2].                                                                        |
| Protenix-v2 [@protenix_v2]                                    | VHH-Fc and mAb, 4 GPCRs                                             |                              16–30/target | VHH-Fc 16 / 62 / 40 / 88%; mAb 0 / 17 / 50 / 44%                                                                                                  | 112 pM (GPRC5D, avidity)                           | BLI > background + 0.05 nm (most hits $K_D < 1,000$ nM); bivalent VHH-Fc and mAb avidity [@protenix_v2].                                                                               |
| Protenix-v2 [@protenix_v2]                                    | VHH-Fc, soluble targets                                             |                               Figure only | 2–48% per target; binders on all targets                                                                                                          | Figure only                                        | Same BLI > background + 0.05 nm cutoff; bivalent VHH-Fc avidity (except VEGF-A); per-target counts/affinities figure-only (see footnote) [@protenix_v2].                               |
| BindCraft [@bindcraft]                                        | Minibinders, 12 targets                                             |                               6–53/target | 10–100%, mean 46.3%                                                                                                                               | < 1 nM (PD-1, bivalent Fc); 5 nM (CbAgo)           | Binding observed on SPR (no numeric threshold stated); PD-1 is bivalent Fc (exact $K_D$ undetermined) [@bindcraft].                                                                    |
| ESMFold2 campaign [@esmc]                                     | Minibinders, 5 targets                                              |                                 84/cohort | 36–88%, mean 70.0% (higher compute)                                                                                                               | 68 pM (target not stated in text)                  | Dual BLI criteria: stringent target-specific (0.25–0.4 nm) and inclusive (> 0.1 nm), probe loading > 0.5 nm, positive exponential association; Fig. 3 shading image-only [@esmc].      |
| ESMFold2 campaign [@esmc]                                     | scFv, 5 targets                                                     |                                 84/cohort | 15–29%, mean 21.0% (higher compute)                                                                                                               | Not reported                                       | Same dual BLI criteria and image-only Fig. 3 shading caveat [@esmc].                                                                                                                   |
| RFdiffusion [@rfdiffusion]                                    | Minibinders, 5 targets                                              |                           95/target (475) | 19% pooled over 475                                                                                                                               | 28 nM (influenza HA)                               | Single-point BLI at 10 µM ≥ 50% of positive control; lower hit rates on yeast-display re-assay by AlphaProteo [@rfdiffusion; @alphaproteo].                                            |
| AlphaProteo [@alphaproteo]                                    | Minibinders, 8 targets                                              |                             54–172/target | 9% (TrkA) to 88% (BHRF1); 0/54 on TNFα                                                                                                            | 82 pM (IL-7Rα)                                     | Yeast-display flow-cytometry signal > 0.2 (raised to 1.3 for IL-17A due to background); generator undisclosed [@alphaproteo].                                                          |
| **Display or enrichment signal without affinity measurement** |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| BoltzGen [@boltzgen]                                          | VHH, 2 targets                                                      |                  7/target (yeast display) | 1/7 and 7/7 showing signal                                                                                                                        | "At best 2 µM" (no EC50 computable)                | Qualitative yeast-display binding signal without computable EC50 [@boltzgen].                                                                                                          |
| RFantibody [@rfantibody]                                      | VHH, 3 targets                                                      |                           95/target (SPR) | 0–2% range                                                                                                                                        | Not separately listed                              | Single-concentration SPR following *E. coli* expression [@rfantibody].                                                                                                                 |
| RFantibody [@rfantibody]                                      | VHH, 4 targets                                                      |              9,000/target (yeast display) | 0–2% per target                                                                                                                                   | 78 nM (HA), 1.4 µM (RSV site III) by SPR           | Authors note experimental library screening remains necessary given current success rates [@rfantibody].                                                                               |
| mBER [@mber]                                                  | VHH, 145 of 436 targets assayed                                     |  1,153,241 designs (pooled phage display) | 45% (65/145) targets elevated; per-design 0.02–8% (median ~0.4%); 38% (8/21) in one ipTM-filtered epitope bin                                     | Not measured                                       | Per-sequence replicate order statistic (< 1 expected false positive/target); phage display cannot quantify exact affinities [@mber].                                                   |
| **Functional readout without direct binding assay**           |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| BoltzGen [@boltzgen]                                          | Peptides, NPM1                                                      |                                         5 | 1/5 showed nucleolar co-localization in live cells                                                                                                | Not measured                                       | Live-cell co-localization does not confirm specific disordered-region binding [@boltzgen].                                                                                             |
| BoltzGen [@boltzgen]                                          | Antimicrobial peptides, GyrA                                        |                                     1,808 | 352 (19.5%) inhibited *E. coli* growth ≥ 4-fold; 54 lost activity upon 3-residue interface alanine mutation                                       | Not measured                                       | Functional growth-inhibition readout rather than direct binding assay [@boltzgen].                                                                                                     |
| **In-silico evaluation only**                                 |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| BoltzDesign1 [@boltzdesign1]                                  | Protein and biomolecular targets                                    |                            In-silico only | Computational metrics only                                                                                                                        | Not applicable                                     | No wet-lab validation [@boltzdesign1].                                                                                                                                                 |
| RFOptimization [@rfoptimization]                              | Protein–protein interfaces, cyclic peptides, small-molecule binders |  In-silico only (denominators not stated) | AF3-refolded success (iPAE < 2.5, ipTM > 0.8): 6.73% to 22.31% (PPI), 1.25% to 12.57% (cyclic peptides), 5.62% to 24.91% (small-molecule binders) | Not applicable                                     | AlphaFold3 held out of optimization; no wet-lab testing; denominators not stated [@rfoptimization].                                                                                    |

*Notes for Table 2B:* Within each validation group, campaigns are ordered by
designs tested per target (ranging from 5 to 9,000, or pooled at $>10^6$ for
mBER). Several source values are subject to figure-only reporting constraints:
Protenix-v2's soluble-target per-target denominators and affinities appear only
in Fig. 4A (per-epitope ratios 2/50 and 13/27 on AMBP and 12/50 on IDI2 are
transcribed in BoltzProt-1) [@protenix_v2; @boltzprot1], and ESMFold2's shading
distinguishing stringent from inclusive BLI cutoffs in Fig. 3 is image-only
[@esmc]. In BoltzProt-1 [@boltzprot1], an internal discrepancy exists for
revised screening hits (Table 1 lists 7/150 [4.7%] for BoltzGen and 14/150
[9.3%] for BoltzProt-1, whereas the prose states 14/150 [9.3%] and 24/150
[16.0%]), while the confirmed-binder figures reported in Table 2B (5/150 [3.3%]
and 12/150 [8.0%]) are consistent in both table and prose.

# Conclusions and Open Challenges

## From in vitro binding to therapeutic utility

Most binder-design papers motivate their methods through therapeutic
development, citing goals such as automating drug discovery [@boltzgen], tuning
species cross-reactivity [@chai2], reducing IgE binding in patient-derived
samples [@bindcraft], matching approved-antibody developability [@latentx2], and
accelerating protein therapeutics [@mber]. Evaluating a decade of artificial
intelligence in pharmaceutical R&D, Bender et al. report substantial technical
progress alongside limited evidence of clinical impact so far
[@bender_perspective]. They distinguish *model validation* (accuracy on held-out
benchmarks or isolated in vitro assays, including structure prediction and
binding hit rates) from *process validation* (improved downstream clinical
decisions), noting that AlphaFold exemplifies model validation for folding
rather than process validation for drug discovery [@bender_perspective].

Although biologics have aided recent approval gains through higher clinical
success rates and stronger intellectual-property protection than small
molecules, Bender et al.'s review of protein-design methods (citing RFdiffusion,
ProteinMPNN, BoltzGen, and Chai-2) notes that binding remains easier to predict
than functional activity and developability [@bender_perspective]. This mirrors
small-molecule discovery, where ChEMBL and PubChem catalog over $10^6$ bioactive
ligands versus roughly $10^3$ marketed drugs [@bender_perspective]. They also
emphasize matching evaluation metrics to the decision task (selection,
deselection, or quantification), local generalization outside training
distributions, and verifiability: open-source co-folding models have largely
caught up with closed alternatives, whereas proprietary systems such as IsoDDE
disclose too little detail for independent evaluation [@bender_perspective].
Because their Perspective draws mainly on small-molecule and clinical-pipeline
evidence, relying on one benchmark preprint (FLAb2) for biologic developability,
these conclusions provide context rather than a direct audit of protein design
[@bender_perspective].

## Open technical and methodological limitations

Five technical and methodological limitations recur across current binder-design
pipelines. First, nearly all open systems generate, filter, and report solely on
binding. Latent-X2 notes that therapeutic campaigns often fail not for lack of
binding, but because binding alone is insufficient when clinical success demands
developability and low immunogenicity [@latentx2]; Latent-X2 reports such
measurements for designed antibodies, yet its generative architecture is
undisclosed [@latentx2]. Second, current scoring functions act mainly as binary
binding indicators rather than quantitative affinity estimators. BindCraft
reports that AlphaFold2 ipTM predicts whether a design binds rather than its
dissociation constant ($K_D$) [@bindcraft], and Boltz-2's affinity module covers
small-molecule ligands on single-protein targets rather than multimeric
protein–protein interfaces [@boltz2], leaving affinity to experimental
measurement. Third, most wet-lab campaigns condition on experimentally solved or
high-confidence predicted structures, and Germinal notes that how strongly
design success depends on predicted antigen-model accuracy remains an open
question [@germinal].

Fourth, no shared, blinded prospective benchmark exists for de novo binder
design, and independent replication of a full published campaign has occurred
only once, when AlphaProteo re-tested RFdiffusion's published designs (including
nonbinders) by yeast display [@alphaproteo; @rfdiffusion]. The closest
prospective standard is the AIntibody challenge, which evaluated 511 antibodies
from 29 organizations across three tasks, expressed as full IgGs and assayed
independently under one protocol combining high-throughput surface plasmon
resonance (HT-SPR), kinetic exclusion assays (KinExA), and a five-assay
developability panel with explicit pass thresholds [@aintibody]. The top
computational design (95 pM) was statistically indistinguishable from the best
wet-lab antibody (113 pM), and the Challenge 1 winner used an open-code
Protenix-derived pairformer with a direct preference optimization (DPO) fitness
head, yet a non-ML consensus of selection data ranked third [@aintibody]. On
Challenge 2 (within-HCDR3-cluster affinity ranking), only 1 of 26 groups
outperformed random clone selection; on the out-of-library task, 30.4% of
designs were nonbinders, and the highest-affinity winner (2.9 pM) failed to
elute from the hydrophobic interaction chromatography (HIC) column [@aintibody].
AIntibody also has clear scope limits: it tested one extensively characterized
antigen (SARS-CoV-2 RBD, described as "deliberately primed for success"),
captures a Q1 2025 snapshot missing several prominent de novo antibody-design
groups, and evaluated library-conditioned engineering with provided affinities
in Challenges 2 and 3 rather than target-conditioned de novo design
[@aintibody].

Fifth, structure-prediction confidence scores remain unreliable for per-design
selection. Metrics such as ipTM and ipSAE enrich hit rates across large pools,
as observed at million-design scale in mBER [@mber], yet often fail to separate
individual binders from nonbinders, as seen in Germinal where nonbinders cleared
the same ipSAE threshold as binders [@germinal]. Pooling 3,766 experimentally
tested designs from six published campaigns across 15 targets under one
re-scoring pipeline, Overath et al. found AlphaFold3 ipSAE to be the strongest
single predictor of binding overall, yet its average precision spanned 0.1–1.0
across targets [@overath_meta]. Uniform re-scoring also leaves each campaign's
heterogeneous wet-lab assays and binding cutoffs unchanged and reflects
earlier-generation designs rather than the newest 2025–2026 models
[@overath_meta].

Current co-folding and generative models can produce epitope-targeted protein
and peptide binders across several structural formats while often testing tens
rather than thousands or millions of sequences per target. Quantitative
protein–protein affinity prediction, joint control of functional activity,
developability, and immunogenicity in inspectable architectures, reliable
per-design filtering on structurally uncharacterized targets, and comparative
performance under shared blinded wet-lab benchmarks remain to be demonstrated.
