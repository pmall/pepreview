# De Novo Binder Design with Co-Folding and Generative Models

## Abstract

Designing new molecules that bind a chosen target protein selectively is a
central challenge in therapeutics, diagnostics, and molecular biology. General
co-folding and generative models now address this task across amino-acid-based
modalities, including de novo minibinders, macrocyclic peptides, single-domain
nanobodies, single-chain variable fragments, and full antibodies, which can
engage broad, flat protein surfaces. Historically, discovering such binders
required animal immunization or screening display libraries containing $10^{12}$
or more random sequences. Those workflows must be repeated for each target and
are difficult to direct toward a chosen epitope. Recent advances in
deep-learning structure prediction and biomolecular co-folding have enabled
computational pipelines that propose candidate binder sequences directly for a
specified target and binding site. We focus on general structure-based platforms
for amino-acid chains built from the 20-letter alphabet, setting aside
small-molecule generation over variable chemical graphs and specialized
antibody-only sequence models. Modern co-folding architectures differ along two
primary axes. First, evolutionary information enters through multiple sequence
alignments, protein language models, or hybrid tracks. Second, three-dimensional
atomic coordinates are produced via single-pass regression, iterative diffusion,
or flow matching. Building on these predictors, binder-design pipelines operate
as joint or fine-tuned predictor-generators, generate-and-filter workflows
paired with inverse folding, or gradient-based sequence optimizers. Finally, we
examine how experimental conditions shape reported wet-lab hit rates and review
five open limitations: protein–protein binding affinity prediction,
developability and immunogenicity, targets without experimental structures,
blinded prospective benchmarks, and the per-design discrimination limits of
confidence filters.

# Introduction and Conceptual Background

## From experimental search to computational binder design

Binding a target protein selectively is the basis for blocking, detecting,
tagging, or modulating biological activity. Unlike small-molecule drugs that
usually require buried binding pockets, amino-acid-based binders can recognize
broad, relatively flat protein surfaces. Historically, discovering such
molecules has relied on experimental search rather than rational design.
Laboratories immunize animals or screen phage and yeast display libraries
containing $10^{12}$ or more random sequences. Those methods remain standard,
yet they require wet-lab screening per target and usually recover binders
against immunogenic or accessible regions rather than a chosen epitope
[@rfantibody].

Computational de novo binder design aims to propose candidate sequences directly
for a chosen target protein and binding site. Modern co-folding and generative
platforms tackle three main structural regimes, each drawn from the
20-amino-acid alphabet and evaluated by how it folds against the target. De novo
minibinders are compact scaffolds invented from scratch without a fixed
framework, and they provided the earliest high-hit-rate wet-lab demonstrations
of diffusion and gradient-based design. Macrocyclic peptides are short chains
closed head-to-tail, requiring cyclic positional encodings and careful
stereochemical modeling. Antibodies and single-domain nanobodies (VHHs, scFvs,
and full monoclonal antibodies) combine conserved immunoglobulin frameworks with
hypervariable complementarity-determining region (CDR) loops, especially
flexible CDR-H3 loops that lack strong evolutionary co-variation and remain the
hardest test case for co-folding predictors. Small-molecule ligand generation
over variable chemical graphs, as well as specialized antibody-only sequence
models outside the co-folding paradigm, fall outside our scope. Across de novo
binder design, one practical indicator of recent progress is the experimental
testing budget needed per target. The number of candidates synthesized and
assayed to identify binders has fallen from thousands or millions in display
libraries and early computational pipelines [@chai2; @rfantibody] to tens of
designs in recent generative campaigns \[@chai2; @rfpeptides; @boltzgen;
@protenix_v2\].

This shift became practical once deep-learning structure prediction reached
experimental accuracy. AlphaFold2 solved single-chain structure prediction at
CASP14 [@alphafold2], and AlphaFold3 extended prediction to complexes of
proteins, nucleic acids, small-molecule ligands, and ions [@alphafold3].
Designing a binder, however, differs fundamentally from predicting a fold. A
structure predictor maps an existing sequence to its three-dimensional
coordinates and can be checked directly against an experimental structure. A
binder generator must invent a new sequence from $20^L$ possibilities for a
chain of length *L*, and functional binding can only be confirmed in a wet lab.

## How co-folding structure predictors work

Modern structure prediction rests on an evolutionary principle: pairs of
positions that coevolve across a multiple sequence alignment (MSA) usually lie
close together in the folded three-dimensional structure. AlphaFold2 used this
signal at CASP14 to achieve a median backbone error of 0.96 Å r.m.s.d.95 (Cα
root-mean-square deviation across 95% of residues; 95% CI 0.85–1.16 Å), compared
with 2.8 Å for the next best method [@alphafold2]. AlphaFold3 extended the
framework from single protein chains to multi-molecule complexes, a task widely
termed co-folding [@alphafold3].

Most modern co-folding models use a two-stage architecture. Earlier RoseTTAFold
versions (RF1 and RF2) instead ran a parallel three-track network that updated
1D sequence, 2D pairwise, and 3D coordinate representations simultaneously from
input to output [@rosettafold; @rosettafold2]. In the two-stage design, a
differentiable **trunk** first maps sequence and evolutionary inputs into
single-residue and pairwise representations. This trunk is called the Evoformer
in AlphaFold2 [@alphafold2], the Pairformer in AlphaFold3, Boltz, Chai,
Protenix, and RoseTTAFold3 \[@alphafold3; @boltz1; @chai1; @protenix_v1;
@rosettafold3\], and the folding trunk in ESMFold and ESMFold2 [@esm2; @esmc]. A
linear head on the pair representation predicts a **distogram**, which outputs a
probability distribution over inter-residue distances for every residue pair
[@alphafold2; @boltzdesign1; @esmc]. Evolutionary information enters the trunk
through three distinct mechanisms. MSA-based models retrieve homologous
sequences from databases at inference time, as in AlphaFold, Boltz, Protenix,
and RoseTTAFold \[@alphafold2; @alphafold3; @boltz1; @protenix_v1;
@rosettafold3\]. Protein language model (PLM) predictors instead encode
evolutionary statistics in pre-trained weights for single-sequence inference
(ESMFold, ESMFold2, and AtlasFold [@esm2; @esmc; @atlasfold]), whereas Chai-1
combines both tracks in a hybrid design [@chai1].

The second stage translates trunk representations into explicit 3D atomic
coordinates, and its formulation governs both speed and differentiability.
AlphaFold2 and ESMFold use single-pass coordinate regression through an
end-to-end differentiable structure module based on Invariant Point Attention
(IPA) [@alphafold2; @esm2]. Removing those end-to-end structure gradients lowers
prediction accuracy in AlphaFold2 [@alphafold2]. AlphaFold3 and other AF3-class
co-folders replace IPA with an iterative **diffusion** module adapted from image
generation that denoises Gaussian coordinate noise along a stochastic
differential equation (SDE) trajectory \[@alphafold3; @boltz1; @chai1;
@protenix_v1; @rosettafold3; @esmc\]. Producing high-quality samples with
diffusion can require hundreds or roughly 1,000 forward passes [@frameflow]. A
related family based on **flow matching** recasts coordinate generation as an
ordinary differential equation (ODE) with straighter trajectories and fewer
inference steps. FrameFlow demonstrated this approach on monomers [@frameflow],
and PPIFlow [@ppiflow], OriginFlow [@originflow], AtomFlow [@atomflow], and
D-Flow [@dflow] extended it to target-conditioned binders. Unlike image
generation, which lacks an objective structural correctness metric and relies on
human judgment, protein coordinate generators can be scored automatically by
structure predictors.

## Three ways structure predictors drive binder design

Structure prediction and binder design can run on the same underlying neural
network simply by changing which inputs are held fixed. Supplying all chain
sequences predicts the complex structure, whereas leaving one chain unspecified
or noised asks the network to generate a binder that folds against the target
[@boltzgen; @rfdiffusion]. Across the field, binder-design pipelines connect
structure predictors to sequence and structure generation through three main
workflows (**Figure 1**): joint or fine-tuned predictor-generators,
generate-and-filter pipelines, and gradient-based sequence optimization.

**Figure 1. Co-folding architectures and binder-design workflows.** **(A)**
Two-stage co-folding architecture. Sequence and evolutionary context enter via
database-retrieved multiple sequence alignments (MSAs), pre-trained protein
language models (PLMs), or hybrid tracks into a differentiable trunk (Evoformer,
Pairformer, or folding trunk) that produces single-residue representations,
pairwise representations, and a distogram. A coordinate stage then generates 3D
atomic positions through single-pass Invariant Point Attention (IPA) regression,
iterative stochastic differential equation (SDE) diffusion, or ordinary
differential equation (ODE) flow matching. **(B)** Three workflows connecting
structure predictors to binder design: (1) joint or fine-tuned
predictor-generators that denoise unspecified binder chains directly against a
fixed target; (2) generate-and-filter pipelines pairing backbone generation with
inverse folding and ranking by confidence thresholds or trained binding
classifiers; and (3) gradient-based sequence optimization updating a continuous
*L* × 20 sequence relaxation (or discrete point mutations) via gradients from
IPA modules, trunk distogram and confidence heads, or short ODE samplers.
*Illustrator specification (remove prior to submission): Clean two-panel
horizontal schematic using muted, colorblind-safe palettes. Use solid dark
arrows for forward inference passes and dashed contrasting arrows for gradient
backpropagation. Clearly separate fixed target inputs from generated or
optimized binder variables in Panel B, and mark the single-sequence input
constraint on the gradient-optimization path.*

In **joint or fine-tuned predictor-generators**, a structure predictor's weights
are adapted directly to denoise binder geometry against a fixed target.
RFdiffusion and RFdiffusion2 fine-tune RoseTTAFold weights for backbone and
active-site denoising [@rfdiffusion; @rfdiffusion2], whereas BoltzGen trains a
single all-atom diffusion network jointly for both prediction and design
[@boltzgen]. In **generate-and-filter pipelines**, geometry generation runs
without design-time gradients. These workflows generate candidate backbones and
assign sequences with an inverse-folding model such as ProteinMPNN
[@proteinmpnn]. A separate scoring step then ranks designs using refolding
confidence thresholds (for instance, interchain PAE < 10 Å, binder-aligned RMSD
< 1 Å, and pLDDT > 80 in AlphaProteo [@alphaproteo]). Alternatively, BoltzPPI
replaces confidence thresholds with a classifier trained directly on
experimental binding outcomes [@boltzprot1]. In **gradient-based sequence
optimization** (often called hallucination or backpropagation design), a binder
sequence is relaxed into a continuous *L* × 20 probability matrix over the 20
amino acids. A differentiable predictor evaluates that matrix and updates it
along confidence or distogram gradients while annealing toward discrete one-hot
sequences [@bindcraft; @germinal; @boltzdesign1; @pxdesign; @esmc]. One variant,
RFOptimization, keeps sequences strictly discrete and uses predictor gradients
only to rank single-point mutations [@rfoptimization].

Three practical engineering constraints shape how these workflows behave. First,
gradient-based optimization requires single-sequence evaluation of the designed
chain because MSA database lookups are non-differentiable and undefined for
sequences being invented. Single-sequence input is the documented weakest
accuracy regime for MSA-trained models such as AlphaFold2, which BindCraft
inverts [@alphafold2; @bindcraft]. By contrast, natively single-sequence PLMs
such as ESMC/ESMFold2 remain within their training distribution during
backpropagation [@esmc]. Second, while AlphaFold2's IPA module is differentiable
in a single pass, unrolling hundreds or roughly 1,000 denoising steps to
backpropagate through an AF3-class diffusion module is computationally
impractical [@frameflow; @boltzdesign1]. Designers bypass that bottleneck either
by taking gradients from trunk distogram and confidence heads without
differentiating through diffusion (BoltzDesign1 [@boltzdesign1], RFOptimization
[@rfoptimization], and ESMFold2 [@esmc]) or by substituting a differentiable
2-step ODE sampler (PXDesign-h [@pxdesign]).

Third, post-generation filtering strongly affects wet-lab yield independently of
the generator. Keeping the BoltzGen candidate pool fixed and replacing
confidence thresholds with the trained BoltzPPI classifier more than doubled
confirmed binders, from 3.3% to 8.0% [@boltzprot1]. Similarly, PXDesign reported
that Protenix and AlphaFold2-Initial-Guess (AF2-IG) filters retain largely
non-overlapping sets of experimentally verified binders [@pxdesign]. To limit
overfitting to one predictor's biases, RFOptimization mixes RoseTTAFold3 and
Boltz gradients inside the optimization loop while holding out AlphaFold3 as an
independent check [@rfoptimization].

## Core evaluation metrics

Evaluation metrics separate external checks against experimental coordinates or
physical chemistry from internal scores estimated by the model itself. **lDDT**
(Local Distance Difference Test) measures local interatomic distance accuracy
without global superposition, so a correctly folded domain in the wrong
orientation still scores highly [@lddt]. **TM-score** measures length-normalized
global fold similarity [@tm_score], and **RMSD** computes atomic deviation in
ångströms after optimal superposition [@kabsch]. In design pipelines without
experimental structures, self-consistency RMSD compares a generated backbone to
a predicted refolding of its own sequence. **DockQ** scores protein–protein
interface accuracy from 0 to 1, with DockQ ≥ 0.23 commonly marking an acceptable
interface [@dockq]. **PoseBusters (PB-valid)** applies pass/fail
physical-chemistry checks for chemical validity, bond geometry, chirality,
steric clashes, and internal energy [@posebusters].

Because de novo binders lack experimental structures before synthesis, pipelines
rely on model self-estimates to rank candidates. AlphaFold2 introduced three
empirically calibrated scores: per-residue predicted lDDT (**pLDDT**, 0–100),
predicted global TM-score (**pTM**), and **Predicted Aligned Error (PAE)**, a
residue-pair matrix estimating positional error in ångströms [@alphafold2].
AlphaFold-Multimer restricted these scores to interchain pairs, defining
interface predicted TM-score (**ipTM**) and interchain PAE (**iPAE**, often
thresholded below 10 Å in design filters) [@alphafold_multimer; @alphaproteo].
To remove sensitivity to disordered tails and chain trimming, **ipSAE** computes
ipTM only over well-predicted interchain pairs below a PAE cutoff such as 10 or
15 Å [@ipsae].

# Approaches and Representative Systems

Modern de novo binder design draws on five broad families of methods: all-atom
co-folding predictors, structure diffusion and inverse folding pipelines,
gradient-based sequence optimizers, protein language models, and proprietary
design platforms. **Table 1** compares twelve representative systems across
these approaches, summarizing their evolutionary inputs, coordinate-generation
modules, core mechanisms, and openness.

**Table 1. Representative structure predictors and binder-design systems.**

| System / Archetype                                                                                                 | Primary Role                                   | Evolutionary Input                               | Coordinate Stage                                                       | Key Mechanism & Modalities                                                                                                                            | Openness                                                                   |
| ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| AlphaFold2 / AF-Multimer [@alphafold2; @alphafold_multimer]                                                        | Monomer & complex prediction; refolding filter | MSA                                              | Single-pass IPA regression                                             | Evoformer trunk; differentiable coordinates; ipTM and iPAE interface metrics                                                                          | Open weights; open-source retraining (OpenFold [@openfold])                |
| AlphaFold3 & OpenFold3 [@alphafold3; @openfold3]                                                                   | All-atom co-folding prediction                 | MSA                                              | All-atom SDE diffusion                                                 | Pairformer trunk; proteins, nucleic acids, ligands, ions; multi-seed antibody sampling                                                                | Restricted weights (AF3); Apache-2.0 weights, code, and corpus (OpenFold3) |
| RoseTTAFold3 (RF3) [@rosettafold3]                                                                                 | All-atom co-folding prediction                 | MSA                                              | All-atom SDE diffusion                                                 | Learned ligand and peptide stereochemistry without inference-time steering                                                                            | BSD-licensed open weights                                                  |
| RFdiffusion 1–3 + ProteinMPNN / LigandMPNN [@rfdiffusion; @rfdiffusion2; @rfdiffusion3; @proteinmpnn; @ligandmpnn] | Structure diffusion & inverse folding          | Target structure (no binder MSA)                 | Frame (RFD1/2) or all-atom U-Net (RFD3) diffusion                      | Backbone or atom generation paired with inverse folding; minibinders, active sites, antibodies [@rfantibody], macrocycles [@rfpeptides]               | Open weights and code                                                      |
| Boltz-1/2, BoltzGen & BoltzProt-1 [@boltz1; @boltz2; @boltzgen; @boltzprot1]                                       | Co-folding, unified design, & binding filter   | MSA (target); none for designed chain            | All-atom SDE diffusion                                                 | FK steering (1x); ligand affinity (2); joint prediction and design (BoltzGen, excl. mAbs); trained classifier (BoltzPPI)                              | MIT weights/code (Boltz-1/2/Gen); commercial API-only (BoltzProt-1)        |
| Chai-1 & Chai-2 [@chai1; @chai2]                                                                                   | Hybrid co-folding & zero-shot design           | Hybrid MSA + PLM (either or both)                | All-atom SDE diffusion (Chai-1 / Chai-2f)                              | Experimental restraints and single-seq antibody parity (Chai-1); zero-shot scFv, VHH, and minibinders (Chai-2)                                        | Non-commercial weights (Chai-1); generator undisclosed (Chai-2)            |
| Protenix-v1/v2 & PXDesign [@protenix_v1; @protenix_v2; @pxdesign]                                                  | Co-folding, diffusion, & gradient design       | MSA (target); single-seq binder in PXDesign-h    | SDE diffusion (Protenix, DiT in PXDesign-d) or 2-step ODE (PXDesign-h) | AF3-class predictor; minibinders, VHH, Fv, and full mAbs; paired diffusion and hallucination modes                                                    | Open weights and code                                                      |
| BindCraft & AfCycDesign [@bindcraft; @afcycdesign]                                                                 | End-to-end AF2 sequence inversion              | Target MSA (BindCraft); single-seq binder        | Single-pass IPA regression (AF2 / AF-Multimer)                         | ColabDesign [@colabdesign] continuous-to-discrete annealing; induced-fit minibinders; cyclic-offset macrocycles                                       | Open-source pipelines on AF2/AF-Multimer weights                           |
| BoltzDesign1 & RFOptimization [@boltzdesign1; @rfoptimization]                                                     | Trunk-gradient optimization & refinement       | Target MSA; single-seq binder                    | Diffusion bypassed during gradient steps                               | Pairformer distogram/confidence gradients; continuous annealing (BoltzDesign1) or discrete mutations + Boltz/LigandMPNN cycling (RFO); in silico only | Published pipelines on open Boltz-1 / RF3 weights                          |
| Germinal & mBER [@germinal; @opengerminal; @mber]                                                                  | Antibody hallucination with LM priors          | Single-seq + LM prior (IgLM or ESM-2) + template | Single-pass IPA regression (AF-Multimer)                               | Live IgLM + AF-Multimer gradients for CDRs (Germinal); static ESM-2 bias + framework template for VHHs (mBER)                                         | Published pipelines; Apache-2.0 port (OpenGerminal [@opengerminal])        |
| ESMFold2 & AtlasFold [@esmc; @atlasfold]                                                                           | Single-seq folding & gradient design           | Pre-trained PLM (optional MSA in ESMFold2)       | Sliding-window diffusion transformer (ESMFold2)                        | Single-seq Ab–Ag folding; ESMC + distogram gradient design for minibinders and scFvs; open PLM folder and benchmark (AtlasFold)                       | Released model (ESMFold2); MIT weights, code, and data (AtlasFold)         |
| AlphaProteo & Latent-X1/X2 [@alphaproteo; @latentx1; @latentx2]                                                    | Proprietary generative binder design           | Undisclosed                                      | Undisclosed (all-atom in Latent-X1/X2)                                 | Minibinders with disclosed AF2 filter (AlphaProteo); minibinders, macrocycles, and developable antibodies (Latent-X1/X2)                              | Closed weights; generative architectures undisclosed                       |

## All-atom co-folding predictors

AlphaFold2 established the modern MSA-driven folding architecture by combining
an Evoformer trunk with an end-to-end differentiable IPA structure module
[@alphafold2]. AlphaFold-Multimer retrained this architecture on protein
complexes and introduced ipTM and iPAE, which became standard filtering metrics
across binder design [@alphafold_multimer]. Because coordinates emerge from one
differentiable regression pass, downstream pipelines can both refold candidate
binders and backpropagate gradients through the full network \[@alphafold2;
@bindcraft\]. Accuracy degrades markedly, however, as MSA depth shrinks toward
single-sequence inputs [@alphafold2]. OpenFold later provided an open-source
retraining of AlphaFold2 and built structural distillation datasets reused by
subsequent open predictors [@openfold; @boltz1].

AlphaFold3 generalized structure prediction to complexes of proteins, nucleic
acids, small-molecule ligands, and ions [@alphafold3]. It replaced the Evoformer
with a simplified Pairformer trunk and substituted iterative all-atom diffusion
for IPA regression [@alphafold3]. While diffusion broadened chemical scope,
antibody–antigen predictions relied on ranking across 1,000 random seeds instead
of five, with accuracy still rising at 1,000 seeds [@alphafold3]. Diffusion also
introduced physical-validity caveats: AlphaFold3 showed a 4.4% chirality
violation rate on PoseBusters despite a ranking penalty, residual steric
clashes, and static PDB-like outputs rather than conformational ensembles
[@alphafold3]. It also hallucinated secondary structure in disordered regions,
which cross-distillation from AlphaFold-Multimer mitigated [@alphafold3].
Restricted model weights spurred independent and open-weights reproductions
[@alphafold3; @boltz1; @protenix_v1; @openfold3].

Developed independently of AlphaFold, RoseTTAFold began as a parallel
three-track network propagating 1D sequence, 2D distance, and 3D coordinate
representations from input to output [@rosettafold]. RoseTTAFold2 ablated
AlphaFold2 design choices and showed that frame-aligned point error loss,
recycling, distillation, and depth drove accuracy, whereas IPA and triangle
attention were unnecessary [@rosettafold2]. RoseTTAFold All-Atom extended this
backbone to nucleic acids, small molecules, and metals two months before
AlphaFold3 [@rosettafold_all_atom]. BSD-licensed RoseTTAFold3 (RF3) then adopted
all-atom diffusion while learning stereochemistry through geometric features
rather than inference-time steering, which can shift samples outside the
training distribution [@rosettafold3]. Without steering, RF3 predicted correct
chirality for 88% of ligand chiral centers (versus 84% for AlphaFold3 and 76%
for Boltz-2) and achieved 1.74 Å mean backbone RMSD on mixed L/D peptides
[@rosettafold3].

Open AF3-class predictors rapidly diversified this baseline. Boltz-1 released
the first MIT-licensed all-atom co-folder, and Boltz-1x added inference-time
Feynman-Kac steering to curb clashes and chirality errors [@boltz1]. Boltz-2
kept similar structural accuracy while adding a small-molecule affinity module
limited to single-protein ligand assays [@boltz2]. Under a non-commercial
license, Chai-1 paired MSA and protein language model tracks, supported
experimental restraints, and achieved single-sequence parity with MSA-enabled
runs on antibody–protein interfaces [@chai1]. Protenix-v1 matched AlphaFold3
under matched cutoffs and budgets, while Protenix-v2 raised antibody–antigen
DockQ success by 9–13 percentage points so five-seed v2 runs outperformed
1,000-seed v1 runs [@protenix_v1; @protenix_v2]. Finding twisted amides and flat
sp3 centers that cleared PoseBusters, the Protenix team added explicit planarity
checks to its open PXMeter toolkit [@protenix_v2; @pxmeter]. Two Apache-2.0
releases further expanded open training and scale. OpenFold3 published full
training code and a 13-million-sequence distillation corpus alongside its
weights [@openfold3]. OpenDDE tripled the Pairformer hidden width from 128 to
384 and added an atom-level refinement stage before diffusion [@opendde].

## Structure diffusion, inverse folding, and trained filters

Backbone-first pipelines separate 3D structure generation from amino-acid
sequence assignment. RFdiffusion fine-tuned RoseTTAFold1 predictor weights into
an SE(3)-equivariant frame diffusion model representing each residue by its Cα
position and backbone orientation [@rfdiffusion]. It established the widely used
three-step workflow: diffuse candidate backbones against a target, assign
sequences via inverse folding, and filter candidates by AlphaFold2 refolding
[@rfdiffusion]. ProteinMPNN became the standard inverse-folding model for fixed
backbones, though its authors noted that offline native sequence recovery does
not reliably predict whether a designed sequence will fold accurately
[@proteinmpnn]. LigandMPNN extended this message-passing architecture to
condition sequence design on ligands, nucleic acids, and metal ions
[@ligandmpnn]. AlphaDesign offered an autoregressive diffusion model (ADM)
alternative with comparable accuracy and complementary structural preferences
[@alphadesign]. Across early pipelines, reported in silico success reflected
agreement with AlphaFold2 confidence and self-consistency RMSD rather than
experimental binding [@rfdiffusion].

Later generators shifted from residue frames to all-atom representations and
faster sampling. RFdiffusion2 remained fine-tuned from RoseTTAFold to scaffold
enzyme active sites directly from functional-group coordinates [@rfdiffusion2].
RFdiffusion3 broke with predictor fine-tuning entirely: it pre-trained an
all-atom transformer U-Net modeled on AlphaFold3's diffusion module directly on
PDB structures and AlphaFold2 distillation data [@rfdiffusion3]. Cutting the
Pairformer from 48 to 2 layers (168 million parameters) with 100-step sampling
made RFdiffusion3 roughly an order of magnitude faster than earlier versions
[@rfdiffusion3]. Despite the similar names, RoseTTAFold3 predicts structures
from known sequences, whereas RFdiffusion3 is a distinct generator requiring
downstream inverse folding [@rosettafold3; @rfdiffusion3]. In parallel,
PXDesign-d generated Cartesian atomic coordinates with a Diffusion Transformer
rather than equivariant frames [@pxdesign]. Flow-matching models instead
formulated coordinate generation as straighter ODE trajectories, moving from
unconditional monomers in FrameFlow [@frameflow] to target-conditioned binders
in PPIFlow, OriginFlow, AtomFlow, and D-Flow \[@ppiflow; @originflow; @atomflow;
@dflow\].

Rather than adapting a predictor into a separate generator, BoltzGen trained one
MIT-licensed all-atom diffusion model (with released weights, code, and data)
for both prediction and design [@boltzgen]. It generates proteins, peptides, and
nanobodies, while excluding full monoclonal antibodies (mAbs) from training
[@boltzgen]. Filtered by Boltz-2 refolding across 26 experimental targets,
BoltzGen produced nanomolar binders on six of nine novel targets at 15 or fewer
designs per target [@boltzgen]. Its authors documented specific caveats,
including diversity collapse onto ubiquitin at lengths of 73–76 residues due to
over 900 ubiquitin PDB entries, and emphasized that practical campaigns still
require structural inspection and reruns [@boltzgen]. BoltzProt-1 paired a
refined BoltzGen generator with BoltzPPI, a classifier trained directly on
experimental binding outcomes instead of structure-confidence scores
[@boltzprot1]. On identical candidate pools across 10 low-homology targets,
replacing confidence ranking with BoltzPPI raised confirmed binders from 3.3% to
8.0% [@boltzprot1]. The study also separated initial screening hits from binders
confirmed by inverted-orientation and independent-vendor assays [@boltzprot1].
Unlike BoltzGen, BoltzProt-1 is accessible only through a commercial API without
released weights [@boltzprot1].

Dedicated diffusion pipelines also target antibody loops and macrocyclic
peptides. RFantibody fine-tuned RFdiffusion for epitope-specific VHH, scFv, and
mAb design, but achieved 0–2% hit rates alongside 9,000-design yeast-display
screens [@rfantibody]. Its authors concluded that experimental library screening
remained necessary [@rfantibody]. RFpeptides added cyclic relative positional
encodings to RFdiffusion and RoseTTAFold2, pairing them with ProteinMPNN and
AfCycDesign filtering [@rfpeptides; @afcycdesign]. It yielded
crystal-structure-verified head-to-tail macrocycles on all four tested targets
from fewer than 20 synthesized peptides each [@rfpeptides]. Newer antibody
platforms reduced experimental testing to tens of designs per target without
affinity maturation or display libraries. Chai-2 built on Chai-1 to design
scFvs, VHHs, and minibinders at 20 or fewer designs per target, reaching a 16%
combined antibody hit rate across 52 novel targets [@chai2]. Its paper describes
only the folding submodule (`Chai-2f`), leaving the generative architecture
undisclosed [@chai2]. Protenix-v2 extended all-atom design to VHH, Fv, and full
mAbs in epitope-specific and site-agnostic modes [@protenix_v2]. It generated
binders across a novelty-controlled soluble VHH-Fc panel and four GPCRs tested
at 16–30 designs per target [@protenix_v2]. Hit rates remained sensitive to
epitope choice: two manually selected epitopes on the same antigen (AMBP)
yielded 4% versus 48% hit rates, prompting focus on native ligand-binding
interfaces [@protenix_v2].

## Gradient-based sequence optimization

Rather than generating structures with diffusion and assigning sequences
afterward, gradient-based methods optimize amino-acid sequences directly by
inverting a pretrained structure predictor. Because AlphaFold2 uses a
regression-based structure module, gradients flow end-to-end from predicted
coordinates and confidence heads back to the input sequence [@alphafold2]. The
ColabDesign library implements this inversion workflow with loss functions,
sequence-logit backpropagation, and continuous-to-discrete annealing
[@colabdesign]. Using ColabDesign, AfCycDesign adds cyclic relative positional
encoding to close peptide chains head-to-tail while leaving protein targets
linear [@afcycdesign]. Eight crystal structures of hallucinated 7–10-residue
macrocycles matched their design models within 1.0 Å, though AfCycDesign's MDM2
and Keap1 binders relied on motif grafting onto monomeric scaffolds rather than
direct binder hallucination [@afcycdesign]. BindCraft inverts AlphaFold-Multimer
for de novo minibinders by backpropagating confidence losses into an *L* × 20
sequence gradient [@bindcraft]. It randomly swaps among the five
AlphaFold-Multimer weight sets and repredicts the target at every step,
permitting induced-fit target adaptation (0.5–5.5 Å Cα RMSD) [@bindcraft]. A
four-stage schedule moves from continuous logits and annealed softmax to
straight-through estimation and discrete mutation search, followed by soluble
ProteinMPNN surface redesign [@bindcraft]. Across 12 targets (6–53 designs per
target), BindCraft achieved 10–100% wet-lab hit rates (mean 46.3%) [@bindcraft].
Running AlphaFold2 in single-sequence mode places designed chains outside its
MSA training regime, and ipTM predicts binding rather than affinity
[@alphafold2; @bindcraft].

Unrolling hundreds of stochastic diffusion steps is impractical for
backpropagation, so diffusion-predictor inversion uses two alternatives.
BoltzDesign1 stops gradients at Boltz-1's diffusion module and minimizes
interchain and intrachain contact losses over the Pairformer's 64-bin distogram,
with an optional confidence-head path [@boltz1; @boltzdesign1]. Optimizing the
distogram shapes the distance distribution sampled by diffusion rather than a
single draw, while nucleic-acid targets rely on the confidence module instead
[@boltzdesign1]. BoltzDesign1 adapts BindCraft's four-stage loop with an initial
softmax warm-up and optional LigandMPNN surface redesign, evaluated only in
silico [@boltzdesign1; @ligandmpnn]. RFOptimization also reads distogram and
confidence gradients from RoseTTAFold3, but avoids continuous sequence
relaxation altogether [@rosettafold3; @rfoptimization]. It proposes discrete
single-position mutations from negative normalized gradients via annealed
Metropolis–Hastings, alternating with Boltz refolding and LigandMPNN cycling
while holding AlphaFold3 out as an independent check [@rfoptimization].
Evaluated in silico, this loop raised AlphaFold3-refolded success across
protein–protein interfaces, cyclic peptides, and small-molecule binders
[@rfoptimization]. By contrast, PXDesign-h replaces Protenix's 200-step
diffusion decoder with a differentiable 2-step ODE sampler, backpropagating
end-to-end across five resampled Protenix models [@pxdesign].

Confidence scores alone do not guarantee natural antibody sequences, motivating
explicit language-model priors. Germinal designs CDR loops on a CDR-masked
framework template by merging live IgLM gradients with AlphaFold-Multimer
gradients via a weighted sum, MGDA, or weighted PCGrad [@germinal]. A
position-specific scoring matrix (PSSM) feeds AlphaFold-Multimer directly and
sends discrete tokens to IgLM via a straight-through estimator before AbMPNN
redesigns non-interface CDR residues [@germinal]. Experimentally, nonbinders
cleared the ipSAE filter alongside binders, showing incomplete per-design
separation [@germinal]. OpenGerminal provides an Apache-2.0 reimplementation of
this workflow [@opengerminal]. In contrast, mBER applies a static sequence prior
for VHH design by adding single-pass ESM-2 logits over a NanoBodyBuilder2
framework template as a fixed bias at every ColabDesign step [@mber]. In a
1.15-million-design phage-display sweep across randomized hotspots on 436 human
cell-surface targets (145 assayed), single-target hit rates spanned 0.4% overall
to 7.5% at the best hotspot [@mber]. Within an ipTM-filtered epitope bin,
enrichment reached 38% (8/21), though binding affinities were not measured
[@mber].

## Protein language models and single-sequence design

Protein language models replace inference-time MSA searches with representations
learned from billions of natural sequences. ESM-2 and ESMFold showed that
scaling masked language models enables single-sequence 3D folding through a
folding trunk and IPA module without MSAs or templates, trading some accuracy
relative to AlphaFold2 for speed [@esm2]. ESM-3 extended this approach to a
multimodal model up to 98 billion parameters trained on 2.78 billion proteins,
encoding sequence, 3D structure, and function as discrete token tracks [@esm3].
At 98 billion parameters, ESM-3 surpassed ESMFold on single-sequence CAMEO
prediction (0.880 vs. 0.861 lDDT) and generated `esmGFP`, an experimentally
fluorescent protein sharing 58% sequence identity with the nearest known
fluorescent protein [@esm3]. Only the 1.4-billion-parameter `ESM3-open`
checkpoint is downloadable for academic use, whereas the 98-billion-parameter
model is API-only [@esm3].

ESMC and ESMFold2 pair a frozen 6-billion-parameter protein language model with
a 48-layer recurrent folding trunk and a sliding-window diffusion transformer
for atomic coordinates [@esmc]. Without MSAs, ESMFold2 matches AlphaFold3 run
with MSAs on antibody–antigen prediction, retaining an optional detachable MSA
encoder for high-perplexity sequences [@esmc]. Independent AtlasFold benchmarks
place the margin between ESMFold2 and AlphaFold3 within error bars across runs
[@atlasfold]. Because ESMFold2 operates natively on single sequences, its binder
loop runs 150 single-stage gradient steps directly through ESMC as an
evolutionary prior and through the trunk distogram across two replicates
[@esmc]. Final diffusion and confidence forward passes compute ipTM to rank
candidates [@esmc]. Testing 84 designs per cohort across five targets yielded
36–88% hit rates (mean 70.0%, best 68 pM) for minibinders and 15–29% (mean
21.0%) for scFvs [@esmc]. Independently, AtlasFold released an MIT-licensed
single-sequence language-model folding model with training code, data, and
checkpoints alongside a multi-model FoldBench evaluation comparing seven
predictors [@atlasfold].

## Undisclosed and proprietary systems

Several binder-design platforms report wet-lab outcomes while withholding their
generative architectures or weights. AlphaProteo achieved 9–88% minibinder hit
rates on seven of eight targets (0/54 on TNFα) and disclosed its AlphaFold2
filter thresholds [@alphaproteo]. Its generator remains undisclosed beyond
training on PDB structures and AlphaFold distillation data, though the study
also resynthesized and re-assayed RFdiffusion's published designs by yeast
display [@alphaproteo; @rfdiffusion]. Latent-X1 and Latent-X2 use a proprietary
atom-level platform to generate macrocycles, minibinders, and developable,
low-immunogenicity antibodies [@latentx1; @latentx2]. Latent-X1 also
resynthesized RFpeptides' two top-affinity macrocycles for direct affinity
comparison rather than replicating the full campaign [@latentx1; @rfpeptides].

Similar disclosure limits apply to Chai-2's withheld generator [@chai2],
API-only BoltzProt-1 [@boltzprot1], and unpublished IsoDDE, which appears
publicly only through reference points on OpenDDE's scaling curves \[@opendde;
@bender_perspective\]. When architectures, training cutoffs, and weights remain
closed, outside researchers can inspect reported assay outcomes but cannot
separate generator gains from downstream filtering [@bender_perspective].
Independent checks of training-set overlap and side-by-side benchmarking also
remain out of reach.

# Interpreting Benchmarks and Wet-Lab Campaigns

Published structure-prediction and binder-design metrics depend strongly on
evaluation definitions, making direct cross-study comparisons difficult.
FoldBench evaluates 1,522 all-atom assemblies released between January 2023 and
November 2024, yet predictors fail on different targets because of memory limits
or unsupported glycans [@foldbench; @protenix_v1]. Across the common
intersection of targets completed by seven models (AlphaFold3, Boltz-1, Chai-1,
HelixFold3, and three Protenix checkpoints), monomer accuracy clusters tightly
at 0.85–0.89 mean lDDT [@protenix_v1]. Protein–protein DockQ success (DockQ ≥
0.23) spans 65.4–72.7%, whereas antibody–antigen success spans more than a
factor of two at 23.1–52.3% [@protenix_v1]. Boltz-2 is excluded from these
comparisons because its June 2023 training cutoff overlaps the benchmark release
window [@boltz2; @protenix_v1; @protenix_v2; @esmc].

Identical metric names also shift substantially with target filtering and
aggregation rules. On FoldBench protein–protein interfaces, unequal inference
failures left Boltz-1 scored on 252 interfaces (68.3%) and Chai-1 on 251 (68.5%)
[@protenix_v1; @boltz1; @chai1]. Restricting both predictors to their 237 shared
interfaces reversed that ordering to 68.4% for Boltz-1 versus 67.5% for Chai-1
[@protenix_v1]. Averaging units create even wider swings on antibodies. Chai-1
reports 52.9% DockQ success when averaging across 40%-identity interface
clusters, compared with 25.2% on FoldBench when averaging per interface
\[@chai1; @foldbench\]. Boltz-1 applies a third convention that averages
interfaces within each complex before averaging across complexes [@boltz1].

Multi-sample predictors lose further accuracy when selecting a top structure
from their internal confidence heads. In AtlasFold's template-free FoldBench
evaluation of seven predictors, confidence-ranked predictions trailed oracle
selection (picking the best generated sample against the experimental structure)
by 11–21 percentage points on antibody–antigen complexes (4.5 points for
Boltz-1) [@atlasfold]. The corresponding rank-to-oracle gap on general
protein–protein interfaces was smaller at 3–8 percentage points [@atlasfold].
FoldBench similarly notes that predicting an accurate CDR-H3 loop does not
guarantee correct antibody–antigen docking, because per-sample confidence scores
fail to isolate near-native poses reliably [@foldbench]. Consequently, antibody
evaluations rely on large sampling budgets: AlphaFold3 ranked predictions over
1,000 seeds [@alphafold3], and Protenix-v1 rose from 36.01% at 1 seed to 47.68%
at 80 seeds [@protenix_v1]. At several hundred seeds, OpenDDE's FoldBench
antibody oracle success similarly climbed from roughly 66% at 1 seed to above
90% [@opendde].

Wet-lab binder-design campaigns introduce still wider confounders (**Table 2**).
Testing budgets have dropped from thousands or millions of library-screened
designs [@rfantibody; @mber] to tens of individually assayed candidates per
target. Even so, no two de novo campaigns share the same targets, assay formats,
or binding thresholds. Confirmation rigor sharply alters counts: BoltzProt-1
separates initial screening hits from confirmed binders verified by inverted
assay orientation and independent vendor re-testing, leaving 12 confirmed VHH
binders out of 150 tested [@boltzprot1]. Target and epitope selection also
strongly shapes outcomes. In mBER's randomized-hotspot phage screen of 1.15
million VHHs, the median per-design hit rate sat near 0.4%, whereas one
ipTM-filtered epitope bin reached 38% (8/21) [@mber]. Several headline
affinities further reflect bivalent Fc fusions or avidity-affected formats
rather than monovalent $K_D$, including Protenix-v2's 112 pM GPRC5D binder
[@protenix_v2], Chai-2's sub-nanomolar EFNA5 scFv [@chai2], and BindCraft's
bivalent Fc PD-1 construct [@bindcraft].

Denominator choices and cross-laboratory replication add further complexity
across **Table 2**. Synthesis or expression attrition often narrows the tested
set before measurement. RFpeptides assayed 14 of 27 selected MCL-1 macrocycles
and 11 of 26 for RbtA [@rfpeptides], and Latent-X1 tested 11–17 synthesized
macrocycles from 30 submitted [@latentx1]. On PD-L1, PXDesign's hit rate falls
from 72.7% of tested designs to 47.1% of designs sent for expression once six
poorly expressed constructs are retained [@pxdesign]. Studies also emphasize
different summaries, with BoltzGen, Protenix-v2, and Latent-X2 reporting
target-level success [@boltzgen; @protenix_v2; @latentx2] while Chai-2,
PXDesign, BindCraft, and ESMFold2 highlight per-design hit rates \[@chai2;
@pxdesign; @bindcraft; @esmc\]. Finally, re-testing another group's designs
under a new assay shifts both hit rates and affinities. When AlphaProteo
re-assayed RFdiffusion designs by yeast display at 10–20× lower target
concentration, hit rates dropped from 33% to 16% on IL-7Rα and from 6% to 0% on
TrkA [@alphaproteo; @rfdiffusion]. Latent-X1 similarly resynthesized RFpeptides'
two top macrocycles and measured affinities 4.4× and 5× weaker than originally
reported [@latentx1; @rfpeptides].

**Table 2. Representative wet-lab binder-design campaigns grouped by
experimental validation format.**

| Validation format | System                     | Modality & targets              | Tested                                | Outcome / hit rate                                        | Best affinity & notes                                  |
| ----------------- | -------------------------- | ------------------------------- | ------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------ |
| Dual assay        | BoltzProt-1 [@boltzprot1]  | VHH; 10 low-homology targets    | 15/target (150)                       | 12/150 (8.0%); BoltzGen on same pools: 5/150 (3.3%)       | NR; inverted orientation + external vendor check       |
| Dual assay        | Germinal [@germinal]       | VHH; 4 targets                  | 43–101 ordered/target                 | 7, 2, 4, 5 confirmed by BLI after split-luciferase        | 170 nM (PD-L1); 42 nM after rescaffolding              |
| Dual assay        | Latent-X1 [@latentx1]      | Minibinders; 5 targets          | 100 HT-BLI; 88 mDisplay/target        | 10–64% per target (Pearson *r* = 0.68–0.79)               | \<0.01 nM (IL-7Rα, SC2RBD); closed platform            |
| Single assay      | RFpeptides [@rfpeptides]   | Macrocycles; 4 targets          | 6–14/target (of 11–27 selected)       | 2–4 hits/target (4/4 targets)                             | 6 nM (GABARAP); SPR + crystal structures               |
| Single assay      | BoltzGen [@boltzgen]       | VHH & proteins; 9 novel targets | ≤15/target                            | Binders on 6/9 targets (both formats)                     | 6.1 nM VHH (PMVK); 9.8 nM protein (MZB1)               |
| Single assay      | PXDesign [@pxdesign]       | Minibinders; 6 targets          | 9–17/target                           | 20–73% on 5 targets; 0/16 on TNFα                         | Multiple nM (exact NR); BLI; PXDesign-d                |
| Single assay      | Latent-X2 [@latentx2]      | VHH & scFv; 18 targets          | 4–24/target/format                    | Binders on 9/18 targets (up to 25% of designs)            | 26.2 pM (HDAC8 scFv); BLI; closed platform             |
| Single assay      | Chai-2 [@chai2]            | scFv & VHH; 52 novel targets    | ≤20/target/format                     | 13.7% scFv (68/496), 20.0% VHH (41/205); 26/52 targets    | \<1 nM (EFNA5 scFv, avidity-flagged); closed generator |
| Single assay      | Protenix-v2 [@protenix_v2] | VHH-Fc & mAb; 4 GPCRs           | 16–30/target                          | VHH-Fc 16–88% (4/4); mAb 0–50% (3/4)                      | 112 pM (GPRC5D, avidity); BLI                          |
| Single assay      | BindCraft [@bindcraft]     | Minibinders; 12 targets         | 6–53/target                           | 10–100%, mean 46.3%                                       | \<1 nM (PD-1, bivalent Fc); 5 nM (CbAgo); SPR          |
| Single assay      | ESMFold2 [@esmc]           | Minibinders & scFv; 5 targets   | 84/cohort                             | Minibinders 36–88% (mean 70.0%); scFv 15–29% (mean 21.0%) | 68 pM minibinder (target NR); scFv $K_D$ NR; BLI\*     |
| Single assay      | RFdiffusion [@rfdiffusion] | Minibinders; 5 targets          | 95/target                             | 19% pooled (475 designs)                                  | 28 nM (influenza HA); single-point BLI                 |
| Single assay      | AlphaProteo [@alphaproteo] | Minibinders; 8 targets          | 54–172/target                         | 9% (TrkA) to 88% (BHRF1); 0/54 on TNFα                    | 82 pM (IL-7Rα); yeast display; closed generator        |
| Display screen    | RFantibody [@rfantibody]   | VHH; 4 targets (+3 by SPR)      | 9,000/target (yeast); 95/target (SPR) | 0–2% per target                                           | 78 nM (HA), 1.4 µM (RSV site III) on follow-up SPR     |
| Display screen    | mBER [@mber]               | VHH; 145 assayed (436 designed) | 1,153,241 pooled (phage)              | 45% targets (65/145); median ≈0.4% (38% in 1 ipTM bin)    | None (phage enrichment only); random hotspots          |

*Table 2 notes:* One representative campaign is listed per major system (`NR`,
not reported; `BLI`, biolayer interferometry; `SPR`, surface plasmon resonance;
`mDisplay`, mammalian display); additional campaigns from BoltzGen, Germinal,
Chai-2, Protenix-v2, and Latent-X1/X2 are omitted for brevity \[@boltzgen;
@germinal; @chai2; @protenix_v2; @latentx1; @latentx2\]. Several published
values appear only in source figures rather than extractable text, including
Protenix-v2's soluble-target denominators and affinities [@protenix_v2], the
stringent-versus-inclusive cutoff shading in ESMFold2's higher-compute campaign
plot (`*`) [@esmc], and per-class headline structure-prediction tables for
AlphaFold3, Boltz-1, Boltz-2, and RoseTTAFold2 \[@alphafold3; @boltz1; @boltz2;
@rosettafold2\]. BoltzDesign1 [@boltzdesign1] and RFOptimization
[@rfoptimization] are omitted because they report in-silico evaluation without
wet-lab testing.

# Conclusions and Open Challenges

## From in vitro binding to therapeutic utility

Most binder-design papers motivate their methods through therapeutic
applications. Published goals include automating drug discovery [@boltzgen],
optimizing species cross-reactivity [@chai2], reducing IgE binding in
patient-derived samples [@bindcraft], matching approved antibody developability
[@latentx2], and accelerating protein therapeutics [@mber]. In a Perspective
reviewing a decade of artificial intelligence in pharmaceutical research, Bender
et al. distinguish *model validation* from *process validation*
[@bender_perspective]. High accuracy on held-out structure benchmarks or in
vitro binding assays establishes model validation, whereas process validation
evaluates whether a method improves downstream clinical decisions
[@bender_perspective].

Biologics show higher average clinical approval rates than small molecules, yet
target binding remains only an early step [@bender_perspective]. Reviewing
protein-design methods alongside small-molecule pipelines, Bender et al. note
that binding is easier to predict than functional activity or developability
[@bender_perspective]. Small-molecule repositories illustrate the scale of
downstream attrition: ChEMBL and PubChem hold more than $10^6$ bioactive
ligands, whereas only about $10^3$ compounds have become marketed drugs
[@bender_perspective]. Closing that gap requires task-matched metrics (for
selection, deselection, or quantification), caution regarding local
generalization outside training distributions, and sufficient technical
disclosure for independent verification [@bender_perspective]. Bender et al.
present a secondary Perspective centered mainly on small-molecule and clinical
pipeline evidence, so its observations on biologic developability rest on a
narrower evidence base [@bender_perspective].

## Open technical and methodological limitations

First, nearly all open binder-design pipelines optimize and filter exclusively
for target binding. As the Latent-X2 authors note, therapeutic campaigns often
fail not for lack of binding, but because clinical use also requires
developability and low immunogenicity [@latentx2]. Latent-X2 reports favorable
developability and low-immunogenicity data for its AI-designed antibodies, yet
its generative architecture remains undisclosed [@latentx2].

Second, current scoring functions cannot predict quantitative protein–protein
binding affinity. BindCraft reports that AlphaFold2 ipTM indicates whether a
design binds rather than its dissociation constant ($K_D$) [@bindcraft], and
Boltz-2 restricts its affinity head to small-molecule ligands on single-protein
targets [@boltz2]. Designers therefore measure $K_D$ experimentally after
synthesis rather than predicting it beforehand. Third, most wet-lab campaigns
target experimentally solved or high-confidence predicted structures. As the
Germinal authors note, how strongly design success depends on predicted
antigen-model accuracy remains an open question [@germinal].

Fourth, the field lacks shared, blinded prospective benchmarks for de novo
binder design. AlphaProteo's yeast-display re-testing of RFdiffusion's published
set, including nonbinders, remains the only full-campaign independent
replication [@alphaproteo; @rfdiffusion]. The AIntibody challenge provides the
main blinded prospective benchmark, assaying 511 full IgGs from 29 organizations
under one kinetics and five-assay developability protocol [@aintibody]. Its
Challenge 1 winner achieved 95 pM, statistically indistinguishable from the best
wet-lab antibody (113 pM), using a disclosed Protenix-derived pairformer with a
direct preference optimization (DPO) fitness head [@aintibody]. A non-ML
consensus of selection data ranked third [@aintibody]. However, only 1 of 26
groups beat random within-cluster affinity ranking [@aintibody]. In the
out-of-library task, 30.4% of designs were nonbinders, and the highest-affinity
winner (2.9 pM) failed to elute from the hydrophobic interaction chromatography
(HIC) developability column [@aintibody]. Moreover, AIntibody captures a Q1-2025
snapshot of library-conditioned engineering on one well-characterized antigen
(SARS-CoV-2 RBD) rather than target-conditioned de novo design, and several
major de novo groups did not participate [@aintibody].

Fifth, structure-prediction confidence filters still struggle with per-design
discrimination. Metrics such as ipTM and ipSAE enrich hit rates across large
candidate pools, as demonstrated at million-design scale in mBER [@mber]. On
individual candidates, however, nonbinders often clear the same ipSAE cutoffs as
confirmed binders in Germinal [@germinal]. In a unified re-scoring of 3,766
experimentally tested designs from six published campaigns across 15 targets,
Overath et al. identified AlphaFold3 ipSAE as the strongest overall predictor
[@overath_meta]. Even so, its average precision spanned 0.1–1.0 across targets
[@overath_meta]. Unified re-scoring leaves each source campaign's heterogeneous
wet-lab assays unchanged and reflects earlier-generation designs rather than
2025–2026 models, yet this spread highlights wide target-to-target variability
[@overath_meta].

Co-folding and generative models can now produce minibinders, macrocycles, and
antibody fragments against chosen epitopes from tens of tested sequences rather
than large random libraries. Turning those in vitro binding hits into
therapeutic candidates will require quantitative protein–protein affinity
prediction and joint optimization of function, immunogenicity, and
developability. Measuring progress reliably will likewise require stronger
per-design filters and blinded prospective benchmarks built specifically for de
novo design.
