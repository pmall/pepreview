# Literature Map

# Introduction

- Binding a target protein selectively is the basis for blocking, detecting,
  tagging, or modulating biological activity. Antibodies, nanobodies (VHHs),
  scFvs, minibinders, and macrocyclic peptides represent a major class of
  therapeutics and laboratory reagents capable of engaging broad, flat protein
  surfaces.
- Historically, discovering such binders has relied on experimental search
  rather than rational design: immunizing animals or screening libraries of 10¹²
  or more random sequences via phage or yeast display. These methods remain
  standard, but they require wet-lab screening from the start, must be repeated
  per target, and return binders to whichever regions happen to be immunogenic
  or accessible rather than a user-specified site.
- Computational de novo binder design aims to propose candidate sequences
  directly for a chosen target protein and epitope.
- This shift became practical once protein structure prediction reached
  experimental accuracy. AlphaFold2 solved single-chain structure prediction at
  CASP14 [@alphafold2], and AlphaFold3 extended structure prediction to
  complexes involving proteins, nucleic acids, small-molecule ligands, and ions
  [@alphafold3].
- Designing a binder differs fundamentally from predicting a structure. A
  structure predictor maps a known sequence to its 3D fold and can be checked
  directly against an experimental structure. A binder generator proposes a new
  sequence intended to fold and bind a target, which can only be confirmed
  experimentally in a wet lab.
- Between 2024 and 2026, the field expanded rapidly across multiple predictor
  families, open-source reproductions, and design pipelines. Industry investment
  in inference speed reflects active deployment: in September 2026, NVIDIA,
  Anthropic, and ESM teams released optimized inference kernels for Boltz,
  Chai-1, Protenix, OpenFold, RoseTTAFold3, RFdiffusion, BindCraft, PXDesign,
  and ESMFold2, reporting 2–4× throughput gains. (No peer-reviewed publication;
  blog posts and repositories:
  [NVIDIA](https://developer.nvidia.com/blog/high-throughput-structure-prediction-with-bionemo-inference-runtime/),
  [Anthropic](https://www.anthropic.com/research/claude-uplifts-biomolecular-modeling),
  [Anthropic kits](https://github.com/anthropics/uplifting-biomolecular-modeling).)
- **Scope:** De novo design of amino-acid-based binders (antibodies,
  nanobodies/VHHs, scFvs, minibinders, and macrocyclic peptides) against a
  target protein. All of these modalities are modeled as linear or cyclized
  chains drawn from the 20-letter amino-acid alphabet and evaluated by how they
  fold against the target. Small-molecule ligand generation is out of scope
  because small molecules are variable-size chemical graphs constrained by
  valence rules, requiring different model architectures and evaluation
  benchmarks.
- **Organization:** Background on co-folding architectures and how structure
  predictors are adapted for design; definitions of standard evaluation metrics;
  model families traced from structure predictors to design systems (AlphaFold,
  RoseTTAFold/RFdiffusion, Boltz, Chai, gradient-based backpropagation methods,
  Protenix, ESM); closed and undisclosed systems; a consolidated overview of
  quantitative benchmarks, wet-lab campaign results, and experimental
  conditions; and translational context plus open limitations.
- A practical indicator of progress across these methods is the number of
  candidate designs that must be synthesized and experimentally tested per
  target to obtain a binder. This number has fallen from thousands or millions
  in display-based and early computational workflows [@chai2; @rfantibody] down
  to tens of designs in recent generative campaigns \[@chai2; @rfpeptides;
  @boltzgen; @protenix_v2\].

______________________________________________________________________

# Background

## Structure prediction and co-folding architecture

- Modern protein structure prediction relies on the principle that coevolution
  between pairs of positions in a multiple sequence alignment (MSA) correlates
  with spatial proximity in the folded 3D structure. AlphaFold2 demonstrated
  this at CASP14 with a median backbone accuracy of 0.96 Å r.m.s.d.95 (Cα RMSD
  at 95% residue coverage; 95% CI 0.85–1.16 Å), compared to 2.8 Å r.m.s.d.95 for
  the next best method [@alphafold2]. AlphaFold3 extended the framework from
  single protein chains to complexes of proteins, nucleic acids, ligands, and
  ions ("co-folding") [@alphafold3].
- Most modern co-folding models follow a two-stage architecture (whereas earlier
  RoseTTAFold 1 and 2 used a parallel three-track 1D/2D/3D network running from
  input to output [@rosettafold; @rosettafold2]):
  1. **Trunk (sequence-to-pairwise reasoning):** Processes sequence and
     evolutionary inputs (Evoformer in AlphaFold2 [@alphafold2], Pairformer in
     AlphaFold3/Boltz/Protenix/Chai/RF3 \[@alphafold3; @boltz1; @chai1;
     @protenix_v1; @rosettafold3\], or folding trunk in ESMFold/ESMFold2
     \[@esm2; @esmc\]) to produce single and pair residue representations. A
     linear head on the pair representation predicts a **distogram** (a
     probability distribution over inter-residue distances for each pair of
     residues), used both as a training loss and as a differentiable surrogate
     in gradient-based design [@alphafold2; @boltzdesign1; @esmc]. The trunk is
     differentiable throughout and runs once per complex/seed [@boltz1]. Models
     differ in how evolutionary information enters the trunk:
     - **MSA-based:** Evolutionary sequences are retrieved from sequence
       databases at inference time (AlphaFold2 [@alphafold2], AlphaFold3
       [@alphafold3], RoseTTAFold [@rosettafold; @rosettafold3], Boltz
       [@boltz1], Protenix [@protenix_v1]).
     - **Protein language model (PLM)-based:** Evolutionary statistics are
       learned into model weights during pre-training, allowing single-sequence
       inference without database lookups (ESM-2/ESMFold [@esm2], ESMC/ESMFold2
       [@esmc], AtlasFold [@atlasfold]).
     - **Hybrid:** Chai-1 includes both an MSA track and a protein language
       model track and can operate with either [@chai1].
  1. **Structure or diffusion module (representations to 3D coordinates):**
     Consumes the trunk's single and pair representations to generate explicit
     3D atomic coordinates. Models differ in the coordinate-generation
     formalism, which determines inference speed and differentiability:
     - **Single-pass coordinate regression (AlphaFold2, ESMFold):** An
       end-to-end differentiable structure module using Invariant Point
       Attention (IPA) [@alphafold2; @esm2]. AlphaFold2's ablation study shows
       that removing end-to-end structure gradients reduces prediction accuracy
       [@alphafold2].
     - **Diffusion (AlphaFold3 and AF3-class co-folders, including Boltz, Chai,
       Protenix, RF3, and ESMFold2):** Generates atomic coordinates iteratively
       by denoising Gaussian noise along a stochastic differential equation
       (SDE) trajectory \[@alphafold3; @boltz1; @chai1; @protenix_v1;
       @rosettafold3; @esmc\]. FrameFlow notes that diffusion-based protein
       generators often require roughly 1,000 forward passes to generate
       high-quality samples [@frameflow].
     - **Flow matching:** Formulates generation as an ordinary differential
       equation (ODE) with straighter sampling trajectories, requiring fewer
       inference steps.
       - **FrameFlow** [@frameflow] (`10.48550/arXiv.2310.05297`): Recasts
         FrameDiff using flow matching, reporting twofold better designability
         at five times fewer sampling timesteps on unconditional protein
         monomers (not target-conditioned binders).
       - Target-conditioned binder generators using flow matching include
         **PPIFlow** [@ppiflow] (`10.64898/2026.01.19.700484`), **OriginFlow**
         [@originflow] (`10.1101/2025.04.29.651154`), **AtomFlow** [@atomflow]
         (`10.48550/arXiv.2409.12080`), and **D-Flow** [@dflow]
         (`10.1109/JBHI.2026.3683934`).
- Both diffusion and flow matching were adapted from image generation, replacing
  noised image pixels with noised atomic coordinates [@alphafold3; @frameflow].
  In AlphaFold3, the diffusion module replaced AlphaFold2's IPA structure module
  for structure prediction itself, independent of design [@alphafold3].

## From structure prediction to binder generation

- Structure prediction and binder design can operate on the same underlying
  neural network by changing which inputs are fixed. Supplying all chain
  sequences predicts the complex structure; leaving the binder chain unspecified
  or noised asks the model to generate a chain that folds against the target.
  - BoltzGen describes itself as "a single all-atom diffusion model capable of
    performing both structure prediction and protein design" [@boltzgen].
  - RFdiffusion reached the same duality by fine-tuning the RoseTTAFold
    structure predictor into a backbone generator [@rfdiffusion]. RoseTTAFold's
    3D coordinate track runs from input to output, allowing target geometry or
    active-site motifs to be supplied directly as coordinates rather than only
    pairwise distances [@rosettafold2; @rfdiffusion].
- A structure predictor alone cannot easily discover binders because it only
  evaluates a given sequence, whereas a chain of length *L* has 20^*L* possible
  sequences. Traditional display libraries and animal immunization search large
  sequence spaces experimentally, but as RFantibody notes, immunization, random
  library screening, and patient-derived isolation cannot readily be directed to
  a chosen target epitope; libraries return binders against accessible or
  immunogenic regions [@rfantibody].
- Generative design reduces the number of candidates that must be physically
  synthesized and tested per target:
  - Chai-2 characterizes prior screening and early computational approaches as
    requiring "thousands to millions of designs to reliably identify hits"
    [@chai2].
  - Recent generative and filtering workflows test tens of designs per target:
    16–30 (Protenix-v2 [@protenix_v2]), ≤20 (Chai-2 [@chai2]), ≤20 (RFpeptides
    [@rfpeptides]), 30–100 (Latent-X1 [@latentx1]), 43–101 (Germinal
    [@germinal]), and 84 (ESMFold2 [@esmc]).
  - Reported wet-lab hit rates include 16% overall for Chai-2 de novo antibodies
    [@chai2], 2–48% on soluble targets and 16–88% on GPCRs for Protenix-v2
    VHH-Fc designs [@protenix_v2], and 70.0% mean for ESMFold2 minibinders
    [@esmc].
- Two methodological factors strongly affect how reported hit rates compare
  across studies:
  - **Hit definitions vary:** BoltzProt-1 distinguishes initial *screening hits*
    (noting that these correspond to what prior binder-design papers typically
    report as binders) from *confirmed binders* verified in follow-up assays,
    reporting an 8.0% confirmed-binder rate versus a higher initial
    screening-hit rate [@boltzprot1].
  - **Target and epitope selection strongly affect success rates:** Most
    campaigns evaluate targets and epitopes selected by the authors. By
    contrast, mBER tested 1,153,241 unique VHH designs across 436 human
    cell-surface proteins (145 assayed) using randomly selected surface hotspots
    (assayed via phage display enrichment, without affinity confirmation)
    [@mber]. Its median per-design hit rate (~0.4%) was roughly two orders of
    magnitude lower than typical small-panel headline rates, while its best
    individual hotspots achieved hit rates comparable to those reported in
    smaller campaigns (up to 38% under strict filtering) [@mber].
- Unlike image generation, where outputs lack an objective structural
  correctness metric and rely on human preference, protein design can
  automatically score candidates using structure predictors.

## Ways structure predictors are used in binder design

Across the literature, binder-design systems combine sequence/structure
generation with structure predictors in three main ways:

1. **Direct reuse or joint training of a structure predictor as a generator:**
   Either fine-tuning a structure predictor's weights to denoise unknown binder
   backbones (RFdiffusion and RFdiffusion2 from RoseTTAFold \[@rfdiffusion;
   @rfdiffusion2\]) or training one all-atom diffusion model jointly for both
   structure prediction and design (BoltzGen [@boltzgen]).
1. **Generate-and-filter pipelines (no gradients during design):** Generating
   candidate backbones, designing sequences onto those backbones via inverse
   folding (most commonly ProteinMPNN [@proteinmpnn]), and ranking or filtering
   candidates after generation. Filtering uses either:
   - *Structure-prediction confidence metrics:* The standard workflow in systems
     such as RFdiffusion → ProteinMPNN → AlphaFold2 [@rfdiffusion], RFpeptides
     [@rfpeptides], BoltzGen [@boltzgen], PXDesign-d [@pxdesign], and
     Protenix-v2 [@protenix_v2]. A widely cited filtering threshold (stated in
     AlphaProteo) is interchain AF2 PAE < 10, binder-aligned binder RMSD < 1 Å,
     and pLDDT > 80 [@alphaproteo].
   - *A separately trained binding classifier:* BoltzProt-1 replaces BoltzGen's
     confidence-based ranking with BoltzPPI, a model trained on experimental
     binding outcomes [@boltzprot1].
1. **Gradient-based sequence optimization (hallucination / backpropagation):**
   Representing the designed sequence as a continuous probability distribution
   over the 20 amino acids at each of *L* positions (an *L* × 20 simplex),
   feeding this relaxed sequence into a differentiable structure predictor, and
   descending gradients of structural confidence or distogram losses while
   annealing the distribution toward discrete one-hot amino acids (BindCraft
   [@bindcraft], Germinal [@germinal], BoltzDesign1 [@boltzdesign1], PXDesign-h
   [@pxdesign], ESMFold2 [@esmc]). One exception, RFOptimization, keeps
   sequences strictly discrete and uses predictor gradients only to rank
   single-point mutations [@rfoptimization].

Three technical constraints govern how these methods work in practice:

- **Single-sequence requirement for gradient optimization:** An MSA requires a
  database search on an existing sequence and is neither defined for a sequence
  being invented nor differentiable. Gradient-based optimization must therefore
  run the designed chain in single-sequence mode. For MSA-trained models such as
  AlphaFold2 (used by BindCraft [@bindcraft]), shallow-MSA / single-sequence
  mode is documented as their weakest regime [@alphafold2]. Protein language
  models such as ESMC/ESMFold2 are natively single-sequence and can
  backpropagate through a 6B-parameter language model and folding trunk without
  leaving their training distribution [@esmc].
- **Differentiating through diffusion modules:** AlphaFold2's regression-based
  structure module is differentiable end-to-end [@alphafold2; @bindcraft]. In
  AF3-class diffusion models, unrolling hundreds or ~1,000 denoising steps to
  compute gradients is computationally impractical [@frameflow; @boltzdesign1].
  Systems address this in two ways:
  - Computing gradients from the trunk's distogram and/or confidence heads
    without backpropagating through the diffusion module (BoltzDesign1
    [@boltzdesign1], RFOptimization [@rfoptimization], and ESMFold2, which
    optimizes distogram-entropy and ESMC losses and runs its diffusion and
    confidence modules only in the final steps to score ipTM [@esmc]).
  - Replacing the 200-step diffusion decoder with a differentiable 2-step ODE
    sampler (PXDesign-h [@pxdesign]).
- **Impact of filtering and ranking on wet-lab hit rates:** Several studies show
  that candidate selection strongly influences experimental yield independently
  of the generator:
  - In BoltzProt-1, keeping the BoltzGen candidate pool fixed and replacing
    confidence scores with the trained BoltzPPI classifier raised
    confirmed-binder rates from 3.3% to 8.0% (and confirmed-target coverage from
    2/10 to 4/10) [@boltzprot1].
  - PXDesign found that Protenix and AlphaFold2-Initial-Guess (AF2-IG) filters
    retain largely non-overlapping sets of true positives [@pxdesign].
  - RFOptimization mixes multiple predictor families (RF3 and Boltz inside the
    optimization loop, holding out AlphaFold3 as an independent check) to reduce
    overfitting to a single predictor's biases [@rfoptimization].

## Openness and disclosure of methods

- Systems in this field span a wide spectrum of openness:
  - *Fully reproducible releases* providing weights, training code, and training
    datasets (OpenFold3 [@openfold3], AtlasFold [@atlasfold], BoltzGen
    [@boltzgen]).
  - *Open-weights models* under permissive licenses (MIT, Apache-2.0, BSD:
    Boltz-1 [@boltz1], Boltz-2 [@boltz2], Protenix [@protenix_v1], RF3
    [@rosettafold3], OpenDDE [@opendde], OpenGerminal [@opengerminal]) or
    non-commercial licenses (Chai-1 [@chai1], ESM3-open [@esm3]).
  - *Published wet-lab and benchmark results with undisclosed generative
    architectures* (AlphaProteo [@alphaproteo], Latent-X1 [@latentx1], Latent-X2
    [@latentx2], Chai-2's generator [@chai2]) or API-only commercial access
    without weights (BoltzProt-1 [@boltzprot1], ESM3-98B [@esm3]).
  - *Unpublished commercial or private systems* known publicly only through web
    platforms or third-party benchmark points (IsoDDE [@opendde], Chai-3,
    SeedFold [@opendde]).
- Within individual organizations, openness has shifted over time. In the Boltz
  family, Boltz-1, Boltz-2, and BoltzGen are MIT-licensed with released weights
  [@boltz1; @boltz2; @boltzgen], whereas BoltzProt-1 publishes a paper and
  wet-lab data while offering API-only commercial access [@boltzprot1].
  Similarly, AlphaFold3 was co-authored by Google DeepMind and Isomorphic Labs
  [@alphafold3], whereas Isomorphic Labs' subsequent IsoDDE model has no
  publication [@opendde; @bender_perspective].
- Because wet-lab campaigns are evaluated on author-selected targets, assays,
  and hit criteria, results from undisclosed or closed-weight systems cannot be
  independently audited or reproduced from the published papers alone
  [@bender_perspective].

______________________________________________________________________

# Evaluation metrics

Metrics fall into two categories: external metrics comparing a structure against
an experimental reference (or physical chemistry rules), and internal confidence
metrics estimated by the model itself without an experimental structure. Because
de novo designed binders have no experimental structure prior to synthesis,
computational design pipelines rely on self-estimated metrics and
self-consistency comparisons.

- **lDDT** [@lddt] (`10.1093/bioinformatics/btt473`): Local Distance Difference
  Test. Compares local interatomic distances against a reference structure
  without global superposition, so a correctly folded domain in the wrong
  relative orientation still receives a high score.
- **TM-score** [@tm_score] (`10.1002/prot.20264`): Measures global fold
  similarity to a reference structure, normalized for protein length.
- **RMSD** [@kabsch] (`10.1107/S0567739476001873`): Root-mean-square deviation
  in ångströms between two sets of atomic coordinates after optimal
  superposition (computed via Kabsch's algorithm). Against an experimental
  structure, RMSD measures prediction accuracy; in design pipelines,
  "self-consistency RMSD" compares a generated backbone against a predicted
  refolding of its own designed sequence (no experimental structure involved).
- **DockQ** [@dockq] (`10.1371/journal.pone.0161879`): Combines interface
  accuracy metrics into a single score from 0 to 1, with DockQ ≥ 0.23 commonly
  used as the acceptable-interface success threshold.
- **PoseBusters / PB-valid** [@posebusters] (`10.1039/D3SC04185A`): Pass/fail
  physical plausibility test checking chemical validity, bond geometry,
  stereochemistry/chirality, steric clashes, and internal energy, paired with a
  protein–ligand benchmark set (308 complexes in the published benchmark set
  alongside 85 Astex Diverse complexes [@posebusters]; AlphaFold3 evaluated on
  the 428-structure PoseBusters benchmark set [@alphafold3], while PoseBusters
  V2 is an updated benchmark revision without a separate publication). Reported
  by AlphaFold3 [@alphafold3], Chai-1 [@chai1], Boltz-1 [@boltz1], and Protenix
  [@protenix_v1].
- **AlphaFold2 confidence metrics** \[@alphafold2\]: Introduced with empirical
  calibration against ground-truth metrics:
  - **pLDDT:** Per-residue predicted lDDT (0–100).
  - **pTM:** Predicted TM-score for the overall structure.
  - **PAE (Predicted Aligned Error):** A residue-by-residue matrix estimating
    positional error in ångströms between pairs of residues.
- **AlphaFold-Multimer interface metrics** \[@alphafold_multimer\]: Computed
  over interchain residue pairs only:
  - **ipTM:** Interface predicted TM-score over interchain residue pairs.
  - **iPAE / interchain PAE:** PAE restricted to interchain residue pairs
    (AlphaProteo uses an interchain PAE < 10 Å cutoff [@alphaproteo]; the ipSAE
    paper suggests PAE cutoffs of 10 or 15 Å [@ipsae]).
- **ipSAE** [@ipsae] (`10.1101/2025.02.10.637595`): Restricts ipTM calculation
  to well-predicted interchain residue pairs (below a PAE cutoff such as 10 or
  15 Å), removing sensitivity to how disordered or non-interacting regions of
  the input chains are trimmed. Used in Germinal [@germinal] and the Overath et
  al. meta-analysis [@overath_meta].

| Metric         | Reference                           | What it measures                                                                                   | Introduced by                            |
| -------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **lDDT**       | Experimental structure              | Local interatomic distance accuracy without superposition                                          | lDDT [@lddt]                             |
| **TM-score**   | Experimental structure              | Length-normalized global fold similarity                                                           | TM-score [@tm_score]                     |
| **RMSD**       | Experimental or predicted structure | Å deviation after optimal superposition (accuracy only when compared to an experimental structure) | Kabsch [@kabsch]                         |
| **DockQ**      | Experimental structure              | Protein–protein interface accuracy on a 0–1 scale (threshold commonly ≥ 0.23)                      | DockQ [@dockq]                           |
| **PB-valid**   | Physical chemistry rules            | Pass/fail check for chemical validity, geometry, chirality, and clashes                            | PoseBusters [@posebusters]               |
| **pLDDT**      | Model self-estimate                 | Per-residue predicted lDDT                                                                         | AlphaFold2 [@alphafold2]                 |
| **pTM**        | Model self-estimate                 | Predicted global TM-score                                                                          | AlphaFold2 [@alphafold2]                 |
| **PAE**        | Model self-estimate                 | Residue-pair matrix of predicted positional error (Å)                                              | AlphaFold2 [@alphafold2]                 |
| **ipTM**       | Model self-estimate                 | Predicted TM-score over interchain residue pairs                                                   | AlphaFold-Multimer [@alphafold_multimer] |
| **pAE / iPAE** | Model self-estimate                 | PAE over interchain residue pairs                                                                  | AlphaFold-Multimer [@alphafold_multimer] |
| **ipSAE**      | Model self-estimate                 | ipTM restricted to well-predicted interchain residue pairs                                         | ipSAE [@ipsae]                           |

______________________________________________________________________

# AlphaFold and open reproductions

Structure prediction models that established the MSA-trunk, co-folding, and
diffusion paradigms used across subsequent open lineages and design systems.

## AlphaFold2 and open reproductions

- **AlphaFold2** [@alphafold2] (`10.1038/s41586-021-03819-2`): Single-chain
  structure predictor achieving experimental-level accuracy at CASP14 (median
  0.96 Å r.m.s.d.95, 95% CI 0.85–1.16 Å, vs. 2.8 Å r.m.s.d.95 for the next best
  method) using an MSA-driven Evoformer trunk, distogram head, and an end-to-end
  differentiable IPA structure module. Because the entire network is
  differentiable in a single regression pass, gradient-based design loops (such
  as BindCraft [@bindcraft]) can backpropagate through the full network. It is
  also widely used as a post-hoc refolding filter across design pipelines
  [@rfdiffusion; @alphaproteo].
  - *Limitations:* Accuracy drops markedly as MSA depth decreases (weakest in
    single-sequence / shallow-MSA mode), as documented in the original paper
    [@alphafold2].
- **AlphaFold-Multimer** [@alphafold_multimer] (`10.1101/2021.10.04.463034`):
  AlphaFold2 retrained specifically on multimeric protein complexes. Introduced
  ipTM and interchain PAE, which became standard filtering metrics across binder
  design. Gradient-based complex design tools (BindCraft [@bindcraft], Germinal
  [@germinal], mBER [@mber]) backpropagate through AlphaFold-Multimer rather
  than monomer AlphaFold2.
  - *Note:* Released as a bioRxiv preprint; never peer-reviewed in a journal.
- **OpenFold** [@openfold] (`10.1038/s41592-024-02272-z` ·
  [GitHub](https://github.com/aqlaboratory/openfold)): AlQuraishi Lab's
  open-source retraining of AlphaFold2; provided the structural distillation
  dataset later used to train Boltz-1 [@boltz1].

## AlphaFold3 and open reproductions

- **AlphaFold3** [@alphafold3] (`10.1038/s41586-024-07487-w`): Generalizes
  structure prediction to complexes of proteins, nucleic acids, small-molecule
  ligands, and ions. Replaces AlphaFold2's Evoformer with a simplified
  Pairformer trunk and replaces the IPA structure module with an all-atom
  diffusion module.
  - *Performance and sampling:* On the 428-structure PoseBusters benchmark set,
    outperforms classical docking (AutoDock Vina) and RoseTTAFold All-Atom
    without requiring solved pocket coordinates as input [@alphafold3]. For
    antibody–antigen complexes, reported accuracy relies on top-ranked
    predictions over 1,000 random seeds rather than the 5 seeds used for other
    classes, with accuracy still improving at 1,000 seeds [@alphafold3].
  - *Architectural and practical caveats:* Diffusion sampling prevents
    straightforward end-to-end gradient backpropagation through coordinates.
    Diffusion also introduces physical-validity failure modes documented in the
    paper: a 4.4% chirality violation rate on PoseBusters even after adding a
    chirality penalty to sample ranking, residual steric clashes, and
    hallucinated secondary structure in intrinsically disordered regions
    (mitigated via cross-distillation from AlphaFold-Multimer v2.3 predictions)
    [@alphafold3]. Predictions represent static PDB-like structures rather than
    conformational ensembles, and accuracy still degrades with shallow MSAs
    [@alphafold3]. Restricted/closed model weights motivated open reproductions
    including Boltz-1 [@boltz1], Protenix [@protenix_v1], and OpenFold3
    [@openfold3].
- **OpenFold3** [@openfold3] (`10.5281/zenodo.17485509` ·
  [GitHub](https://github.com/aqlaboratory/openfold-3)): Apache-2.0 reproduction
  of AlphaFold3 releasing model weights, training code, and the full training
  corpus (including a reproduction of AlphaFold3's 13M-sequence MGnify
  distillation dataset), enabling retraining from scratch.
  - *Caveats:* Software release rather than a peer-reviewed publication;
    benchmark claims are self-reported, and its technical report covers
    superseded `preview2` weights rather than the current `OpenBind-0` default.

______________________________________________________________________

# RoseTTAFold and RFdiffusion

Developed at the Baker Lab / Institute for Protein Design (IPD) independently of
AlphaFold, this family spans structure predictors, backbone and all-atom
diffusion generators, inverse folding models, specialized modality generators,
and a discrete gradient-based optimizer.

*Naming note:* **RoseTTAFold3 (RF3)** [@rosettafold3] is an all-atom structure
predictor (denoising coordinates for a known sequence), whereas **RFdiffusion3
(RFD3)** [@rfdiffusion3] is a generative design model (denoising coordinates
with sequence unknown, followed by inverse folding). They are distinct models
rather than versions of the same tool.

## Structure predictors

- **RoseTTAFold3 (RF3)** [@rosettafold3] (`10.1101/2025.08.14.670328`):
  BSD-licensed all-atom diffusion structure predictor benchmarked directly
  against AlphaFold3, Boltz-2, and Chai-1. Provides the distogram and confidence
  gradients used by RFOptimization [@rfoptimization]. Addresses ligand chirality
  via learned geometric features rather than inference-time guidance, predicting
  correct chirality for 88% of ligand chiral centers on its test set vs. 84% for
  AlphaFold3 and 76% for Boltz-2 without inference-time guidance (and achieving
  1.74 Å mean backbone RMSD on mixed L/D peptides vs. 1.88 Å for AF3 and 2.24 Å
  for Boltz-1x, noting that inference-time modifications "may shift the network
  outside the training distribution") [@rosettafold3].
- **RoseTTAFold All-Atom (RFAA)** [@rosettafold_all_atom]
  (`10.1126/science.adl2528`): Generalization of RoseTTAFold to proteins,
  nucleic acids, small molecules, and metals, published two months before
  AlphaFold3.
- **RoseTTAFold2 (RF2)** [@rosettafold2] (`10.1101/2023.05.24.542179`): Rebuilt
  RF1 by incrementally testing AlphaFold2 architectural ideas. Found that FAPE
  loss, recycling, distillation, and network depth drove accuracy, whereas
  AlphaFold2's Invariant Point Attention and triangle attention were not
  required: RF2 matched AlphaFold2 on monomers and AlphaFold-Multimer on
  complexes without either module, and scaled better past 1,000 residues
  [@rosettafold2]. Notes that maintaining a 3D coordinate track from input to
  output enables encoding spatial design constraints directly as coordinates
  [@rosettafold2]. Serves as the base architecture for RFAA
  [@rosettafold_all_atom] and RFpeptides [@rfpeptides].
  - *Caveat:* Remains a bioRxiv preprint (not peer-reviewed).
- **RoseTTAFold (RF1)** [@rosettafold] (`10.1126/science.abj8754`): Three-track
  (1D sequence, 2D pairwise distance, 3D coordinate) structure predictor
  developed contemporaneously with AlphaFold2; complex prediction emerged
  without dedicated multimer training via discontinuous two-segment cropping
  [@rosettafold]. Fine-tuned directly into RFdiffusion [@rfdiffusion]. As a
  structure predictor, it has been superseded and is no longer included in
  recent co-folding benchmarks.

## Generative models

- **RFdiffusion3 (RFD3)** [@rfdiffusion3] (`10.1126/science.aeh2982`): All-atom
  diffusion generator using a transformer-based U-Net modeled on AlphaFold3's
  diffusion module (Pairformer reduced from 48 to 2 layers, 168M trainable
  parameters, 100-step sampling, roughly an order of magnitude faster than
  earlier RFdiffusion versions) [@rfdiffusion3]. Unlike RFdiffusion 1 and 2, it
  is not initialized from a RoseTTAFold predictor; it is pre-trained directly on
  PDB structures and AlphaFold2-predicted distillation data [@rfdiffusion3].
- **RFdiffusion2 (RFD2)** [@rfdiffusion2] (`10.1038/s41592-025-02975-x`):
  Fine-tuned from RoseTTAFold; performs sequence-agnostic, atom-level enzyme
  active-site scaffolding from functional-group coordinates.
- **RFdiffusion (RFD1)** [@rfdiffusion] (`10.1038/s41586-023-06415-8` ·
  [GitHub](https://github.com/RosettaCommons/RFdiffusion)): Equivariant frame
  diffusion (representing each residue by its Cα position and N–Cα–C frame
  orientation) fine-tuned directly from RoseTTAFold predictor weights.
  Established the widely adopted three-step design workflow: backbone diffusion,
  sequence design with ProteinMPNN, and filtering via AlphaFold2 refolding
  [@rfdiffusion]. Outperformed earlier RoseTTAFold-based hallucination on Baker
  Lab benchmarks [@rfdiffusion].
  - *Caveat:* Reported "in silico success" metrics measure agreement with
    AlphaFold2 confidence and self-consistency RMSD filters, not experimental
    binding [@rfdiffusion].

### Inverse folding (sequence design)

Backbone generators output 3D geometry without amino-acid sequences. Inverse
folding models assign sequences to those backbones.

- **ProteinMPNN** [@proteinmpnn] (`10.1126/science.add2187` ·
  [GitHub](https://github.com/dauparas/ProteinMPNN)): Autoregressive
  message-passing neural network predicting amino-acid sequences for fixed
  protein backbones. Widely used across labs and design pipelines (including
  RFdiffusion [@rfdiffusion], RFpeptides [@rfpeptides], BindCraft surface
  redesign [@bindcraft], PXDesign [@pxdesign], and others). **AlphaDesign**
  [@alphadesign] (`10.1038/s44320-025-00119-z`) provides an alternative
  sequence-design component (an Autoregressive Diffusion Model, ADM) benchmarked
  as comparable to ProteinMPNN with complementary structural preferences.
  - *Caveat:* The ProteinMPNN paper notes that native sequence recovery (the
    standard offline training metric) does not necessarily correlate with
    whether a designed sequence folds accurately [@proteinmpnn].
- **LigandMPNN** [@ligandmpnn] (`10.1038/s41592-025-02626-1`): Extends
  ProteinMPNN to condition sequence design on non-protein context
  (small-molecule ligands, nucleic acids, metal ions). Used in BoltzDesign1
  [@boltzdesign1] and RFOptimization [@rfoptimization] alongside ProteinMPNN.

## Specialized design systems and optimization

- **RFantibody** [@rfantibody] (`10.1038/s41586-025-09721-5`): Fine-tuned
  RFdiffusion for epitope-specific design of VHHs, scFvs, and full antibodies.
  Screened designs via yeast surface display (9,000 designs per target across
  RSV sites I and III, SARS-CoV-2 RBD, and influenza HA) and *E. coli*
  expression with single-concentration SPR (95 designs per target across TcdB,
  IL-7Rα, and influenza HA), reporting confirmed hit rates of 0–2% across
  targets (best SPR affinities 78 nM on influenza HA and 1.4 µM on RSV site III)
  and stating that experimental library screening remains necessary given
  current computational success rates [@rfantibody].
- **RFpeptides** [@rfpeptides] (`10.1038/s41589-025-01929-w`): Extends
  RFdiffusion and RF2 with a cyclic relative positional encoding to generate
  head-to-tail macrocyclic peptides. Sequences are assigned with ProteinMPNN and
  filtered using AfCycDesign [@afcycdesign] (AlphaFold2 with a cyclic positional
  offset) and Rosetta interface metrics. Produced binders against all four
  targets from fewer than 20 synthesized designs each, supported by crystal
  structures [@rfpeptides]. (Latent-X1 later designed against the same targets
  and epitopes and resynthesized two RFpeptides binders for comparison
  [@latentx1].)
- **RFOptimization (RFO)** [@rfoptimization] (`10.64898/2026.09.04.749184`):
  Training-free discrete refinement of existing designs using gradients from RF3
  interleaved with Boltz/LigandMPNN resampling (detailed under Design by
  backpropagation; evaluated in silico only).

______________________________________________________________________

# Boltz

An open-weights AF3-class lineage that introduced open co-folding,
protein–ligand affinity prediction, unified prediction-and-design diffusion, and
a trained experimental-binding classifier, while transitioning to API-only
commercial access for its most recent binder model.

- **Boltz-1** [@boltz1] (`10.1101/2024.11.19.624167` ·
  [GitHub](https://github.com/jwohlwend/boltz)): First fully open (MIT-licensed)
  AF3-class all-atom co-folder, trained partly on OpenFold distillation
  structures [@boltz1; @openfold]. Enabled downstream open design tools
  including BoltzDesign1 [@boltzdesign1] and BoltzGen [@boltzgen].
  - **Boltz-1x** adds Boltz-steering, an inference-time steering method based on
    Feynman-Kac (FK) steering potentials, to reduce physical-validity errors
    (chirality violations and steric clashes) [@boltz1].
- **Boltz-2** [@boltz2] (`10.1101/2025.06.14.659707`): Adds a small-molecule
  binding-affinity prediction module and expanded conditioning controls; serves
  as the refolding filter for BoltzGen [@boltzgen] and BoltzProt-1
  [@boltzprot1].
  - *Affinity performance:* Achieves an average Pearson correlation of 0.66 on
    the 4-target FEP+ subset at over 1,000× less compute than free-energy
    perturbation (FEP), and Pearson > 0.55 on 3 of 8 blinded industrial assays
    (weaker on the other 5) [@boltz2]. Trained on single-protein ligand assays;
    does not predict protein–protein binding affinity [@boltz2].
  - *Caveats:* Structure prediction accuracy "does not significantly deviate"
    from Boltz-1 [@boltz2]. Its 2023-06-01 training cutoff overlaps standard
    FoldBench evaluation windows (2023-01-13 to 2024-11-01), causing temporal
    leakage on FoldBench comparisons (noted by Protenix-v1 [@protenix_v1],
    Protenix-v2 [@protenix_v2], and ESMFold2 [@esmc]).
- **BoltzGen** [@boltzgen] (`10.1101/2025.11.20.689494`): MIT-licensed (weights,
  training code, and data) all-atom diffusion model trained to perform both
  structure prediction (matching Boltz-2 on Boltz-2's test set) and de novo
  binder design across proteins, peptides, nanobodies, and related formats (full
  antibodies were excluded from training data), against targets ranging from
  disordered proteins to small molecules [@boltzgen]. Candidates are filtered
  via Boltz-2 refolding.
  - *Wet-lab results:* Evaluated across 8 campaigns covering 26 targets
    [@boltzgen]. On 9 novel targets (\<30% PDB sequence identity in a bound
    context), testing ≤15 designs per target yielded nanomolar binders for 6 of
    9 targets in both nanobody and miniprotein formats [@boltzgen]. On 5
    established benchmark targets, it yielded binders on 4 of 5 in each format,
    including picomolar hits on PDGFR (0.81 nM) [@boltzgen].
  - *Disclosed limitations:* Diversity collapses for binder lengths 73–76, where
    the model overwhelmingly samples ubiquitin (attributed to >900 ubiquitin
    entries in the PDB) [@boltzgen]. An earlier version (`BoltzGenv0`)
    mis-assigned fixed binder residues to the target chain during refolding,
    preventing confidence scores from filtering bad designs (yielding 0/7 hits
    on two targets where the corrected pipeline achieved 1/7 and 7/7)
    [@boltzgen]. The authors also caution that binder design is not "zero-shot"
    or "plug-and-play" and advise manual structural inspection and reruns
    [@boltzgen].
- **BoltzProt-1** [@boltzprot1] (`10.64898/2026.06.23.733997`): Combines a
  refined BoltzGen generator with **BoltzPPI**, a classifier trained directly on
  experimental binding outcomes rather than reusing structure-confidence heads.
  - *Controlled filter comparison:* On the exact same candidate pools and
    15-design-per-target budget across 10 low-homology targets (150 designs
    total), switching ranking from BoltzGen's confidence scores to BoltzPPI
    raised confirmed binders from 3.3% (5/150; 2/10 targets) to 8.0% (12/150;
    4/10 targets) [@boltzprot1].
  - *Hit definition:* Explicitly separates initial *screening hits* from
    *confirmed binders* verified via flipped assay orientation and independent
    vendor re-testing [@boltzprot1].
  - *Availability:* Commercial API and platform access only; model weights are
    not released [@boltzprot1].
- **BoltzDesign1** [@boltzdesign1] (`10.1101/2025.04.06.647261`): Gradient-based
  binder design inverting Boltz-1's Pairformer trunk and confidence heads
  (detailed under Design by backpropagation).

______________________________________________________________________

# Chai

Diffusion co-folding supporting both MSA and protein language model inputs,
followed by zero-shot antibody and minibinder design.

- **Chai-1** [@chai1] (`10.1101/2024.10.10.615955` ·
  [GitHub](https://github.com/chaidiscovery/chai-lab)): AF3-class diffusion
  co-folder carrying both an MSA track and a protein language model track,
  usable independently or together. Supports optional experimental restraints
  (pocket, contact, docking), which yield double-digit accuracy gains when
  supplied [@chai1].
  - *Performance:* Matches AlphaFold3 on PoseBusters (77% vs. 76% ligand RMSD
    success) [@chai1]. On antibody–protein interfaces, single-sequence Chai-1
    matches MSA-enabled Chai-1, and both outperform AlphaFold-Multimer v2.3 with
    MSAs, which the authors attribute to antibodies' weak evolutionary signal
    [@chai1].
  - *Licensing and benchmarking caveats:* Weights are released under a
    non-commercial license, with commercial use provided through a web server
    [@chai1]. The authors could not benchmark against AlphaFold3 or ESM-3 "due
    to commercial use restrictions," evaluating instead on CASP15 against
    AlphaFold-Multimer v2.3 [@chai1].
- **Chai-2** [@chai2] (`10.1101/2025.07.05.663018`): Zero-shot de novo antibody
  (scFv, VHH) and minibinder design system building on Chai-1 (via an
  intermediate "Chai-1d" prototype).
  - *Wet-lab results:* Testing ≤20 designs per target per format without
    affinity maturation or library screening, reported 13.7% hit rate for scFvs
    (68/496) and 20.0% for VHHs (41/205), or 16% combined, finding binders for
    26 of 52 novel targets (50%) [@chai2]. On minibinders (5 targets, 20–25
    designs/target), reported a 68% hit rate (75/111) across all 5 targets, with
    best affinity 18.3 pM (IL-7Rα) [@chai2].
  - *Disclosure caveat:* The paper describes only the folding submodule
    (`Chai-2f`, "a similar architecture as Chai-1") and does not disclose the
    generative architecture [@chai2].
- **Chai-3 (2026):** High-throughput commercial 3D foundation model accessible
  via web platform ([Chai Discovery](https://lab.chaidiscovery.com/)); no
  publication.

______________________________________________________________________

# Design by backpropagation

These systems take a pretrained structure predictor and optimize a binder
sequence by backpropagating structural confidence or distogram losses into the
sequence representation (often called hallucination or inversion). They specify
a loss function, a sequence representation (typically a continuous relaxation
over amino acids annealed to discrete tokens, or discrete mutation ranking), an
optimization schedule, and post-processing/refolding steps.

## Backpropagation through AlphaFold2

AlphaFold2's regression-based structure module allows gradients to propagate
end-to-end from predicted coordinates and confidence heads back to the input
sequence [@alphafold2].

- **ColabDesign** [@colabdesign] (`10.5281/zenodo.13309080`): Open-source
  software library (versioned Zenodo release, no separate paper) providing
  AlphaFold2 input handling, loss functions, backpropagation to input sequence
  logits, and standard annealing schedules (`design_3stage`). Used directly by
  AfCycDesign [@afcycdesign], BindCraft [@bindcraft], Germinal [@germinal], and
  mBER [@mber].
- **AfCycDesign** [@afcycdesign] (`10.1038/s41467-025-59940-7`): Modifies
  AlphaFold2's relative positional encoding to be cyclic so the network treats a
  peptide chain as closed head-to-tail (in complexes, the cyclic offset applies
  only to the peptide, leaving the target linear). Runs ColabDesign's unmodified
  three-stage continuous-to-one-hot optimization protocol [@afcycdesign].
  - *Losses and results:* Uses distogram cross-entropy for fixed-backbone
    redesign, and `(1 − pLDDT) + PAE/31 + contact term` for hallucination
    [@afcycdesign]. Generated 48,000 hallucinated models per length (7–10
    residues), clustered by backbone torsion bins and filtered by pLDDT and
    Rosetta energy; 8 experimental crystal structures all matched their design
    models within 1.0 Å [@afcycdesign].
  - *Caveat:* Its MDM2 and Keap1 binders were not hallucinated directly as
    binders; known binding motifs were grafted onto hallucinated monomeric
    scaffolds, redesigned with ProteinMPNN and Rosetta, and filtered with
    AfCycDesign confidence [@afcycdesign]. Direct de novo binder hallucination
    is listed as future work [@afcycdesign].
- **BindCraft** [@bindcraft] (`10.1038/s41586-025-09429-6`): Full-network
  backpropagation through AlphaFold-Multimer for de novo minibinder design.
  - *Gradient and induced fit:* Backpropagates a loss over AF2 confidence
    outputs (plus optional helicity and radius-of-gyration terms) into an *L* ×
    20 sequence error gradient [@bindcraft]. Randomly swaps among the five
    trained AF2-Multimer weight sets between iterations to prevent overfitting a
    single weight set [@bindcraft]. Repredicts the target structure at every
    iteration, allowing target backbone and side chains to adapt to the binder
    (observed target Cα RMSD of 0.5–5.5 Å across designs) [@bindcraft].
  - *Four-stage sequence optimization:* (1) 75 iterations in continuous logit
    space using `(1 − λ)·logits + λ·softmax(logits/T)` with λ ramped up; (2) 45
    iterations on softmax probabilities with temperature and learning rate
    decayed to 0.01; (3) 5 iterations of straight-through estimation (one-hot
    forward pass, softmax gradient backward); (4) 15 iterations of discrete
    search sampling `0.05·L` mutations per step from the previous distribution
    and retaining the best. Low-confidence trajectories are terminated at
    iteration 50 [@bindcraft].
  - *Post-processing and results:* ProteinMPNN (soluble weights) redesigns
    residues more than 4 Å from the binding interface; complexes are repredicted
    with single-sequence AF2 monomer weights and relaxed/scored with Rosetta
    (requiring 300–3,000 trajectories per 100 filter-passing designs)
    [@bindcraft]. Wet-lab testing across 12 targets (6–53 designs/target)
    yielded 10–100% hit rates (mean 46.3%) [@bindcraft].
  - *Caveats:* Runs AF2 in single-sequence mode on the designed chain, outside
    AF2's MSA training regime [@alphafold2; @bindcraft]. The paper also notes
    that AF2 ipTM predicts whether a design binds, not how tightly [@bindcraft].
- **BindCraft2:** Successor released as code (paper announced as forthcoming; no
  published benchmarks or hit rates yet). Retains the same optimization loop
  while expanding supported binder modalities (cyclic peptides, VHHs, scFv/Fab,
  ankyrin repeats, multidomain binders) and target classes (disordered motifs,
  molecular glues).

## Gradient optimization with diffusion-based predictors

Because unrolling hundreds of stochastic diffusion steps for backpropagation is
computationally impractical, these systems read gradients from the Pairformer
distogram and confidence heads instead of the diffusion coordinate module (the
same distogram-gradient strategy is also used by ESMFold2, covered under ESM
[@esmc]).

- **BoltzDesign1** [@boltzdesign1] (`10.1101/2025.04.06.647261`): Adapts the
  BindCraft optimization loop to Boltz-1 [@boltz1].
  - *Gradient path:* Places a stop-gradient on Boltz-1's diffusion module and
    optimizes interchain and intrachain contact losses over the Pairformer's
    64-bin distogram (optionally including the confidence module: confidence →
    Pairformer → sequence) [@boltzdesign1]. Because the distogram represents the
    distance distribution from which diffusion samples, optimizing it optimizes
    the distribution rather than a single sampled structure [@boltzdesign1]. On
    212 BindCraft binders, Pairformer contacts matched diffusion-sampled
    contacts with P@K > 0.5 for 76% of designs, and contact loss correlated with
    pLDDT and inter-PAE; for nucleic-acid targets, the correlation did not hold
    and the confidence module carried the loss instead [@boltzdesign1].
  - *Sequence update and post-processing:* Reimplements BindCraft's four-stage
    schedule with an initial softmax warm-up (to avoid off-distribution raw
    logits) [@boltzdesign1]. Optionally uses LigandMPNN [@ligandmpnn] to
    redesign surface residues (holding interface residues fixed) or to
    initialize logits [@boltzdesign1].
  - *Caveats:* Evaluated in silico only (no wet-lab validation); shares senior
    authors with BindCraft [@boltzdesign1; @bindcraft].
- **RFOptimization (RFO)** [@rfoptimization] (`10.64898/2026.09.04.749184`):
  Training-free discrete refinement of existing designs rather than de novo
  design from scratch.
  - *Gradient path:* Uses differentiable surrogate losses on RoseTTAFold3's
    [@rosettafold3] distogram and confidence heads (iPAE, pLDDT, ipTM),
    bypassing the diffusion module [@rfoptimization].
  - *Discrete sequence updates:* Never relaxes the sequence continuously,
    avoiding potential adversarial artifacts of continuous sequence optimization
    [@rfoptimization]. Computes mutation logits from negative normalized
    gradients (penalizing the resident amino acid), proposes a single-position
    substitution, and accepts or rejects it via Metropolis–Hastings under an
    annealed temperature, recomputing gradients after each acceptance
    [@rfoptimization].
  - *Multi-predictor cycling:* With 50% probability per step, performs a
    resampling cycle instead (folding the sequence with Boltz and redesigning it
    with LigandMPNN), while holding AlphaFold3 out as an independent check to
    guard against overfitting a single predictor [@rfoptimization].
  - *Results and caveats:* Reports lower compute cost per filter-passing design
    than BindCraft and improved AF3-refolded success (AF3 iPAE < 2.5 and ipTM >
    0.8) across protein–protein interfaces (6.73% to 22.31%), cyclic peptides
    (1.25% to 12.57%), and small-molecule binders (5.62% to 24.91%)
    [@rfoptimization]. Evaluated in silico only; no wet-lab validation
    [@rfoptimization].

## Combining structure predictors with language-model sequence priors

Structural confidence scores alone do not guarantee that a designed sequence
looks like a natural, stable protein or antibody. These methods incorporate a
protein or antibody language model as a sequence prior, either via live
backpropagation or as a fixed logit bias.

- **Germinal** [@germinal] (`10.1038/s41587-026-03187-0`): Designs antibody CDR
  loops on a user-supplied framework by combining AlphaFold-Multimer gradients
  with live gradients from an antibody language model (IgLM).
  - *Gradient and inputs:* Merges AF-Multimer structural confidence gradients
    and IgLM sequence-naturalness gradients via a weighted sum, MGDA, or
    weighted PCGrad [@germinal]. Framework positions are initialized to one-hot
    encodings with a soft sequence bias (still permitting framework mutations);
    the framework structure is supplied as a template with all CDR atoms masked
    to avoid biasing loops toward native conformations; a paratope loss directs
    contacts to CDRs rather than the framework [@germinal].
  - *Sequence update and post-processing:* Represents the sequence as a
    position-specific scoring matrix (PSSM; initialized with uniform noise,
    Gumbel noise around the framework, or zeros), updated across logit, softmax,
    and 10 semigreedy discrete steps (sampling 5 candidates per step)
    [@germinal]. AF-Multimer reads the PSSM directly while IgLM receives
    discrete tokens via a straight-through estimator [@germinal]. AbMPNN
    redesigns non-interface CDR residues; 43–101 designs per antigen are
    selected for experimental testing [@germinal].
  - *Caveats:* Nonbinders passed the ipSAE filter alongside binders, indicating
    that ipSAE did not cleanly separate them [@germinal]. Antigen structures
    were AlphaFold3 predictions, and the authors note that dependence on
    antigen-model accuracy remains an open question [@germinal].
- **OpenGerminal** [@opengerminal] (`10.64898/2026.06.25.734527`): Apache-2.0
  open-stack reimplementation of Germinal.
- **mBER** [@mber] (`10.1101/2025.09.26.678877`): Manifold Bio's VHH design
  pipeline combining AlphaFold-Multimer, ColabDesign (`design_3stage` with
  BindCraft's PAE-centered losses), structural templates, and a static ESM-2
  sequence prior.
  - *Mechanism:* Templates the target (truncated around a chosen hotspot) and
    VHH framework (predicted by NanoBodyBuilder2) separately with interchain
    contacts masked and no MSA [@mber]. Runs ESM-2 once over the masked VHH
    framework and adds the resulting logits as a fixed bias at every
    optimization step (with temperature annealing and increasing mixing weight)
    [@mber]. Ablations show that neither the sequence prior alone (disordered
    loops) nor the template alone is sufficient, whereas both together yield
    confident docked folds [@mber]. Designs are filtered by refolding with a
    held-out AF-Multimer weight set (3 recycles, scored on ipTM) [@mber].
  - *Large-scale randomized-epitope campaign:* Designed 1,153,241 unique VHHs
    across 436 human cell-surface targets (145 assayed) with hotspots drawn
    randomly from exposed surface residues [@mber]. Hit rate across epitopes on
    a single target ranged from 0.4% overall to 7.5% at the best hotspot, and
    reached 38% (8/21) in an ipTM-filtered epitope bin [@mber].
  - *Caveat:* Hits are measured by phage-display enrichment without affinity
    quantification [@mber].
- **mBER-2:** Follow-up company technical report (no peer-reviewed publication)
  extending mBER to microbinders with reported hit rates roughly an order of
  magnitude higher; does not specify whether targets and hotspots were randomly
  chosen as in the 2025 campaign.

______________________________________________________________________

# Protenix

ByteDance Seed's open all-atom modeling platform, encompassing an AF3-class
structure predictor, both diffusion-based and gradient-based binder design
modes, antibody design extensions, and an open benchmarking toolkit.

- **Protenix-v1** [@protenix_v1] (`10.64898/2026.02.05.703733` ·
  [GitHub](https://github.com/bytedance/Protenix)): Open-weights all-atom
  co-folder reproducing AlphaFold3.
  - *Controlled comparison:* Under matched training cutoff, model scale, and
    inference budget against AlphaFold3, scores higher on protein–protein and
    antibody–antigen interfaces and lower on protein–ligand and protein–DNA
    interfaces [@protenix_v1].
  - *Inference scaling and benchmark analysis:* Exhibits roughly log-linear
    accuracy scaling with sampling budget (DockQ success rising from 36.01% at 1
    seed to 47.68% at 80 seeds) [@protenix_v1]. Highlights that model-specific
    inference failures on FoldBench [@foldbench] cause different models to be
    scored on different target subsets (e.g., Boltz-1 on 252 interfaces, Chai-1
    on 251, with 237 shared), and restricting to the common intersection
    reverses which model leads [@protenix_v1]. Estimates a 95% bootstrap
    confidence interval of 49.3–56.3% DockQ success for a single 5×5 run
    [@protenix_v1].
  - *Caveat:* The recommended applied release (`Protenix-v1-20250630`) is
    trained on data past the strict cutoff used in the controlled AlphaFold3
    comparison [@protenix_v1].
- **PXDesign** [@pxdesign] (`10.1101/2025.08.15.670450`): Binder design platform
  shipping both a diffusion generator and a gradient-based hallucination
  generator built on Protenix.
  - **PXDesign-d (diffusion mode):** Generates Cartesian atomic coordinates
    using a Diffusion Transformer (DiT) backbone rather than SE(3)-equivariant
    frame representations [@pxdesign].
  - **PXDesign-h (hallucination mode):** Replaces Protenix's 200-step diffusion
    decoder with a **2-step ODE sampler**, allowing continuous sequence
    gradients to flow end-to-end through the entire predictor [@pxdesign].
    Optimizes against an ensemble of five Protenix models resampled at each step
    to prevent overfitting [@pxdesign].
  - *Results and filtering findings:* In silico, PXDesign-d and PXDesign-h each
    outperform the other on different targets; all six wet-lab campaigns used
    PXDesign-d, achieving 20–73% nanomolar hit rates on 5 of 6 targets (0/16 on
    TNFα) [@pxdesign]. In-house benchmarks compare PXDesign-h against BindCraft
    and BoltzDesign1 [@pxdesign]. Filtering analysis shows that Protenix and
    AF2-IG filters retain largely distinct true positives with little overlap,
    and that optimal confidence thresholds do not transfer reliably across
    targets [@pxdesign].
- **Protenix-v2** [@protenix_v2] (`10.64898/2026.04.10.717613`): Updated
  predictor and design platform extending generation from miniproteins to VHH,
  Fv, and full monoclonal antibodies (mAbs) in both epitope-specific and
  site-agnostic modes.
  - *Prediction:* Improves antibody–antigen DockQ > 0.23 success by 9–13
    percentage points over Protenix-v1 across three benchmark collections
    (PXMeter-AB, FoldBench-AB, AF3-AB); v2 at 5 seeds outperforms v1 at 1,000
    seeds [@protenix_v2]. Identifies cases where predictions pass PoseBusters
    despite twisted amide groups or flat sp3 centers, motivating additional
    planarity checks in PXMeter v1.1.0 [@protenix_v2].
  - *Wet-lab design:* Across a novelty-controlled soluble antigen panel (modeled
    on BoltzGen's 30%-identity filter and Chai-2's SAbDab novelty filter),
    produced BLI-confirmed binders for every tested antigen (100% target-level
    success) at 2–48% hit rates [@protenix_v2]. On four GPCRs (small, flexible
    extracellular epitopes), achieved 16–88% hit rates in VHH-Fc format and
    0–50% in full mAb format with 16–30 designs tested per target
    [@protenix_v2]. Two different epitopes on the same antigen (AMBP) yielded 4%
    and 48% hit rates, after which the authors prioritized native ligand-binding
    interfaces [@protenix_v2].
  - *Caveats:* Targets were chosen from in-stock proteins and epitopes were
    manually selected [@protenix_v2]. No direct head-to-head against Chai-2 was
    run because overlapping targets used different antibody formats
    [@protenix_v2]. Automated rankers were compared against a single human
    expert on one target [@protenix_v2].
- **PXMeter** [@pxmeter] (`10.1101/2025.07.17.664878` ·
  [GitHub](https://github.com/bytedance/PXMeter)): ByteDance Seed's open
  evaluation toolkit and hand-curated PDB benchmark set (evaluating Chai-1,
  Boltz-1, and Protenix). Version 1.1.0 (introduced in the Protenix-v2 release
  [@protenix_v2]) extends PoseBusters with sp2-planarity, amide-planarity, and
  sp3-non-planarity checks. Used externally by OpenDDE (`PXMeter-AB`)
  [@opendde].

______________________________________________________________________

# ESM

Models replacing MSA database retrieval with protein language models trained on
billions of sequences, progressing from single-sequence folding to multimodal
generation and single-sequence gradient-based binder optimization.

- **ESM-2 & ESMFold** [@esm2] (`10.1126/science.ade2574`): Demonstrated that
  scaling masked protein language models allows single-sequence 3D structure
  prediction via a folding trunk and IPA structure module without MSAs or
  structural templates at inference (used to generate the ESM Metagenomic Atlas)
  [@esm2]. Traded lower accuracy than MSA-based AlphaFold2 for much faster,
  single-sequence inference [@esm2].
- **ESM-3** [@esm3] (`10.1126/science.ads0018`): Multimodal generative
  masked-token language model representing sequence, 3D structure, and function
  as discrete token tracks, allowing any track to be prompted or generated.
  Trained at 1.4B, 7B, and 98B parameters across 2.78 billion natural proteins
  [@esm3].
  - *Results:* At 98B parameters, outperforms ESMFold on single-sequence CAMEO
    structure prediction (0.880 vs. 0.861 lDDT) [@esm3]. Generated `esmGFP`
    (prompted from six chromophore residues; 58% sequence identity to the
    nearest known fluorescent protein; experimentally fluorescent) [@esm3].
  - *Availability:* Only the 1.4B `ESM3-open` model is downloadable (academic
    use only); the 98B model is API-only [@esm3].
- **ESMC & ESMFold2** [@esmc] (`10.64898/2026.06.03.729735`): Biohub /
  EvolutionaryScale release combining a protein language model (ESMC, trained on
  ~2.8 billion sequences, with a 6B-parameter model driving structure
  prediction), a folding model built on frozen ESMC representations (ESMFold2 /
  ESMFold2-Fast), and a binder design campaign [@esmc].
  - *Architecture and structure prediction:* ESMFold2 uses 48 recurrent
    pair-state folding layers (24 in ESMFold2-Fast) feeding a diffusion
    transformer with sliding-window atom attention to generate atomic
    coordinates [@esmc]. Achieves single-sequence antibody–antigen prediction
    accuracy matching AlphaFold3 run with MSAs, with an optional detachable MSA
    encoder retained for high-perplexity sequences [@esmc]. (Independent
    benchmarking by AtlasFold places the margin between ESMFold2 and AlphaFold3
    within error bars, reversing sign depending on the run; matching rather than
    exceeding AlphaFold3 is supported across runs [@atlasfold].)
  - *Binder design:* Performs single-stage continuous gradient optimization (150
    steps, temperature annealing down to 0.01) directly through ESMC
    (evolutionary prior) and ESMFold2's folding trunk and distogram output
    across two ESMFold2 replicates, avoiding the single-sequence mismatch
    encountered when inverting MSA-trained predictors [@esmc]. Forward passes
    through the diffusion and confidence modules are run in the final
    optimization steps to compute ipTM, and candidates are ranked by ensemble
    ipTM or a distogram-entropy ipTM proxy (with a pI ≤ 6.0 filter for
    minibinders) [@esmc].
  - *Wet-lab campaign:* Tested 84 designs per cohort across 5 targets (EGFR,
    PD-L1, PDGFRβ, CTLA-4, CD45) for minibinders (36–88% hit rate, mean 70.0% at
    higher compute; best affinity 68 pM) and scFvs (15–29%, mean 21.0%) [@esmc].
    Targets were author-selected.
- **AtlasFold** [@atlasfold] (`10.64898/2026.09.04.749352`): Independent
  single-sequence folding model built on a protein language model, releasing
  training code, training data, intermediate checkpoints, and weights under an
  MIT license. Also provides an independent multi-model FoldBench evaluation
  comparing confidence-ranked and oracle selection across seven predictors
  [@atlasfold].

______________________________________________________________________

# Closed and undisclosed systems

Systems whose benchmark or wet-lab results are public (or reported by third
parties), but whose generative mechanisms, weights, or papers are withheld.

## Published results with undisclosed generative architectures

- **AlphaProteo** [@alphaproteo] (`10.48550/arXiv.2409.08022`): Google DeepMind
  generative minibinder design system and multi-stage filtering pipeline.
  - *Results:* Tested 54–172 designs per target across 8 targets, achieving 9%
    (TrkA) to 88% (BHRF1) hit rates (0/54 on TNFα) and picomolar/nanomolar
    affinities (best 82 pM on IL-7Rα) [@alphaproteo]. Also resynthesized and
    re-assayed RFdiffusion's published designs (including nonbinders) by yeast
    display [@alphaproteo].
  - *Disclosure:* Describes the generator only as "a generative model trained on
    structure and sequence data from the PDB and a distillation set of AlphaFold
    predictions." Discloses its filtering thresholds (`interchain AF2 pAE < 10`,
    `binder-aligned binder RMSD < 1 Å`, `pLDDT > 80`) [@alphaproteo].
- **Latent-X1** [@latentx1] (`10.48550/arXiv.2507.19375`) and **Latent-X2**
  [@latentx2] (`10.48550/arXiv.2512.20263`): Latent Labs' atom-level binder
  design platform for macrocycles and minibinders (X1) and low-immunogenicity,
  drug-like antibodies and macrocycles (X2). Architecture is described only as
  "our proprietary architecture"; candidates are filtered using ipTM/PAE and
  self-consistency [@latentx1; @latentx2].
  - *Wet-lab results and comparisons:* Latent-X1 achieved 10–64% hit rates on
    minibinders (5 targets; best < 0.01 nM) and 91–100% on macrocycles (3
    targets; 11–17 peptides tested) [@latentx1]. Latent-X1 designed macrocycles
    against RFpeptides' targets and epitopes and resynthesized RFpeptides' two
    best binders for direct affinity comparison (MDM2: 5.35 µM for Latent-X1 vs.
    8.38 µM replicated RFpeptides; MCL-1: 18.4 µM vs. 10.0 µM) [@latentx1].
    Because only the two winning binders were resynthesized rather than an
    entire campaign, hit-rate comparisons (91–100% vs. RFpeptides' published
    21–38%) compare different assays [@latentx1; @rfpeptides]. Latent-X2
    reported macrocycle binders on 2 targets (9/10 PHD2, 8/10 K-Ras G12D; best
    1.54 nM), VHH/scFv binders on 9 of 18 targets (50% target-level success;
    best 26.2 pM HDAC8 scFv), and developability and low-immunogenicity profiles
    matching or exceeding approved antibody therapeutics [@latentx2].
- *Related entries covered above:* **Chai-2** [@chai2] (generative architecture
  undisclosed) and **BoltzProt-1** [@boltzprot1] (API-only, weights
  undisclosed).

## Systems without publications

- **OpenDDE** [@opendde] (`10.48550/arXiv.2607.03787` ·
  [GitHub](https://github.com/aurekaresearch/OpenDDE)): Apache-2.0 all-atom
  co-folder building on Protenix-v1 and OpenFold3 by scaling the Pairformer
  hidden dimension from 128 to 384 (3× wider, increasing Pairformer parameters
  ~3× and compute ~9×), adding an atom-level refinement stage prior to
  diffusion, and training prediction and design jointly (design capabilities
  remain on the roadmap; evaluated as a structure predictor) [@opendde].
  Provides a third-party antibody–antigen comparison across AlphaFold3, Boltz-1,
  Chai-1, Protenix-v1, and OpenFold3, as well as the only public scaling-curve
  measurements for IsoDDE and SeedFold [@opendde].
- **IsoDDE** (Isomorphic Labs): Private system with no publication, weights, or
  disclosed architecture; known publicly only as reference points on OpenDDE's
  scaling curves [@opendde] (also noted as lacking public technical verification
  by Bender et al. [@bender_perspective]).
- **Chai-3** and **SeedFold**: Commercial web platform (Chai-3) and unpublished
  model appearing on OpenDDE's scaling curve (SeedFold [@opendde]); no
  publications.

______________________________________________________________________

# Quantitative overview and evaluation conditions

## Prediction accuracy on a shared target set (FoldBench)

**FoldBench** [@foldbench] (`10.1038/s41467-025-67127-3`) is a peer-reviewed
all-atom structure prediction benchmark of 1,522 assemblies across nine tasks
(monomers, protein–protein, antibody–antigen, protein–ligand, and
protein–nucleic acid interfaces), scored with lDDT, DockQ, and RMSD.

Because models fail on different inputs (e.g., out-of-memory errors, unsupported
glycans, token limits), Protenix-v1 reports FoldBench results restricted to the
**common intersection** of targets completed by all compared models
[@protenix_v1].

- *Metrics:* Monomer, DNA, and RNA columns are mean lDDT. Protein–protein,
  antibody–antigen, protein–RNA, and protein–DNA are DockQ success rate (DockQ ≥
  0.23, %). Protein–ligand is joint success rate (ligand RMSD < 2 Å and lDDT-PLI
  \> 0.8, %) [@protenix_v1].

| Model                          | Monomer | Prot–Prot | Ab–Ag | Prot–Lig | Prot–RNA | Prot–DNA |    DNA |    RNA |
| ------------------------------ | ------: | --------: | ----: | -------: | -------: | -------: | -----: | -----: |
| AlphaFold3 [@alphafold3]       |  0.8803 |     71.73 | 48.75 |    62.59 |    65.22 |    75.91 | 0.5278 | 0.6140 |
| Boltz-1 [@boltz1]              |  0.8664 |     68.35 | 34.38 |    54.65 |    65.22 |    67.15 | 0.3388 | 0.4416 |
| Chai-1 [@chai1]                |  0.8639 |     67.51 | 23.12 |    50.79 |    50.00 |    66.06 | 0.4574 | 0.4852 |
| HelixFold3                     |  0.8547 |     65.40 | 28.75 |    52.38 |    52.17 |    49.27 | 0.2909 | 0.5487 |
| Protenix-v0.2.0 [@protenix_v1] |  0.8622 |     66.24 | 35.62 |    51.02 |    56.52 |    64.60 | 0.4384 | 0.5903 |
| Protenix-v0.5.0 [@protenix_v1] |  0.8717 |     68.06 | 43.94 |    58.49 |    59.37 |    68.02 | 0.4960 | 0.6046 |
| Protenix-v1 [@protenix_v1]     |  0.8857 |     72.70 | 52.31 |    62.54 |    68.46 |    69.13 | 0.5693 | 0.6547 |

- *Conditions:* Target counts: 287 monomers, 237 protein–protein, 160
  antibody–antigen, 441 protein–ligand, 46 protein–RNA, 274 protein–DNA, 14 DNA
  monomers, 15 RNA monomers. PDB release window: 2023-01-13 to 2024-11-01,
  homology-reduced against a reproduction of AlphaFold3's 2021-09-30 training
  set. Protocol: 5 seeds × 5 diffusion samples, 10 recycles, top-ranked
  prediction [@protenix_v1].
- *Provenance:* AlphaFold3, Boltz-1, Chai-1, HelixFold3, and Protenix-v0.2.0
  rows were recomputed by the Protenix-v1 authors from published per-instance
  logs with the intersection filter applied; Protenix-v0.5.0 and Protenix-v1 are
  the authors' own runs (Protenix-v1 bootstrapped over 5-seed draws from 20
  seeds) [@protenix_v1].
- *Boltz-2 absence:* Boltz-2 [@boltz2] is excluded because its 2023-06-01
  training cutoff overlaps the benchmark window (noted by Protenix-v1
  [@protenix_v1], Protenix-v2 [@protenix_v2], and ESMFold2 [@esmc]).
- *Summary pattern:* Monomer accuracy is tightly clustered (0.85–0.89 lDDT),
  protein–protein spans ~7 percentage points (65.4–72.7%), and antibody–antigen
  spans more than a factor of two (23.1–52.3%) [@protenix_v1].

## Sensitivity of reported metrics to evaluation definitions

Identical metric names can yield different values depending on target filtering,
averaging unit, and run protocol:

**AlphaFold3 on FoldBench antibody–antigen:**

|      Reported | Source                     | Condition                                                                                     |
| ------------: | -------------------------- | --------------------------------------------------------------------------------------------- |
|        47.90% | FoldBench [@foldbench]     | n = 167 (out of 172 Ab–Ag pairs), no intersection filter                                      |
|        48.75% | Protenix-v1 [@protenix_v1] | n = 160, common intersection of compared models                                               |
| 48.8% (0.488) | OpenDDE [@opendde]         | AlphaFold3 re-run by OpenDDE on FoldBench-AB (n = 160; OpenDDE reaches 0.700 on the same set) |

**Chai-1 on antibody interfaces (clustering vs. per-interface averaging):**

|      Reported | Source                 | Averaging unit                                                            |
| ------------: | ---------------------- | ------------------------------------------------------------------------- |
| 52.9% (0.529) | Chai-1 [@chai1]        | Per 40%-identity interface cluster (n = 122 clusters from 268 interfaces) |
|         25.2% | FoldBench [@foldbench] | Per interface (n = 123 antibody targets)                                  |

Boltz-1 uses a third convention for "DockQ success rate": averaging per
interface within each complex first, then across complexes [@boltz1].

**Intersection filtering on FoldBench protein–protein (Protenix-v1 analysis
[@protenix_v1]):**

| Model             |    As published | Common set (n = 237) |
| ----------------- | --------------: | -------------------: |
| Boltz-1 [@boltz1] | 172/252 = 0.683 |      162/237 = 0.684 |
| Chai-1 [@chai1]   | 172/251 = 0.685 |      160/237 = 0.675 |

## Confidence-based ranking versus oracle selection

Multi-sample predictors select a top prediction using internal confidence scores
("rank"). Comparing this against selecting the best generated sample using the
experimental reference ("oracle", unavailable at inference) measures how much
accuracy is lost in candidate ranking [@atlasfold].

**AtlasFold evaluation on FoldBench antibody–antigen (172 targets, DockQ > 0.23,
%) \[@atlasfold\]:**

| Model                                  |   Rank | Oracle |
| -------------------------------------- | -----: | -----: |
| AlphaFold3 [@alphafold3]               | 49.285 | 66.168 |
| Protenix-v1 [@protenix_v1]             | 44.945 | 65.818 |
| ESMFold2 (MSA) [@esmc]                 | 52.270 | 63.427 |
| ESMFold2 (seq only) [@esmc]            | 48.602 | 61.489 |
| AtlasFold-M [@atlasfold]               | 46.955 | 64.733 |
| AF-Multimer v2.3 [@alphafold_multimer] | 40.924 | 52.921 |
| Boltz-1 [@boltz1]                      | 34.967 | 39.505 |

**AtlasFold evaluation on FoldBench protein–protein (278 targets, DockQ > 0.23,
%) \[@atlasfold\]:**

| Model                                  |   Rank | Oracle |
| -------------------------------------- | -----: | -----: |
| Protenix-v1 [@protenix_v1]             | 74.445 | 81.572 |
| ESMFold2 (MSA) [@esmc]                 | 73.230 | 77.237 |
| AlphaFold3 [@alphafold3]               | 73.006 | 78.028 |
| Boltz-1 [@boltz1]                      | 71.120 | 76.632 |
| ESMFold2 (seq only) [@esmc]            | 69.216 | 74.071 |
| AF-Multimer v2.3 [@alphafold_multimer] | 65.206 | 68.615 |
| AtlasFold-M [@atlasfold]               | 63.358 | 71.560 |

- *Conditions:* Mean across 252 five-seed subsets drawn from 10 seeds,
  template-free throughout, metrics computed with OpenStructure 2.9.1.
  AlphaFold3, Boltz-1, Protenix-v1, and ESMFold2-MSA used MSAs from the
  AlphaFold3 pipeline; ESMFold2 (seq only) and AtlasFold-M ran without MSAs
  [@atlasfold].
- *Observations:* The rank-to-oracle gap is 11–21 percentage points on
  antibody–antigen (4.5 points for Boltz-1) and 3–8 percentage points on
  protein–protein [@atlasfold]. Similarly, FoldBench notes that an accurate
  CDR-H3 loop is necessary but not sufficient for correct antibody–antigen
  docking, and per-sample confidence scores do not reliably select near-native
  poses [@foldbench].
- *Seed-scaling figures:* AlphaFold3 reported antibody–antigen results ranked
  over 1,000 seeds rather than 5 [@alphafold3]; Protenix-v1 DockQ success rose
  from 36.01% (1 seed) to 47.68% (80 seeds) [@protenix_v1]; OpenDDE reported
  oracle success on FoldBench-AB rising from ~66% (1 seed) to >90% at several
  hundred seeds [@opendde].

## Wet-lab and in-silico design campaigns

Campaigns are grouped by the type of experimental evidence reported and ordered
within each group by designs tested per target (ranging from 5 to 9,000).

### Binding confirmed across two assay formats

| System                    | Modality, targets             |                                Tested | Outcome                                                                  | Best affinity                                      |
| ------------------------- | ----------------------------- | ------------------------------------: | ------------------------------------------------------------------------ | -------------------------------------------------- |
| BoltzProt-1 [@boltzprot1] | VHH, 10 low-homology targets  |                       15/target (150) | 12 confirmed binders (8.0%); BoltzGen on same pools and budget: 5 (3.3%) | not reported                                       |
| Germinal [@germinal]      | scFv tested as Fab, 2 targets |                             48/target | 3/48 PD-L1 and 1/48 IL-3 confirmed on both SPR and BLI                   | 360 nM SPR / 650 nM BLI                            |
| Latent-X1 [@latentx1]     | Minibinders, 5 targets        | 100/target HT-BLI, 88/target mDisplay | 10–64% per target; platforms correlate at Pearson r = 0.68–0.79          | < 0.01 nM (IL-7Rα, SC2RBD)                         |
| Germinal [@germinal]      | VHH, 4 targets                |            101 / 46 / 43 / 52 ordered | 7 / 2 / 4 / 5 confirmed by BLI after split-luciferase screen             | 170 nM (PD-L1); 42 nM after Legobody rescaffolding |

*Notes:* BoltzProt-1 confirmed binders via flipped assay orientation and
independent vendor re-testing [@boltzprot1]. Germinal's quoted VHH hit fractions
use the BLI sub-denominators (25 / 11 / 11 / 20 out of 101 / 46 / 43 / 52
ordered) [@germinal]. Latent-X1 noted robust dynamic range for mammalian display
on 3 of 5 targets [@latentx1].

### Single assay format

| System                     | Modality, targets                     |                        Tested | Hit rate                                               | Best affinity                                 |
| -------------------------- | ------------------------------------- | ----------------------------: | ------------------------------------------------------ | --------------------------------------------- |
| Latent-X2 [@latentx2]      | Macrocycles, 2 targets                |                     10/target | 9/10 (PHD2), 8/10 (K-Ras G12D)                         | 1.54 nM (PHD2)                                |
| RFpeptides [@rfpeptides]   | Macrocycles, 4 targets                | 6–14 tested of 11–27 selected | 2–4 hits per target                                    | 6 nM (GABARAP)                                |
| BoltzGen [@boltzgen]       | VHH and proteins, 9 novel targets     |                     15/target | Binders on 6/9 targets, both modalities                | 6.1 nM VHH (PMVK); 9.8 nM protein (MZB1)      |
| PXDesign [@pxdesign]       | Minibinders, 6 targets                |                   9–17/target | 20–73% on 5 targets; 0/16 on TNFα                      | "multiple nanomolar" (no exact value in text) |
| Latent-X1 [@latentx1]      | Macrocycles, 3 targets                |                  11–17/target | 91 / 100 / 94%                                         | 5.35 µM (MDM2)                                |
| Chai-2 [@chai2]            | scFv + VHH, 52 targets                |             ≤20/target/format | 13.7% scFv (68/496), 20.0% VHH (41/205); 26/52 targets | < 1 nM (EFNA5 scFv, avidity-flagged)          |
| BoltzGen [@boltzgen]       | VHH and proteins, 5 benchmark targets |                  15–20/target | Binders on 4/5 targets                                 | 0.81 nM (PDGFR)                               |
| Latent-X2 [@latentx2]      | VHH and scFv, 18 targets              |            4–24/target/format | Binders on 9/18 targets; up to 25% of designs          | 26.2 pM (HDAC8 scFv)                          |
| Chai-2 [@chai2]            | Minibinders, 5 targets                |                  20–25/target | 68% (75/111), binders on 5/5 targets                   | 18.3 pM (IL-7Rα)                              |
| Protenix-v2 [@protenix_v2] | VHH-Fc and mAb, 4 GPCRs               |                  16–30/target | VHH-Fc 16 / 62 / 40 / 88%; mAb 0 / 17 / 50 / 44%       | 112 pM (GPRC5D, avidity)                      |
| Protenix-v2 [@protenix_v2] | VHH-Fc, soluble targets               |                   figure only | 2–48% per target; binders on all targets               | figure only                                   |
| BindCraft [@bindcraft]     | Minibinders, 12 targets               |                   6–53/target | 10–100%, mean 46.3%                                    | < 1 nM (PD-1, bivalent Fc); 5 nM (CbAgo)      |
| ESMFold2 campaign [@esmc]  | Minibinders, 5 targets                |                     84/cohort | 36–88%, mean 70.0% at higher compute                   | 68 pM (target not stated in text)             |
| ESMFold2 campaign [@esmc]  | scFv, 5 targets                       |                     84/cohort | 15–29%, mean 21.0% at higher compute                   | not reported                                  |
| RFdiffusion [@rfdiffusion] | Minibinders, 5 targets                |                     95/target | 19% pooled over 475                                    | 28 nM (influenza HA)                          |
| AlphaProteo [@alphaproteo] | Minibinders, 8 targets                |                 54–172/target | 9% (TrkA) to 88% (BHRF1); 0/54 on TNFα                 | 82 pM (IL-7Rα)                                |

*Cross-cutting experimental factors:*

- **Avidity:** Several headline affinities come from bivalent Fc fusions or
  avidity-affected formats: Protenix-v2's 112 pM (and its VHH-Fc constructs
  except VEGF-A) [@protenix_v2], four of Chai-2's ten quoted miniprotein
  affinities plus its sub-nanomolar EFNA5 scFv [@chai2], and BindCraft's PD-1
  bivalent Fc construct (exact K_D undetermined) [@bindcraft].
- **Attrition between selection and testing:** Some designs fail synthesis or
  expression before testing. RFpeptides selected 27 macrocycles for MCL-1 (14
  tested) and 26 for RbtA (11 tested) [@rfpeptides]. Latent-X1's macrocycle
  rates cover 11–17 synthesized peptides out of 30 submitted (700 generated)
  [@latentx1]. PXDesign reports both denominators for PD-L1: 72.7% of designs
  tested vs. 47.1% of designs sent for expression (Table 5, six excluded for low
  expression) [@pxdesign].
- **Target-level vs. per-design rates:** Some studies emphasize target-level
  success (fraction of targets with ≥1 binder: BoltzGen [@boltzgen], Protenix-v2
  [@protenix_v2], Latent-X2 [@latentx2]), while others report per-design hit
  rates (fraction of tested designs that bind: Chai-2 [@chai2], PXDesign
  [@pxdesign], BindCraft [@bindcraft], ESMFold2 [@esmc]).

### Display or enrichment signal without affinity measurement

| System                   | Modality, targets               |                      Tested | Outcome                                                                                                                                       |
| ------------------------ | ------------------------------- | --------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------- |
| BoltzGen [@boltzgen]     | VHH, 2 targets                  |     7/target, yeast display | 1/7 and 7/7 showing signal; binding "at best 2 µM", no EC50 computable                                                                        |
| RFantibody [@rfantibody] | VHH, 3 targets                  |              95/target, SPR | 0–2% range                                                                                                                                    |
| RFantibody [@rfantibody] | VHH, 4 targets                  | 9,000/target, yeast display | 0–2% per target (best SPR affinities 78 nM HA, 1.4 µM RSV site III)                                                                           |
| mBER [@mber]             | VHH, 145 of 436 targets assayed |   1,153,241 designs, pooled | 45% (65/145) of targets with statistically elevated rate; per-design rate 0.02–8%, median ≈ 0.4%; 38% (8/21) in one ipTM-filtered epitope bin |

*Notes:* mBER notes phage display cannot quantify exact binding affinities
[@mber]. RFantibody notes yeast-display screening remains necessary given
current success rates [@rfantibody].

### Functional readout without direct binding assay

| System               | Modality, target             | Tested | Outcome                                                                                                                            |
| -------------------- | ---------------------------- | -----: | ---------------------------------------------------------------------------------------------------------------------------------- |
| BoltzGen [@boltzgen] | Peptides, NPM1               |      5 | 1/5 showed nucleolar co-localization in live cells (does not confirm specific disordered-region binding)                           |
| BoltzGen [@boltzgen] | Antimicrobial peptides, GyrA |  1,808 | 352 (19.5%) inhibited *E. coli* growth ≥4-fold; 54 lost activity when the three closest interface residues were mutated to alanine |

### In-silico evaluation only

- **BoltzDesign1** [@boltzdesign1] and **RFOptimization** [@rfoptimization]
  report computational metrics without wet-lab testing.
- **RFOptimization** [@rfoptimization] improves AF3-refolded success (defined as
  AF3 iPAE < 2.5 and ipTM > 0.8, with AF3 held out of optimization) from 6.73%
  to 22.31% on protein–protein interfaces, 1.25% to 12.57% on cyclic peptides,
  and 5.62% to 24.91% on small-molecule binders (denominators not stated).

## Binding definitions across studies

| Paper                               | Stated criterion for calling a design a binder                                                                                                                                                                                |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BoltzProt-1 [@boltzprot1]           | Clean sensorgram or similarly conclusive data confirming binding; affinity reported only when kinetic data support a fit                                                                                                      |
| Latent-X2 [@latentx2]               | Reference-subtracted single-point BLI > 0.1 nm advances to kinetics; multi-point BLI kinetics reported for global fits with R² > 0.95 (R² > 0.90 with visual review for AHSP)                                                 |
| ESMFold2 campaign [@esmc]           | Two definitions: stringent target-specific cutoffs (0.25–0.4 nm, borderline cases manually inspected) and inclusive universal > 0.1 nm; both require probe-loading signal > 0.5 nm and positive exponential association curve |
| Chai-2 [@chai2]                     | Binding-positive curve signature with signal > 0.1 nm above background and > 300% of background                                                                                                                               |
| PXDesign [@pxdesign]                | BLI response > 0.06 nm at 1 µM, followed by measured K_D < 1,000 nM                                                                                                                                                           |
| Protenix-v2 [@protenix_v2]          | BLI response > background + 0.05 nm (most hits subsequently showed K_D < 1,000 nM)                                                                                                                                            |
| AlphaProteo [@alphaproteo]          | Yeast-display flow-cytometry binding signal > 0.2 (raised to 1.3 for IL-17A due to background)                                                                                                                                |
| BoltzGen [@boltzgen]                | Quantifiable sensorgram, or association signal ≥ 300% of negative control where kinetic fitting failed                                                                                                                        |
| RFdiffusion [@rfdiffusion]          | Single-point BLI at 10 µM ≥ 50% of positive control response                                                                                                                                                                  |
| Germinal [@germinal]                | Expression luminescence > 150,000 RLU and rising binding ratio between two timepoints, followed by detectable BLI binding                                                                                                     |
| mBER [@mber]                        | Per-sequence order statistic across replicate wells above threshold, set so expected false positives per target < 1                                                                                                           |
| BindCraft [@bindcraft]              | Binding observed on SPR; no numeric threshold stated                                                                                                                                                                          |
| RFpeptides [@rfpeptides]            | Binding signal at 100 µM by SPR single-cycle kinetics; no numeric threshold stated                                                                                                                                            |
| Latent-X1 (macrocycles) [@latentx1] | Measurable binding signal by SPR; no numeric threshold stated                                                                                                                                                                 |

*BoltzProt-1 distinction:* Separately defines *screening hits* (initial
sensorgrams suggesting interaction, including ambiguous signals) and *confirmed
binders* (clean sensorgrams resolved by varying capture levels, adjusting target
concentrations, or inverting assay orientation) [@boltzprot1].

## Notes on comparability and data availability

- **Cross-study comparability:** No two wet-lab de novo design campaigns share a
  common benchmark protocol; each selects its own targets, epitopes, assay
  format, and threshold. Recurring targets include PD-L1, IL-7Rα, InsulinR,
  TrkA, TNFα, and SARS-CoV-2 RBD, sometimes sharing hotspot definitions, but
  assays remain separate.
- **Independent re-measurements of prior designs:** Three studies resynthesized
  another group's molecules under their own assays:
  - *AlphaProteo* [@alphaproteo] resynthesized RFdiffusion's [@rfdiffusion]
    published designs (including nonbinders) and tested them by yeast display,
    recovering 16% vs. RFdiffusion's published 33% on IL-7Rα and 0% vs. 6% on
    TrkA (attributed to assay format and 10–20× lower target concentration).
  - *Latent-X1* [@latentx1] resynthesized RFpeptides' [@rfpeptides] two best
    macrocycles, measuring affinities 4.4× and 5× weaker than published;
    Latent-X1's best binder led on MDM2 (5.35 vs. 8.38 µM) and trailed on MCL-1
    (18.4 vs. 10.0 µM).
  - *Latent-X2* [@latentx2] resynthesized two RaPID mRNA-display macrocycles
    using a different cyclization chemistry than its own designs.
- **Figure-only values in source publications:** Per-class headline tables for
  AlphaFold3 (Extended Data Table 1 / Fig. 1c [@alphafold3]), Boltz-1 [@boltz1],
  Boltz-2 [@boltz2], RoseTTAFold2 [@rosettafold2], and Protenix-v2's
  soluble-target per-target denominators/affinities (Fig. 4A [@protenix_v2])
  appear only in figures/images rather than extractable text (per-epitope ratios
  2/50 and 13/27 on AMBP and 12/50 on IDI2 come from BoltzProt-1's transcription
  of Protenix-v2 Fig. 4A [@boltzprot1]). ESMFold2 campaign rates come from its
  Figure 3, where shading distinguishing stringent vs. inclusive cutoffs is
  image-only [@esmc].
- **Internal discrepancy in BoltzProt-1:** Table 1 lists revised screening hits
  as 7/150 (4.7%) for BoltzGen and 14/150 (9.3%) for BoltzProt-1, whereas the
  prose states 14/150 (9.3%) and 24/150 (16.0%). Confirmed-binder figures of
  5/150 (3.3%) and 12/150 (8.0%) are consistent in both places [@boltzprot1].
- **OpenFold3 external check:** Because OpenFold3 [@openfold3] has no
  peer-reviewed paper, its public metrics come from its repository and a
  `preview2` technical report. Protenix-v2's external run of
  `OpenFold3-preview2` measured 69.29% DockQ success on 267 FoldBench
  protein–protein interfaces (vs. 70.79% in public FoldBench tables), noting a
  difference in MSA pipelines [@protenix_v2].

______________________________________________________________________

# Conclusion

## Translational context: binder design and drug discovery

- Most binder-design papers explicitly motivate their work through therapeutic
  development, including automating drug discovery (BoltzGen [@boltzgen]),
  optimizing species cross-reactivity (Chai-2 [@chai2]), reducing IgE binding in
  patient-derived samples (BindCraft [@bindcraft]), matching approved antibody
  developability (Latent-X2 [@latentx2]), and accelerating protein therapeutics
  (mBER [@mber]).
- **Bender et al., *AI in drug discovery*** [@bender_perspective]
  (`10.1038/s41573-026-01496-2`): *Nature Reviews Drug Discovery* Perspective
  (August 2026; 16 authors across academia, pharma, and biotech; 221 references)
  evaluating a decade of AI in drug R&D against clinical delivery of safer, more
  efficacious medicines. Finds strong technological progress but limited
  evidence of clinically relevant impact so far [@bender_perspective].
  - *Model validation vs. process validation:* Distinguishes validating a model
    on held-out benchmarks or isolated assays (including structure prediction
    and in vitro binding hit rates) from validating whether it improves
    downstream drug-discovery decisions. Notes that AlphaFold's success is model
    validation for protein folding rather than process validation in drug
    discovery [@bender_perspective].
  - *Biologics vs. small molecules:* Attributes part of recent clinical approval
    gains to increased investment in biologics (higher average clinical success
    and IP protection than small molecules). For protein design (specifically
    citing RFdiffusion, ProteinMPNN, BoltzGen, and Chai-2 in Table 3), notes
    that "although binding is relatively easier to predict, functional effects
    and developability also remain challenges." This parallels small-molecule
    discovery (Box 1), where over 10⁶ bioactive ligands exist in ChEMBL/PubChem
    compared to ~10³ marketed drugs [@bender_perspective].
  - *Evaluation and openness:* Emphasizes matching metrics to the task setting
    (selection, deselection, quantification; Box 2), cautions that every model
    behaves locally outside its training distribution, and observes that
    open-source co-folding models have largely caught up with closed-source ones
    while closed in-house systems such as IsoDDE provide too few technical
    details for independent verification [@bender_perspective].
  - *Scope caveat:* Secondary Perspective whose primary evidence base is
    small-molecule and clinical pipeline data; biologic developability relies on
    a single benchmark preprint (FLAb2) [@bender_perspective].

## Open technical and methodological limitations

1. **Developability, function, and immunogenicity:** Nearly all open systems
   generate, filter, and report solely on binding. Latent-X2 notes that
   therapeutic campaigns often fail "not because they lack binding, but because
   binding alone is insufficient when clinical success demands developability
   and low immunogenicity" [@latentx2]. Latent-X2 reports developability and
   low-immunogenicity data for AI-designed antibodies, though its generative
   architecture is undisclosed [@latentx2].
1. **Protein–protein binding affinity prediction:** Current scoring functions
   act primarily as binary binding indicators. BindCraft reports that AlphaFold2
   ipTM predicts whether a design binds rather than its affinity (K_D)
   [@bindcraft]. Boltz-2's affinity module applies only to small-molecule
   ligands and single-protein targets, not multimeric protein–protein
   interactions [@boltz2]. Binding affinity is therefore measured experimentally
   after design rather than predicted beforehand.
1. **Targets without experimental structures:** Most published wet-lab campaigns
   design against experimentally solved structures or high-confidence predicted
   structures. Germinal explicitly notes that how strongly design success
   depends on predicted antigen-model accuracy "remains an open question"
   [@germinal].
1. **Absence of shared, blinded prospective benchmarks for de novo binder
   design:** No two de novo campaigns were evaluated on a shared standardized
   benchmark, and full-campaign independent replication is rare (AlphaProteo's
   yeast-display re-testing of RFdiffusion's published set, including
   nonbinders, is the sole example [@alphaproteo; @rfdiffusion]).
   - **AIntibody challenge** [@aintibody] (`10.1038/s41587-026-03238-6`): The
     field's main blinded, prospective wet-lab benchmark, evaluating 511
     antibodies from 29 organizations across three tasks, expressed as full IgGs
     and assayed independently under one protocol (HT-SPR, KinExA, and a
     five-assay developability panel with explicit pass thresholds)
     [@aintibody].
   - *Key findings:* The top computational design (95 pM) was statistically
     indistinguishable from the best wet-lab campaign antibody (113 pM); a
     non-ML consensus of selection data ranked third [@aintibody]. On Challenge
     2 (ranking sequences by affinity within HCDR3 clusters), only 1 of 26
     participating groups beat random clone selection [@aintibody]. On the
     out-of-library task, 30.4% of designs were nonbinders and the
     highest-affinity winner (2.9 pM) failed to elute from the HIC
     developability column [@aintibody]. The Challenge 1 winner used a
     Protenix-derived pairformer with a DPO fitness head (disclosed with code)
     [@aintibody].
   - *Limitations:* Evaluated a single well-characterized antigen (SARS-CoV-2
     RBD, described as "deliberately primed for success"); represents a Q1-2025
     snapshot; several prominent de novo antibody-design groups did not
     participate; and tests library-conditioned antibody engineering (with
     measured affinities provided in Challenges 2 and 3) rather than
     target-conditioned de novo binder design [@aintibody].
1. **Per-design discrimination limits of confidence filters:**
   Structure-prediction confidence metrics (ipTM, ipSAE) enrich hit rates across
   large candidate pools (as observed in mBER at million-design scale [@mber]),
   yet frequently fail to separate individual binders from nonbinders (as seen
   in Germinal, where nonbinders cleared the same ipSAE threshold as binders
   [@germinal]).
   - **Overath et al. binder meta-analysis** [@overath_meta]
     (`10.1101/2025.08.14.670059`): Independent group that pooled 3,766
     experimentally tested designs from six published campaigns across 15
     targets and re-scored all designs under a unified computational pipeline
     [@overath_meta]. AlphaFold3 ipSAE was the strongest single predictor of
     experimental binding overall, yet its average precision ranged from 0.1 to
     1.0 depending on the target. Predictive power therefore varies widely
     across targets [@overath_meta].
   - *Scope caveats:* Re-scoring standardizes computational metrics but leaves
     each source campaign's heterogeneous wet-lab assays and binding definitions
     unchanged; the pooled dataset also reflects earlier-generation designs
     rather than the newest 2025–2026 models [@overath_meta].
