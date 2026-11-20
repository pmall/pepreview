# Deep-Learning Methods for Protein and Peptide Binder Generation

## Abstract

Selective binding to a target protein underlies therapeutics, diagnostics, and
laboratory reagents, typically carried out by protein or peptide modalities such
as antibodies, nanobodies, single-chain variable fragments, minibinders, and
macrocyclic peptides. Historically, discovering these binders has relied on
animal immunization or combinatorial display libraries containing trillions of
random sequences, an approach that is wet-lab intensive per target and difficult
to aim at a chosen epitope. Recent advances in deep-learning structure
prediction and biomolecular co-folding have enabled computational binder
generation, reducing experimental screening from vast random pools to tens of
designed sequences per target. Unlike small-molecule generation over variable
chemical graphs, protein and peptide binder design searches chains drawn from
the 20-amino-acid alphabet evaluated by how they fold against a target surface.
Across open and proprietary systems, architectures vary along three primary
axes: how evolutionary information enters the sequence trunk (multiple sequence
alignment retrieval, protein language models, or both), how three-dimensional
coordinates are generated (single-pass coordinate regression, iterative
stochastic diffusion, or straighter-trajectory flow matching), and how structure
predictors drive sequence design (joint or fine-tuned predictor-generators,
generate-and-filter pipelines with inverse folding and learned scorers, or
gradient-based sequence optimization). Reported hit rates depend strongly on
testing budgets, assay confirmation criteria, target and epitope selection, and
method disclosure. Major open challenges remain in predicting quantitative
protein–protein binding affinity, jointly optimizing developability and
immunogenicity, establishing shared prospective benchmarks, and overcoming
per-design limits of confidence filtering.

# Introduction and Conceptual Background

## Why protein binders matter and how discovery shifted from search to design

Binding a target protein selectively is the physical basis for blocking a
signaling pathway, detecting an analyte, tagging a cellular structure, or
modulating enzymatic activity. For protein targets, the binding partner is often
another protein or a peptide: full-length antibodies, single-domain nanobodies
(VHHs), single-chain variable fragments (scFvs), compact de novo minibinders, or
head-to-tail macrocyclic peptides. Together, these modalities account for a
large share of modern biologics and research reagents because extended
protein–protein interfaces can recognize flat or shallow surfaces that are
difficult to engage with small chemical compounds.

Historically, obtaining a protein binder has been an experimental search problem
rather than a design problem. Standard workflows rely on immunizing animals,
isolating clones from patients, or panning phage and yeast display libraries
containing $10^{12}$ or more random sequences. While effective and still
standard across academia and industry, these approaches require wet-lab
screening from the first step, must be repeated per target, and return binders
against whichever surfaces happen to be immunogenic or accessible rather than a
site chosen by the investigator [@rfantibody]. Computational binder generation
aims to propose candidate amino-acid sequences directly for a specified target
protein and epitope.

Focusing on protein and peptide binders defines a clean technical boundary
distinct from small-molecule generation. Whether a model designs a macrocyclic
peptide, a minibinder, or the complementarity-determining regions (CDRs) of a
nanobody, its output is a linear or cyclized chain from the fixed 20-letter
amino-acid alphabet evaluated by how it folds against the target. Small-molecule
generation instead operates over variable-size chemical graphs constrained by
atomic valence rules and synthetic accessibility, requiring different
architectures and benchmarks.

Direct computational binder design became practical once deep learning reached
experimental accuracy on structure prediction: AlphaFold2 solved single-chain
folding at CASP14 [@alphafold2], and AlphaFold3 extended prediction to complexes
containing proteins, nucleic acids, ligands, and ions [@alphafold3]. Designing a
binder, however, differs fundamentally from predicting a structure. A structure
predictor maps a known sequence to its three-dimensional fold, which can be
checked directly against a crystal or cryo-electron microscopy structure. A
binder generator must invent a sequence out of $20^L$ possibilities for a chain
of length $L$ that folds stably and engages the intended target, an outcome only
a wet lab can confirm. Between 2024 and 2026, the field expanded rapidly across
open-source reproductions, specialized design stacks, and dedicated engineering
for inference throughput, including September 2026 inference-kernel releases
from NVIDIA, Anthropic, and ESM teams reporting 2–4× speedups across major open
models in public engineering posts and repositories.

## How co-folding predictors are built

Modern structure prediction rests on the principle that correlated mutations
(coevolution) between positions in a multiple sequence alignment (MSA) reflect
spatial proximity in the folded protein. AlphaFold2 confirmed how accurately
neural networks can extract this signal at CASP14, reaching a median backbone
accuracy of 0.96 Å r.m.s.d.95 (Cα RMSD at 95% residue coverage; 95% CI 0.85–1.16
Å) compared with 2.8 Å r.m.s.d.95 for the next best method [@alphafold2].
AlphaFold3 generalized this paradigm from single chains to multi-component
biomolecular complexes, commonly termed co-folding [@alphafold3].

Whereas early RoseTTAFold 1 and 2 models processed 1D sequence, 2D pairwise, and
3D coordinate tracks in parallel from input to output \[@rosettafold;
@rosettafold2\], most modern co-folders organize computation into two sequential
stages: a differentiable trunk followed by a coordinate-generation module.

The first stage, the trunk (instantiated as the Evoformer in AlphaFold2
[@alphafold2], the Pairformer in AlphaFold3-class co-folders \[@alphafold3;
@boltz1; @chai1; @protenix_v1; @rosettafold3\], or the folding trunk in ESMFold
and ESMFold2 [@esm2; @esmc]), converts sequence and evolutionary inputs into
single-residue and pairwise representations. A linear head on the pair
representation predicts a distogram, a probability distribution over
inter-residue distances used both for training supervision and as a
differentiable geometric surrogate in several design methods \[@alphafold2;
@boltzdesign1; @esmc\]. The trunk is differentiable throughout and runs once per
complex or random seed [@boltz1]. Predictor lineages differ primarily in how
evolutionary context enters this trunk: MSA-based models retrieve homologous
sequences from databases at inference time (AlphaFold, RoseTTAFold, Boltz,
Protenix), protein language model (PLM)-based models store evolutionary
statistics in pre-trained weights for single-sequence inference (ESMFold,
ESMFold2, AtlasFold [@esm2; @esmc; @atlasfold]), and hybrid models such as
Chai-1 include both tracks and run on either [@chai1].

The second stage turns the trunk's single and pair representations into 3D
atomic coordinates, and its mathematical formalism governs both speed and
differentiability. AlphaFold2 and ESMFold use single-pass coordinate regression
via an end-to-end differentiable Invariant Point Attention (IPA) structure
module; AlphaFold2 ablations showed that removing end-to-end structural
gradients degrades accuracy [@alphafold2; @esm2]. AlphaFold3 and subsequent
AF3-class co-folders replaced IPA with a diffusion module for structure
prediction itself, independent of design \[@alphafold3; @boltz1; @chai1;
@protenix_v1; @rosettafold3; @esmc\]. Borrowed from image generation by
replacing noised pixels with noised atomic coordinates, diffusion denoises
Gaussian noise iteratively along a stochastic differential equation (SDE)
trajectory, often requiring hundreds to roughly 1,000 forward passes in protein
generators [@alphafold3; @frameflow]. Flow matching lowers this sampling cost by
modeling coordinate transport as an ordinary differential equation (ODE) with
straighter trajectories: FrameFlow recast FrameDiff this way, reporting twofold
better designability at five times fewer steps on unconditional monomers
[@frameflow], and target-conditioned binder variants include PPIFlow [@ppiflow],
OriginFlow [@originflow], AtomFlow [@atomflow], and D-Flow [@dflow]. Unlike
image generation, where outputs depend on subjective human judgment, protein
designs can be scored automatically using structure predictors.

## Turning structure predictors into binder generators

Structure prediction and binder design can run on the same neural network simply
by changing which inputs are fixed. Supplying all chain sequences predicts the
complex; holding the target fixed while leaving the binder chain unspecified or
noised generates a partner folding against that target. BoltzGen implements this
directly as a single all-atom diffusion model trained for both prediction and
design [@boltzgen], while RFdiffusion reached a related duality by fine-tuning
RoseTTAFold into a backbone generator whose input-to-output 3D track encodes
spatial target constraints directly as coordinates \[@rosettafold2;
@rfdiffusion\].

Across the field, design pipelines use structure predictors in three main ways
(**Figure 1**):

1. **Joint or fine-tuned predictor-generators** reuse prediction weights
   directly to denoise unknown binder structures, either by fine-tuning a
   predictor into a generator (RFdiffusion and RFdiffusion2 \[@rfdiffusion;
   @rfdiffusion2\]) or by training one diffusion model jointly on prediction and
   design (BoltzGen [@boltzgen]).
1. **Generate-and-filter pipelines** sample candidate backbones without
   design-time gradients, assign sequences via inverse folding (most commonly
   ProteinMPNN [@proteinmpnn]), and rank candidates post hoc. Filtering
   typically uses refolding confidence scores, such as AlphaProteo's criterion
   of interchain AlphaFold2 PAE < 10 Å, binder-aligned binder RMSD < 1 Å, and
   pLDDT > 80 [@alphaproteo], or replaces confidence heads with a classifier
   trained directly on experimental binding outcomes, as in BoltzProt-1's
   BoltzPPI [@boltzprot1].
1. **Gradient-based sequence optimization (hallucination or backpropagation)**
   represents a binder of length $L$ as a continuous probability distribution
   over 20 amino acids per position (an $L \\times 20$ simplex), passes it
   through a differentiable predictor, and descends confidence or distogram
   losses while annealing toward discrete one-hot amino acids (BindCraft
   [@bindcraft], Germinal [@germinal], BoltzDesign1 [@boltzdesign1], PXDesign-h
   [@pxdesign], ESMFold2 [@esmc]). RFOptimization instead keeps sequences
   strictly discrete and uses predictor gradients solely to rank point mutations
   [@rfoptimization].

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
stacked panels (A top, B bottom). Panel A flows left-to-right across three
columns: Input sources (MSA lookup, PLM embeddings, hybrid dual track) → Trunk
(single/pair representations + distogram head) → three coordinate branches
(1-step IPA regression, 200–1,000-step SDE diffusion, few-step ODE flow
matching). Panel B shows three workflow lanes: Lane 1, shared diffusion network
(fixed target + noised binder → complex); Lane 2, Backbone Generator → Inverse
Folding (ProteinMPNN) → Confidence Filter or Trained Classifier (BoltzPPI); Lane
3, closed feedback loop from an $L \\times 20$ relaxed sequence through the
predictor with three gradient return paths (end-to-end IPA, trunk
distogram/confidence shortcut with diffusion stop-gradient, and 2-step ODE
decoder).

Three practical constraints govern how these workflows perform. First, gradient
optimization requires single-sequence input on the binder chain because MSA
database search is neither defined for an invented sequence nor differentiable.
Inverting an MSA-trained predictor such as AlphaFold2 therefore operates in its
documented weakest regime [@alphafold2; @bindcraft], whereas natively
single-sequence PLMs such as ESMC and ESMFold2 backpropagate without leaving
their training distribution [@esmc]. Second, unrolling hundreds or ~1,000
diffusion steps for backpropagation is computationally impractical \[@frameflow;
@boltzdesign1\]. Diffusion-based design loops therefore either compute gradients
from the trunk distogram and confidence heads without backpropagating through
diffusion (BoltzDesign1 [@boltzdesign1], RFOptimization [@rfoptimization],
ESMFold2 [@esmc]) or replace the 200-step diffusion decoder with a
differentiable 2-step ODE sampler (PXDesign-h [@pxdesign]). Third, candidate
filtering strongly drives experimental yield independently of the generator:
replacing BoltzGen's confidence ranking with BoltzPPI on the same candidate
pools raised confirmed binders from 3.3% to 8.0% [@boltzprot1], Protenix and
AlphaFold2-Initial-Guess (AF2-IG) filters retain largely non-overlapping true
positives [@pxdesign], and RFOptimization mixes multiple predictor families to
limit single-predictor overfitting [@rfoptimization].

## Reading reported numbers: testing budgets, hit definitions, and disclosure

A practical indicator of progress is how many candidate sequences must be
physically synthesized and tested per target to find a binder. Where display
libraries and early computational pipelines often tested thousands to millions
of designs [@chai2; @rfantibody], recent generative workflows routinely test 10
to 100 designs per target and report double-digit hit rates across multiple
formats [@chai2; @rfpeptides; @boltzgen; @protenix_v2; @esmc].

Raw hit rates cannot be compared at face value, however, for three reasons.
First, hit definitions vary widely: BoltzProt-1 separates initial screening hits
(matching what prior binder literature commonly reports as binders) from
follow-up confirmed binders [@boltzprot1]. Second, target and epitope choice
shifts outcomes by orders of magnitude: whereas small targeted campaigns choose
their own epitopes, mBER's 1.15-million-VHH phage-display sweep against randomly
chosen surface hotspots across 436 human cell-surface proteins (145 assayed)
yielded a ~0.4% median per-design hit rate, while its best individual hotspots
still reached up to 38% under strict filtering [@mber]. Third, method openness
spans four regimes: fully reproducible releases with weights, training code, and
datasets (OpenFold3, AtlasFold, BoltzGen [@openfold3; @atlasfold; @boltzgen]);
open-weights releases under permissive or non-commercial licenses (Boltz-1/2,
Protenix, RoseTTAFold3, OpenDDE, OpenGerminal, Chai-1, ESM3-open \[@boltz1;
@boltz2; @protenix_v1; @rosettafold3; @opendde; @opengerminal; @chai1; @esm3\]);
published results with undisclosed generators or commercial API-only access
(AlphaProteo, Latent-X1/X2, Chai-2's generator, BoltzProt-1, ESM3-98B
[@alphaproteo; @latentx1; @latentx2; @chai2; @boltzprot1; @esm3]); and
unpublished private systems visible only through web platforms or third-party
benchmarks (IsoDDE, SeedFold, Chai-3 [@opendde; @bender_perspective]). Because
campaigns choose their own targets, assays, and thresholds, results from closed
systems cannot be independently audited from papers alone [@bender_perspective].

Finally, interpreting benchmarks alongside design campaigns requires separating
external accuracy and physical-validity metrics from model self-estimates (**Box
1**). Because de novo binders have no experimental structure before synthesis,
design pipelines rely on internal confidence scores and self-consistency RMSD
(comparing a designed backbone against a predicted refolding of its own
sequence).

### Box 1: Core Evaluation Metrics

| Category                     | Metric                | Reference                 | Definition and role                                                                                                                                                                                                      | Source                |
| ---------------------------- | --------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- |
| External accuracy / validity | **lDDT**              | Experimental              | Local interatomic distance accuracy without global superposition; a correct domain in the wrong pose still scores high.                                                                                                  | [@lddt]               |
| External accuracy / validity | **TM-score**          | Experimental              | Length-normalized global fold similarity to a reference structure.                                                                                                                                                       | [@tm_score]           |
| External accuracy / validity | **RMSD** (and scRMSD) | Experimental or predicted | Optimal-superposition deviation (Å, Kabsch algorithm). Measures accuracy against an experimental structure; self-consistency RMSD (scRMSD) compares a generated backbone to a refolding of its own sequence.             | [@kabsch]             |
| External accuracy / validity | **DockQ**             | Experimental              | Composite protein–protein interface score (0–1; DockQ ≥ 0.23 is the standard acceptable threshold).                                                                                                                      | [@dockq]              |
| External accuracy / validity | **PB-valid**          | Physical chemistry        | PoseBusters pass/fail check for chemical validity, bond geometry, chirality, clashes, and energy (308 complexes + 85 Astex Diverse in original benchmark [@posebusters]; 428 complexes in AF3 evaluation [@alphafold3]). | [@posebusters]        |
| Self-estimate                | **pLDDT**             | Model estimate            | Per-residue predicted lDDT (0–100), calibrated against ground-truth lDDT.                                                                                                                                                | [@alphafold2]         |
| Self-estimate                | **pTM**               | Model estimate            | Predicted global TM-score for the overall fold.                                                                                                                                                                          | [@alphafold2]         |
| Self-estimate                | **PAE**               | Model estimate            | Predicted Aligned Error matrix (Å) estimating positional error between residue pairs.                                                                                                                                    | [@alphafold2]         |
| Self-estimate                | **ipTM**              | Model estimate            | Interface predicted TM-score over interchain residue pairs only.                                                                                                                                                         | [@alphafold_multimer] |
| Self-estimate                | **iPAE**              | Model estimate            | PAE restricted to interchain pairs (e.g., < 10 Å in AlphaProteo [@alphaproteo]; 10–15 Å in ipSAE [@ipsae]).                                                                                                              | [@alphafold_multimer] |
| Self-estimate                | **ipSAE**             | Model estimate            | ipTM restricted to well-predicted interchain pairs below a PAE cutoff, removing sensitivity to input chain trimming (used in Germinal [@germinal] and Overath et al. [@overath_meta]).                                   | [@ipsae]              |

# Model Families: From Predictors to Design Systems

Tracing each lineage from structure prediction to binder generation illustrates
how trunk design, coordinate formalism, and release choices shape downstream
workflows (**Table 1**).

**Table 1. Overview of major structure predictors and binder-design families.**

| Family / System                                                                                             | Role                                      | Evolutionary Input                            | Coordinate Stage                                                               | Modalities & Mechanism                                                                                                     | Openness                                                     |
| ----------------------------------------------------------------------------------------------------------- | ----------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| AlphaFold2 / AF-Multimer [@alphafold2; @alphafold_multimer]                                                 | Monomer & complex predictors              | MSA                                           | Single-pass IPA regression                                                     | Refolding filter (pLDDT, ipTM, iPAE); inverted by backpropagation pipelines                                                | Open code & weights                                          |
| OpenFold / OpenFold3 [@openfold; @openfold3]                                                                | Open AF2 & AF3 reproductions              | MSA                                           | IPA (OF); all-atom SDE diffusion (OF3)                                         | Retraining from scratch (OF3 includes 13M-sequence MGnify distillation set)                                                | Open / Apache-2.0 (weights, code, data)                      |
| AlphaFold3 [@alphafold3]                                                                                    | All-atom co-folding predictor             | MSA                                           | All-atom SDE diffusion                                                         | Proteins, nucleic acids, ligands, ions (up to 1,000 seeds for Ab–Ag)                                                       | Restricted / closed weights                                  |
| RoseTTAFold 1 / 2 / RFAA [@rosettafold; @rosettafold2; @rosettafold_all_atom]                               | Protein & all-atom predictors             | MSA                                           | Parallel 3-track (1D/2D/3D) regression                                         | Base architectures fine-tuned into RFdiffusion and RFpeptides                                                              | Open code & weights                                          |
| RoseTTAFold3 (RF3) [@rosettafold3]                                                                          | All-atom co-folding predictor             | MSA                                           | All-atom SDE diffusion (learned chirality)                                     | Biomolecular complexes, mixed L/D peptides; supplies gradients for RFOptimization                                          | BSD                                                          |
| RFdiffusion 1 / 2 / 3 [@rfdiffusion; @rfdiffusion2; @rfdiffusion3]                                          | Backbone & all-atom generators            | Target structure conditioned                  | Frame diffusion (RFD1/2); all-atom U-Net (RFD3)                                | RFD1/2 fine-tuned from RF; RFD3 pre-trained (2 Pairformer layers); + MPNN + refolding                                      | Open code & weights                                          |
| ProteinMPNN / LigandMPNN / AlphaDesign [@proteinmpnn; @ligandmpnn; @alphadesign]                            | Inverse folding (sequence design)         | None (backbone conditioned)                   | Fixed backbone (autoregressive MPNN / ADM)                                     | Designs/redesigns sequences on generated backbones (+ ligand/nucleic context in LigandMPNN)                                | Open code & weights                                          |
| RFantibody / RFpeptides [@rfantibody; @rfpeptides]                                                          | Antibody & macrocycle generators          | Target structure (+ framework)                | Fine-tuned / cyclic-offset RFdiffusion                                         | Epitope-specific VHH/scFv/mAb (+ display/SPR); head-to-tail macrocycles (+ AfCycDesign)                                    | Open code & weights                                          |
| FrameFlow / PPIFlow / OriginFlow / AtomFlow / D-Flow [@frameflow; @ppiflow; @originflow; @atomflow; @dflow] | Flow-matching generators                  | Target structure (binder variants)            | ODE flow matching                                                              | Straighter coordinate trajectories for monomers (FrameFlow) and protein binders                                            | Research publications                                        |
| Boltz-1 / Boltz-1x / Boltz-2 [@boltz1; @boltz2]                                                             | All-atom predictors (+ ligand affinity)   | MSA                                           | All-atom SDE diffusion (FK steering in 1x)                                     | Refolding filter for BoltzGen/BoltzProt-1; protein–ligand affinity head (Boltz-2)                                          | MIT (weights, code)                                          |
| BoltzGen / BoltzProt-1 [@boltzgen; @boltzprot1]                                                             | Unified designer & trained classifier     | MSA / target conditioned                      | Unified all-atom SDE diffusion                                                 | Proteins, peptides, VHHs (no full mAbs); BoltzProt-1 swaps confidence ranking for BoltzPPI                                 | BoltzGen MIT (full); BoltzProt-1 API-only                    |
| Chai-1 / Chai-2 / Chai-3 [@chai1; @chai2]                                                                   | Hybrid co-folder & antibody designer      | Hybrid MSA/PLM (Chai-1); undisclosed (Chai-2) | All-atom SDE diffusion (Chai-1); undisclosed (Chai-2)                          | Experimental restraints & single-seq antibody parity (Chai-1); zero-shot scFv/VHH/minibinders (Chai-2)                     | Chai-1 non-commercial; Chai-2/3 closed                       |
| ColabDesign / AfCycDesign / BindCraft [@colabdesign; @afcycdesign; @bindcraft]                              | AF2 backpropagation pipelines             | Single-sequence on binder                     | Full AF2 / AF-Multimer IPA regression                                          | Continuous-to-discrete gradient optimization (cyclic offset in AfCycDesign; 5-model induced fit in BindCraft)              | Open code (BindCraft2 unpublished code)                      |
| BoltzDesign1 / RFOptimization [@boltzdesign1; @rfoptimization]                                              | Diffusion-trunk gradient optimizers       | Single-sequence on binder                     | Distogram/confidence heads (diffusion bypassed)                                | Continuous 64-bin distogram loss (BoltzDesign1); discrete Metropolis–Hastings + Boltz/LigandMPNN cycling (RFO)             | Open code / preprint (in-silico only)                        |
| Germinal / OpenGerminal / mBER [@germinal; @opengerminal; @mber]                                            | PLM-guided antibody/VHH optimizers        | Single-seq + IgLM/AbLang1 or static ESM-2     | AF-Multimer IPA + masked framework template                                    | Live LM gradient merging via PSSM+STE (Germinal) vs. fixed ESM-2 logit bias + template (mBER)                              | Open code (OpenGerminal Apache-2.0)                          |
| Protenix-v1 / v2 / PXDesign / PXMeter [@protenix_v1; @protenix_v2; @pxdesign; @pxmeter]                     | Co-folding, dual-mode design & benchmarks | MSA / single-seq (PXDesign-h)                 | All-atom SDE diffusion; DiT (-d) & 2-step ODE (-h)                             | Miniproteins (PXDesign), VHH/Fv/mAb incl. GPCRs (v2); PXMeter v1.1.0 planarity checks                                      | Protenix-v1 & PXMeter open; PXDesign server                  |
| ESM-2 / ESM-3 / ESMC & ESMFold2 [@esm2; @esm3; @esmc]                                                       | PLMs, single-seq folding & binder design  | PLM (single-seq; optional MSA in ESMFold2)    | IPA (ESMFold); discrete tokens (ESM-3); recurrent trunk + diffusion (ESMFold2) | Multimodal generation (ESM-3); 150-step single-stage ESMC + distogram optimization (ESMFold2)                              | ESM-2 open; ESM-3 1.4B academic / 98B API; ESMC preprint     |
| AtlasFold [@atlasfold]                                                                                      | Single-sequence PLM folder                | PLM (single-sequence, no MSA)                 | 48-block Pairformer + all-atom diffusion                                       | Independent single-sequence co-folding + 7-model FoldBench rank/oracle benchmark                                           | MIT (weights, code, checkpoints, data)                       |
| OpenDDE [@opendde]                                                                                          | Scaled all-atom co-folder                 | MSA                                           | Atom-level refiner + all-atom diffusion (3× Pairformer)                        | Scaled Pairformer (128 → 384); third-party Ab–Ag benchmarks (joint design on roadmap)                                      | Apache-2.0                                                   |
| AlphaProteo / Latent-X1 & X2 / IsoDDE & SeedFold [@alphaproteo; @latentx1; @latentx2; @opendde]             | Closed & unpublished systems              | Undisclosed                                   | Undisclosed                                                                    | Minibinders (AlphaProteo); macrocycles, minibinders & developable antibodies (Latent-X); IsoDDE/SeedFold in OpenDDE curves | Closed weights & architectures (IsoDDE/SeedFold unpublished) |

## AlphaFold and open reproductions

AlphaFold2 [@alphafold2] established the Evoformer trunk, distogram head, and
single-pass differentiable IPA structure module that enabled both post-hoc
refolding filters [@rfdiffusion; @alphaproteo] and full-network gradient-based
design [@bindcraft], while documenting sharp accuracy losses as MSA depth falls
toward single sequences [@alphafold2]. AlphaFold-Multimer [@alphafold_multimer],
an unreviewed bioRxiv preprint, retrained the network on protein complexes and
introduced ipTM and interchain PAE; gradient-based complex designers such as
BindCraft [@bindcraft], Germinal [@germinal], and mBER [@mber] invert
AlphaFold-Multimer rather than monomer AlphaFold2. OpenFold [@openfold] openly
retrained AlphaFold2 and supplied the structural distillation dataset later used
to train Boltz-1 [@boltz1].

AlphaFold3 [@alphafold3] generalized co-folding to proteins, nucleic acids,
small molecules, and ions by replacing the Evoformer with a simplified
Pairformer trunk and replacing IPA with an all-atom diffusion module. On the
428-structure PoseBusters set, it outperformed AutoDock Vina and RoseTTAFold
All-Atom without pocket coordinates [@alphafold3]. For antibody–antigen
complexes, however, reported accuracy required top-ranking across 1,000 random
seeds rather than five, with performance still rising at 1,000 seeds
[@alphafold3]. Multi-step diffusion prevents direct end-to-end coordinate
backpropagation and introduces physical-validity artifacts noted in the paper: a
4.4% chirality violation rate on PoseBusters despite a chirality ranking
penalty, residual clashes, and hallucinated order in disordered regions
(mitigated via cross-distillation from AlphaFold-Multimer v2.3) [@alphafold3].
Predictions remain static PDB-like structures rather than ensembles, and shallow
MSAs still degrade accuracy [@alphafold3].

AlphaFold3's restricted weights motivated open reproductions including Boltz-1
[@boltz1], Protenix [@protenix_v1], and OpenFold3 [@openfold3]. OpenFold3
releases Apache-2.0 weights, training code, and its full training corpus,
including a reproduction of AlphaFold3's 13-million-sequence MGnify distillation
set, enabling retraining from scratch [@openfold3]. As a software release rather
than a peer-reviewed paper, its benchmarks are self-reported, and its technical
report covers superseded `preview2` weights rather than the current `OpenBind-0`
default [@openfold3].

## RoseTTAFold, RFdiffusion, and inverse folding

Developed independently of AlphaFold at the Baker Lab and the Institute for
Protein Design, this lineage spans predictors, diffusion generators, inverse
folding, and modality-specific extensions. Two similarly named recent models
serve opposite roles: RoseTTAFold3 (RF3) [@rosettafold3] is an all-atom
structure predictor denoising coordinates for a known sequence, whereas
RFdiffusion3 (RFD3) [@rfdiffusion3] is a generator denoising coordinates with
sequence unknown prior to inverse folding.

The predictor track began with RoseTTAFold (RF1) [@rosettafold], a three-track
(1D/2D/3D) network in which complex prediction emerged via discontinuous
two-segment cropping; though superseded as a predictor, RF1 supplied the weights
fine-tuned into RFdiffusion [@rfdiffusion]. RoseTTAFold2 (RF2), an unreviewed
preprint, ablated AlphaFold2 and showed that FAPE loss, recycling, distillation,
and depth mattered while IPA and triangle attention were unnecessary, matching
AlphaFold2 and AlphaFold-Multimer while scaling better past 1,000 residues and
keeping a 3D input-to-output track suited to spatial constraints
[@rosettafold2]. Built on RF2, RoseTTAFold All-Atom (RFAA) added non-protein
chemistry two months before AlphaFold3 [@rosettafold_all_atom]. RoseTTAFold3
(RF3) then adopted a BSD-licensed all-atom diffusion architecture learning
ligand chirality from geometric features rather than inference-time guidance,
getting 88% of ligand chiral centers right versus 84% for AlphaFold3 and 76% for
Boltz-2 without guidance, and achieving 1.74 Å mean backbone RMSD on mixed L/D
peptides versus 1.88 Å for AlphaFold3 and 2.24 Å for Boltz-1x (cautioning that
inference-time steering may shift networks out of distribution) [@rosettafold3].

On the generative side, RFdiffusion (RFD1) fine-tuned RF1 for equivariant frame
diffusion over Cα coordinates and N–Cα–C orientations, outperforming earlier
RoseTTAFold hallucination and establishing the backbone diffusion, ProteinMPNN,
and AlphaFold2 refolding pipeline (noting that reported in silico success
reflects AlphaFold2 filter agreement rather than experimental binding)
[@rfdiffusion]. RFdiffusion2 (RFD2) extended this to sequence-agnostic,
atom-level enzyme active-site scaffolding [@rfdiffusion2]. RFdiffusion3 (RFD3)
broke with predictor initialization by pre-training an all-atom transformer
U-Net modeled on AlphaFold3's diffusion module directly on PDB structures and
AlphaFold2 distillations; shrinking the Pairformer from 48 to 2 layers (168
million trainable parameters) with 100-step sampling makes it roughly an order
of magnitude faster than earlier versions [@rfdiffusion3].

Because backbone generators omit amino-acid identities, ProteinMPNN
[@proteinmpnn] (an autoregressive message-passing network) became the standard
inverse-folding module across labs and pipelines \[@rfdiffusion; @rfpeptides;
@bindcraft; @pxdesign\], although its authors caution that native sequence
recovery does not guarantee accurate folding [@proteinmpnn]. LigandMPNN
[@ligandmpnn] adds conditioning on small molecules, nucleic acids, and metals,
while AlphaDesign's Autoregressive Diffusion Model (ADM) [@alphadesign] performs
comparably to ProteinMPNN with complementary structural preferences.

Specialized extensions target antibodies and cyclic peptides. RFantibody
[@rfantibody] fine-tuned RFdiffusion for epitope-specific VHHs, scFvs, and
antibodies, pairing computational design with yeast-display screening (9,000
designs/target) and SPR (95/target); confirmed hit rates of 0–2% led the authors
to note that experimental screening remains necessary [@rfantibody]. RFpeptides
[@rfpeptides] added cyclic relative positional encoding to RFdiffusion and RF2
for head-to-tail macrocycles, pairing ProteinMPNN with AfCycDesign
[@afcycdesign] and Rosetta filtering to obtain crystal-verified binders across
four targets from fewer than 20 synthesized designs each. A separate tool,
RFOptimization [@rfoptimization], uses RF3 gradients for discrete refinement and
is covered below.

## Boltz

Boltz-1 [@boltz1], the first MIT-licensed AF3-class all-atom co-folder, trained
partly on OpenFold distillation structures [@openfold] and enabled downstream
open design tools such as BoltzDesign1 [@boltzdesign1]. Boltz-1x added
Boltz-steering, using Feynman-Kac steering potentials at inference time to fix
chirality violations and clashes [@boltz1]. Boltz-2 [@boltz2] kept structure
accuracy essentially unchanged while adding conditioning controls and a
small-molecule affinity head reaching a mean Pearson correlation of 0.66 on the
four-target FEP+ subset at over 1,000-fold lower compute than free-energy
perturbation (and >0.55 on three of eight blinded industrial assays, weaker on
the other five), but trained only on single-protein ligand assays rather than
protein–protein interactions [@boltz2]. Its June 1, 2023 training cutoff
overlaps the standard FoldBench window, causing temporal leakage noted in later
benchmarks [@protenix_v1; @protenix_v2; @esmc].

BoltzGen [@boltzgen] released an MIT-licensed (weights, code, and data) all-atom
diffusion model trained jointly for structure prediction (matching Boltz-2 on
its test set) and de novo design across proteins, peptides, and nanobodies
against targets from disordered proteins to small molecules, excluding full
antibodies and filtering with Boltz-2 refolding. Across eight campaigns covering
26 targets, testing ≤15 designs per target yielded nanomolar binders on 6 of 9
novel targets (\<30% bound PDB identity) in both nanobody and miniprotein
formats, alongside 4 of 5 established targets (down to 0.81 nM on PDGFR)
[@boltzgen]. Disclosed caveats include diversity collapse into ubiquitin at
binder lengths 73–76 (over 900 PDB ubiquitin entries) and an earlier
`BoltzGenv0` bug that mis-assigned fixed binder residues to the target chain
during refolding (0/7 hits on two targets versus 1/7 and 7/7 once fixed); the
authors emphasize that binder design is not plug-and-play and recommend manual
inspection and reruns [@boltzgen].

BoltzProt-1 [@boltzprot1] paired a refined BoltzGen generator with BoltzPPI, a
classifier trained directly on experimental binding outcomes. Across 10
low-homology targets on identical candidate pools (15 designs/target, 150
total), replacing confidence ranking with BoltzPPI raised confirmed binders from
3.3% (5/150; 2/10 targets) to 8.0% (12/150; 4/10 targets), explicitly separating
initial screening hits from follow-up confirmed binders [@boltzprot1]. Unlike
earlier MIT Boltz releases, BoltzProt-1 is commercial API-only without released
weights [@boltzprot1].

## Chai

Chai-1 [@chai1] is an AF3-class diffusion co-folder supporting both MSA and
protein language model tracks, usable alone or together, plus optional
experimental restraints (pocket, contact, docking) yielding double-digit
accuracy gains. It matched AlphaFold3 on PoseBusters (77% vs. 76% ligand RMSD
success), and on antibody–protein interfaces single-sequence Chai-1 matched
MSA-enabled Chai-1 while both outperformed AlphaFold-Multimer v2.3 with MSAs,
reflecting antibodies' weak evolutionary signal [@chai1]. Weights are
non-commercial (commercial use via web server), and commercial restrictions
prevented benchmarking against AlphaFold3 or ESM-3 [@chai1].

Chai-2 [@chai2] built on Chai-1 (via a `Chai-1d` prototype) for zero-shot scFv,
VHH, and minibinder design without display screening or affinity maturation.
Testing ≤20 designs per target and format across 52 novel targets achieved 13.7%
scFv and 20.0% VHH hit rates (16% combined; binders on 26/52 targets), alongside
68% on five minibinder targets (best 18.3 pM on IL-7Rα) [@chai2]. The paper
describes only the folding submodule (`Chai-2f`, similar to Chai-1) and
withholds the generative architecture [@chai2]. Chai-3 (2026) operates as a
commercial web platform without a publication.

## Gradient-based design by backpropagation

Gradient-based design inverts a pretrained predictor, updating candidate
sequences to satisfy structural confidence or contact losses. Methods differ in
gradient path (full coordinate regression vs. trunk distograms and confidence
heads), sequence representation (continuous relaxation vs. discrete mutations),
and language-model priors (live gradients vs. static biases). Because
AlphaFold2's IPA module predicts coordinates in one differentiable pass,
gradients propagate end-to-end [@alphafold2]. ColabDesign supplies the
open-source AlphaFold2 backpropagation library and three-stage schedule
(`design_3stage`) underlying AfCycDesign, BindCraft, Germinal, and mBER
[@colabdesign]. AfCycDesign adds cyclic relative positional encoding to the
peptide chain, producing eight monomeric macrocycle crystal structures within
1.0 Å of design models, though its MDM2 and Keap1 binders grafted known motifs
onto hallucinated scaffolds before ProteinMPNN and Rosetta redesign rather than
hallucinating binders directly [@afcycdesign]. BindCraft backpropagates
confidence losses through AlphaFold-Multimer into an $L \\times 20$ matrix,
swapping five weight sets randomly and repredicting the target each step for
induced fit (0.5–5.5 Å target Cα RMSD) [@bindcraft]. A four-stage schedule
anneals logits through softmax, straight-through estimation, and discrete
mutation search, followed by soluble-weight ProteinMPNN surface redesign (>4 Å
from the interface), single-sequence AlphaFold2 refolding, and Rosetta scoring,
reaching 10–100% hit rates (mean 46.3%) across 12 targets while noting that
single-sequence inversion leaves AlphaFold2's MSA regime and that ipTM predicts
binding rather than affinity [@alphafold2; @bindcraft]. A code release,
BindCraft2, extends this loop to cyclic peptides, antibodies, repeats,
disordered motifs, and molecular glues without published benchmarks yet.

To avoid unrolling multi-step diffusion, BoltzDesign1 and RFOptimization
backpropagate from Pairformer distograms and confidence heads while diverging in
sequence representation. BoltzDesign1 adapts BindCraft's continuous schedule to
Boltz-1 (adding a softmax warm-up), places a stop-gradient on diffusion, and
optimizes 64-bin Pairformer distogram contact losses (plus the confidence head
for nucleic-acid targets) with optional LigandMPNN redesign \[@boltzdesign1;
@boltz1; @ligandmpnn\]. RFOptimization refines existing designs strictly in
discrete space to avoid relaxation artifacts, proposing single-point
substitutions from negative normalized gradients of RoseTTAFold3's distogram and
confidence heads via annealed Metropolis–Hastings \[@rfoptimization;
@rosettafold3\]. Half of its steps instead run a Boltz folding and LigandMPNN
resampling cycle with AlphaFold3 held out, lifting AF3-refolded success (iPAE \<
2.5, ipTM > 0.8) across protein–protein interfaces (6.73% to 22.31%), cyclic
peptides (1.25% to 12.57%), and small-molecule binders (5.62% to 24.91%)
[@rfoptimization]. Both systems are evaluated in silico only \[@boltzdesign1;
@rfoptimization\].

To promote natural antibody sequences, Germinal and mBER pair AlphaFold-Multimer
with language-model priors differently. Germinal designs CDR loops on a
CDR-masked framework template by merging live AlphaFold-Multimer and IgLM
gradients (weighted sum, MGDA, or PCGrad), passing a continuous
position-specific scoring matrix to AlphaFold-Multimer and straight-through
discrete tokens to IgLM, followed by semigreedy steps and AbMPNN redesign
[@germinal]. Nonbinders cleared the same ipSAE cutoff as binders, and dependence
on AlphaFold3-predicted antigen accuracy remains open [@germinal]; OpenGerminal
reimplements the workflow under Apache-2.0 with AbLang1 [@opengerminal]. By
contrast, mBER runs ESM-2 once over a NanoBodyBuilder2-templated VHH framework
(templated separately from the target hotspot, without MSAs) and adds fixed
logits as a static bias throughout `design_3stage`, with ablations showing both
template and prior are required [@mber]. Its 1.15-million-VHH randomized-hotspot
phage-display sweep showed hit rates shifting from 0.4% overall to 7.5% at one
target's best hotspot and 38% (8/21) in an ipTM-filtered bin without affinity
quantification [@mber]; a follow-up technical report, mBER-2, extends to
microbinders at roughly tenfold higher rates without stating whether hotspots
were randomized.

## Protenix

ByteDance Seed's Protenix platform combines open-weights co-folding, dual-mode
binder design, antibody generation, and benchmarking. Protenix-v1 reproduces
AlphaFold3 openly; under matched training cutoff, scale, and inference budget,
it leads AlphaFold3 on protein–protein and antibody–antigen interfaces and
trails on protein–ligand and protein–DNA complexes, though its recommended
`Protenix-v1-20250630` checkpoint trains past that strict cutoff [@protenix_v1].
Accuracy scales roughly log-linearly with sampling seeds (36.01% at 1 seed to
47.68% at 80 seeds; 95% CI 49.3–56.3% for one 5×5 run), and common-intersection
FoldBench analysis showed that unequal failure subsets flip Boltz-1 versus
Chai-1 rankings [@protenix_v1; @foldbench]. Built on Protenix, PXDesign provides
two design modes: PXDesign-d uses a Diffusion Transformer (DiT) over Cartesian
coordinates, whereas PXDesign-h replaces 200-step diffusion with a 2-step ODE
sampler for end-to-end gradient hallucination across five resampled Protenix
models [@pxdesign]. All six wet-lab campaigns ran PXDesign-d (20–73% nanomolar
hit rates on 5/6 targets; 0/16 on TNFα), while filtering analysis showed that
Protenix and AF2-IG retain largely distinct true positives with target-dependent
thresholds [@pxdesign].

Protenix-v2 gains 9–13 percentage points over Protenix-v1 on antibody–antigen
DockQ > 0.23 across PXMeter-AB, FoldBench-AB, and AF3-AB, with 5 seeds
surpassing Protenix-v1 at 1,000 seeds [@protenix_v2]. Extending design to VHH,
Fv, and full mAbs, it produced BLI-confirmed binders for every antigen on a
novelty-controlled soluble panel (2–48% hit rates) and 16–88% VHH-Fc / 0–50% mAb
hit rates across four GPCRs at 16–30 designs/target [@protenix_v2]. Two AMBP
epitopes gave 4% versus 48% hit rates, leading authors to prioritize native
ligand-binding sites; caveats include manual epitope choice on in-stock targets
and no direct Chai-2 comparison due to format differences [@protenix_v2].
ByteDance Seed's open PXMeter toolkit [@pxmeter] added sp2-, amide-, and
sp3-planarity checks in v1.1.0 (introduced with Protenix-v2 and adopted as
PXMeter-AB by OpenDDE) after observing twisted amides and flat sp3 centers
passing PoseBusters [@protenix_v2; @opendde; @posebusters].

## ESM

The ESM lineage replaces inference-time MSA retrieval with protein language
models trained on billions of sequences. ESM-2 and ESMFold demonstrated
single-sequence 3D folding via a masked language model, folding trunk, and IPA
module without MSAs or templates, trading lower accuracy than AlphaFold2 for
fast inference across the ESM Metagenomic Atlas [@esm2]. ESM-3 scaled to a
multimodal discrete-token transformer (1.4B, 7B, and 98B parameters over 2.78
billion proteins) covering sequence, structure, and function, outperforming
ESMFold on CAMEO single-sequence lDDT (0.880 vs. 0.861) and generating
fluorescent `esmGFP` at 58% sequence identity; `ESM3-open` (1.4B) is
academic-only while the 98B model is API-only [@esm3].

ESMC and ESMFold2 extend single-sequence language modeling to all-atom complexes
and binder design [@esmc]. Frozen 6B-parameter ESMC representations (~2.8
billion sequences) feed 48 recurrent pair-state folding layers (24 in
ESMFold2-Fast) and a sliding-window diffusion transformer, with an optional
detachable MSA encoder [@esmc]. Single-sequence ESMFold2 matches MSA-enabled
AlphaFold3 on antibody–antigen interfaces within error bars across independent
AtlasFold runs [@esmc; @atlasfold]. Because single-sequence input is native,
binder optimization backpropagates directly through ESMC and the folding trunk's
distogram for 150 single-stage steps across two replicates, running diffusion
and confidence heads only in final steps to rank by ensemble ipTM or a
distogram-entropy proxy (plus pI ≤ 6.0 for minibinders) [@esmc]. Testing 84
designs per cohort across five author-selected targets yielded 36–88% hit rates
(mean 70.0%, best 68 pM) for minibinders and 15–29% (mean 21.0%) for scFvs
[@esmc]. Independently, AtlasFold released an MIT-licensed single-sequence PLM
folder (weights, code, data, and checkpoints) alongside a seven-model FoldBench
rank-versus-oracle benchmark [@atlasfold].

## Closed and undisclosed systems

Several systems publish wet-lab outcomes while withholding generative
architectures or weights. Google DeepMind's AlphaProteo reported 9–88%
minibinder hit rates across eight targets (0/54 on TNFα; best 82 pM on IL-7Rα)
and resynthesized RFdiffusion designs for yeast-display comparison; it discloses
its AF2 filter (`interchain PAE < 10`, `RMSD < 1 Å`, `pLDDT > 80`) while
describing the generator only as trained on PDB and AlphaFold distillations
[@alphaproteo]. Latent Labs' Latent-X1 and Latent-X2 likewise cite only a
proprietary all-atom architecture filtered by ipTM, PAE, and self-consistency
[@latentx1; @latentx2]. Latent-X1 reported 10–64% minibinder hit rates (best \<
0.01 nM) and 91–100% on macrocycles, resynthesizing RFpeptides' two best binders
for affinity comparison while leaving hit rates across distinct assays
[@latentx1; @rfpeptides]; Latent-X2 reported macrocycles (best 1.54 nM) and
VHH/scFv binders on 9/18 targets (best 26.2 pM) with drug-like developability
and low immunogenicity [@latentx2]. Chai-2 similarly withholds its generator
beyond `Chai-2f` [@chai2], and BoltzProt-1 restricts access to a commercial API
[@boltzprot1].

Other models lack primary publications and appear only via platforms or
third-party benchmarks. OpenDDE, an Apache-2.0 co-folder built on Protenix-v1
and OpenFold3, triples Pairformer hidden width from 128 to 384 (~3× parameters,
~9× compute), adds an atom-level refiner before diffusion, and lists joint
design on its roadmap [@opendde]. Alongside third-party antibody–antigen
evaluations, OpenDDE provides the only public scaling-curve points for
unpublished IsoDDE (also noted as lacking public verification by Bender et al.
[@bender_perspective]) and SeedFold [@opendde], alongside the commercial web
platform Chai-3.

# Quantitative Landscape and Evaluation Pitfalls

Interpreting structure-prediction and binder-design benchmarks requires reading
every metric alongside its evaluation protocol. On the common target
intersection of FoldBench (1,522 assemblies across nine tasks), monomer accuracy
across seven AF3-class predictors sits in a narrow 0.85–0.89 lDDT band and
general protein–protein DockQ success spans roughly 7 percentage points
(65.4–72.7%), whereas antibody–antigen success spans more than a factor of two
(23.1–52.3%; **Table 2A**) [@foldbench; @protenix_v1]. Training cutoffs further
restrict comparisons: Boltz-2 is excluded from FoldBench common-intersection
tables because its 2023-06-01 cutoff overlaps the 2023-01-13 to 2024-11-01
benchmark window [@boltz2; @protenix_v1; @protenix_v2; @esmc].

Identical metric names also shift under different target filters, averaging
units, or MSA pipelines. Because models fail on different inputs (out-of-memory
errors, unsupported glycans, or token limits), restricting FoldBench
protein–protein pairs to the common completed set ($n = 237$) reverses Boltz-1
(68.4% vs. 68.3% published) and Chai-1 (67.5% vs. 68.5% published), while
AlphaFold3's FoldBench antibody–antigen score varies across unfiltered (47.90%),
intersection-filtered (48.75%), and independently re-run (48.8%) runs
[@foldbench; @protenix_v1; @opendde]. Averaging conventions cause larger swings:
Chai-1 reports 52.9% antibody DockQ success over 40%-identity interface clusters
[@chai1], whereas FoldBench evaluates per interface and obtains 25.2%
[@foldbench]; Boltz-1 averages per interface within each complex before
averaging across complexes [@boltz1], and external FoldBench runs of OpenFold3
shifted from 70.79% to 69.29% under a different MSA pipeline \[@openfold3;
@protenix_v2\].

A second bottleneck separates generating a near-native complex from recognizing
it with internal confidence scores. Across seven predictors evaluated
template-free by AtlasFold (**Table 2A**), confidence-ranked selection loses
11–21 percentage points relative to oracle selection against the experimental
structure on antibody–antigen interfaces (4.5 points for Boltz-1) and 3–8 points
on protein–protein interfaces [@atlasfold]. FoldBench similarly noted that a
near-native CDR-H3 loop is necessary but not sufficient for accurate docking
because per-sample confidence does not reliably pick near-native poses
[@foldbench]. This ranking gap motivates large seed budgets: AlphaFold3 ranked
antibody poses over 1,000 seeds [@alphafold3], Protenix-v1 rose from 36.01% (1
seed) to 47.68% (80 seeds) [@protenix_v1], and OpenDDE reported oracle
antibody–antigen success climbing from ~66% to >90% at several hundred seeds
[@opendde].

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

*Notes for Table 2A:* FoldBench common-intersection columns cover PDB releases
from 2023-01-13 to 2024-11-01 (homology-reduced against an AF3 2021-09-30
cutoff) at 5 seeds × 5 samples, 10 recycles, top-ranked \[@foldbench;
@protenix_v1\]. Monomer is mean lDDT; Prot–Prot and Ab–Ag are DockQ ≥ 0.23 (%);
Prot–Lig is ligand RMSD < 2 Å and lDDT-PLI > 0.8 (%). Non-Protenix and v0.2.0
rows were recomputed by the Protenix-v1 authors from published logs;
nucleic-acid subsets on the same intersection span 50.00–68.46% (Prot–RNA, $n =
46$), 49.27–75.91% (Prot–DNA, $n = 274$), 0.2909–0.5693 lDDT (DNA, $n = 14$),
and 0.4416–0.6547 lDDT (RNA, $n = 15$) [@protenix_v1]. Boltz-2 [@boltz2] is
excluded due to its 2023-06-01 training cutoff \[@protenix_v1; @protenix_v2;
@esmc\]. AtlasFold columns report mean DockQ > 0.23 (%) across 252 five-seed
draws from 10 seeds, template-free, via OpenStructure 2.9.1 [@atlasfold].
Per-class headline tables in AlphaFold3 [@alphafold3], Boltz-1 [@boltz1],
Boltz-2 [@boltz2], and RoseTTAFold2 [@rosettafold2] appear as figure-only
images.

Wet-lab binder campaigns are even less directly comparable because no two de
novo studies share targets, assays, or binding thresholds. Grouping campaigns by
validation format (**Table 2B**) highlights four confounders. First, several
headline affinities reflect bivalent Fc fusions or avidity rather than
monovalent binding, including Protenix-v2's VHH-Fc constructs (except VEGF-A)
[@protenix_v2], four of Chai-2's ten miniproteins plus its EFNA5 scFv [@chai2],
and BindCraft's PD-1 Fc construct [@bindcraft]. Second, synthesis and expression
attrition changes denominators, as in RFpeptides [@rfpeptides], Latent-X1
macrocycles [@latentx1], and PXDesign's PD-L1 campaign (72.7% of tested designs
vs. 47.1% sent for expression) [@pxdesign]. Third, some studies emphasize
target-level coverage (BoltzGen, Protenix-v2, Latent-X2) \[@boltzgen;
@protenix_v2; @latentx2\] while others report per-design hit rates (Chai-2,
PXDesign, BindCraft, ESMFold2) [@chai2; @pxdesign; @bindcraft; @esmc]. Fourth,
binding cutoffs span unthresholded SPR responses \[@bindcraft; @rfpeptides;
@latentx1\], BLI thresholds from 0.05 to 0.4 nm \[@protenix_v2; @pxdesign;
@chai2; @esmc; @latentx2\], and BoltzProt-1's explicit split between screening
hits and confirmed binders [@boltzprot1]. Cross-lab resynthesis experiments
confirm this sensitivity: AlphaProteo's yeast-display re-assay of RFdiffusion's
designs at 10–20× lower concentrations shifted hit rates from 33% to 16%
(IL-7Rα) and 6% to 0% (TrkA) [@alphaproteo; @rfdiffusion]; Latent-X1 measured
RFpeptides' two best macrocycles 4.4× and 5× weaker than published (leading on
MDM2 and trailing on MCL-1) [@latentx1; @rfpeptides]; and Latent-X2 tested two
RaPID macrocycles under different cyclization chemistry [@latentx2]. **Table
2B** therefore summarizes each campaign within its own experimental regime
rather than on a shared scale.

**Table 2B. Representative wet-lab binder design campaigns grouped by
experimental validation format.**

| System                                                        | Modality & Targets                     |                                   Tested | Reported Outcome                                                                         | Best Affinity                       | Assay Criterion & Key Caveats                                                                                |
| ------------------------------------------------------------- | -------------------------------------- | ---------------------------------------: | ---------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Confirmed across two assay formats**                        |                                        |                                          |                                                                                          |                                     |                                                                                                              |
| BoltzProt-1 [@boltzprot1]                                     | VHH, 10 low-homology targets           |                          15/target (150) | 8.0% (12/150; 4/10 targets) vs. BoltzGen 3.3% (5/150; 2/10)                              | Not reported                        | Clean sensorgram + flipped orientation & independent vendor re-test (see footnote).                          |
| Germinal [@germinal]                                          | scFv (as Fab), 2 targets               |                                48/target | 3/48 PD-L1, 1/48 IL-3                                                                    | 360 nM (SPR) / 650 nM (BLI)         | Confirmed on both SPR and BLI.                                                                               |
| Latent-X1 [@latentx1]                                         | Minibinders, 5 targets                 |                  100 HT-BLI, 88 mDisplay | 10–64%/target ($r = 0.68$–$0.79$)                                                        | < 0.01 nM (IL-7Rα, SC2RBD)          | Robust mDisplay dynamic range on 3/5 targets; architecture undisclosed.                                      |
| Germinal [@germinal]                                          | VHH, 4 targets                         |               101 / 46 / 43 / 52 ordered | 7 / 2 / 4 / 5 BLI-confirmed                                                              | 170 nM (PD-L1); 42 nM (Legobody)    | Split-luciferase (>150,000 RLU) then BLI (sub-denominators 25/11/11/20).                                     |
| **Single assay format**                                       |                                        |                                          |                                                                                          |                                     |                                                                                                              |
| Latent-X2 [@latentx2]                                         | Macrocycles, 2 targets                 |                                10/target | 9/10 (PHD2), 8/10 (K-Ras G12D)                                                           | 1.54 nM (PHD2)                      | Single-point BLI > 0.1 nm → kinetics ($R^2 > 0.95$); undisclosed.                                            |
| RFpeptides [@rfpeptides]                                      | Macrocycles, 4 targets                 |                 6–14 (of 11–27 selected) | 2–4 hits/target                                                                          | 6 nM (GABARAP)                      | SPR at 100 µM (no numeric cutoff); synthesis attrition; crystal structures solved.                           |
| BoltzGen [@boltzgen]                                          | VHH & proteins, 9 novel targets        |                                15/target | Binders on 6/9 targets (both formats)                                                    | 6.1 nM VHH; 9.8 nM protein          | Quantifiable sensorgram or ≥ 300% negative control; target-level rate.                                       |
| PXDesign [@pxdesign]                                          | Minibinders, 6 targets                 |                              9–17/target | 20–73% on 5 targets; 0/16 TNFα                                                           | "Multiple nanomolar"                | BLI > 0.06 nm at 1 µM, $K_D < 1,000$ nM; PD-L1: 72.7% tested vs. 47.1% expressed.                            |
| Latent-X1 [@latentx1]                                         | Macrocycles, 3 targets                 |                             11–17/target | 91 / 100 / 94%                                                                           | 5.35 µM (MDM2)                      | Measurable SPR (no numeric cutoff); 11–17 synthesized of 30 submitted (700 generated); undisclosed.          |
| Chai-2 [@chai2]                                               | scFv & VHH, 52 novel targets           |                       ≤ 20/target/format | 13.7% scFv (68/496), 20.0% VHH (41/205); 26/52 targets                                   | < 1 nM (EFNA5 scFv, avidity)        | Curve > 0.1 nm & > 300% background; EFNA5 avidity-flagged; generator undisclosed.                            |
| BoltzGen [@boltzgen]                                          | VHH & proteins, 5 benchmark targets    |                             15–20/target | Binders on 4/5 targets                                                                   | 0.81 nM (PDGFR)                     | Same sensorgram / ≥ 300% criterion; target-level rate.                                                       |
| Latent-X2 [@latentx2]                                         | VHH & scFv, 18 targets                 |                       4–24/target/format | 9/18 targets; up to 25% of designs                                                       | 26.2 pM (HDAC8 scFv)                | BLI > 0.1 nm → kinetics ($R^2 > 0.95$; >0.90 for AHSP); undisclosed.                                         |
| Chai-2 [@chai2]                                               | Minibinders, 5 targets                 |                             20–25/target | 68% (75/111); 5/5 targets                                                                | 18.3 pM (IL-7Rα)                    | Same BLI criterion; 4/10 quoted affinities avidity-affected; generator undisclosed.                          |
| Protenix-v2 [@protenix_v2]                                    | VHH-Fc & mAb, 4 GPCRs                  |                             16–30/target | VHH-Fc 16/62/40/88%; mAb 0/17/50/44%                                                     | 112 pM (GPRC5D, avidity)            | BLI > background + 0.05 nm (most $K_D < 1,000$ nM); bivalent avidity.                                        |
| Protenix-v2 [@protenix_v2]                                    | VHH-Fc, soluble targets                |                              Figure only | 2–48%/target; 100% targets                                                               | Figure only                         | Same BLI cutoff; bivalent Fc (except VEGF-A); counts/affinities figure-only.                                 |
| BindCraft [@bindcraft]                                        | Minibinders, 12 targets                |                              6–53/target | 10–100%, mean 46.3%                                                                      | < 1 nM (PD-1 Fc); 5 nM (CbAgo)      | SPR binding (no numeric cutoff); PD-1 is bivalent Fc ($K_D$ undetermined).                                   |
| ESMFold2 [@esmc]                                              | Minibinders & scFv, 5 targets each     |                                84/cohort | Minibinders 36–88% (mean 70.0%); scFv 15–29% (mean 21.0%)                                | 68 pM (minibinder; target unstated) | Dual BLI cutoffs (0.25–0.4 nm stringent; >0.1 nm inclusive; loading >0.5 nm); Fig. 3 shading image-only.     |
| RFdiffusion [@rfdiffusion]                                    | Minibinders, 5 targets                 |                          95/target (475) | 19% pooled                                                                               | 28 nM (influenza HA)                | Single-point BLI at 10 µM ≥ 50% positive control; lower on yeast-display re-assay [@alphaproteo].            |
| AlphaProteo [@alphaproteo]                                    | Minibinders, 8 targets                 |                            54–172/target | 9% (TrkA) to 88% (BHRF1); 0/54 TNFα                                                      | 82 pM (IL-7Rα)                      | Yeast-display signal > 0.2 (1.3 for IL-17A); generator undisclosed.                                          |
| **Display enrichment or functional readout without affinity** |                                        |                                          |                                                                                          |                                     |                                                                                                              |
| BoltzGen [@boltzgen]                                          | VHH (2 targets); peptides (NPM1, GyrA) | 7/target (yeast); 5 (NPM1); 1,808 (GyrA) | 1/7 & 7/7 yeast; 1/5 co-localization; 19.5% (352/1,808) growth inhibition                | "At best 2 µM" (yeast, no EC50)     | Yeast display without EC50; live-cell/growth readouts do not directly confirm binding.                       |
| RFantibody [@rfantibody]                                      | VHH, 4 targets (yeast) & 3 (SPR)       |    9,000/target (yeast); 95/target (SPR) | 0–2% per target                                                                          | 78 nM (HA), 1.4 µM (RSV III) by SPR | Authors note experimental screening remains necessary.                                                       |
| mBER [@mber]                                                  | VHH, 145 of 436 targets assayed        |                 1,153,241 (pooled phage) | 45% (65/145) targets elevated; per-design 0.02–8% (median ~0.4%); 38% (8/21) in ipTM bin | Not measured                        | Replicate order statistic (\<1 expected false positive/target); phage display lacks affinity quantification. |

*Notes for Table 2B:* Campaigns are ordered within each group by designs tested
per target. In-silico-only systems (BoltzDesign1 [@boltzdesign1], RFOptimization
[@rfoptimization]) are omitted from Table 2B and detailed in the text.
Figure-only source data include Protenix-v2's soluble-target per-target
counts/affinities in Fig. 4A (AMBP ratios 2/50, 13/27 and IDI2 12/50 transcribed
in BoltzProt-1 [@protenix_v2; @boltzprot1]) and ESMFold2's Fig. 3 cutoff shading
[@esmc]. In BoltzProt-1 [@boltzprot1], revised screening hits differ between
Table 1 (7/150 [4.7%] BoltzGen, 14/150 [9.3%] BoltzProt-1) and prose (14/150
[9.3%], 24/150 [16.0%]), whereas the confirmed-binder counts shown above (5/150
[3.3%] and 12/150 [8.0%]) match in both places.

# Conclusions and Open Challenges

## From in vitro binding to therapeutic utility

Most binder-design papers frame their motivation around therapeutic development,
citing automated drug discovery [@boltzgen], species cross-reactivity [@chai2],
reduced IgE binding in patient samples [@bindcraft], antibody developability
[@latentx2], and protein therapeutics [@mber]. Auditing a decade of AI in
pharmaceutical R&D, Bender et al. report strong technical advances alongside
limited evidence of clinical impact so far [@bender_perspective]. They
distinguish *model validation* (accuracy on held-out benchmarks or isolated in
vitro binding assays) from *process validation* (improving downstream clinical
decisions), noting that AlphaFold represents model validation for folding rather
than process validation for drug discovery [@bender_perspective].

Although biologics have supported recent approval gains through higher clinical
success rates and stronger intellectual-property protection than small
molecules, Bender et al. observe (citing RFdiffusion, ProteinMPNN, BoltzGen, and
Chai-2) that binding remains easier to predict than functional activity and
developability, echoing small-molecule discovery where ChEMBL and PubChem
catalog over $10^6$ bioactive ligands versus roughly $10^3$ marketed drugs
[@bender_perspective]. They also emphasize matching metrics to the decision task
(selection, deselection, or quantification), local generalization outside
training distributions, and independent verifiability: open co-folding models
have largely caught up with closed ones, whereas proprietary systems such as
IsoDDE disclose too little detail for independent evaluation
[@bender_perspective]. Because that Perspective draws mainly on small-molecule
and clinical pipelines (relying on one preprint, FLAb2, for biologic
developability), it provides translational context rather than a direct audit of
protein design [@bender_perspective].

## Open technical and methodological limitations

Five technical and methodological limitations recur across current binder-design
pipelines. First, nearly all open systems generate, filter, and report solely on
binding. Latent-X2 notes that therapeutic campaigns often fail not for lack of
binding, but because clinical success requires developability and low
immunogenicity [@latentx2]; it reports such profiles for designed antibodies,
yet its generative architecture is undisclosed [@latentx2]. Second, current
scoring functions act primarily as binary binding indicators rather than
quantitative affinity estimators: BindCraft notes that AlphaFold2 ipTM predicts
whether a design binds rather than its $K_D$ [@bindcraft], and Boltz-2's
affinity head covers protein–ligand complexes on single-protein targets rather
than multimeric protein–protein interfaces [@boltz2], leaving affinity to
wet-lab measurement. Third, most campaigns condition on experimentally solved or
high-confidence predicted structures, and Germinal notes that how strongly
design success depends on predicted antigen-model accuracy remains an open
question [@germinal].

Fourth, no shared, blinded prospective benchmark exists for de novo binder
design, and independent replication of a full published campaign has occurred
only once, when AlphaProteo re-tested RFdiffusion's published designs (including
nonbinders) by yeast display [@alphaproteo; @rfdiffusion]. The closest
prospective standard is the AIntibody challenge, which independently assayed 511
IgG antibodies from 29 organizations across three tasks using high-throughput
SPR (HT-SPR), kinetic exclusion assays (KinExA), and a five-assay developability
panel [@aintibody]. The top computational design (95 pM) matched the best
wet-lab antibody (113 pM), and Challenge 1 was won by an open-code
Protenix-derived pairformer with a direct preference optimization (DPO) fitness
head, yet a non-ML consensus ranked third [@aintibody]. On Challenge 2
(within-HCDR3-cluster affinity ranking), only 1 of 26 groups beat random
selection; on the out-of-library task, 30.4% were nonbinders and the
highest-affinity winner (2.9 pM) failed to elute from the hydrophobic
interaction chromatography (HIC) column [@aintibody]. AIntibody also carries
scope limits: it tested one well-characterized antigen (SARS-CoV-2 RBD,
described as "deliberately primed for success"), reflects a Q1 2025 snapshot
missing several prominent de novo groups, and evaluated library-conditioned
engineering with provided affinities rather than de novo binder design
[@aintibody].

Fifth, structure-prediction confidence scores remain unreliable for per-design
discrimination. Metrics such as ipTM and ipSAE enrich hit rates across large
pools, as in mBER [@mber], yet often fail on individual candidates, as in
Germinal where nonbinders cleared the same ipSAE threshold as binders
[@germinal]. Re-scoring 3,766 tested designs from six campaigns across 15
targets under one pipeline, Overath et al. found AlphaFold3 ipSAE to be the
strongest single predictor overall, yet its average precision ranged from 0.1 to
1.0 across targets (while leaving heterogeneous source assays unchanged and
reflecting earlier-generation designs) [@overath_meta].

Current co-folding and generative models can produce epitope-targeted protein
and peptide binders across multiple formats while often testing tens rather than
thousands or millions of sequences per target. Quantitative protein–protein
affinity prediction, joint optimization of function, developability, and
immunogenicity in inspectable architectures, reliable per-design filtering on
structurally uncharacterized targets, and comparative performance under shared
blinded benchmarks remain to be demonstrated.
