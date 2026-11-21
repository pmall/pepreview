# Review Outline: Co-folding and Generative Methods for De Novo Binder Design

- **Venue & target length:** *PLOS Computational Biology* Review (3,000–6,000
  words, max 3 heading levels, 2–3 display items). Aim to land comfortably in
  the middle at **~3,800–4,500 words** of main text by keeping each section
  selective in scope rather than compressing prose.
- **Editorial perspective:** Descriptive and mechanistic, written from a
  drug-discovery and protein-engineering viewpoint rather than as a model
  ranking or thesis defense. Prose explains key mechanisms using 1–3
  illustrative examples from `literature/map.md`, while two compact tables carry
  broader side-by-side reference coverage.
- **Scope:** De novo design of peptides, macrocyclic peptides, and compact
  protein binders (minibinders) targeting protein–protein interactions as
  candidate drug precursors. Nanobodies (VHHs) and antibodies (scFvs, mAbs) are
  integrated accurately where relevant without dominating the opening or
  framing. Small-molecule ligand generation is out of scope.

## Narrative Arc

The review moves from **(1) motivation** (engaging flat protein–protein surfaces
at chosen epitopes) to **(2) co-folding mechanisms** (evolutionary inputs and
coordinate generation), **(3) binder-design workflows** (turning predictors into
generators), **(4) candidate selection and experimental caveats** (filtering
limits and reading wet-lab hit rates), and **(5) translational bottlenecks**
separating in vitro binding hits from viable drug leads.

## Section-by-Section Plan

### Abstract (~150–180 words)

Keep the Abstract short, unhurried, and high-level by limiting its content to
three points rather than previewing every subsection or caveat:

- **Problem and shift:** Engaging flat protein–protein interfaces with designed
  peptides, macrocycles, and minibinders (alongside nanobodies and antibodies)
  has moved from random library screening toward epitope-directed computational
  design, enabled by co-folding models where binder generation is closely
  related to complex prediction.
- **Architectural focus:** This review examines how key design choices in
  co-folding networks, notably evolutionary inputs (multiple sequence alignments
  versus protein language models) and coordinate generation, shape practical
  binder-design workflows.
- **Experimental and translational perspective:** We discuss how to read
  computational filters and wet-lab hit rates critically, and why a gap still
  separates in vitro binding hits from developable drug leads.

Leave detailed lists of workflow variants, coordinate formalisms, assay
confounders, and individual bottlenecks out of the Abstract so each sentence
reads naturally without compression.

### Introduction (~450 words)

- Motivate de novo design of peptides, macrocyclic peptides, and minibinders for
  engaging broad, flat protein–protein interfaces as candidate drug precursors,
  noting antibodies and nanobodies as established clinical formats.
- Contrast traditional discovery (immunization and display libraries searching
  vast random sequence spaces toward immunogenic or accessible sites) with
  computational design directed at a chosen target and epitope.
- Explain that architecturally binder generation is closely related to
  co-folding (leaving the binder chain masked or noised on the same network),
  whereas search and validation differ in practice (exploring 20^*L* possible
  sequences without natural alignments for the designed chain and confirming
  binding experimentally), reflected in synthesis budgets falling from
  thousands–millions of variants down to tens of designs per target.
- Define scope (de novo peptides, macrocyclic peptides, minibinders, and
  antibody formats against protein targets; excluding small-molecule ligands)
  and briefly preview the review's structure.

### 1. Co-folding Architectures and Mechanistic Trade-offs (~900 words)

- **Two-stage prediction pipeline:** Explain how modern co-folding models
  separate a differentiable sequence-to-pairwise reasoning trunk (producing
  residue representations and a pairwise distogram) from a 3D coordinate module,
  with only a brief contrast to earlier three-track RoseTTAFold networks (omit
  detailed RoseTTAFold2 ablation history).
- **Evolutionary inputs (MSAs versus protein language models):** Explain why MSA
  database lookups are non-differentiable and undefined for invented sequences,
  forcing MSA-trained models into their weakest single-sequence regime during
  design. Detail how replacing MSA retrieval with a protein language model trunk
  (focusing on ESMC/ESMFold2, with Chai-1 as a hybrid contrast; omit lengthy
  ESM-2/ESM-3 scaling history) enables native single-sequence inference and
  end-to-end gradient backpropagation all the way back to the input sequence
  within the model's training distribution.
- **Coordinate-generation strategies:** Compare single-pass differentiable
  coordinate regression (AlphaFold2's IPA module), iterative all-atom diffusion
  (AlphaFold3-class models), and straighter-trajectory flow matching or few-step
  ODE samplers across speed, chemical generality, and differentiability. Include
  one concise point on diffusion stereochemistry (learned geometric features in
  RoseTTAFold3 versus inference-time steering in Boltz-1x; omit multi-seed
  scaling tables and PoseBusters/PXMeter sub-debates).
- *Placement:* **Figure 1** follows the first citing paragraph.

### 2. Design Workflows: Turning Predictors into Binder Generators (~1,050 words)

Explain each workflow through 1–3 flagship systems and let **Table 1** carry the
broader catalog instead of narrating every tool in prose:

- **Structure generation with inverse folding (generate-and-filter):** Explain
  the decoupled workflow using RFdiffusion + ProteinMPNN (including the offline
  sequence-recovery caveat), RFpeptides (cyclic positional encodings for
  macrocycles), and RFdiffusion3 (fast pre-trained all-atom U-Net). Leave
  additional inverse-folding and flow-matching variants (LigandMPNN,
  AlphaDesign, RFantibody, PXDesign-d, PPIFlow/AtomFlow) to Table 1.
- **Unified prediction-and-design all-atom models:** Focus on BoltzGen as the
  joint prediction-and-design diffusion example alongside training-set
  memorization (ubiquitin mode collapse at lengths 73–76) and the need for
  manual structural inspection. Omit early prototype bug stories and secondary
  unfinished models.
- **Gradient-based sequence optimization (backpropagation):** Explain continuous
  sequence relaxation and annealing through regression models (BindCraft with
  induced-fit target reprediction, AfCycDesign for macrocycles) versus diffusion
  workarounds: distogram/confidence trunk gradients without unrolling diffusion
  (BoltzDesign1, and natively single-sequence ESMC/ESMFold2) or a differentiable
  few-step ODE decoder (PXDesign-h). Briefly explain how sequence priors (native
  ESMC; live IgLM in Germinal) and discrete gradient-ranked mutations
  (RFOptimization) curb off-distribution drift. Omit multi-stage iteration
  counts and in-silico ablation numbers.
- *Placement:* **Table 1** follows the first citing paragraph.

### 3. Candidate Selection and Experimental Evidence (~850 words)

Keep this section focused on what directly impacts binder design rather than
re-explaining textbook metrics, structure-prediction leaderboards, or every row
of Table 2:

- **Candidate selection and filtering limits:** Briefly contrast external
  accuracy checks with the self-estimated confidence scores used before
  synthesis (self-consistency RMSD, pLDDT, ipTM/iPAE, ipSAE), skipping textbook
  definitions of lDDT/TM-score/RMSD and FoldBench ranking quirks. Focus on three
  core findings: (1) the rank-to-oracle gap showing models sample near-native
  poses that confidence heads miss (AtlasFold/FoldBench), (2) wide
  target-to-target variation in confidence-filter precision (Overath et al.
  0.1–1.0 average precision; Germinal nonbinders clearing ipSAE), and (3)
  classifiers trained directly on wet-lab binding data (BoltzPPI doubling
  confirmed binders on identical BoltzGen pools).
- **Reading wet-lab campaigns critically:** Let a concise **Table 2** (~10–12
  rows) carry campaign-by-campaign specifics. In two focused paragraphs of
  prose, synthesize the main comparability caveats: (1) hit criteria and assay
  rigor (screening hits vs. orthogonal confirmation as in BoltzProt-1), bivalent
  Fc avidity, and synthesis/expression attrition; and (2) target/epitope
  selection bias (mBER's randomized-hotspot scaling vs. curated panels), rare
  cross-group resynthesis shifts (AlphaProteo on RFdiffusion, Latent-X1 on
  RFpeptides), and why undisclosed commercial generators cannot be audited
  independently (replacing a standalone Openness subsection; Table 1 covers
  openness per system).
- *Placement:* **Table 2** follows the first citing paragraph.

### 4. From In Vitro Binding Hits to Drug Leads and Conclusions (~750 words)

- **The translational gap:** Situate in vitro binding hits within drug discovery
  using Bender et al.'s distinction between model validation and process
  validation. Explain why clinical translation requires developability, low
  immunogenicity, and functional modulation, illustrated by high-affinity
  developability failures in blinded testing (AIntibody 2.9 pM HIC failure) and
  closed multi-objective efforts (Latent-X2).
- **Three unresolved technical bottlenecks (one concise paragraph each):**
  - *Quantitative protein–protein affinity prediction:* Confidence scores act as
    binary binding filters rather than $K_D$ estimators, while co-folding
    affinity heads (Boltz-2) remain limited to small-molecule ligands.
  - *Targets without experimental structures and dynamics:* Static PDB-like
    predictions leave uncharacterized, flexible, and disordered targets hard to
    engage reliably (Germinal's predicted-antigen caveat).
  - *Blinded prospective de novo benchmarks:* Standardized multi-group wet-lab
    benchmarks for target-conditioned de novo design remain absent (building on
    library-conditioned antibody engineering in AIntibody).
- **Conclusions (~150 words):** One concise closing paragraph synthesizing how
  single-sequence language-model trunks, all-atom diffusion/flow models, and
  wet-lab-trained rankers have made small-budget binder design practical, and
  stating the central remaining challenge of moving from in vitro binding hits
  to developable, functional drug precursors.

## Planned Display Items (3 Total)

1. **Figure 1: Co-folding Architecture Trade-offs and Binder-Design Workflows.**
   Two-panel schematic showing (A) trunk and coordinate-module choices (MSA vs.
   PLM trunk; regression vs. diffusion/flow coordinate head, marking gradient
   paths) and (B) how they map onto generate-and-filter, unified all-atom
   diffusion, and gradient-based sequence optimization.
1. **Table 1: Representative Co-folding and Binder-Design Systems.** Compact
   architectural reference (~12–14 rows) covering *System*, *Input trunk* (MSA /
   PLM / hybrid), *Coordinate formalism*, *Design workflow*, *Modalities*
   (peptides, macrocycles, minibinders, VHH/antibodies), and *Openness*.
1. **Table 2: Representative Wet-Lab De Novo Binder Campaigns and Assay
   Context.** Compact side-by-side summary (~10–12 rows) grouped by modality,
   covering *System*, *Target scope & selection*, *Designs tested per target*,
   *Assay & hit criterion*, and *Key caveats* (avidity, attrition, confirmation
   tier, disclosure).
