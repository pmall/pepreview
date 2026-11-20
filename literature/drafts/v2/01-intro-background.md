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
peptide, a minibinder, or the complementarity-determining regions of a nanobody,
the generated object is a linear or cyclized chain drawn from the fixed
20-letter amino-acid alphabet, evaluated by how that chain folds against the
target surface. Small-molecule generation instead operates over variable-size
chemical graphs constrained by atomic valence rules, bond orders, and synthetic
accessibility, requiring different neural architectures and evaluation
benchmarks.

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

*Schematic specification for Figure 1:* Two horizontally stacked panels (Panel A
on top, Panel B below). Panel A flows left-to-right across three boxed columns:
(1) Input sources (stacked branches for MSA database lookup, PLM embeddings, and
hybrid dual tracks) feeding into (2) a central Trunk block labeled with
single/pair representations and an outgoing distogram head, feeding into (3)
three parallel coordinate-module branches illustrating single-pass IPA
regression (1 step), curved noisy SDE diffusion (200–1,000 steps), and
straighter ODE flow-matching trajectories (few steps). Panel B shows three
stacked horizontal workflow lanes: Lane 1 depicts a shared diffusion network
with fixed target coordinates and noised binder coordinates entering and a
designed binder complex exiting; Lane 2 depicts a sequential pipeline (Backbone
Generator → Inverse Folding [ProteinMPNN] → Predictor Confidence Filter or
Learned Classifier [BoltzPPI]); Lane 3 depicts a closed feedback loop from an $L
\\times 20$ relaxed sequence matrix through the predictor with three color-coded
gradient return paths (full end-to-end through IPA regression; trunk
distogram/confidence shortcut with a stop-gradient icon before diffusion; and a
2-step ODE decoder loop).

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
openness and disclosure across the field. Systems span four tiers of
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
