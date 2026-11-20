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
BindCraft backpropagates confidence losses through AlphaFold-Multimer into an
*L* × 20 sequence matrix, randomly swapping five weight sets and repredicting
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
confidence heads via annealed Metropolis-Hastings [@rfoptimization;
@rosettafold3]. On half of its steps, it runs a Boltz folding and LigandMPNN
resampling cycle while holding AlphaFold3 out, raising AF3-refolded success
(iPAE < 2.5, ipTM > 0.8) across protein-protein interfaces (6.73% to 22.31%),
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
and inference budget, it outperforms AlphaFold3 on protein-protein and
antibody-antigen interfaces and trails on protein-ligand and protein-DNA
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

Protenix-v2 improves antibody-antigen DockQ > 0.23 success by 9–13 percentage
points over Protenix-v1 across PXMeter-AB, FoldBench-AB, and AF3-AB, with 5
seeds outperforming Protenix-v1 at 1,000 seeds [@protenix_v2]. It expands design
to VHH, Fv, and full mAbs in epitope-specific and site-agnostic modes. On a
novelty-controlled soluble panel (applying BoltzGen's 30%-identity and Chai-2's
SAbDab filters), BLI-confirmed VHH-Fc binders were found for every antigen (100%
target-level success; 2–48% hit rates); on four GPCRs with small, flexible
extracellular epitopes, testing 16–30 designs per target yielded 16–88% VHH-Fc
and 0–50% mAb hit rates [@protenix_v2]. Two AMBP epitopes produced 4% versus 48%
hit rates, prompting prioritization of native ligand-binding interfaces; caveats
include manual epitope selection on in-stock targets and no direct Chai-2
head-to-head because overlapping targets differed in format [@protenix_v2].
ByteDance Seed's open PXMeter benchmark toolkit [@pxmeter] added sp2-planarity,
amide-planarity, and sp3-non-planarity checks in v1.1.0 (introduced with
Protenix-v2 and used as PXMeter-AB by OpenDDE) after observing twisted amides
and flat sp3 centers passing PoseBusters [@protenix_v2; @opendde; @posebusters].

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
AlphaFold3 on antibody-antigen interfaces within error bars across independent
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
its roadmap [@opendde]. Alongside third-party antibody-antigen comparisons,
OpenDDE supplies the only public scaling-curve points for unpublished IsoDDE
(also noted as lacking public verification by Bender et al.
[@bender_perspective]) and SeedFold [@opendde], alongside the commercial web
platform Chai-3.

**Table 1. Overview of major structure predictors and binder-design systems.**

| System / Lineage                                     | Primary Role                                                   | Evolutionary Input                                      | Coordinate Stage                                                      | Target / Binder Modalities                                                        | Design or Filtering Mechanism                                                                          | Openness / License                                           | Reference                                              |
| ---------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------ |
| AlphaFold2 / AF-Multimer                             | Structure predictor (monomer & multimer)                       | MSA                                                     | Single-pass IPA regression                                            | Protein chains and multimers                                                      | Refolding filter (pLDDT, ipTM, iPAE); inverted by backpropagation pipelines                            | Open code & weights                                          | [@alphafold2; @alphafold_multimer]                     |
| OpenFold                                             | Structure predictor (AF2 reproduction)                         | MSA                                                     | Single-pass IPA regression                                            | Protein chains                                                                    | Open retraining and structural distillation dataset                                                    | Open source (code, weights, data)                            | [@openfold]                                            |
| AlphaFold3                                           | All-atom co-folding predictor                                  | MSA                                                     | All-atom SDE diffusion                                                | Proteins, nucleic acids, ligands, ions (incl. Ab-Ag)                              | Refolding / ranking filter (up to 1,000 seeds for Ab-Ag)                                               | Closed / restricted weights                                  | [@alphafold3]                                          |
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
| RFOptimization (RFO)                                 | Discrete gradient-guided design refiner                        | Single-sequence / predictor trunk                       | Bypasses RF3 diffusion (distogram/confidence heads)                   | Protein-protein, cyclic peptide, small-molecule binders                           | Discrete Metropolis-Hastings mutations from RF3 gradients + 50% Boltz/LigandMPNN cycling               | Preprint method (in-silico evaluated)                        | [@rfoptimization]                                      |
| Germinal / OpenGerminal                              | Gradient-based antibody CDR designer                           | Single-sequence + antibody LM (IgLM / AbLang1)          | Full AF-Multimer IPA regression + masked framework template           | Antibody CDR loops (VHH, scFv/Fab)                                                | Live AF-Multimer + LM gradient merging (PSSM + STE) + AbMPNN + co-folding/ipSAE filter                 | Open code; OpenGerminal Apache-2.0                           | [@germinal; @opengerminal]                             |
| mBER (and mBER-2)                                    | Template- and PLM-biased VHH designer                          | Single-sequence + static ESM-2 prior                    | AF-Multimer IPA regression + NanoBodyBuilder2 template                | VHHs (mBER-2 extends to microbinders)                                             | ColabDesign 3-stage loop with fixed ESM-2 logit bias + held-out AF-Multimer ipTM filter                | Open code (mBER-2 technical report)                          | [@mber]                                                |
| Protenix-v1 / Protenix-v2                            | All-atom co-folding predictors & antibody/binder designer (v2) | MSA                                                     | All-atom SDE diffusion                                                | Biomolecular complexes; v2 designs miniproteins, VHH, Fv, full mAbs (incl. GPCRs) | Co-folding + epitope-specific/site-agnostic design & ranking (paired with PXMeter)                     | Protenix-v1 open weights & code; Protenix-v2 preprint        | [@protenix_v1; @protenix_v2; @pxmeter]                 |
| PXDesign (PXDesign-d / -h)                           | Dual-mode binder designer                                      | Target conditioned / single-sequence (PXDesign-h)       | DiT Cartesian diffusion (-d); 2-step ODE sampler (-h)                 | Minibinders                                                                       | Diffusion + inverse folding (-d) or end-to-end 2-step ODE hallucination (-h) + Protenix/AF2-IG filters | Open benchmark & web server (built on Protenix)              | [@pxdesign]                                            |
| ESM-2 / ESMFold                                      | PLM & single-sequence monomer folder                           | PLM (single-sequence, no MSA)                           | Single-pass IPA regression                                            | Monomeric proteins                                                                | Single-sequence structure prediction; ESM-2 also used as static prior (mBER)                           | Open weights & code                                          | [@esm2]                                                |
| ESM-3                                                | Multimodal generative protein LM                               | Multimodal discrete tokens (no MSA)                     | Discrete 3D structure tokens                                          | Sequence, structure, and function generation (e.g., esmGFP)                       | Masked-token multimodal prompting and generation (1.4B, 7B, 98B)                                       | 1.4B academic-only; 98B API-only                             | [@esm3]                                                |
| ESMC / ESMFold2                                      | PLM, all-atom co-folder, & binder designer                     | PLM (6B ESMC, single-sequence; optional detachable MSA) | 48-layer recurrent trunk + sliding-window diffusion transformer       | Biomolecular complexes, Ab-Ag; minibinders & scFvs                                | 150-step single-stage gradient optimization via ESMC + distogram + final ipTM ranking                  | Preprint (Biohub / EvolutionaryScale)                        | [@esmc]                                                |
| AtlasFold                                            | Single-sequence PLM structure predictor                        | PLM (single-sequence, no MSA)                           | 48-block Pairformer + all-atom diffusion                              | Protein monomers and complexes (AtlasFold-M)                                      | Independent single-sequence co-folding + rank vs. oracle benchmarking                                  | MIT (weights, code, checkpoints, data)                       | [@atlasfold]                                           |
| OpenDDE                                              | Scaled all-atom co-folding predictor                           | MSA                                                     | Atom-level refiner + all-atom diffusion (3x wider Pairformer)         | Biomolecular complexes, Ab-Ag (joint design on roadmap)                           | Scaled Pairformer (128 to 384) co-folding + third-party Ab-Ag scaling benchmarks                       | Apache-2.0                                                   | [@opendde]                                             |
| AlphaProteo                                          | De novo minibinder designer                                    | Undisclosed (AF2 used for filtering)                    | Undisclosed                                                           | Minibinders                                                                       | Undisclosed generator + disclosed AF2 PAE/RMSD/pLDDT filter                                            | Closed weights & undisclosed architecture                    | [@alphaproteo]                                         |
| Latent-X1 / Latent-X2                                | All-atom binder & antibody designer                            | Undisclosed                                             | Undisclosed (all-atom)                                                | Macrocycles, minibinders (X1); drug-like VHH/scFv & macrocycles (X2)              | Undisclosed generator + ipTM/PAE and self-consistency filtering                                        | Closed weights & undisclosed architecture                    | [@latentx1; @latentx2]                                 |
| IsoDDE / SeedFold                                    | Unpublished structure predictors                               | Undisclosed                                             | Undisclosed                                                           | Biomolecular complexes, Ab-Ag                                                     | Known publicly only via third-party scaling-curve points in OpenDDE                                    | Closed / unpublished                                         | [@opendde; @bender_perspective]                        |
