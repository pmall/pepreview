# Deep-Learning Methods for Protein and Peptide Binder Generation

## Abstract

Many modern therapeutics, diagnostics, and laboratory reagents rely on proteins
or peptides that bind a chosen target protein selectively. These binders include
antibodies, nanobodies, single-chain variable fragments, compact minibinders,
and macrocyclic peptides. Historically, finding such molecules has meant
searching rather than designing them: immunizing animals or screening
combinatorial display libraries of trillions of random sequences. Both
strategies demand extensive wet-lab screening for every new target and rarely
allow investigators to direct binding to a chosen surface site. Deep-learning
advances in protein structure prediction and biomolecular co-folding have made
direct computational binder generation practical, often reducing experimental
testing from vast libraries to tens of designed sequences per target. Unlike
small-molecule generation, which builds variable chemical graphs under strict
valence rules, protein and peptide design searches chains drawn from the
20-amino-acid alphabet evaluated by how they fold against a target. Across open
and proprietary systems, architectures differ in three main respects.
Evolutionary context enters the sequence trunk through multiple sequence
alignment retrieval, through protein language models, or through both.
Three-dimensional coordinates emerge from single-pass regression, iterative
stochastic diffusion, or straighter-trajectory flow matching. Finally, structure
predictors drive sequence design either as joint predictor-generators, as
post-hoc filters in generate-and-filter pipelines, or as differentiable
objectives for gradient-based sequence optimization. Interpreting reported
success rates requires close attention to testing budgets, confirmation assays,
target and epitope choice, and method disclosure. Predicting quantitative
protein–protein binding affinity, optimizing developability and immunogenicity
alongside binding, building shared prospective benchmarks, and improving
per-design filtering remain central open problems.

# Introduction and Conceptual Background

## Why protein binders matter and how discovery shifted from search to design

Selective recognition of a target protein is the basis for blocking a signaling
pathway, detecting a biomarker, labeling a cellular component, or modulating an
enzyme. When the target is a protein, the binding partner is frequently another
protein or a peptide. Full-length antibodies, single-domain nanobodies (VHHs),
single-chain variable fragments (scFvs), compact de novo minibinders, and
head-to-tail macrocyclic peptides make up a large share of modern biologics and
research reagents. Unlike small chemical compounds, which typically require a
deep pocket, extended protein–protein interfaces can recognize flat or shallow
molecular surfaces.

For decades, discovering a protein binder has been an experimental search
problem. Standard workflows immunize animals, isolate clones from patients, or
pan phage and yeast display libraries containing $10^{12}$ or more random
sequences. These methods work reliably and remain foundational across academia
and industry. Yet they require wet-lab screening from the first step, must be
repeated from scratch for every new target, and tend to recover binders against
whichever regions happen to be immunogenic or accessible rather than an epitope
chosen by the investigator [@rfantibody]. Computational binder generation takes
the opposite route, proposing candidate sequences directly for a specified
target and binding site.

Focusing on protein and peptide binders draws a clear technical boundary apart
from small-molecule generation. Whether a system generates a macrocyclic
peptide, a compact minibinder, or the complementarity-determining regions (CDRs)
of a nanobody, its output is a linear or cyclized chain of amino acids drawn
from a fixed 20-letter alphabet and judged by how it folds against the target.
Small-molecule generation instead constructs variable-size chemical graphs
governed by valence rules, bond orders, and synthetic accessibility, which calls
for different neural architectures and evaluation benchmarks.

Direct computational design became practical once deep learning reached
experimental accuracy on protein structure prediction. AlphaFold2 solved
single-chain folding at CASP14 [@alphafold2], and AlphaFold3 extended prediction
to biomolecular complexes containing proteins, nucleic acids, small-molecule
ligands, and ions [@alphafold3]. Designing a binder, however, is not the same
problem as predicting a structure. A predictor maps a known sequence to a
three-dimensional fold that can be checked against a crystal or cryo-electron
microscopy structure. A generator must invent a new sequence from $20^L$
possibilities for a chain of length $L$ such that the molecule folds stably and
binds its target. Only a wet-lab experiment can confirm whether it succeeded.
Between 2024 and 2026, the field expanded rapidly across open reproductions and
specialized design stacks. Engineering investments have followed active
deployment: in September 2026, teams at NVIDIA, Anthropic, and ESM released
optimized inference kernels reporting 2–4× throughput gains across major open
folding and design models in public engineering posts and repositories.

## How co-folding predictors are built

Modern structure prediction relies on the observation that correlated mutations
(coevolution) between pairs of positions in a multiple sequence alignment (MSA)
indicate spatial proximity in the folded protein. AlphaFold2 demonstrated how
accurately deep networks can extract this signal at CASP14, reaching a median
backbone accuracy of 0.96 Å r.m.s.d.95 (Cα RMSD at 95% residue coverage; 95% CI
0.85–1.16 Å) compared with 2.8 Å r.m.s.d.95 for the next best method
[@alphafold2]. AlphaFold3 extended this capability from single chains to
multi-component complexes, a task widely called co-folding [@alphafold3].

Early RoseTTAFold 1 and 2 networks processed 1D sequence, 2D pairwise, and 3D
coordinate tracks in parallel from input to output \[@rosettafold;
@rosettafold2\]. Most current co-folding models instead separate computation
into two sequential stages: a differentiable trunk followed by a
coordinate-generation module.

The first stage, the trunk, processes sequence and evolutionary inputs into
single-residue and pairwise representations. It appears as the Evoformer in
AlphaFold2 [@alphafold2], the Pairformer in AlphaFold3-class co-folders
[@alphafold3; @boltz1; @chai1; @protenix_v1; @rosettafold3], and the folding
trunk in ESMFold and ESMFold2 [@esm2; @esmc]. A linear head attached to the pair
representation predicts a distogram, which gives a probability distribution over
inter-residue distances for every pair of residues. Models use the distogram
both as a training loss and, in several design loops, as a differentiable
geometric surrogate [@alphafold2; @boltzdesign1; @esmc]. Because the trunk is
differentiable throughout and runs once per complex or random seed [@boltz1],
the main distinction at this stage is how evolutionary context enters. MSA-based
models retrieve homologous sequences from databases at inference time, as in
AlphaFold, RoseTTAFold, Boltz, and Protenix. Protein language model (PLM)-based
models instead absorb evolutionary statistics into their weights during
pre-training, allowing single-sequence inference without database searches, as
in ESMFold, ESMFold2, and AtlasFold [@esm2; @esmc; @atlasfold]. Hybrid models
such as Chai-1 carry both tracks and can run on either [@chai1].

The second stage converts the trunk's single and pair representations into 3D
atomic coordinates, and its mathematical formalism governs both inference speed
and differentiability. AlphaFold2 and ESMFold rely on single-pass coordinate
regression through an end-to-end differentiable structure module built on
Invariant Point Attention (IPA) [@alphafold2; @esm2]. Ablation studies in
AlphaFold2 showed that removing end-to-end structural gradients reduces accuracy
[@alphafold2]. AlphaFold3 and subsequent AF3-class co-folders replaced IPA with
a diffusion module for structure prediction itself, independent of generative
design [@alphafold3; @boltz1; @chai1; @protenix_v1; @rosettafold3; @esmc].
Adapted from image generation by replacing noised pixels with noised atomic
coordinates, diffusion iteratively denoises Gaussian noise along a stochastic
differential equation (SDE) trajectory [@alphafold3; @frameflow]. High-quality
diffusion sampling in protein generators often demands hundreds to roughly 1,000
forward passes [@frameflow]. Flow matching lowers this cost by recasting
coordinate transport as an ordinary differential equation (ODE) with straighter
trajectories. FrameFlow applied flow matching to the earlier FrameDiff
generator, achieving twofold better designability at five times fewer sampling
steps on unconditional monomers [@frameflow], and target-conditioned binder
variants include PPIFlow [@ppiflow], OriginFlow [@originflow], AtomFlow
[@atomflow], and D-Flow [@dflow]. Unlike image generation, where outputs depend
on subjective human judgment, protein designs can be scored automatically by
structure predictors.

## Turning structure predictors into binder generators

Structure prediction and binder generation can run on the same neural network
simply by changing which inputs are held fixed. Supplying all chain sequences
asks the model to predict the bound complex. Holding the target fixed while
leaving the binder chain unspecified or corrupted with noise asks the same model
to build a partner that folds against the target. BoltzGen implements this
duality directly as a single all-atom diffusion model trained for both
prediction and design [@boltzgen]. RFdiffusion reached a related duality by
fine-tuning the RoseTTAFold structure predictor into a backbone generator, using
RoseTTAFold's input-to-output 3D coordinate track to encode target structures or
active-site motifs directly as spatial coordinates \[@rosettafold2;
@rfdiffusion\].

Across current pipelines, structure predictors drive binder design in three main
ways (**Figure 1**):

1. **Joint or fine-tuned predictor-generators** reuse prediction weights to
   denoise unknown binder structures directly, either by fine-tuning a predictor
   into a generator (RFdiffusion and RFdiffusion2 [@rfdiffusion; @rfdiffusion2])
   or by training one all-atom diffusion model jointly on prediction and design
   (BoltzGen [@boltzgen]).
1. **Generate-and-filter pipelines** sample candidate backbones without passing
   gradients through the predictor during generation, assign sequences through
   inverse folding (most commonly ProteinMPNN [@proteinmpnn]), and rank
   candidates afterward. Filtering usually relies on refolding confidence
   metrics, such as AlphaProteo's threshold of interchain AlphaFold2 PAE < 10 Å,
   binder-aligned binder RMSD < 1 Å, and pLDDT > 80 [@alphaproteo].
   Alternatively, confidence scores can be replaced by a classifier trained
   directly on experimental binding outcomes, as in BoltzProt-1's BoltzPPI
   [@boltzprot1].
1. **Gradient-based sequence optimization (hallucination or backpropagation)**
   represents a binder of length $L$ as a continuous probability distribution
   over the 20 amino acids at each position (an *L* × 20 simplex). The loop
   passes this relaxed sequence into a differentiable predictor and descends
   structural confidence or distogram losses while annealing toward discrete
   one-hot amino acids, as in BindCraft [@bindcraft], Germinal [@germinal],
   BoltzDesign1 [@boltzdesign1], PXDesign-h [@pxdesign], and ESMFold2 [@esmc].
   One variant, RFOptimization, keeps sequences strictly discrete and uses
   predictor gradients solely to rank point mutations [@rfoptimization].

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
sequence optimization over a continuous *L* × 20 sequence relaxation annealed to
one-hot amino acids, differentiating end-to-end through a regression module
(BindCraft, Germinal), through trunk distograms and confidence heads while
stopping gradients before diffusion (BoltzDesign1, ESMFold2, and discrete
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
3, closed feedback loop from an *L* × 20 relaxed sequence through the predictor
with three gradient return paths (end-to-end IPA, trunk distogram/confidence
shortcut with diffusion stop-gradient, and 2-step ODE decoder).

Three practical engineering constraints shape how these workflows behave. First,
gradient optimization requires single-sequence input on the binder chain because
an MSA lookup is neither defined for an invented sequence nor differentiable.
Inverting an MSA-trained predictor such as AlphaFold2 therefore operates in its
documented weakest regime [@alphafold2; @bindcraft], whereas natively
single-sequence PLMs such as ESMC and ESMFold2 backpropagate without leaving
their training distribution [@esmc].

Second, unrolling hundreds or roughly 1,000 diffusion steps to compute sequence
gradients is computationally impractical [@frameflow; @boltzdesign1].
Diffusion-based design loops handle this obstacle in two ways. BoltzDesign1
[@boltzdesign1], RFOptimization [@rfoptimization], and ESMFold2 [@esmc] read
gradients from the trunk distogram and confidence heads without backpropagating
through diffusion. PXDesign-h instead replaces the 200-step diffusion decoder
with a differentiable 2-step ODE sampler [@pxdesign].

Third, candidate filtering strongly shapes experimental yield independently of
the generator. In BoltzProt-1, replacing BoltzGen's confidence ranking with the
trained BoltzPPI classifier more than doubled confirmed binders on identical
candidate pools [@boltzprot1]. Similarly, PXDesign found that Protenix and
AlphaFold2-Initial-Guess (AF2-IG) filters retain largely non-overlapping true
positives [@pxdesign], while RFOptimization mixes multiple predictor families
inside its loop to limit single-predictor overfitting [@rfoptimization].

## Reading reported numbers: testing budgets, hit definitions, and disclosure

A clear practical measure of progress is how many candidate sequences must be
synthesized and tested per target to obtain a working binder. Display libraries
and early computational pipelines often required screening thousands to millions
of designs [@chai2; @rfantibody]. Recent generative pipelines routinely test
between 10 and 100 designs per target and report double-digit hit rates across
several binder formats [@chai2; @rfpeptides; @boltzgen; @protenix_v2; @esmc].

Raw hit rates, however, cannot be compared directly across studies. First, hit
definitions differ substantially: BoltzProt-1 separates initial screening hits
(which correspond to what prior binder papers commonly call binders) from
confirmed binders verified in follow-up assays [@boltzprot1]. Second, target and
epitope choice can shift success rates by orders of magnitude. Most small
campaigns select their own targets and epitopes. In contrast, mBER tested 1.15
million VHH designs by phage display against randomly selected surface hotspots
across 436 human cell-surface proteins (145 assayed) [@mber]. Across those
unchosen sites, the median per-design hit rate fell to roughly 0.4%, even though
the best individual hotspots reached up to 38% under strict filtering [@mber].

Method openness also varies widely across the field (**Table 1**). A few
releases are fully reproducible with weights, training code, and datasets, such
as OpenFold3 [@openfold3], AtlasFold [@atlasfold], and BoltzGen [@boltzgen].
Many others provide open weights under permissive or non-commercial licenses
[@boltz1; @protenix_v1; @rosettafold3; @chai1; @esm3]. By contrast, several
prominent studies report wet-lab outcomes while withholding generative
architectures or limiting access to commercial APIs \[@alphaproteo; @latentx1;
@latentx2; @chai2; @boltzprot1\], and private systems such as IsoDDE, SeedFold,
and Chai-3 have no primary publications [@opendde; @bender_perspective]. Because
wet-lab campaigns choose their own targets, assays, and hit cutoffs, claims from
closed systems cannot be independently audited from papers alone
[@bender_perspective].

Reading prediction benchmarks alongside design campaigns also requires
distinguishing external accuracy and physical-validity metrics from model
self-estimates (**Box 1**). Because de novo binders lack experimental structures
before synthesis, computational design pipelines rely on internal confidence
scores and self-consistency RMSD (comparing a designed backbone against a
predicted refolding of its own sequence).

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

Tracing each model family from structure prediction to binder generation shows
how trunk architecture, coordinate formalism, and release choices shape
downstream design workflows (**Table 1**).

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

AlphaFold2 [@alphafold2] introduced the Evoformer trunk, distogram head, and
single-pass differentiable IPA structure module. That end-to-end
differentiability made it useful both as a post-hoc refolding filter
[@rfdiffusion; @alphaproteo] and as a direct substrate for gradient-based
sequence optimization [@bindcraft]. Its main limitation, documented in the
original study, is a marked drop in accuracy when MSA depth shrinks toward
single-sequence inputs [@alphafold2]. AlphaFold-Multimer [@alphafold_multimer],
released as a bioRxiv preprint without peer review, retrained the model on
protein complexes and introduced ipTM and interchain PAE. Complex-design tools
such as BindCraft [@bindcraft], Germinal [@germinal], and mBER [@mber]
backpropagate through AlphaFold-Multimer rather than the monomer model. OpenFold
[@openfold] provided an open retraining of AlphaFold2 along with the structural
distillation dataset later used to train Boltz-1 [@boltz1].

AlphaFold3 [@alphafold3] generalized structure prediction to complexes of
proteins, nucleic acids, small molecules, and ions. It simplified the Evoformer
into a Pairformer trunk and replaced the IPA structure module with an all-atom
diffusion module. Antibody–antigen prediction proved demanding: reported
accuracy required selecting the top-ranked pose across 1,000 random seeds rather
than five, with accuracy still climbing at 1,000 seeds [@alphafold3]. Switching
to multi-step diffusion also precluded simple end-to-end coordinate
backpropagation and introduced physical-validity artifacts. The authors reported
a 4.4% chirality violation rate on PoseBusters even after adding a chirality
ranking penalty, residual steric clashes, and hallucinated structure in
disordered regions (mitigated by cross-distillation from AlphaFold-Multimer
v2.3) [@alphafold3]. Predictions remain static PDB-like structures rather than
conformational ensembles, and shallow MSAs still reduce accuracy [@alphafold3].

Restricted access to AlphaFold3's weights prompted several open reproductions,
including Boltz-1 [@boltz1], Protenix [@protenix_v1], and OpenFold3
[@openfold3]. OpenFold3 distributes Apache-2.0 weights, training code, and its
full training corpus, including a reproduction of AlphaFold3's
13-million-sequence MGnify distillation set, enabling full retraining from
scratch [@openfold3]. Because OpenFold3 is a software release rather than a
peer-reviewed paper, its benchmarks remain self-reported [@openfold3].

## RoseTTAFold, RFdiffusion, and inverse folding

Developed independently of AlphaFold at the Baker Lab and the Institute for
Protein Design, this lineage spans predictors, diffusion generators, inverse
folding, and modality-specific extensions. Two similarly named recent releases
serve opposite purposes: RoseTTAFold3 (RF3) [@rosettafold3] is an all-atom
structure predictor that denoises coordinates for a known sequence, whereas
RFdiffusion3 (RFD3) [@rfdiffusion3] is a generative model that denoises
coordinates with sequence unknown prior to inverse folding.

The predictor branch started with RoseTTAFold (RF1) [@rosettafold], a
three-track (1D, 2D, and 3D) network in which complex prediction emerged through
discontinuous two-segment cropping. Although superseded as a benchmark
predictor, RF1 supplied the weights fine-tuned into RFdiffusion [@rfdiffusion].
RoseTTAFold2 (RF2), an unreviewed preprint, systematically tested AlphaFold2
components and found that FAPE loss, recycling, distillation, and depth drove
accuracy while IPA and triangle attention were unnecessary [@rosettafold2]. RF2
matched AlphaFold2 and AlphaFold-Multimer without either module, scaled more
cleanly past 1,000 residues, and preserved a 3D track suited to spatial design
constraints [@rosettafold2]. Built on RF2, RoseTTAFold All-Atom (RFAA) extended
prediction to non-protein chemistry two months before AlphaFold3
[@rosettafold_all_atom]. RoseTTAFold3 (RF3) later adopted a BSD-licensed
all-atom diffusion architecture that learns stereochemistry from geometric
features rather than inference-time guidance [@rosettafold3]. It predicted 88%
of ligand chiral centers correctly, compared with 84% for AlphaFold3 and 76% for
Boltz-2 without guidance, and reached 1.74 Å mean backbone RMSD on mixed L/D
peptides versus 1.88 Å for AlphaFold3 and 2.24 Å for Boltz-1x [@rosettafold3].
Its authors note that inference-time steering may shift diffusion models outside
their training distribution [@rosettafold3].

On the generative side, RFdiffusion (RFD1) fine-tuned RF1 for equivariant frame
diffusion over Cα positions and N–Cα–C orientations [@rfdiffusion]. It
outperformed earlier RoseTTAFold hallucination and established the standard
workflow of backbone diffusion, ProteinMPNN sequence design, and AlphaFold2
refolding. The authors note that reported in silico success reflects agreement
with AlphaFold2 filters rather than experimental binding [@rfdiffusion].
RFdiffusion2 (RFD2) extended this framework to sequence-agnostic, atom-level
enzyme active-site scaffolding [@rfdiffusion2]. RFdiffusion3 (RFD3) departed
from predictor fine-tuning by pre-training an all-atom transformer U-Net modeled
on AlphaFold3's diffusion module directly on PDB structures and AlphaFold2
distillations [@rfdiffusion3]. Reducing the Pairformer from 48 to 2 layers (168
million trainable parameters) with 100-step sampling makes RFD3 roughly an order
of magnitude faster than earlier versions [@rfdiffusion3].

Because backbone generators output geometry without amino-acid identities,
inverse folding models supply sequences. ProteinMPNN [@proteinmpnn], an
autoregressive message-passing network for fixed backbones, became the field's
default sequence designer across RFdiffusion [@rfdiffusion], RFpeptides
[@rfpeptides], BindCraft [@bindcraft], and PXDesign [@pxdesign]. Its authors
caution that native sequence recovery does not guarantee accurate folding
[@proteinmpnn]. LigandMPNN [@ligandmpnn] adds conditioning on ligands, nucleic
acids, and metals, while AlphaDesign's Autoregressive Diffusion Model (ADM)
[@alphadesign] performs comparably to ProteinMPNN with complementary structural
preferences.

Two modality extensions adapted this stack to antibodies and macrocycles.
RFantibody [@rfantibody] fine-tuned RFdiffusion for epitope-specific VHHs,
scFvs, and antibodies, pairing computational generation with yeast-display
screening (9,000 designs per target) and SPR (95 per target). Confirmed hit
rates remained between 0% and 2%, leading the authors to state that experimental
screening is still necessary [@rfantibody]. RFpeptides [@rfpeptides] added
cyclic relative positional encoding to RFdiffusion and RF2 for head-to-tail
macrocycles, combining ProteinMPNN with AfCycDesign [@afcycdesign] and Rosetta
filtering to obtain crystal-verified binders across four targets from fewer than
20 synthesized designs each. A separate optimizer in this family, RFOptimization
[@rfoptimization], uses RF3 gradients for discrete refinement and is discussed
below.

## Boltz

Boltz-1 [@boltz1] was the first MIT-licensed AF3-class all-atom co-folder.
Trained partly on OpenFold distillation structures [@openfold], it gave external
groups an open platform for downstream design tools such as BoltzDesign1
[@boltzdesign1]. Boltz-1x added Boltz-steering, which applies Feynman-Kac
steering potentials during sampling to reduce chirality violations and steric
clashes [@boltz1]. Boltz-2 [@boltz2] maintained essentially unchanged structure
accuracy while adding expanded conditioning controls and a small-molecule
affinity module. That affinity head reached a mean Pearson correlation of 0.66
on the four-target FEP+ subset at over 1,000-fold lower compute than free-energy
perturbation, with mixed performance on blinded industrial assays [@boltz2].
Because it trains only on single-protein ligand assays, it does not predict
protein–protein binding affinity [@boltz2]. Its June 1, 2023 training cutoff
also excludes it from standard FoldBench comparisons (**Table 2A**)
[@protenix_v1; @protenix_v2; @esmc].

BoltzGen [@boltzgen] introduced an MIT-licensed all-atom diffusion model
(weights, code, and training data) trained jointly for structure prediction and
de novo design. It matched Boltz-2 on Boltz-2's prediction test set while
designing proteins, peptides, and nanobodies against targets ranging from
disordered proteins to small molecules, excluding full antibodies from training
and filtering designs with Boltz-2 refolding [@boltzgen]. Across eight campaigns
covering 26 targets, testing at most 15 designs per target produced nanomolar
binders for 6 of 9 novel targets (\<30% bound PDB identity) in both nanobody and
miniprotein formats (**Table 2B**) [@boltzgen]. It also yielded binders on 4 of
5 established targets, with affinities down to 0.81 nM on PDGFR [@boltzgen]. The
authors disclosed two instructive failure modes. First, diversity collapsed into
ubiquitin at binder lengths of 73–76 residues, reflecting over 900 ubiquitin
entries in the PDB [@boltzgen]. Second, an early `BoltzGenv0` bug mis-assigned
fixed binder residues to the target chain during refolding, dropping hits to 0/7
on two targets where the corrected pipeline achieved 1/7 and 7/7 [@boltzgen].
They emphasize that binder design is not plug-and-play and advise manual
structural inspection and reruns [@boltzgen].

BoltzProt-1 [@boltzprot1] paired a refined BoltzGen generator with BoltzPPI, a
classifier trained directly on experimental binding outcomes. Across 10
low-homology targets using identical candidate pools and 15 designs per target
(150 total), replacing BoltzGen's confidence ranking with BoltzPPI raised
confirmed binders from 3.3% (5/150; 2/10 targets) to 8.0% (12/150; 4/10 targets)
[@boltzprot1]. The study also separated initial screening hits from confirmed
binders validated in follow-up assays [@boltzprot1]. Unlike earlier MIT-licensed
Boltz releases, BoltzProt-1 is offered strictly through a commercial API without
released weights [@boltzprot1].

## Chai

Chai-1 [@chai1] is an AF3-class diffusion co-folder equipped with both an MSA
track and a protein language model track, usable independently or together. It
also supports optional experimental restraints (pocket, contact, or docking)
that provide double-digit accuracy gains when supplied [@chai1]. On
antibody–protein interfaces, single-sequence Chai-1 matched MSA-enabled Chai-1,
and both outperformed AlphaFold-Multimer v2.3 with MSAs, which the authors
attribute to weak evolutionary signal in antibodies [@chai1]. Model weights
carry a non-commercial license (with commercial use through a web server), and
licensing restrictions prevented benchmarking against AlphaFold3 or ESM-3
[@chai1].

Chai-2 [@chai2] built on Chai-1 (via an intermediate `Chai-1d` prototype) for
zero-shot scFv, VHH, and minibinder design without display screening or affinity
maturation. Testing at most 20 designs per target and format across 52 novel
targets produced a 16% combined antibody hit rate, finding binders for half of
the targets (**Table 2B**) [@chai2]. Across five minibinder targets, hit rates
reached 68%, with affinities down to 18.3 pM on IL-7Rα [@chai2]. The paper
describes only the folding submodule (`Chai-2f`, similar in architecture to
Chai-1) and leaves the generative architecture undisclosed [@chai2]. A
commercial successor, Chai-3 (2026), runs on Chai Discovery's web platform
without a publication.

## Gradient-based design by backpropagation

Gradient-based methods invert a pretrained structure predictor, iteratively
updating a candidate sequence so the predicted complex satisfies structural
confidence or contact losses. These pipelines differ along three design choices:
whether gradients flow through coordinates or stop at trunk distograms and
confidence heads, whether sequences are relaxed continuously or mutated
discretely, and whether a language-model prior is added as a live gradient or a
static bias.

Because AlphaFold2's IPA module produces coordinates in a single differentiable
pass, gradients propagate all the way back to the input sequence [@alphafold2].
ColabDesign provides the open-source AlphaFold2 backpropagation library and
three-stage annealing schedule (`design_3stage`) used by AfCycDesign, BindCraft,
Germinal, and mBER [@colabdesign]. AfCycDesign modifies AlphaFold2's relative
positional encoding to be cyclic on the peptide chain, yielding eight monomeric
macrocycle crystal structures within 1.0 Å of design models [@afcycdesign]. Its
MDM2 and Keap1 binders, however, were made by grafting known binding motifs onto
hallucinated scaffolds before ProteinMPNN and Rosetta redesign rather than
hallucinating binders directly [@afcycdesign]. BindCraft backpropagates
confidence losses through AlphaFold-Multimer into an *L* × 20 sequence matrix
[@bindcraft]. It swaps randomly among the five trained weight sets to prevent
overfitting and repredicts the target at every step so the target backbone and
side chains adapt to the binder (0.5–5.5 Å target Cα RMSD) [@bindcraft]. A
four-stage schedule anneals logits through softmax, straight-through estimation,
and discrete mutation search, followed by ProteinMPNN surface redesign and
AlphaFold2 and Rosetta filtering [@bindcraft]. Across 12 targets, BindCraft
achieved 10–100% hit rates (mean 46.3%), though the authors note that
single-sequence inversion leaves AlphaFold2's MSA training regime and that ipTM
predicts binding rather than affinity [@alphafold2; @bindcraft]. A code release,
BindCraft2, extends this loop to cyclic peptides, antibodies, repeats,
disordered motifs, and molecular glues without published benchmarks yet.

Diffusion-based predictors require a different gradient path because unrolling
hundreds of denoising steps is impractical. BoltzDesign1 adapts BindCraft's
continuous schedule to Boltz-1 (adding a softmax warm-up), places a
stop-gradient on the diffusion module, and optimizes contact losses over the
64-bin Pairformer distogram, adding the confidence head for nucleic-acid targets
and optional LigandMPNN surface redesign [@boltzdesign1; @boltz1; @ligandmpnn].
RFOptimization takes a different approach to both the task and the sequence
representation: it refines existing designs strictly in discrete sequence space
to avoid continuous-relaxation artifacts [@rfoptimization]. Using negative
normalized gradients from RoseTTAFold3's distogram and confidence heads, it
proposes single-point substitutions accepted via annealed Metropolis–Hastings
[@rfoptimization; @rosettafold3]. On half of its steps, it instead cycles
through Boltz folding and LigandMPNN resampling while holding AlphaFold3 out as
an independent check [@rfoptimization]. Under AF3 refolding (iPAE < 2.5, ipTM >
0.8), this lifted in-silico success from 6.73% to 22.31% on protein–protein
interfaces, from 1.25% to 12.57% on cyclic peptides, and from 5.62% to 24.91% on
small-molecule binders [@rfoptimization]. Both BoltzDesign1 and RFOptimization
are evaluated in silico only [@boltzdesign1; @rfoptimization].

To keep designed antibody sequences realistic, Germinal and mBER pair
AlphaFold-Multimer with language-model priors in contrasting ways. Germinal
designs CDR loops on a CDR-masked framework template by merging live
AlphaFold-Multimer and IgLM gradients through a weighted sum, MGDA, or PCGrad
[@germinal]. AlphaFold-Multimer reads a continuous position-specific scoring
matrix while IgLM receives straight-through discrete tokens, followed by
semigreedy steps and AbMPNN redesign [@germinal]. Nonbinders cleared the same
ipSAE threshold as binders, and dependence on AlphaFold3-predicted antigen
accuracy remains an open question [@germinal]. OpenGerminal reimplements this
workflow under Apache-2.0 with open scoring and AbLang1 [@opengerminal]. By
contrast, mBER runs ESM-2 once over a NanoBodyBuilder2-templated VHH framework
(templated separately from the target hotspot, without MSAs) and adds the
resulting logits as a fixed bias throughout `design_3stage` [@mber]. Ablations
confirm that both template and sequence prior are required. In its
randomized-hotspot phage-display sweep (**Table 2B**), hit rates on a single
target varied from 0.4% overall to 7.5% at the best hotspot, without affinity
measurement [@mber]. A follow-up company technical report, mBER-2, extends the
approach to microbinders at roughly tenfold higher hit rates without specifying
whether hotspots were randomized.

## Protenix

ByteDance Seed's Protenix platform pairs open-weights co-folding with dual-mode
binder design, antibody generation, and open benchmarking. Protenix-v1
reproduces AlphaFold3 under open weights [@protenix_v1]. Under matched training
cutoff, scale, and inference budget, it leads AlphaFold3 on protein–protein and
antibody–antigen interfaces and trails on protein–ligand and protein–DNA
complexes, while its recommended `Protenix-v1-20250630` checkpoint trains past
that strict cutoff [@protenix_v1]. Its authors also documented log-linear
accuracy scaling with random seeds and showed how unequal failure subsets
distort FoldBench rankings (**Table 2A**) [@protenix_v1; @foldbench]. Built on
Protenix, PXDesign ships two modes in one framework: PXDesign-d generates
Cartesian coordinates with a Diffusion Transformer (DiT), whereas PXDesign-h
replaces the 200-step diffusion decoder with a 2-step ODE sampler so gradients
run end-to-end across five resampled Protenix models [@pxdesign]. All six
wet-lab campaigns used PXDesign-d, yielding 20–73% nanomolar hit rates on 5 of 6
targets (0/16 on TNFα). Filtering experiments showed that Protenix and AF2-IG
retain largely distinct true positives and that optimal confidence thresholds
vary by target [@pxdesign].

Protenix-v2 improves antibody–antigen DockQ > 0.23 success by 9–13 percentage
points over Protenix-v1 across PXMeter-AB, FoldBench-AB, and AF3-AB, with 5
seeds surpassing Protenix-v1 at 1,000 seeds [@protenix_v2]. Extending generation
to VHH, Fv, and full mAbs, it yielded BLI-confirmed binders for every antigen on
a novelty-controlled soluble panel (2–48% hit rates) and achieved 16–88% VHH-Fc
and 0–50% mAb hit rates across four GPCRs using 16–30 designs per target
[@protenix_v2]. Two epitopes on the same antigen (AMBP) produced 4% versus 48%
hit rates, prompting prioritization of native ligand-binding interfaces
[@protenix_v2]. Caveats include manual epitope choice on in-stock targets and
the lack of a direct Chai-2 comparison due to format differences [@protenix_v2].
ByteDance Seed's open PXMeter benchmark toolkit [@pxmeter] added sp2-, amide-,
and sp3-planarity checks in v1.1.0 (introduced with Protenix-v2 and adopted as
PXMeter-AB by OpenDDE) after noting twisted amides and flat sp3 centers passing
PoseBusters [@protenix_v2; @opendde; @posebusters].

## ESM

The ESM lineage replaces inference-time MSA retrieval with protein language
models trained on billions of sequences. ESM-2 and ESMFold showed that a masked
language model paired with a folding trunk and IPA module can predict 3D
structures from single sequences without MSAs or templates, trading lower
accuracy than AlphaFold2 for high-speed folding across the ESM Metagenomic Atlas
[@esm2]. ESM-3 scaled to a multimodal discrete-token transformer (1.4B, 7B, and
98B parameters over 2.78 billion proteins) spanning sequence, structure, and
function [@esm3]. At 98B parameters it outperformed ESMFold on CAMEO
single-sequence prediction (0.880 vs. 0.861 lDDT) and generated functional
`esmGFP` at 58% sequence identity to natural fluorescent proteins; `ESM3-open`
(1.4B) is academic-only while the 98B model is API-only [@esm3].

ESMC and ESMFold2 extend single-sequence language modeling to all-atom complexes
and binder design [@esmc]. Frozen 6B-parameter ESMC representations (~2.8
billion sequences) feed 48 recurrent pair-state folding layers (24 in
ESMFold2-Fast) and a sliding-window diffusion transformer, with an optional
detachable MSA encoder for high-perplexity sequences [@esmc]. Single-sequence
ESMFold2 matches MSA-enabled AlphaFold3 on antibody–antigen interfaces within
error bars across independent AtlasFold evaluations [@esmc; @atlasfold]. Because
single-sequence input is native to the model, binder design backpropagates
directly through ESMC and the folding trunk's distogram for 150 single-stage
steps across two replicates [@esmc]. The diffusion and confidence heads run only
in the final steps to rank candidates by ensemble ipTM or a distogram-entropy
proxy, alongside an isoelectric-point filter (pI ≤ 6.0) for minibinders [@esmc].
Testing 84 designs per cohort across five author-selected targets gave mean hit
rates of 70.0% for minibinders (best 68 pM) and 21.0% for scFvs (**Table 2B**)
[@esmc]. Independently, AtlasFold released a fully open MIT-licensed
single-sequence PLM folder (weights, code, data, and checkpoints) alongside a
seven-model FoldBench rank-versus-oracle evaluation [@atlasfold].

## Closed and undisclosed systems

Several binder-design platforms report wet-lab results while withholding
generative architectures or weights. Google DeepMind's AlphaProteo reported
9–88% minibinder hit rates across eight targets (0/54 on TNFα; best 82 pM on
IL-7Rα) and re-assayed RFdiffusion designs by yeast display (**Table 2B**)
[@alphaproteo]. It discloses its AF2 filter (`interchain PAE < 10`,
`RMSD < 1 Å`, `pLDDT > 80`) while describing the generator only as trained on
PDB and AlphaFold distillations [@alphaproteo]. Latent Labs' Latent-X1 and
Latent-X2 likewise cite a proprietary all-atom architecture filtered by ipTM,
PAE, and self-consistency [@latentx1; @latentx2]. Latent-X1 ran minibinder and
macrocycle campaigns and resynthesized RFpeptides' two best binders for affinity
comparison (**Table 2B**) [@latentx1; @rfpeptides]. Latent-X2 reported
macrocycle and VHH/scFv binders alongside drug-like developability and low
immunogenicity [@latentx2]. Within their own lineages, Chai-2 withholds its
generator beyond `Chai-2f` [@chai2], and BoltzProt-1 restricts access to a
commercial API [@boltzprot1].

Other models lack primary publications altogether and appear only via web
platforms or third-party benchmarks. OpenDDE, an Apache-2.0 co-folder built on
Protenix-v1 and OpenFold3, triples Pairformer hidden width from 128 to 384 (~3×
parameters, ~9× compute), adds an atom-level refiner before diffusion, and lists
joint design on its roadmap [@opendde]. Beyond its own antibody–antigen
comparisons, OpenDDE supplies the only public scaling-curve points for
unpublished IsoDDE (also noted as lacking public verification by Bender et al.
[@bender_perspective]) and SeedFold [@opendde], alongside the commercial
platform Chai-3.

# Quantitative Landscape and Evaluation Pitfalls

Interpreting structure-prediction and binder-design benchmarks requires reading
every score alongside its evaluation protocol. On the common target intersection
of FoldBench (1,522 assemblies across nine tasks), monomer accuracy across seven
AF3-class predictors sits in a tight 0.85–0.89 lDDT band and general
protein–protein DockQ success spans roughly 7 percentage points (65.4–72.7%)
[@foldbench; @protenix_v1]. Antibody–antigen accuracy, by contrast, spans more
than a factor of two, from 23.1% to 52.3% (**Table 2A**) [@protenix_v1].
Training cutoffs further restrict direct comparisons: Boltz-2 is excluded from
FoldBench common-intersection tables because its 2023-06-01 cutoff overlaps the
2023-01-13 to 2024-11-01 benchmark window \[@boltz2; @protenix_v1; @protenix_v2;
@esmc\].

Identical metric names also shift when target filters, averaging units, or MSA
pipelines change. Because models fail on different inputs (out-of-memory errors,
unsupported glycans, or token limits), restricting FoldBench protein–protein
pairs to the common completed set ($n = 237$) reverses Boltz-1 (68.4% vs. 68.3%
published) and Chai-1 (67.5% vs. 68.5% published) [@protenix_v1]. AlphaFold3's
FoldBench antibody–antigen score varies more modestly across unfiltered
(47.90%), intersection-filtered (48.75%), and independently re-run (48.8%)
evaluations [@foldbench; @protenix_v1; @opendde]. Averaging conventions create
far larger gaps. Chai-1 reports 52.9% antibody DockQ success over 40%-identity
interface clusters [@chai1], whereas FoldBench evaluates per interface and
obtains 25.2% for the same model [@foldbench]. Boltz-1 uses a third rule,
averaging per interface within each complex before averaging across complexes
[@boltz1], while external FoldBench runs of OpenFold3 moved from 70.79% to
69.29% under a different MSA pipeline [@openfold3; @protenix_v2].

A distinct bottleneck separates generating a near-native complex from
recognizing it with internal confidence scores. Across seven predictors
evaluated template-free by AtlasFold (**Table 2A**), selecting the top sample by
confidence loses 11–21 percentage points relative to oracle selection against
the experimental structure on antibody–antigen interfaces (4.5 points for
Boltz-1) and 3–8 points on protein–protein interfaces [@atlasfold]. FoldBench
similarly found that a near-native CDR-H3 loop is necessary but not sufficient
for accurate docking because confidence scores do not reliably pick near-native
poses [@foldbench]. This ranking gap motivates large seed budgets: AlphaFold3
ranked antibody poses over 1,000 seeds [@alphafold3], Protenix-v1 climbed from
36.01% (1 seed) to 47.68% (80 seeds) [@protenix_v1], and OpenDDE reported oracle
antibody–antigen success rising from ~66% to >90% at several hundred seeds
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
validation rigor (**Table 2B**) brings four confounders into view. First,
several headline affinities reflect bivalent Fc fusions or avidity rather than
monovalent binding, including Protenix-v2's VHH-Fc constructs (except VEGF-A)
[@protenix_v2], four of Chai-2's ten miniproteins plus its EFNA5 scFv [@chai2],
and BindCraft's PD-1 Fc construct [@bindcraft]. Second, synthesis and expression
attrition alters denominators, as documented in RFpeptides [@rfpeptides],
Latent-X1 macrocycles [@latentx1], and PXDesign's PD-L1 campaign (72.7% of
tested designs vs. 47.1% sent for expression) [@pxdesign]. Third, some papers
highlight target-level coverage (BoltzGen, Protenix-v2, Latent-X2 \[@boltzgen;
@protenix_v2; @latentx2\]) while others report per-design hit rates (Chai-2,
PXDesign, BindCraft, ESMFold2 [@chai2; @pxdesign; @bindcraft; @esmc]). Fourth,
operational binding criteria range from unthresholded SPR signals \[@bindcraft;
@rfpeptides; @latentx1\] and BLI cutoffs spanning 0.05 to 0.4 nm \[@protenix_v2;
@pxdesign; @chai2; @esmc; @latentx2\] to BoltzProt-1's split between initial
screening hits and confirmed binders [@boltzprot1].

Three cross-lab resynthesis experiments illustrate how strongly assay conditions
move reported outcomes. When AlphaProteo re-tested RFdiffusion's designs by
yeast display at 10–20× lower target concentrations, hit rates dropped from 33%
to 16% on IL-7Rα and from 6% to 0% on TrkA [@alphaproteo; @rfdiffusion]. When
Latent-X1 resynthesized RFpeptides' two best macrocycles, measured affinities
were 4.4× and 5× weaker than published, with Latent-X1 leading on MDM2 and
trailing on MCL-1 [@latentx1; @rfpeptides]. Latent-X2 likewise re-assayed two
RaPID macrocycles under a different cyclization chemistry than its own designs
[@latentx2]. **Table 2B** therefore documents each campaign within its own
experimental regime rather than on a common scale.

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

Most binder-design papers motivate their work through therapeutic development.
Authors cite automated drug discovery [@boltzgen], species cross-reactivity
[@chai2], reduced IgE binding in patient samples [@bindcraft], antibody
developability [@latentx2], and protein therapeutics [@mber]. Auditing a decade
of artificial intelligence in pharmaceutical R&D, Bender et al. find clear
technological progress alongside limited evidence of clinical impact so far
[@bender_perspective]. They distinguish *model validation* (accuracy on held-out
benchmarks or isolated in vitro binding assays) from *process validation*
(improving downstream clinical decisions), noting that AlphaFold exemplifies
model validation for folding rather than process validation for drug discovery
[@bender_perspective].

Biologics have aided recent clinical approval gains through higher average
success rates and stronger intellectual-property protection than small
molecules. Even so, Bender et al. observe (citing RFdiffusion, ProteinMPNN,
BoltzGen, and Chai-2) that binding remains easier to predict than functional
activity and developability [@bender_perspective]. That gap parallels
small-molecule discovery, where ChEMBL and PubChem catalog over $10^6$ bioactive
ligands versus roughly $10^3$ marketed drugs [@bender_perspective]. They also
highlight the need to match metrics to the decision task (selection,
deselection, or quantification), to account for local generalization outside
training distributions, and to preserve independent verifiability. Open
co-folding models have largely caught up with closed alternatives, whereas
proprietary systems such as IsoDDE disclose too little detail for external
verification [@bender_perspective]. Because that Perspective draws mainly on
small-molecule and clinical pipeline evidence (relying on a single preprint,
FLAb2, for biologic developability), it serves as translational context rather
than a direct audit of protein design [@bender_perspective].

## Open technical and methodological limitations

Five technical and methodological limitations recur across current binder-design
pipelines. First, nearly all open systems generate, filter, and report solely on
binding. Latent-X2 notes that therapeutic campaigns often fail not for lack of
binding, but because clinical success requires developability and low
immunogenicity [@latentx2]. Although Latent-X2 reports those properties for
designed antibodies, its generative architecture remains undisclosed
[@latentx2].

Second, current scoring functions act mainly as binary binding indicators rather
than quantitative affinity estimators. BindCraft notes that AlphaFold2 ipTM
predicts whether a design binds rather than its $K_D$ [@bindcraft]. Boltz-2's
affinity head predicts small-molecule binding on single-protein targets rather
than multimeric protein–protein interfaces [@boltz2], leaving binding strength
to wet-lab measurement. Third, most published campaigns condition on
experimentally solved or high-confidence predicted structures. Germinal notes
that how strongly design success depends on predicted antigen-model quality
remains an open question [@germinal].

Fourth, no shared, blinded prospective benchmark exists for de novo binder
design. Independent replication of a full published campaign has occurred only
once, when AlphaProteo re-tested RFdiffusion's published designs (including
nonbinders) by yeast display [@alphaproteo; @rfdiffusion]. The closest
prospective standard is the AIntibody challenge, which independently assayed 511
IgG antibodies from 29 organizations across three tasks using high-throughput
SPR (HT-SPR), kinetic exclusion assays (KinExA), and a five-assay developability
panel [@aintibody]. The top computational design (95 pM) matched the best
wet-lab antibody (113 pM), and Challenge 1 was won by an open-code
Protenix-derived pairformer with a direct preference optimization (DPO) fitness
head, yet a non-ML consensus ranked third [@aintibody]. On Challenge 2
(within-HCDR3-cluster affinity ranking), only 1 of 26 groups outperformed random
selection. On the out-of-library task, 30.4% of designs failed to bind and the
highest-affinity winner (2.9 pM) failed to elute from the hydrophobic
interaction chromatography (HIC) column [@aintibody]. AIntibody also carries
clear scope limits. It tested a single well-characterized antigen (SARS-CoV-2
RBD, described as "deliberately primed for success") and captures a Q1 2025
snapshot missing several prominent de novo groups [@aintibody]. Its tasks also
evaluated library-conditioned engineering with provided affinities rather than
de novo binder design [@aintibody].

Fifth, structure-prediction confidence scores remain unreliable for per-design
discrimination. Metrics such as ipTM and ipSAE enrich hit rates across large
pools, as seen at million-design scale in mBER [@mber], yet frequently fail on
individual candidates, as seen in Germinal where nonbinders cleared the same
ipSAE cutoff as binders [@germinal]. Re-scoring 3,766 tested designs from six
campaigns across 15 targets under one pipeline, Overath et al. found AlphaFold3
ipSAE to be the strongest single predictor overall, yet its average precision
ranged from 0.1 to 1.0 depending on the target [@overath_meta]. Uniform
re-scoring also leaves heterogeneous source assays unchanged and reflects
earlier-generation designs rather than the newest 2025–2026 models
[@overath_meta].

Current co-folding and generative models can produce epitope-targeted protein
and peptide binders across multiple structural formats while often testing tens
rather than thousands or millions of sequences per target. Quantitative
protein–protein affinity prediction, joint control of functional activity,
developability, and immunogenicity in inspectable architectures, reliable
per-design filtering on structurally uncharacterized targets, and comparative
evaluation under shared blinded benchmarks remain to be demonstrated.
