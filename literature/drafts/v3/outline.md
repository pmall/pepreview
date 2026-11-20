# Review Outline (v3): De Novo Binder Design with Co-Folding and Generative Models

Target venue: **PLOS Computational Biology (Review)** (see `VENUE.md`).

- **Target length:** ~4,300–4,600 words of main text (comfortably centered
  inside PLOS Comp Biol's 3,000–6,000-word Review target so sentences have
  breathing room and zero compression is needed).
- **Heading depth:** Maximum 3 heading levels (`#`, `##`, `###`).
- **Display items:** Exactly **3 compact display items** (1 conceptual figure +
  2 concise ~10–12-row tables, plus an optional compact inline/box metric
  summary).
- **Source of truth:** Draws selectively from `literature/map.md` (which remains
  the full factual repository), keeping the core conceptual and methodological
  landscape while omitting minor checkpoints, unreleased software announcements,
  and small-molecule-only details.
- **Register:** Clear, unhurried, explanatory scientific prose for a curious
  biologist or computational researcher. Describes mechanisms, trade-offs, and
  evaluation conditions without ranking models, arguing a thesis, or using
  invented taxonomies.

______________________________________________________________________

## Front Matter

- **Title:** De Novo Binder Design with Co-Folding and Generative Models
- **Abstract (~220 words):** Why amino-acid-based binders (antibodies,
  nanobodies, scFvs, minibinders, macrocyclic peptides) matter, the shift from
  random library screening to computational de novo binder design, the scope
  boundary separating amino-acid chains from small-molecule ligands, the main
  architectural axes (evolutionary input, coordinate generation, and how
  predictors drive design), and the key open challenges (affinity,
  developability, prospective benchmarks, filtering limits).

______________________________________________________________________

## 1. Introduction and Conceptual Background (~1,350 words)

Unhurried, accessible conceptual foundation for a newcomer to the field.

### 1.1 From experimental search to computational binder design (~320 words)

- Role of amino-acid-based binders capable of engaging flat protein surfaces,
  contrasting the three main design regimes tackled by general co-folding and
  generative platforms: de novo minibinders (invented from scratch), macrocyclic
  peptides (head-to-tail closed chains), and antibodies/nanobodies (conserved
  frameworks with flexible CDR-H3 loops and weak evolutionary signal).
- Scope boundary: general structure-based platforms for amino-acid chains from
  the 20-letter alphabet, excluding small-molecule ligand generation and
  specialized antibody-only sequence models.
- Why accurate structure prediction (AlphaFold2 [@alphafold2], AlphaFold3
  [@alphafold3]) enabled design, and why generating a binder (inventing a
  sequence from $20^L$ possibilities confirmed only in a wet lab) differs
  fundamentally from predicting a fold.

### 1.2 How co-folding structure predictors work (~380 words)

- MSA coevolution principle (AlphaFold2 CASP14 median 0.96 Å r.m.s.d.95 vs. 2.8
  Å next best [@alphafold2]) extended to biomolecular complexes ("co-folding",
  AlphaFold3 [@alphafold3]).
- Two-stage architecture (noting early RoseTTAFold 1/2's parallel 3-track
  1D/2D/3D network as an alternative [@rosettafold; @rosettafold2]):
  - **Trunk (Evoformer, Pairformer, folding trunk):** Sequence + evolutionary
    context → single/pair representations + linear distogram head \[@alphafold2;
    @alphafold3; @boltz1; @esmc\]. Three evolutionary input modes:
    inference-time MSA retrieval (AlphaFold, Boltz, Protenix, RoseTTAFold),
    pre-trained protein language models (ESMFold, ESMFold2, AtlasFold), or
    hybrid dual tracks (Chai-1 [@chai1]).
  - **Coordinate stage:** Single-pass differentiable IPA regression (AlphaFold2,
    ESMFold [@alphafold2; @esm2]), iterative SDE diffusion adapted from image
    generation (AlphaFold3 and AF3-class models [@alphafold3; @frameflow]), or
    straighter-trajectory ODE flow matching (FrameFlow [@frameflow] and binder
    variants PPIFlow, OriginFlow, AtomFlow, D-Flow \[@ppiflow; @originflow;
    @atomflow; @dflow\]). Unlike image generation, protein outputs can be scored
    automatically by structure predictors.

### 1.3 Three ways structure predictors drive binder design (~450 words)

- Shared prediction/generation duality: holding all chains fixed predicts a
  complex; leaving one chain unspecified or noised generates a binder against
  the target (BoltzGen [@boltzgen], RFdiffusion [@rfdiffusion]).
- Three design workflows (**→ Figure 1**):
  1. *Joint or fine-tuned predictor-generators* (RFdiffusion/RFdiffusion2
     [@rfdiffusion; @rfdiffusion2], BoltzGen [@boltzgen]).
  1. *Generate-and-filter pipelines* pairing backbone generation, inverse
     folding (ProteinMPNN [@proteinmpnn]), and ranking via confidence metrics
     (e.g., AlphaProteo's PAE/RMSD/pLDDT thresholds [@alphaproteo]) or a trained
     experimental-binding classifier (BoltzPPI [@boltzprot1]).
  1. *Gradient-based sequence optimization (hallucination / backpropagation)*
     descending confidence or distogram losses over a continuous *L* × 20
     sequence relaxation annealed to one-hot (BindCraft [@bindcraft], Germinal
     [@germinal], BoltzDesign1 [@boltzdesign1], PXDesign-h [@pxdesign], ESMFold2
     [@esmc]), or discrete gradient-ranked point mutations (RFOptimization
     [@rfoptimization]).
- Three practical engineering constraints:
  - *Single-sequence requirement:* MSA lookups are non-differentiable and
    undefined for invented sequences, pushing MSA-trained models out of
    distribution while natively single-sequence PLMs stay in-distribution
    [@alphafold2; @bindcraft; @esmc].
  - *Bypassing multi-step diffusion during backpropagation:* Reading gradients
    from trunk distograms/confidence heads (BoltzDesign1, RFOptimization,
    ESMFold2) vs. substituting a 2-step ODE sampler (PXDesign-h [@pxdesign]).
  - *Independent impact of filtering:* BoltzPPI doubling confirmed binders on
    identical BoltzGen pools [@boltzprot1]; complementary true positives across
    Protenix and AF2-IG filters [@pxdesign].

### 1.4 Core evaluation metrics (~200 words)

- Concise prose distinction between **external metrics** against experimental
  structures or physical chemistry (`lDDT` [@lddt], `RMSD` / self-consistency
  RMSD [@kabsch], `DockQ` [@dockq], `PoseBusters / PB-valid` [@posebusters]) and
  **model self-estimates** used when no experimental structure exists (`pLDDT`,
  `PAE` [@alphafold2], `ipTM`, `iPAE` [@alphafold_multimer], `ipSAE` [@ipsae]).
  *(No separate bulky Box 1 needed; keep definitions crisp and readable in two
  short paragraphs.)*

______________________________________________________________________

## 2. Approaches and Representative Systems (~1,750 words + Table 1)

Organized by methodological approach rather than eight lab-by-lab chronologies,
teaching how the major ideas fit together (**→ Table 1** provides a compact
~11-row side-by-side summary).

### 2.1 All-atom co-folding predictors (~400 words)

- **AlphaFold2 and AlphaFold-Multimer** \[@alphafold2; @alphafold_multimer\]:
  differentiable IPA structure module, ipTM/iPAE interface metrics, shallow-MSA
  weakness; **OpenFold** [@openfold] open retraining.
- **AlphaFold3** \[@alphafold3\]: Pairformer + all-atom diffusion, 1,000-seed
  antibody sampling, documented diffusion caveats (4.4% chirality violations,
  clashes, disordered-region hallucinations, static structures), restricted
  weights.
- **Independent and open AF3-class predictors:** **RoseTTAFold** (RF1 3-track →
  RF2 ablation showing IPA/triangle attention are unnecessary → RFAA → **RF3**
  learning stereochemistry directly without inference steering) \[@rosettafold;
  @rosettafold2; @rosettafold_all_atom; @rosettafold3\]; open-weights co-folders
  **Boltz-1/1x/2** (MIT; Feynman-Kac steering; small-molecule-only affinity
  head) [@boltz1; @boltz2], **Chai-1** (hybrid MSA/PLM tracks; experimental
  restraints; single-sequence antibody parity) [@chai1], **Protenix-v1/v2**
  (matched-conditions AF3 parity; 5-seed v2 surpassing 1,000-seed v1; PXMeter
  planarity checks) [@protenix_v1; @protenix_v2; @pxmeter], **OpenFold3**
  (Apache-2.0 weights, code, and 13M-sequence distillation set) [@openfold3],
  and **OpenDDE** (Apache-2.0, 3× wider Pairformer + atom-level refiner)
  [@opendde].

### 2.2 Structure diffusion, inverse folding, and trained filters (~500 words)

- **Backbone and all-atom diffusion + inverse folding:** **RFdiffusion**
  (equivariant frame diffusion fine-tuned from RF1; established backbone →
  **ProteinMPNN** [@proteinmpnn] → AF2 pipeline; sequence-recovery caveat;
  **LigandMPNN** [@ligandmpnn] and **AlphaDesign** ADM [@alphadesign]
  alternatives) → **RFdiffusion2** (active-site scaffolding) [@rfdiffusion2] →
  **RFdiffusion3** (pre-trained all-atom U-Net, 2 Pairformer layers, ~10×
  faster) [@rfdiffusion3]. Brief pointer to **PXDesign-d** (Cartesian DiT
  diffusion) [@pxdesign] and ODE flow-matching generators \[@frameflow;
  @ppiflow; @originflow; @atomflow; @dflow\].
- **Unified prediction-and-design diffusion and trained scorers:** **BoltzGen**
  (MIT-licensed single all-atom diffusion model for both prediction and
  multi-modality design excluding full mAbs; 26 targets including 6/9 novel
  targets at ≤15 designs; ubiquitin memorization caveat) [@boltzgen] and
  **BoltzProt-1 / BoltzPPI** (controlled filter swap on identical pools raising
  confirmed binders from 3.3% to 8.0%; explicit screening-hit vs.
  confirmed-binder distinction) [@boltzprot1].
- **Antibody and macrocycle pipelines:** **RFantibody** (epitope-specific
  VHH/scFv/mAb still paired with 9,000-design yeast display; 0–2% hit rate)
  [@rfantibody], **RFpeptides** (cyclic relative positional encoding; \<20
  designs/target with crystal structures) [@rfpeptides], **Chai-2** (zero-shot
  scFv/VHH at ≤20 designs/target, 16% combined hit rate; generator undisclosed)
  [@chai2], and **Protenix-v2** (novelty-controlled soluble VHH-Fc and GPCR
  VHH-Fc/mAb campaigns at 16–30 designs/target; AMBP epitope sensitivity 4% vs.
  48%) [@protenix_v2].

### 2.3 Gradient-based sequence optimization (~450 words)

- **Full-network AF2 inversion (ColabDesign [@colabdesign]):** **AfCycDesign**
  (cyclic positional encoding; monomeric hallucination + motif-grafted binders)
  [@afcycdesign] and **BindCraft** (AlphaFold-Multimer inversion, 5-model random
  swap, induced-fit target reprediction, 4-stage continuous-to-discrete
  annealing, ProteinMPNN surface redesign, 10–100% hit rates across 12 targets;
  single-sequence and non-affinity ipTM caveats) [@bindcraft].
- **Handling diffusion predictors:** **BoltzDesign1** (stop-gradient on Boltz-1
  diffusion, 64-bin Pairformer distogram contact loss + optional confidence
  head; in-silico only) [@boltzdesign1], **RFOptimization** (strictly discrete
  Metropolis–Hastings mutations from RF3 distogram/confidence gradients
  interleaved with Boltz/LigandMPNN cycling, AF3 held out; in-silico only)
  [@rfoptimization], and **PXDesign-h** (differentiable 2-step ODE sampler
  across five Protenix models) [@pxdesign].
- **Adding language-model priors for antibodies:** **Germinal** (live IgLM
  gradient merged with AF-Multimer via weighted sum/MGDA/PCGrad; nonbinders
  passing ipSAE caveat; **OpenGerminal** Apache-2.0 port) \[@germinal;
  @opengerminal\] contrasted with **mBER** (static ESM-2 logit bias +
  NanoBodyBuilder2 template; 1.15M-design randomized-hotspot phage sweep)
  [@mber].

### 2.4 Protein language models and single-sequence design (~250 words)

- **ESM-2 / ESMFold** [@esm2] (single-sequence folding without MSAs) → **ESM-3**
  [@esm3] (multimodal sequence/structure/function discrete tokens up to 98B;
  `esmGFP`).
- **ESMC / ESMFold2** [@esmc] (6B LM + 48-layer recurrent folding trunk +
  sliding-window diffusion transformer; single-sequence Ab–Ag matching
  AF3-with-MSA within error bars [@atlasfold]; 150-step single-stage ESMC +
  distogram gradient optimization native to single-sequence input; 84
  designs/cohort across five targets, mean 70.0% minibinders / 21.0% scFvs).
- **AtlasFold** [@atlasfold] (independent MIT-licensed single-sequence PLM
  folder + multi-model FoldBench benchmark).

### 2.5 Undisclosed and proprietary systems (~150 words)

- **AlphaProteo** (9–88% across 8 targets, 0/54 TNFα; disclosed AF2 filter,
  undisclosed generator; resynthesized RFdiffusion designs) [@alphaproteo],
  **Latent-X1 / Latent-X2** (proprietary all-atom platform for macrocycles,
  minibinders, and low-immunogenicity/developable antibodies; partial RFpeptides
  resynthesis) [@latentx1; @latentx2], alongside **Chai-2**'s undisclosed
  generator [@chai2], commercial API-only **BoltzProt-1** [@boltzprot1], and
  unpublished **IsoDDE** (known publicly only through OpenDDE scaling curves
  [@opendde; @bender_perspective]). Focus on what disclosure limits mean for
  independent verification.

______________________________________________________________________

## 3. Interpreting Benchmarks and Wet-Lab Campaigns (~550 words + Table 2)

Concise analytical guide to reading published numbers without ranking models
(key FoldBench/AtlasFold prediction takeaways carried cleanly in prose; **Table
2** carries representative wet-lab campaigns):

- **Prediction convergence vs. antibody difficulty:** On FoldBench's common
  target intersection [@foldbench; @protenix_v1], monomer lDDT sits tightly in
  0.85–0.89 and protein–protein DockQ success spans 65.4–72.7%, while
  antibody–antigen spans 23.1–52.3% (noting Boltz-2's June 2023 training-cutoff
  overlap [@boltz2]).
- **Metric sensitivity and the confidence-ranking gap:** Unequal inference
  failures reverse Boltz-1 vs. Chai-1 rankings on FoldBench PPI [@protenix_v1];
  per-cluster (52.9% [@chai1]) vs. per-interface (25.2% [@foldbench]) averaging
  doubles Chai-1's antibody score; Boltz-1 averages per interface within
  complexes [@boltz1]. Across seven predictors in AtlasFold [@atlasfold],
  confidence-ranked selection trails oracle selection by 11–21 percentage points
  on antibody–antigen (3–8 points on PPI), explaining large seed budgets (1,000
  seeds in AF3 [@alphafold3]; 36.01%→47.68% at 80 seeds in Protenix-v1
  [@protenix_v1]; ~66%→>90% oracle in OpenDDE [@opendde]).
- **Confounders in wet-lab campaigns (**→ Table 2\*\*):\*\* Testing budgets
  dropping from thousands/millions to tens; screening hits vs. confirmed binders
  (BoltzProt-1 [@boltzprot1]); target/epitope selection (mBER's 0.4% median
  across random hotspots vs. 38% on best filtered epitopes [@mber]); bivalent Fc
  avidity [@protenix_v2; @chai2; @bindcraft]; synthesis/expression attrition
  [@rfpeptides; @latentx1; @pxdesign]; target-level vs. per-design rates; and
  cross-lab resynthesis shifts (AlphaProteo on RFdiffusion [@alphaproteo];
  Latent-X1 on RFpeptides [@latentx1]).

______________________________________________________________________

## 4. Conclusions and Open Challenges (~650 words)

### 4.1 From in vitro binding to therapeutic utility (~200 words)

- Therapeutic motivation stated across binder-design papers \[@boltzgen; @chai2;
  @bindcraft; @latentx2; @mber\] contrasted with Bender et al.'s distinction
  between *model validation* (benchmark accuracy and in vitro binding rates) and
  *process validation* (improving clinical decisions), plus biologics vs. small
  molecules (binding easier to predict than function and developability; >$10^6$
  ChEMBL/PubChem ligands vs. ~$10^3$ drugs), task-matched metrics, local
  generalization, and verifiability [@bender_perspective].

### 4.2 Five documented open limitations (~450 words)

1. **Developability, function, and immunogenicity:** Almost all open pipelines
   optimize and filter solely for binding; Latent-X2 reports developability and
   low immunogenicity but withholds its architecture [@latentx2].
1. **Protein–protein binding affinity prediction:** Structure-confidence scores
   predict binding rather than $K_D$ (BindCraft [@bindcraft]); Boltz-2's
   affinity head covers protein–ligand complexes only [@boltz2].
1. **Targets without experimental structures:** Dependence of design success on
   predicted antigen-model accuracy remains open (Germinal [@germinal]).
1. **Lack of shared, blinded prospective de novo benchmarks:** Only one
   full-campaign replication exists (AlphaProteo on RFdiffusion \[@alphaproteo;
   @rfdiffusion\]); **AIntibody** [@aintibody] (511 IgGs, 29 organizations,
   SARS-CoV-2 RBD) demonstrated blinded testing (95 pM top design matching 113
   pM wet-lab best, but only 1/26 beating random within-cluster affinity ranking
   and a 2.9 pM winner failing HIC), while testing library-conditioned
   engineering on one well-characterized antigen rather than de novo design.
1. **Per-design discrimination limits of confidence filters:** Confidence scores
   enrich large libraries (mBER [@mber]) yet often fail on individual candidates
   (Germinal [@germinal]); Overath et al.'s re-scoring of 3,766 designs across
   15 targets found AF3 ipSAE best overall yet spanning average precision
   0.1–1.0 across targets [@overath_meta].

- Grounded closing paragraph summarizing current capabilities and what remains
  to be demonstrated.

______________________________________________________________________

## Compact Display Items (3 total, strictly matching PLOS Comp Biol guidance)

1. **Figure 1 — Co-folding architectures and binder-design workflows:**
   Two-panel schematic (Panel A: MSA/PLM trunk → IPA regression, SDE diffusion,
   or ODE flow matching; Panel B: joint predictor-generators,
   generate-and-filter pipelines, and gradient-based sequence optimization
   paths).
1. **Table 1 — Representative structure predictors and binder-design systems
   (~11 rows × 6 columns):** One clean row per representative archetype/lineage
   (AlphaFold2/Multimer, AlphaFold3 & OpenFold3, RoseTTAFold3, RFdiffusion 1–3 +
   ProteinMPNN/LigandMPNN, Boltz-1/2 & BoltzGen/BoltzProt-1, Chai-1 & Chai-2,
   BindCraft & AfCycDesign, BoltzDesign1 & RFOptimization, Germinal & mBER,
   Protenix-v1/v2 & PXDesign, ESMFold2 & AtlasFold, Closed/undisclosed:
   AlphaProteo & Latent-X1/X2).
1. **Table 2 — Representative wet-lab binder-design campaigns (~12 rows × 6
   columns):** One representative campaign row per major system, grouped by
   validation rigor (dual-assay confirmation: BoltzProt-1, Germinal, Latent-X1
   minibinders; single-assay format: RFpeptides, BoltzGen novel targets,
   PXDesign, Chai-2 antibodies, Protenix-v2 GPCRs, BindCraft, ESMFold2,
   RFdiffusion, AlphaProteo, Latent-X2 antibodies; display enrichment without
   affinity: RFantibody, mBER), keeping cells concise and scannable.

______________________________________________________________________

## Word-Budget Summary

| Section                                        |     Target words |          Share |
| ---------------------------------------------- | ---------------: | -------------: |
| Abstract                                       |             ~220 | (front matter) |
| 1. Introduction & Conceptual Background        |      1,300–1,400 |           ~31% |
| 2. Approaches & Representative Systems         |      1,700–1,850 |           ~40% |
| 3. Interpreting Benchmarks & Wet-Lab Campaigns |          500–600 |           ~13% |
| 4. Conclusions & Open Challenges               |          600–700 |           ~15% |
| **Main Text Total**                            | **~4,300–4,600** |       **100%** |
