# Quantitative Landscape and Evaluation Pitfalls

Interpreting structure-prediction and binder-design benchmarks requires reading
every metric alongside its evaluation protocol. On the common target
intersection of FoldBench (1,522 assemblies across nine tasks scored by lDDT,
DockQ, and RMSD), monomer accuracy across seven AF3-class predictors has
converged into a tight 0.85–0.89 lDDT band and general protein–protein DockQ
success spans roughly 7 percentage points (65.4–72.7%), whereas antibody–antigen
success spans more than a factor of two (23.1–52.3%; Table 2A) \[@foldbench;
@protenix_v1\]. Even on a shared target set, training cutoffs constrain who can
be compared: Boltz-2 is excluded from FoldBench common-intersection tables
because its 2023-06-01 cutoff overlaps the 2023-01-13 to 2024-11-01 benchmark
window [@boltz2; @protenix_v1; @protenix_v2; @esmc].

Identical metric names also shift when target filtering, averaging units, or MSA
pipelines change. Because models fail on different inputs (out-of-memory errors,
unsupported glycans, or token limits), restricting FoldBench protein–protein
pairs to the common completed set (n = 237) reverses Boltz-1 (68.4% vs. 68.3%
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
evaluated template-free by AtlasFold (Table 2A), selecting the top sample by
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

Wet-lab binder campaigns are even less directly comparable because no two de
novo studies share a target panel, assay format, or binding threshold. Grouping
campaigns by confirmation rigor (Table 2B) exposes four recurring confounders.
First, several headline affinities reflect bivalent Fc fusions or
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
[@latentx2]. Table 2B therefore summarizes performance within each study's own
experimental regime rather than a common scale.

## Table 2A: Shared Prediction Benchmarks and Selection Gaps

| Model                                  | FoldBench Monomer (lDDT, n = 287) | FoldBench Prot–Prot (%, n = 237) | FoldBench Ab–Ag (%, n = 160) | FoldBench Prot–Lig (%, n = 441) | AtlasFold Ab–Ag Rank / Oracle (%, n = 172) | AtlasFold Prot–Prot Rank / Oracle (%, n = 278) |
| -------------------------------------- | --------------------------------: | -------------------------------: | ---------------------------: | ------------------------------: | -----------------------------------------: | ---------------------------------------------: |
| Protenix-v1 [@protenix_v1]             |                            0.8857 |                            72.70 |                        52.31 |                           62.54 |                            44.945 / 65.818 |                                74.445 / 81.572 |
| AlphaFold3 [@alphafold3]               |                            0.8803 |                            71.73 |                        48.75 |                           62.59 |                            49.285 / 66.168 |                                73.006 / 78.028 |
| Boltz-1 [@boltz1]                      |                            0.8664 |                            68.35 |                        34.38 |                           54.65 |                            34.967 / 39.505 |                                71.120 / 76.632 |
| Protenix-v0.5.0 [@protenix_v1]         |                            0.8717 |                            68.06 |                        43.94 |                           58.49 |                                        n/a |                                            n/a |
| Protenix-v0.2.0 [@protenix_v1]         |                            0.8622 |                            66.24 |                        35.62 |                           51.02 |                                        n/a |                                            n/a |
| HelixFold3 [@protenix_v1]              |                            0.8547 |                            65.40 |                        28.75 |                           52.38 |                                        n/a |                                            n/a |
| Chai-1 [@chai1]                        |                            0.8639 |                            67.51 |                        23.12 |                           50.79 |                                        n/a |                                            n/a |
| ESMFold2 (MSA) [@esmc]                 |                               n/a |                              n/a |                          n/a |                             n/a |                            52.270 / 63.427 |                                73.230 / 77.237 |
| ESMFold2 (seq only) [@esmc]            |                               n/a |                              n/a |                          n/a |                             n/a |                            48.602 / 61.489 |                                69.216 / 74.071 |
| AtlasFold-M (seq only) [@atlasfold]    |                               n/a |                              n/a |                          n/a |                             n/a |                            46.955 / 64.733 |                                63.358 / 71.560 |
| AF-Multimer v2.3 [@alphafold_multimer] |                               n/a |                              n/a |                          n/a |                             n/a |                            40.924 / 52.921 |                                65.206 / 68.615 |

*Notes for Table 2A:* FoldBench common-intersection columns report PDB entries
released 2023-01-13 to 2024-11-01 (homology-reduced against a reproduction of
AlphaFold3's 2021-09-30 training set) under 5 seeds × 5 diffusion samples, 10
recycles, top-ranked prediction [@foldbench; @protenix_v1]. Monomer is mean
lDDT; Prot–Prot and Ab–Ag are DockQ success rate (DockQ >= 0.23, %); Prot–Lig is
joint success rate (ligand RMSD < 2 Å and lDDT-PLI > 0.8, %). AlphaFold3,
Boltz-1, Chai-1, HelixFold3, and Protenix-v0.2.0 rows were recomputed by the
Protenix-v1 authors from published per-instance logs with the
common-intersection filter applied; Protenix-v0.5.0 and Protenix-v1 are the
authors' own runs (Protenix-v1 bootstrapped over 5-seed draws from 20 seeds)
[@protenix_v1]. On the same common set, nucleic-acid subsets span 50.00–68.46%
(Prot–RNA, n = 46), 49.27–75.91% (Prot–DNA, n = 274), 0.2909–0.5693 lDDT (DNA, n
= 14), and 0.4416–0.6547 lDDT (RNA, n = 15) [@protenix_v1]. Boltz-2 [@boltz2] is
excluded because its 2023-06-01 training cutoff overlaps the FoldBench window
[@protenix_v1; @protenix_v2; @esmc]. AtlasFold columns report mean DockQ > 0.23
(%) across 252 five-seed subsets drawn from 10 seeds, template-free throughout,
computed with OpenStructure 2.9.1; AlphaFold3, Boltz-1, Protenix-v1, and
ESMFold2 (MSA) used AlphaFold3-pipeline MSAs, whereas ESMFold2 (seq only) and
AtlasFold-M ran without MSAs [@atlasfold]. Per-class headline tables in
AlphaFold3 (Extended Data Table 1 / Fig. 1c) [@alphafold3], Boltz-1 [@boltz1],
Boltz-2 [@boltz2], and RoseTTAFold2 [@rosettafold2] are published as figure-only
images rather than extractable text.

## Table 2B: Representative Wet-Lab and In-Silico Binder Design Campaigns

| System                                                        | Modality & Targets                                                  |                            Designs Tested | Reported Outcome / Hit Rate                                                                                                                       | Best Affinity                                      | Key Assay Criterion & Caveats                                                                                                                                                          |
| ------------------------------------------------------------- | ------------------------------------------------------------------- | ----------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Binding confirmed across two assay formats**                |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| BoltzProt-1 [@boltzprot1]                                     | VHH, 10 low-homology targets                                        |                           15/target (150) | 12 confirmed binders (8.0%; 4/10 targets); BoltzGen on same pools and budget: 5 (3.3%; 2/10 targets)                                              | Not reported                                       | Clean sensorgram verified by flipped assay orientation and independent vendor re-testing; separate from initial screening hits (see footnote) [@boltzprot1].                           |
| Germinal [@germinal]                                          | scFv (tested as Fab), 2 targets                                     |                                 48/target | 3/48 PD-L1 and 1/48 IL-3 confirmed on both SPR and BLI                                                                                            | 360 nM (SPR) / 650 nM (BLI)                        | Dual SPR and BLI confirmation [@germinal].                                                                                                                                             |
| Latent-X1 [@latentx1]                                         | Minibinders, 5 targets                                              | 100/target (HT-BLI), 88/target (mDisplay) | 10–64% per target (platforms correlate at Pearson r = 0.68–0.79)                                                                                  | < 0.01 nM (IL-7Rα, SC2RBD)                         | Robust mammalian-display dynamic range on 3 of 5 targets; proprietary architecture undisclosed [@latentx1].                                                                            |
| Germinal [@germinal]                                          | VHH, 4 targets                                                      |                101 / 46 / 43 / 52 ordered | 7 / 2 / 4 / 5 confirmed by BLI after split-luciferase screen                                                                                      | 170 nM (PD-L1); 42 nM after Legobody rescaffolding | Expression luminescence > 150,000 RLU and rising binding ratio between two timepoints, then detectable BLI; quoted fractions use BLI sub-denominators (25 / 11 / 11 / 20) [@germinal]. |
| **Single assay format**                                       |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| Latent-X2 [@latentx2]                                         | Macrocycles, 2 targets                                              |                                 10/target | 9/10 (PHD2), 8/10 (K-Ras G12D)                                                                                                                    | 1.54 nM (PHD2)                                     | Reference-subtracted single-point BLI > 0.1 nm advancing to kinetics (global fit R² > 0.95); architecture undisclosed [@latentx2].                                                     |
| RFpeptides [@rfpeptides]                                      | Macrocycles, 4 targets                                              |           6–14 tested (of 11–27 selected) | 2–4 hits per target                                                                                                                               | 6 nM (GABARAP)                                     | SPR single-cycle kinetics at 100 µM (no numeric threshold stated); synthesis attrition (14/27 MCL-1, 11/26 RbtA); crystal structures solved [@rfpeptides].                             |
| BoltzGen [@boltzgen]                                          | VHH and proteins, 9 novel targets                                   |                                 15/target | Binders on 6/9 targets, both modalities                                                                                                           | 6.1 nM VHH (PMVK); 9.8 nM protein (MZB1)           | Quantifiable sensorgram, or association >= 300% of negative control where fitting failed; target-level rate reported [@boltzgen].                                                      |
| PXDesign [@pxdesign]                                          | Minibinders, 6 targets                                              |                               9–17/target | 20–73% on 5 targets; 0/16 on TNFα                                                                                                                 | "Multiple nanomolar" (no exact value in text)      | BLI > 0.06 nm at 1 µM then K_D < 1,000 nM; PD-L1 attrition: 72.7% of tested vs. 47.1% sent for expression (6 excluded) [@pxdesign].                                                    |
| Latent-X1 [@latentx1]                                         | Macrocycles, 3 targets                                              |                              11–17/target | 91 / 100 / 94%                                                                                                                                    | 5.35 µM (MDM2)                                     | Measurable SPR signal (no numeric threshold stated); 11–17 synthesized of 30 submitted (700 generated); architecture undisclosed [@latentx1].                                          |
| Chai-2 [@chai2]                                               | scFv and VHH, 52 novel targets                                      |                      \<= 20/target/format | 13.7% scFv (68/496), 20.0% VHH (41/205); 26/52 targets                                                                                            | < 1 nM (EFNA5 scFv, avidity-flagged)               | Binding-positive curve > 0.1 nm and > 300% of background; EFNA5 scFv avidity-flagged; generator undisclosed [@chai2].                                                                  |
| BoltzGen [@boltzgen]                                          | VHH and proteins, 5 benchmark targets                               |                              15–20/target | Binders on 4/5 targets                                                                                                                            | 0.81 nM (PDGFR)                                    | Same sensorgram / >= 300% negative-control criterion; target-level rate reported [@boltzgen].                                                                                          |
| Latent-X2 [@latentx2]                                         | VHH and scFv, 18 targets                                            |                        4–24/target/format | Binders on 9/18 targets; up to 25% of designs                                                                                                     | 26.2 pM (HDAC8 scFv)                               | Single-point BLI > 0.1 nm advancing to kinetics (global fit R² > 0.95; R² > 0.90 with visual review for AHSP); architecture undisclosed [@latentx2].                                   |
| Chai-2 [@chai2]                                               | Minibinders, 5 targets                                              |                              20–25/target | 68% (75/111); binders on 5/5 targets                                                                                                              | 18.3 pM (IL-7Rα)                                   | Same > 0.1 nm and > 300% background criterion; 4 of 10 quoted miniprotein affinities avidity-affected [@chai2].                                                                        |
| Protenix-v2 [@protenix_v2]                                    | VHH-Fc and mAb, 4 GPCRs                                             |                              16–30/target | VHH-Fc 16 / 62 / 40 / 88%; mAb 0 / 17 / 50 / 44%                                                                                                  | 112 pM (GPRC5D, avidity)                           | BLI > background + 0.05 nm (most hits K_D < 1,000 nM); bivalent VHH-Fc and mAb avidity [@protenix_v2].                                                                                 |
| Protenix-v2 [@protenix_v2]                                    | VHH-Fc, soluble targets                                             |                               Figure only | 2–48% per target; binders on all targets                                                                                                          | Figure only                                        | Same BLI > background + 0.05 nm cutoff; bivalent VHH-Fc avidity (except VEGF-A); per-target counts/affinities figure-only (see footnote) [@protenix_v2].                               |
| BindCraft [@bindcraft]                                        | Minibinders, 12 targets                                             |                               6–53/target | 10–100%, mean 46.3%                                                                                                                               | < 1 nM (PD-1, bivalent Fc); 5 nM (CbAgo)           | Binding observed on SPR (no numeric threshold stated); PD-1 is bivalent Fc (exact K_D undetermined) [@bindcraft].                                                                      |
| ESMFold2 campaign [@esmc]                                     | Minibinders, 5 targets                                              |                                 84/cohort | 36–88%, mean 70.0% (higher compute)                                                                                                               | 68 pM (target not stated in text)                  | Dual BLI criteria: stringent target-specific (0.25–0.4 nm) and inclusive (> 0.1 nm), probe loading > 0.5 nm, positive exponential association; Fig. 3 shading image-only [@esmc].      |
| ESMFold2 campaign [@esmc]                                     | scFv, 5 targets                                                     |                                 84/cohort | 15–29%, mean 21.0% (higher compute)                                                                                                               | Not reported                                       | Same dual BLI criteria and image-only Fig. 3 shading caveat [@esmc].                                                                                                                   |
| RFdiffusion [@rfdiffusion]                                    | Minibinders, 5 targets                                              |                           95/target (475) | 19% pooled over 475                                                                                                                               | 28 nM (influenza HA)                               | Single-point BLI at 10 µM >= 50% of positive control; lower hit rates on yeast-display re-assay by AlphaProteo [@rfdiffusion; @alphaproteo].                                           |
| AlphaProteo [@alphaproteo]                                    | Minibinders, 8 targets                                              |                             54–172/target | 9% (TrkA) to 88% (BHRF1); 0/54 on TNFα                                                                                                            | 82 pM (IL-7Rα)                                     | Yeast-display flow-cytometry signal > 0.2 (raised to 1.3 for IL-17A due to background); generator undisclosed [@alphaproteo].                                                          |
| **Display or enrichment signal without affinity measurement** |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| BoltzGen [@boltzgen]                                          | VHH, 2 targets                                                      |                  7/target (yeast display) | 1/7 and 7/7 showing signal                                                                                                                        | "At best 2 µM" (no EC50 computable)                | Qualitative yeast-display binding signal without computable EC50 [@boltzgen].                                                                                                          |
| RFantibody [@rfantibody]                                      | VHH, 3 targets                                                      |                           95/target (SPR) | 0–2% range                                                                                                                                        | Not separately listed                              | Single-concentration SPR following *E. coli* expression [@rfantibody].                                                                                                                 |
| RFantibody [@rfantibody]                                      | VHH, 4 targets                                                      |              9,000/target (yeast display) | 0–2% per target                                                                                                                                   | 78 nM (HA), 1.4 µM (RSV site III) by SPR           | Authors note experimental library screening remains necessary given current success rates [@rfantibody].                                                                               |
| mBER [@mber]                                                  | VHH, 145 of 436 targets assayed                                     |  1,153,241 designs (pooled phage display) | 45% (65/145) targets elevated; per-design 0.02–8% (median ~0.4%); 38% (8/21) in one ipTM-filtered epitope bin                                     | Not measured                                       | Per-sequence replicate order statistic (< 1 expected false positive/target); phage display cannot quantify exact affinities [@mber].                                                   |
| **Functional readout without direct binding assay**           |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| BoltzGen [@boltzgen]                                          | Peptides, NPM1                                                      |                                         5 | 1/5 showed nucleolar co-localization in live cells                                                                                                | Not measured                                       | Live-cell co-localization does not confirm specific disordered-region binding [@boltzgen].                                                                                             |
| BoltzGen [@boltzgen]                                          | Antimicrobial peptides, GyrA                                        |                                     1,808 | 352 (19.5%) inhibited *E. coli* growth >= 4-fold; 54 lost activity upon 3-residue interface alanine mutation                                      | Not measured                                       | Functional growth-inhibition readout rather than direct binding assay [@boltzgen].                                                                                                     |
| **In-silico evaluation only**                                 |                                                                     |                                           |                                                                                                                                                   |                                                    |                                                                                                                                                                                        |
| BoltzDesign1 [@boltzdesign1]                                  | Protein and biomolecular targets                                    |                            In-silico only | Computational metrics only                                                                                                                        | Not applicable                                     | No wet-lab validation [@boltzdesign1].                                                                                                                                                 |
| RFOptimization [@rfoptimization]                              | Protein–protein interfaces, cyclic peptides, small-molecule binders |  In-silico only (denominators not stated) | AF3-refolded success (iPAE < 2.5, ipTM > 0.8): 6.73% to 22.31% (PPI), 1.25% to 12.57% (cyclic peptides), 5.62% to 24.91% (small-molecule binders) | Not applicable                                     | AlphaFold3 held out of optimization; no wet-lab testing; denominators not stated [@rfoptimization].                                                                                    |

*Notes for Table 2B:* Within each validation group, campaigns are ordered by
designs tested per target (ranging from 5 to 9,000, or pooled at >10⁶ for mBER).
Several source values are subject to figure-only reporting constraints:
Protenix-v2's soluble-target per-target denominators and affinities appear only
in Fig. 4A (per-epitope ratios 2/50 and 13/27 on AMBP and 12/50 on IDI2 are
transcribed in BoltzProt-1) [@protenix_v2; @boltzprot1], and ESMFold2's shading
distinguishing stringent from inclusive BLI cutoffs in Fig. 3 is image-only
[@esmc]. In BoltzProt-1 [@boltzprot1], an internal discrepancy exists for
revised screening hits (Table 1 lists 7/150 [4.7%] for BoltzGen and 14/150
[9.3%] for BoltzProt-1, whereas the prose states 14/150 [9.3%] and 24/150
[16.0%]), while the confirmed-binder figures reported in Table 2B (5/150 [3.3%]
and 12/150 [8.0%]) are consistent in both table and prose.
