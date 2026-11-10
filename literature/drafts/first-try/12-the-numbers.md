# The numbers

The sections above quoted their figures one claim at a time. Collected, the same
figures say things no single one does: prediction accuracy sits in a narrow band
on every class the co-folding models handle comfortably, and spans a factor of
two on antibody–antigen; and design success rates range over an order of
magnitude between papers pursuing comparable ideas. Neither statement is
readable without the conditions a figure was measured under — which benchmark,
which subset of targets, how many seeds or designs, what counted as a hit — so
each exhibit carries those conditions alongside its figures, and two of the five
are given over to conditions alone.

## Exhibit 1 — Prediction accuracy on a common set of targets

Co-folding models fail on different inputs: out-of-memory on large assemblies,
unsupported glycan formats, token limits. A comparison that scores each model
only on the targets it completed therefore scores each model on a different
subset.

Protenix-v1 reports FoldBench restricted to the **common intersection** —
targets every compared model predicted and scored successfully.

Monomer and nucleic-acid monomer columns are mean lDDT. Protein–protein,
antibody–antigen, protein–RNA and protein–DNA are DockQ success rate (DockQ ≥
0.23), in percent. Protein–ligand is the joint success rate requiring both
ligand RMSD < 2 Å and lDDT-PLI > 0.8, in percent.

| Model           | Monomer | Prot–Prot | Ab–Ag | Prot–Lig | Prot–RNA | Prot–DNA |    DNA |    RNA |
| --------------- | ------: | --------: | ----: | -------: | -------: | -------: | -----: | -----: |
| AlphaFold3      |  0.8803 |     71.73 | 48.75 |    62.59 |    65.22 |    75.91 | 0.5278 | 0.6140 |
| Boltz-1         |  0.8664 |     68.35 | 34.38 |    54.65 |    65.22 |    67.15 | 0.3388 | 0.4416 |
| Chai-1          |  0.8639 |     67.51 | 23.12 |    50.79 |    50.00 |    66.06 | 0.4574 | 0.4852 |
| HelixFold3      |  0.8547 |     65.40 | 28.75 |    52.38 |    52.17 |    49.27 | 0.2909 | 0.5487 |
| Protenix-v0.2.0 |  0.8622 |     66.24 | 35.62 |    51.02 |    56.52 |    64.60 | 0.4384 | 0.5903 |
| Protenix-v0.5.0 |  0.8717 |     68.06 | 43.94 |    58.49 |    59.37 |    68.02 | 0.4960 | 0.6046 |
| Protenix-v1     |  0.8857 |     72.70 | 52.31 |    62.54 |    68.46 |    69.13 | 0.5693 | 0.6547 |

**Conditions.** Targets per column: 287 monomers, 237 protein–protein, 160
antibody–antigen, 441 protein–ligand, 46 protein–RNA, 274 protein–DNA, 14 DNA
monomers, 15 RNA monomers. Benchmark window: PDB entries released 2023-01-13 to
2024-11-01, homology-reduced against a reproduction of AlphaFold3's 2021-09-30
training set. Sampling: 5 seeds × 5 diffusion samples, 10 recycles, top-ranked
structure.

**Provenance.** The AlphaFold3, Boltz-1, Chai-1, HelixFold3 and Protenix-v0.2.0
rows were recomputed from the per-instance prediction logs those models' authors
published, with the intersection filter applied; they were not re-run. The
Protenix-v0.5.0 and Protenix-v1 rows are the Protenix authors' own runs,
bootstrapped by drawing 5 seeds from a pool of 20 (seeds 101–120); the paper's
table note states that draw scheme for Protenix-v1, and the v0.5.0 row carries
error bars without a separately stated scheme.

**Boltz-2 is absent.** Its training cutoff is 2023-06-01, which overlaps this
benchmark window. Protenix-v1, Protenix-v2 and the ESMFold2 authors each note
the overlap.

Monomer accuracy sits between 0.85 and 0.89 lDDT for every model.
Protein–protein spans about seven points. Antibody–antigen spans 23 to 52
percent, roughly the factor of two the antibody-focused sections above reported
one model at a time.

## Exhibit 2 — How much a figure depends on how it was computed

**AlphaFold3, FoldBench antibody–antigen:**

| Reported | Source                | Condition                                               |
| -------: | --------------------- | ------------------------------------------------------- |
|    47.90 | FoldBench leaderboard | n = 167, no intersection filter                         |
|    48.75 | Protenix-v1           | n = 160, intersection of all compared models            |
|    0.488 | OpenDDE               | AlphaFold3, re-run by OpenDDE on FoldBench-AB (n = 160) |

That last figure is OpenDDE's re-run of AlphaFold3, not AlphaFold3's own
posting; on the same subset OpenDDE itself reaches 0.700.

**Chai-1, antibody interfaces:**

| Reported | Source    | Averaging unit                                                            |
| -------: | --------- | ------------------------------------------------------------------------- |
|    0.529 | Chai-1    | per 40%-identity interface cluster (n = 122 clusters from 268 interfaces) |
|    25.2% | FoldBench | per interface (n = 123 antibody targets)                                  |

Clustering at 40% identity keeps a well-represented antigen family from
dominating the mean; averaging per interface treats each measured interface as
one observation. Both are reported as "DockQ success rate". Boltz-1 uses a third
unit, averaging per interface within a complex and then across complexes.

**Intersection filtering, worked example.** Protenix-v1 gives the FoldBench
protein–protein subset as published and as corrected:

| Model   |    As published | Common set (n = 237) |
| ------- | --------------: | -------------------: |
| Boltz-1 | 172/252 = 0.683 |      162/237 = 0.684 |
| Chai-1  | 172/251 = 0.685 |      160/237 = 0.675 |

Boltz-1's figures were computed on 252 interfaces and Chai-1's on 251, with 237
shared between them.

## Exhibit 3 — Confidence-ranked and oracle selection

These models generate several candidate structures and select one using their
own confidence score. AtlasFold reports both that selection ("rank") and
selection of the best candidate against the reference structure ("oracle",
unavailable at inference time).

**FoldBench antibody–antigen, 172 targets, DockQ > 0.23 success rate (%):**

| Model               |   Rank | Oracle |
| ------------------- | -----: | -----: |
| AlphaFold3          | 49.285 | 66.168 |
| Protenix-v1         | 44.945 | 65.818 |
| ESMFold2 (MSA)      | 52.270 | 63.427 |
| ESMFold2 (seq only) | 48.602 | 61.489 |
| AtlasFold-M         | 46.955 | 64.733 |
| AF-Multimer v2.3    | 40.924 | 52.921 |
| Boltz-1             | 34.967 | 39.505 |

**FoldBench protein–protein, 278 targets, same metric:**

| Model               |   Rank | Oracle |
| ------------------- | -----: | -----: |
| Protenix-v1         | 74.445 | 81.572 |
| ESMFold2 (MSA)      | 73.230 | 77.237 |
| AlphaFold3          | 73.006 | 78.028 |
| Boltz-1             | 71.120 | 76.632 |
| ESMFold2 (seq only) | 69.216 | 74.071 |
| AF-Multimer v2.3    | 65.206 | 68.615 |
| AtlasFold-M         | 63.358 | 71.560 |

**Conditions.** Mean across 252 five-seed subsets drawn from 10 seeds; the
source reports error bars as one standard deviation across those subsets.
AlphaFold3, Boltz-1, Protenix-v1 and ESMFold2-MSA were run with MSAs through the
AlphaFold3 input pipeline; ESMFold2 and AtlasFold-M without. All runs
template-free. Metrics computed with OpenStructure 2.9.1.

The rank–oracle gap is the size of the selection step: 11 to 21 points on
antibody–antigen for every model except Boltz-1, whose 4.5-point gap means its
confidence ranking loses little against the best of its samples, and 3 to 8
points on protein–protein. FoldBench reports the corresponding observation on
its own set: a near-native CDR-H3 is necessary but not sufficient for a correct
interface, and per-sample confidence scores do not reliably identify near-native
conformations.

Related figures elsewhere in the corpus: AlphaFold3's antibody results were
ranked across 1,000 seeds rather than the 5 used for its other target classes;
OpenDDE reports oracle success on FoldBench-AB rising from about 66% at one seed
to above 90% at several hundred; Protenix-v1 reports DockQ success rising from
36.01% at one seed to 47.68% at 80.

## Exhibit 4 — Wet-lab design campaigns

Per-target design budgets in this corpus range from 5 to 9,000, and the
criterion for calling a design a binder differs between papers. The campaigns
are grouped below by the kind of evidence reported, and ordered within each
group by designs tested. The groups describe what was measured, not how well.

### Binding reproduced in a second assay format

| System      | Modality, targets             |                                Tested | Outcome                                                                               | Best affinity                                     |
| ----------- | ----------------------------- | ------------------------------------: | ------------------------------------------------------------------------------------- | ------------------------------------------------- |
| BoltzProt-1 | VHH, 10 low-homology targets  |                       15/target (150) | 12 confirmed binders, 8.0%; BoltzGen on the same candidate pools and budget, 5 = 3.3% | not reported                                      |
| Germinal    | scFv tested as Fab, 2 targets |                             48/target | 3/48 PDL1 and 1/48 IL-3 confirmed on both SPR and BLI                                 | 360 nM SPR / 650 nM BLI                           |
| Latent-X1   | Mini-binders, 5 targets       | 100/target HT-BLI, 88/target mDisplay | 10–64% per target; platforms correlate at Pearson r = 0.68–0.79                       | < 0.01 nM (IL-7Rα, SC2RBD)                        |
| Germinal    | VHH, 4 targets                |            101 / 46 / 43 / 52 ordered | 7 / 2 / 4 / 5 confirmed by BLI after a split-luciferase screen                        | 170 nM (PDL1); 42 nM after Legobody rescaffolding |

BoltzProt-1 confirms by re-running in a flipped assay orientation plus
independent vendor re-testing. Germinal's quoted fractions use the BLI
sub-denominator (25 / 11 / 11 / 20); the ordered counts are 101 / 46 / 43 / 52.
Latent-X1 reports its mammalian-display readout having robust dynamic range on
three of its five targets.

### Single assay format

| System            | Modality, targets                     |                        Tested | Hit rate                                               | Best affinity                                          |
| ----------------- | ------------------------------------- | ----------------------------: | ------------------------------------------------------ | ------------------------------------------------------ |
| Latent-X2         | Macrocycles, 2 targets                |                     10/target | 9/10 (PHD2), 8/10 (K-Ras G12D)                         | 1.54 nM (PHD2)                                         |
| RFpeptides        | Macrocycles, 4 targets                | 6–14 tested of 11–27 selected | 2–4 hits per target                                    | 6 nM (GABARAP)                                         |
| BoltzGen          | VHH and proteins, 9 novel targets     |                     15/target | binders on 6/9 targets, both modalities                | 6.1 nM VHH (PMVK); 9.8 nM protein (MZB1)               |
| PXDesign          | Mini-binders, 6 targets               |                   9–17/target | 20–73% on five targets; 0/16 on TNFα                   | "multiple nanomolar", no value in text                 |
| Latent-X1         | Macrocycles, 3 targets                |                  11–17/target | 91 / 100 / 94%                                         | 5.35 µM (MDM2)                                         |
| Chai-2            | scFv + VHH, 52 targets                |             ≤20/target/format | 13.7% scFv (68/496), 20.0% VHH (41/205); 26/52 targets | < 1 nM (EFNA5 scFv, flagged as an avidity measurement) |
| BoltzGen          | VHH and proteins, 5 benchmark targets |                  15–20/target | binders on 4/5 targets                                 | 0.81 nM (PDGFR)                                        |
| Latent-X2         | VHH and scFv, 18 targets              |            4–24/target/format | binders on 9/18 targets; up to 25% of designs          | 26.2 pM (HDAC8 scFv)                                   |
| Chai-2            | Mini-binders, 5 targets               |                  20–25/target | 68% (75/111), binders on 5/5 targets                   | 18.3 pM (IL-7Rα)                                       |
| Protenix-v2       | VHH-Fc and mAb, 4 GPCRs               |                  16–30/target | VHH-Fc 16 / 62 / 40 / 88%; mAb 0 / 17 / 50 / 44%       | 112 pM (GPRC5D, avidity)                               |
| Protenix-v2       | VHH-Fc, soluble targets               |                   figure only | 2–48% per target; binders on all targets               | figure only                                            |
| BindCraft         | Mini-binders, 12 targets              |                   6–53/target | 10–100%, mean 46.3%                                    | < 1 nM (PD-1, bivalent Fc); 5 nM (CbAgo)               |
| ESMFold2 campaign | Mini-binders, 5 targets               |                     84/cohort | 36–88%, mean 70.0% at higher compute                   | 68 pM (target not stated in text)                      |
| ESMFold2 campaign | scFv, 5 targets                       |                     84/cohort | 15–29%, mean 21.0% at higher compute                   | —                                                      |
| RFdiffusion       | Mini-binders, 5 targets               |                     95/target | 19% pooled over 475                                    | 28 nM (influenza HA)                                   |
| AlphaProteo       | Mini-binders, 8 targets               |                 54–172/target | 9% (TrkA) to 88% (BHRF1); 0/54 on TNFα                 | 82 pM (IL-7Rα)                                         |

Three of these rows state no numeric threshold: BindCraft and RFpeptides count a
design a binder when SPR shows a binding signal, and Latent-X1's macrocycle rate
stands on a measurable SPR signal described as such. They belong in this group
because their figures are per-design rates from a single assay format, like the
rows above them; Exhibit 5 records their criteria as each paper states them.

Three conditions apply across this group and are needed to read the columns:

**Avidity.** Protenix-v2's 112 pM is measured under avidity, and its VHHs are
bivalent VHH-Fc fusions except for VEGF-A. Chai-2 marks four of its ten quoted
miniprotein affinities as avidity-affected, and its Table S3 flags the
sub-nanomolar EFNA5 scFv value as an avidity measurement as well. BindCraft's
PD-1 value is a bivalent Fc construct whose exact K<sub>D</sub> could not be
determined.

**Attrition between designed and tested.** RFpeptides selected 27 macrocycles
for MCL1 and tested 14; selected 26 for RbtA and tested 11. Latent-X1's
macrocycle rates are over the 11–17 peptides that survived synthesis, from 30
submitted and 700 generated. PXDesign reports both denominators: for PD-L1,
72.7% over designs tested and 47.1% over designs sent for expression.

**Target-level and per-design rates.** BoltzGen, Protenix-v2 and Latent-X2
report the fraction of targets for which at least one binder was found; Chai-2,
PXDesign and others report the fraction of designs that bound. Both appear above
and they are different quantities.

### Display or enrichment signal, no affinity measured

| System     | Modality, targets               |                      Tested | Outcome                                                                                                                                       |
| ---------- | ------------------------------- | --------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------- |
| BoltzGen   | VHH, 2 targets                  |     7/target, yeast display | 1/7 and 7/7 showing signal; binding "at best 2 µM", no EC<sub>50</sub> computable                                                             |
| RFantibody | VHH, 3 targets                  |              95/target, SPR | same 0–2% range                                                                                                                               |
| RFantibody | VHH, 4 targets                  | 9,000/target, yeast display | 0–2% per target                                                                                                                               |
| mBER       | VHH, 145 of 436 targets assayed |   1,153,241 designs, pooled | 45% of targets with statistically elevated on-design rate; per-design rate 0.02–8%, median ≈0.4%; 38% (8/21) in one ipTM-filtered epitope bin |

mBER states that phage display does not permit precise quantification of binding
affinities. RFantibody pairs design with yeast-display screening and states the
screen is currently necessary given the design success rate.

### Functional readout, no binding assay

| System   | Modality, target             | Tested | Outcome                                                                                                                            |
| -------- | ---------------------------- | -----: | ---------------------------------------------------------------------------------------------------------------------------------- |
| BoltzGen | Peptides, NPM1               |      5 | 1/5 showed nucleolar co-localization in live cells                                                                                 |
| BoltzGen | Antimicrobial peptides, GyrA |  1,808 | 352 (19.5%) inhibited *E. coli* growth ≥4-fold; 54 lost activity when the three closest interface residues were mutated to alanine |

BoltzGen notes of the NPM1 result that the experiment does not confirm binding
at the disordered region specifically.

### No wet-lab validation

BoltzDesign1 and RFOptimization report in-silico success rates only.
RFOptimization improves AF3-refolded success from 6.73% to 22.31% on
protein–protein interfaces, 1.25% to 12.57% on cyclic peptides, and 5.62% to
24.91% on small-molecule binders, with AF3 held out of its optimization loop.
Its success criterion — that AF3 re-fold a design with interface PAE < 2.5 and
interface pTM > 0.8 — is stated; its designs-tested denominators are not.

## Exhibit 5 — Binding criteria, as each paper states them

Exhibit 4 grouped the campaigns rather than sorting them because the hit
definitions are not one definition; they are listed here as each paper states
them.

| Paper                 | A design counts as a binder when                                                                                                                                                                                                                                |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BoltzProt-1           | a clean sensorgram, or similarly conclusive data, confirms binding, and an affinity is reported only when the kinetic data can support one                                                                                                                      |
| Latent-X2             | reference-subtracted single-point BLI > 0.1 nm advances a design to kinetic characterization; multi-point BLI kinetic data are reported only for global fits with R² > 0.95 (R² > 0.90 with visual review for one target, AHSP, where no fit met the criterion) |
| ESMFold2 campaign     | two definitions: stringent, target-specific cutoffs of 0.25–0.4 nm with borderline cases manually inspected, and inclusive, a universal > 0.1 nm; both require a probe-loading signal > 0.5 nm and a positive exponential association line shape                |
| Chai-2                | a binding-positive curve signature, with signal > 0.1 nm above background and > 300% of background                                                                                                                                                              |
| PXDesign              | BLI response > 0.06 nm at 1 µM, then measured K<sub>D</sub> < 1000 nM                                                                                                                                                                                           |
| Protenix-v2           | BLI response > background + 0.05 nm; most such hits went on to show K<sub>D</sub> < 1000 nM                                                                                                                                                                     |
| AlphaProteo           | yeast-display flow-cytometry binding signal > 0.2, raised to 1.3 for IL-17A for background                                                                                                                                                                      |
| BoltzGen              | a quantifiable sensorgram, or association signal ≥ 300% of negative control where kinetic fitting failed                                                                                                                                                        |
| RFdiffusion           | single-point BLI at 10 µM ≥ 50% of the positive control response                                                                                                                                                                                                |
| Germinal              | expression luminescence > 150,000 RLU and a rising binding ratio between two timepoints, then detectable BLI binding                                                                                                                                            |
| mBER                  | per-sequence order statistic across replicate wells above threshold, parameters set so expected false positives per target < 1                                                                                                                                  |
| BindCraft             | binding observed on SPR; no numeric threshold stated                                                                                                                                                                                                            |
| RFpeptides            | a binding signal at 100 µM by SPR single-cycle kinetics; no numeric threshold stated                                                                                                                                                                            |
| Latent-X1 macrocycles | measurable binding signal by SPR; no numeric threshold stated                                                                                                                                                                                                   |

BoltzProt-1 is the one paper here that defines screening hits and confirmed
binders apart. A screening hit's sensorgrams indicate an interaction, including
ambiguous signal, and are reported as hits from an initial screen; a confirmed
binder requires a clean sensorgram or similarly conclusive data, with ambiguous
cases resolved by varying the capture level of the binder on the plate,
adjusting the target's concentration range, or inverting the assay orientation.

## Scope of these numbers

**Comparability across papers.** No two design campaigns above were evaluated
against a benchmark that another used; each paper chose its own targets,
epitopes, assay and threshold. Targets do recur — PD-L1, IL-7Rα, InsulinR, TrkA,
TNFα and SC2RBD appear across several papers — and the hotspot definitions are
sometimes carried over as well, but the measurements are separate. Three papers
re-measured a competitor's molecules under their own conditions: AlphaProteo
resynthesized RFdiffusion's published designs and ran them by yeast display,
recovering 16% against a published 33% on IL-7Rα and 0% against 6% on TrkA,
which it attributes to assay environment and a 10–20× lower target
concentration; Latent-X1 resynthesized RFpeptides' two best macrocycles,
measuring them 4.4× and 5× weaker than published, with its own best beating the
replicated figure on MDM2 (5.35 vs 8.38 µM) and the replicated figure beating
its own on MCL-1 (10.0 vs 18.4 µM); Latent-X2 resynthesized two RaPID
mRNA-display macrocycles, under a different cyclization chemistry from its own
designs.

**Figures not recoverable from the parsed corpus.** AlphaFold3's per-class
results are in Extended Data Table 1 and Fig. 1c, neither of which parsed; every
AF3 figure above is therefore a third-party measurement under that paper's
settings. Boltz-1, Boltz-2 and RoseTTAFold2's headline results are figure-only
for the same reason. Protenix-v2's prose carries the pooled soluble-target rate
range (2–48%), the two AMBP epitope rates (4% and 48%) and the per-format GPCR
rates quoted above, but the soluble panel's per-target rates, designs-tested
denominators and affinities are in Fig. 4A, whose picture text is nearly empty,
and the soluble panel's targets are not enumerated anywhere. The three
per-epitope ratios circulating in the corpus (2/50 and 13/27 on two AMBP
epitopes, 12/50 on IDI2) come from BoltzProt-1's transcription of that figure.
The ESMFold2 campaign's quoted rates come from its Figure 3, and the parse
cannot tell which of its two hit definitions — the stringent target-specific
cutoffs or the inclusive universal 0.1 nm — the figure's shading distinguishes
at each point. Every wet-lab campaign in Exhibit 4 states a designs-tested
denominator except Protenix-v2's soluble panel and mBER, whose designs are
pooled across the cohort.

**One figure conflicts with itself.** BoltzProt-1's Table 1 gives BoltzGen 7
revised screening hits (4.7%) and BoltzProt-1 14 (9.3%); its prose gives
BoltzGen 14 (9.3%) and BoltzProt-1 24 (16.0%). The confirmed-binder figures, 5
(3.3%) and 12 (8.0%), agree in both places, and only those are quoted above.

**OpenFold3 has no publication.** Its figures come from a repository and a
technical report covering superseded weights. Protenix-v2's run of
OpenFold3-preview2 reports a DockQ success rate of 69.29% on 267 FoldBench
protein–protein interfaces against 70.79% in the public FoldBench results, and
notes its MSA pipeline differs from the official one. No exhibit measures
anything a successful design was used for, and that distance is where the review
ends.
