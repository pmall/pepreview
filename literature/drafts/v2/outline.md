# Review Outline: Deep-Learning Methods for Protein and Peptide Binder Generation

Target venue: **PLOS Computational Biology (Review)** (see `VENUE.md`).

- **Target length:** ~5,500–6,000 words of main text (within PLOS Comp Biol's
  3,000–6,000 word Review guidance; PLOS enforces no hard cap at submission, so
  conceptual clarity takes priority over artificial trimming).
- **Heading depth:** Maximum 3 heading levels (`#`, `##`, `###`).
- **Display items:** 1 conceptual figure + 2 structured tables (3 display items
  total, plus an optional compact metrics box if preferred over inline
  definitions).
- **Register:** Descriptive and explanatory for a curious reader entering the
  field. Explains architectures, mechanisms, trade-offs, and evaluation
  conditions without ranking models or arguing a thesis.

______________________________________________________________________

## Front Matter

- **Title:** Clear, descriptive title naming protein and peptide binder
  generation (distinct from small-molecule design).
- **Abstract (~250 words):** Problem scope (protein/peptide binders against
  chosen targets), how accurate structure prediction enabled generative design,
  the main architectural axes (MSA vs. protein language models; regression vs.
  diffusion vs. flow matching; generate-and-filter vs. gradient-based
  optimization), the shift from screening millions of sequences to testing tens
  of designs, and key open challenges (affinity prediction, developability,
  standardized benchmarking, disclosure).

______________________________________________________________________

## 1. Introduction and Conceptual Background (~1,800–2,000 words)

Treated as a unified, unhurried extended introduction so a curious reader builds
complete intuition for the field before meeting individual model families.

### 1.1 Why protein binders matter and how discovery shifted from search to design

- Role of protein and peptide binders (antibodies, nanobodies/VHHs, scFvs,
  minibinders, macrocyclic peptides) in therapeutics and laboratory reagents.
- Traditional discovery (animal immunization, phage/yeast display libraries of
  ≥10¹² random sequences): effective, but wet-lab intensive per target and
  unable to aim reliably at a user-chosen epitope [@rfantibody].
- Scope boundary: why protein/peptide binder generation (fixed 20-amino-acid
  chain folding against a target) is distinct from small-molecule generation
  (variable chemical graphs under valence constraints).
- Why AlphaFold2 [@alphafold2] and AlphaFold3 [@alphafold3] changed the problem,
  and how binder *generation* differs fundamentally from structure *prediction*
  (checking a known sequence against a crystal structure vs. inventing a
  functional sequence that requires wet-lab validation).
- Rapid 2024–2026 ecosystem expansion (multiple open lineages, design stacks,
  and dedicated inference-kernel investments from NVIDIA, Anthropic, and ESM
  teams).

### 1.2 How co-folding predictors are built

- The MSA coevolution principle confirmed by AlphaFold2 (CASP14 median 0.96 Å
  r.m.s.d.95 vs. 2.8 Å next best) [@alphafold2] and extended to biomolecular
  complexes by AlphaFold3 [@alphafold3].
- The two-stage architecture shared by most modern co-folders (noting
  RoseTTAFold 1/2's parallel three-track 1D/2D/3D architecture as an early
  alternative [@rosettafold; @rosettafold2]):
  - **Trunk (Evoformer / Pairformer / folding trunk):** Converts sequence and
    evolutionary inputs into single and pair representations, with a linear
    distogram head [@alphafold2; @alphafold3; @boltz1; @esmc]. Contrast MSA
    retrieval (AlphaFold, RoseTTAFold, Boltz, Protenix), protein language models
    (ESMFold, ESMFold2, AtlasFold), and hybrid dual-track models (Chai-1).
  - **Structure / diffusion module:** Converts representations into 3D
    coordinates via single-pass IPA regression (AlphaFold2, ESMFold
    [@alphafold2; @esm2]), iterative SDE diffusion (AlphaFold3 and AF3-class
    models [@alphafold3; @frameflow]), or ODE flow matching with straighter
    trajectories (FrameFlow [@frameflow] and binder extensions PPIFlow,
    OriginFlow, AtomFlow, D-Flow [@ppiflow; @originflow; @atomflow; @dflow]).
  - Note how diffusion and flow matching transferred from image generation
    (pixels → atomic coordinates), while protein design differs in having
    automated structural predictors to score outputs.

### 1.3 Turning structure predictors into binder generators

- Shared machinery: holding all chains fixed predicts a complex; leaving one
  chain unspecified/noised generates a binder against the target (BoltzGen
  [@boltzgen], RFdiffusion fine-tuned from RoseTTAFold [@rfdiffusion]).
- The three ways structure predictors are used in design workflows (**→ Figure
  1**):
  1. *Joint or fine-tuned predictor-generators* (RFdiffusion 1/2 \[@rfdiffusion;
     @rfdiffusion2\], BoltzGen [@boltzgen]).
  1. *Generate-and-filter pipelines* combining backbone generation, inverse
     folding (ProteinMPNN [@proteinmpnn]), and filtering via confidence scores
     (e.g., AlphaProteo's PAE/RMSD/pLDDT criteria [@alphaproteo]) or a trained
     experimental-binding classifier (BoltzPPI [@boltzprot1]).
  1. *Gradient-based sequence optimization (hallucination / backpropagation)*
     over a continuous *L* × 20 sequence relaxation annealed to one-hot
     (BindCraft [@bindcraft], Germinal [@germinal], BoltzDesign1
     [@boltzdesign1], PXDesign-h [@pxdesign], ESMFold2 [@esmc]), plus discrete
     gradient-ranked point mutation (RFOptimization [@rfoptimization]).
- Practical engineering constraints of gradient-based design:
  - *Single-sequence requirement:* MSA lookups are non-differentiable and
    undefined for invented sequences, pushing MSA-trained models like AF2 out of
    distribution while natively single-sequence PLMs (ESMC/ESMFold2) operate
    in-distribution [@alphafold2; @bindcraft; @esmc].
  - *Bypassing multi-step diffusion during backpropagation:* Computing gradients
    from trunk distograms/confidence heads (BoltzDesign1, RFOptimization,
    ESMFold2 [@boltzdesign1; @rfoptimization; @esmc]) vs. replacing 200-step
    diffusion with a 2-step ODE sampler (PXDesign-h [@pxdesign]).
- Why candidate filtering matters independently of the generator (BoltzPPI
  raising confirmed binders 3.3% → 8.0% on the same candidate pool
  [@boltzprot1]; complementary true positives across Protenix and AF2-IG filters
  [@pxdesign]; multi-predictor optimization in RFOptimization
  [@rfoptimization]).

### 1.4 Reading reported numbers: testing budgets, hit definitions, and disclosure

- The drop in designs tested per target from thousands/millions \[@chai2;
  @rfantibody\] to tens [@chai2; @rfpeptides; @boltzgen; @protenix_v2].
- Why raw hit rates are not directly comparable: screening hits vs. confirmed
  binders (BoltzProt-1 [@boltzprot1]), and author-selected targets/epitopes vs.
  randomized-hotspot screening (mBER's 1.15M-design VHH sweep showing ~0.4%
  median rate vs. up to 38% on best filtered epitopes [@mber]).
- Spectrum of openness and disclosure across the field (fully reproducible
  weights/code/data, open weights, undisclosed architectures with papers,
  API-only models, unpublished commercial systems) and what that means for
  inspecting methods.
- Core evaluation metrics introduced cleanly right before the model families
  (either via a compact **Box 1: Metrics Quick Reference** or inline at first
  use): external accuracy/validity (`lDDT`, `TM-score`, `RMSD` /
  self-consistency RMSD, `DockQ`, `PoseBusters / PB-valid`) and model
  self-estimates (`pLDDT`, `pTM`, `PAE`, `ipTM`, `iPAE`, `ipSAE`) \[@lddt;
  @tm_score; @kabsch; @dockq; @posebusters; @alphafold2; @alphafold_multimer;
  @ipsae\].

______________________________________________________________________

## 2. Model Families: From Predictors to Design Systems (~2,400–2,700 words)

Traces each major architectural family from structure prediction to binder
design (**→ Table 1** summarizes all families side by side so the prose focuses
on mechanisms, key contributions, and caveats rather than repetitive lists).

### 2.1 AlphaFold and open reproductions (~350 words)

- **AlphaFold2** [@alphafold2], **AlphaFold-Multimer** [@alphafold_multimer]
  (unreviewed preprint; introduced ipTM/iPAE; inverted by backpropagation
  methods), and **OpenFold** [@openfold] (open retraining + distillation set).
- **AlphaFold3** [@alphafold3] (Pairformer + all-atom diffusion; 1,000-seed
  antibody sampling; PoseBusters docking; physical-validity caveats including
  4.4% chirality errors, clashes, disordered-region hallucinations; closed
  weights) and **OpenFold3** [@openfold3] (Apache-2.0 weights, code, and
  13M-sequence distillation set; software release caveats).

### 2.2 RoseTTAFold, RFdiffusion, and inverse folding (~550 words)

- Clear distinction between **RoseTTAFold3 (RF3)** (structure predictor) and
  **RFdiffusion3 (RFD3)** (generative model).
- *Predictors:* Independent three-track **RoseTTAFold** [@rosettafold] →
  ablation insights of **RoseTTAFold2** (no IPA or triangle attention needed;
  \>1,000-residue scaling; 3D input track) [@rosettafold2] → **RoseTTAFold
  All-Atom** [@rosettafold_all_atom] → **RoseTTAFold3** (all-atom diffusion,
  learned chirality achieving 88% vs. 84% AF3 and 76% Boltz-2 without steering)
  [@rosettafold3].
- *Generators:* **RFdiffusion** (equivariant frame diffusion fine-tuned from
  RF1; established backbone → ProteinMPNN → AF2 workflow) [@rfdiffusion] →
  **RFdiffusion2** (atom-level active-site scaffolding) [@rfdiffusion2] →
  **RFdiffusion3** (all-atom U-Net, 168M params, 2 Pairformer layers, 100 steps,
  pre-trained directly rather than fine-tuned from RF weights) [@rfdiffusion3].
- *Inverse folding:* **ProteinMPNN** [@proteinmpnn] (shared backbone-to-sequence
  workhorse; sequence-recovery caveat), **LigandMPNN** [@ligandmpnn]
  (non-protein context), and **AlphaDesign**'s Autoregressive Diffusion Model
  [@alphadesign].
- *Modality arms:* **RFantibody** (epitope-specific VHH/scFv/antibody design
  still paired with 9,000-design yeast display; 0–2% hit rate) [@rfantibody] and
  **RFpeptides** (cyclic relative positional encoding for head-to-tail
  macrocycles; \<20 designs/target with crystal structures) [@rfpeptides].

### 2.3 Boltz (~350 words)

- **Boltz-1 / Boltz-1x** [@boltz1] (first MIT-licensed AF3-class co-folder;
  Feynman-Kac inference-time steering).
- **Boltz-2** [@boltz2] (small-molecule affinity module: r = 0.66 on FEP+ at
  \>1,000× lower compute, protein–ligand only; 2023-06-01 FoldBench cutoff
  overlap caveat).
- **BoltzGen** [@boltzgen] (MIT-licensed single diffusion model for both
  prediction and multi-modality design excluding full antibodies; 26 targets
  including 6/9 novel targets at ≤15 designs; disclosed ubiquitin memorization
  at lengths 73–76 and `BoltzGenv0` refolding bug).
- **BoltzProt-1 / BoltzPPI** [@boltzprot1] (controlled filter comparison on
  identical candidate pools: 3.3% → 8.0% confirmed binders; explicit
  screening-hit vs. confirmed-binder split; shift to commercial API-only
  access).

### 2.4 Chai (~200 words)

- **Chai-1** [@chai1] (dual MSA + PLM tracks; experimental restraints;
  single-sequence parity on antibodies; non-commercial license and benchmarking
  restrictions).
- **Chai-2** [@chai2] (zero-shot scFv/VHH design at ≤20 designs/target/format,
  16% combined hit rate across 52 novel targets; 68% minibinder hit rate;
  generative architecture undisclosed beyond `Chai-2f`). Brief note on
  commercial **Chai-3**.

### 2.5 Gradient-based design by backpropagation (~450 words)

- *Through AlphaFold2:* **ColabDesign** [@colabdesign] library; **AfCycDesign**
  (cyclic positional encoding; monomeric hallucination + grafted binders)
  [@afcycdesign]; **BindCraft** (full AF-Multimer backpropagation, 5-model
  random swap, induced-fit target reprediction, 4-stage
  logit→softmax→STE→discrete schedule, ProteinMPNN surface redesign, 10–100% hit
  rates across 12 targets; single-sequence regime and ipTM non-affinity caveats;
  **BindCraft2** code release) [@bindcraft].
- *With diffusion-based predictors:* **BoltzDesign1** (stop-gradient on
  diffusion, 64-bin Pairformer distogram contact loss + optional confidence
  head; in-silico validation) [@boltzdesign1]; **RFOptimization** (strictly
  discrete Metropolis–Hastings point mutations ranked by RF3
  distogram/confidence gradients, interleaved 50% with Boltz + LigandMPNN
  cycling, AF3 held out; in-silico only) [@rfoptimization].
- *Adding language-model sequence priors:* **Germinal** (live IgLM gradient
  merged with AF-Multimer via weighted sum/MGDA/PCGrad for antibody CDRs;
  nonbinders passing ipSAE caveat; **OpenGerminal** Apache-2.0 port)
  \[@germinal; @opengerminal\] vs. **mBER** (static ESM-2 logit bias +
  NanoBodyBuilder2 template; 1.15M-design randomized-epitope phage sweep;
  **mBER-2** technical report) [@mber].

### 2.6 Protenix (~300 words)

- **Protenix-v1** [@protenix_v1] (matched-conditions AF3 comparison; log-linear
  seed scaling 36.01% → 47.68%; FoldBench common-intersection analysis).
- **PXDesign** [@pxdesign] (dual modes on one backbone: DiT Cartesian diffusion
  **PXDesign-d** used for 6 wet-lab campaigns at 20–73% hit rates on 5/6
  targets, and 2-step ODE end-to-end hallucination **PXDesign-h**; complementary
  Protenix vs. AF2-IG filter finding).
- **Protenix-v2** [@protenix_v2] (9–13 pt Ab–Ag gain, 5 seeds beating v1's 1,000
  seeds; novelty-controlled soluble VHH-Fc 2–48% and GPCRs 16–88% VHH-Fc / 0–50%
  mAb at 16–30 designs/target; epitope sensitivity on AMBP 4% vs. 48%) and
  **PXMeter** [@pxmeter] (open benchmark toolkit + v1.1.0 planarity checks
  [@protenix_v2]).

### 2.7 ESM (~250 words)

- **ESM-2 / ESMFold** [@esm2] (single-sequence folding without MSAs) → **ESM-3**
  [@esm3] (multimodal sequence/structure/function masked-token model up to 98B;
  `esmGFP`; academic vs. API availability).
- **ESMC / ESMFold2** [@esmc] (6B LM + 48-layer recurrent folding trunk +
  sliding-window diffusion transformer; single-sequence Ab–Ag matching
  AF3-with-MSA within error bars [@atlasfold]; single-stage 150-step distogram +
  ESMC gradient optimization native to single-sequence input; 84 designs/cohort
  across 5 targets, 70.0% mean minibinder / 21.0% scFv hit rates).
- **AtlasFold** [@atlasfold] (independent fully open MIT single-sequence PLM
  folder + multi-model FoldBench rank/oracle benchmark).

### 2.8 Closed and undisclosed systems (~200 words)

- *Published results, undisclosed generators:* **AlphaProteo** (9–88% across 8
  targets, 0/54 TNFα; disclosed AF2 filter; resynthesized RFdiffusion designs)
  [@alphaproteo]; **Latent-X1 / Latent-X2** (proprietary all-atom platform;
  macrocycles, minibinders, low-immunogenicity/developable antibodies; partial
  RFpeptides resynthesis) [@latentx1; @latentx2]; cross-reference to Chai-2 and
  BoltzProt-1.
- *Unpublished systems known via third-party benchmarks:* **OpenDDE**
  (Apache-2.0, 3× wider Pairformer 128→384, atom-level refiner; third-party
  Ab–Ag benchmarks) [@opendde] providing the only public scaling-curve points
  for **IsoDDE** and **SeedFold**, alongside commercial **Chai-3**.

______________________________________________________________________

## 3. Quantitative Landscape and Evaluation Pitfalls (~550–700 words + Table 2)

Short analytical synthesis anchored by **Table 2**, focusing on *how to read*
the published numbers rather than declaring winners:

- **Structure prediction convergence vs. antibody gap:** On FoldBench's common
  intersection [@foldbench; @protenix_v1], monomer lDDT sits in a narrow
  0.85–0.89 band, protein–protein spans ~7 points (65.4–72.7%), while
  antibody–antigen spans 23.1–52.3%.
- **Sensitivity to metric definitions:** Target-set intersection filtering
  reverses Boltz-1 vs. Chai-1 rankings on FoldBench PPI [@protenix_v1];
  averaging per 40%-identity cluster (52.9% [@chai1]) vs. per interface (25.2%
  [@foldbench]) doubles Chai-1's reported antibody DockQ success; Boltz-1
  averages per interface within complexes [@boltz1].
- **Confidence ranking vs. oracle ceiling:** Across seven models evaluated by
  AtlasFold [@atlasfold], selecting the top sample by confidence loses 11–21
  percentage points relative to oracle selection on antibody–antigen (3–8 points
  on PPI), motivating large seed budgets [@alphafold3; @protenix_v1; @opendde]
  and trained scorers [@boltzprot1].
- **Reading wet-lab campaign tables responsibly:** Grouping campaigns by
  validation rigor (two-assay confirmation, single assay, display enrichment,
  functional readout, in-silico only), plus cross-cutting confounders: bivalent
  Fc avidity [@protenix_v2; @chai2; @bindcraft], synthesis/expression attrition
  [@rfpeptides; @latentx1; @pxdesign], target-level vs. per-design hit rates,
  heterogeneous binding thresholds, and why rare resynthesis tests shift
  reported rates/affinities (AlphaProteo on RFdiffusion [@alphaproteo];
  Latent-X1 on RFpeptides [@latentx1]).

______________________________________________________________________

## 4. Conclusions and Open Challenges (~650–800 words)

### 4.1 From in vitro binding to therapeutic utility

- Most systems motivate their work via drug discovery \[@boltzgen; @chai2;
  @bindcraft; @latentx2; @mber\], yet Bender et al. [@bender_perspective]
  distinguish *model validation* (benchmark accuracy and in vitro binding rates)
  from *process validation* (improving downstream clinical decisions). Even for
  biologics, binding is easier to predict than functional activity and
  developability.

### 4.2 Five documented open limitations

1. **Developability, function, and immunogenicity:** Almost all open pipelines
   optimize and filter solely for binding; Latent-X2 addresses developability
   and immunogenicity but withholds its architecture [@latentx2].
1. **Protein–protein binding affinity prediction:** Confidence scores (e.g., AF2
   ipTM) act as binary binding predictors rather than quantitative K_D
   estimators [@bindcraft]; Boltz-2's affinity head covers protein–ligand
   interactions only [@boltz2].
1. **Targets without experimental structures:** Dependence of design success on
   predicted antigen-model quality remains open [@germinal].
1. **Lack of shared, blinded prospective benchmarks for de novo binder design:**
   No shared de novo wet-lab benchmark exists; **AIntibody** [@aintibody] (511
   IgGs, 29 organizations, SARS-CoV-2 RBD) demonstrated blinded independent
   testing (top design 95 pM matching wet-lab 113 pM, but only 1/26 groups
   beating random within-cluster affinity ranking and a 2.9 pM winner failing
   HIC developability), while testing library-conditioned engineering rather
   than de novo design.
1. **Per-design discrimination limits of confidence filters:** Confidence scores
   enrich large libraries (mBER [@mber]) but often fail on individual candidates
   (Germinal [@germinal]); Overath et al.'s meta-analysis of 3,766 designs
   across 15 targets found AF3 ipSAE was the strongest single predictor yet
   spanned average precision 0.1–1.0 across targets [@overath_meta].

______________________________________________________________________

## Planned Display Items (3 total, matching PLOS Comp Biol guidance)

1. **Figure 1 — Co-folding architecture and binder-design workflows:** Two-panel
   schematic illustrating (A) trunk (MSA vs. PLM) → structure/diffusion stage
   (regression vs. diffusion vs. flow matching), and (B) the three design
   paradigms (joint/fine-tuned generator; backbone generation + inverse folding
   \+ confidence/classifier filter; gradient-based sequence optimization through
   full regression, trunk distogram, or 2-step ODE).
1. **Table 1 — Overview of model families:** Columns: Model / lineage, Primary
   role, Evolutionary input (MSA / PLM / both), Coordinate stage, Binder
   modalities, Design/filtering mechanism, Openness / license.
1. **Table 2 — Quantitative benchmarks and wet-lab campaigns:** Two concise
   panels (or split into Table 2A prediction benchmarks & rank/oracle gap +
   Table 2B wet-lab campaigns grouped by assay confirmation format with designs
   tested, hit rates, best affinity, and key caveats/avidity flags).
   - *(Optional compact **Box 1** for evaluation metric definitions if you
     prefer a dedicated lookup box over inline definitions.)*

______________________________________________________________________

## Word-Budget Summary

| Section                                         |     Target words |          Share |
| ----------------------------------------------- | ---------------: | -------------: |
| Abstract                                        |             ~250 | (front matter) |
| 1. Introduction & Conceptual Background         |      1,800–2,000 |           ~33% |
| 2. Model Families (8 subsections)               |      2,400–2,700 |           ~45% |
| 3. Quantitative Landscape & Evaluation Pitfalls |          550–700 |           ~11% |
| 4. Conclusions & Open Challenges                |          650–800 |           ~12% |
| **Main Text Total**                             | **~5,400–6,000** |       **100%** |
