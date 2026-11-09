# The numbers

_Draft of the review's closing quantitative section (map unit: "Tables A and
B"). Every figure here is quoted from a parsed paper in `literature/corpus/`;
provenance is stated per exhibit. Where a paper's own headline number exists
only inside a figure the parser could not read, this draft says so rather than
approximating it._

The preceding sections quoted accuracy figures one lineage at a time. Gathering
them in one place is useful, and it is also the most dangerous thing this review
does: five tidy columns read as a leaderboard, and a leaderboard is precisely
the claim the evidence does not support.

So this section is built the other way round. Each exhibit below answers one
question, and two of the five exist only to show how much a number moves when
the bookkeeping behind it changes. A reader who takes nothing else from this
section should take this: **in this field a reported score is a property of a
model, a benchmark, a target subset, a selection rule and an averaging unit, and
changing any one of the last four moves the score by more than the differences
between models.**

______________________________________________________________________

## Exhibit 1 — How accurate is prediction, measured on one common set

Most co-folding papers report accuracy on targets that only their own model
completed. Models fail on different inputs — out-of-memory on large assemblies,
unsupported glycans, token limits — so each row of a typical comparison is
scored on a different subset, and the aggregate difference between two models
partly reflects which targets each one dropped.

Protenix-v1 is the one paper in the corpus that enforces a **common
intersection**: every cell below is computed only on targets that all compared
models predicted and scored successfully.

**FoldBench, common intersection of all models.** Monomer and nucleic-acid
monomer columns are mean lDDT; protein–protein, antibody–antigen, protein–RNA
and protein–DNA are DockQ success rate (DockQ > 0.23) in percent; protein–ligand
is the joint RMSD < 2 Å and lDDT-PLI > 0.8 success rate in percent.

| Model           | Monomer | Prot–Prot | **Ab–Ag** | Prot–Lig | Prot–RNA | Prot–DNA |    DNA |    RNA |
| --------------- | ------: | --------: | --------: | -------: | -------: | -------: | -----: | -----: |
| AlphaFold3      |  0.8803 |     71.73 | **48.75** |    62.59 |    65.22 |    75.91 | 0.5278 | 0.6140 |
| Boltz-1         |  0.8664 |     68.35 | **34.38** |    54.65 |    65.22 |    67.15 | 0.3388 | 0.4416 |
| Chai-1          |  0.8639 |     67.51 | **23.12** |    50.79 |    50.00 |    66.06 | 0.4574 | 0.4852 |
| HelixFold3      |  0.8547 |     65.40 | **28.75** |    52.38 |    52.17 |    49.27 | 0.2909 | 0.5487 |
| Protenix-v0.2.0 |  0.8622 |     66.24 | **35.62** |    51.02 |    56.52 |    64.60 | 0.4384 | 0.5903 |
| Protenix-v0.5.0 |  0.8717 |     68.06 | **43.94** |    58.49 |    59.37 |    68.02 | 0.4960 | 0.6046 |
| Protenix-v1     |  0.8857 |     72.70 | **52.31** |    62.54 |    68.46 |    69.13 | 0.5693 | 0.6547 |

_n per column: 287 monomers, 237 protein–protein, 160 antibody–antigen, 441
protein–ligand, 46 protein–RNA, 274 protein–DNA, 14 DNA, 15 RNA. Benchmark
window: PDB entries released 2023-01-13 to 2024-11-01, homology-reduced against
a reproduction of AlphaFold3's 2021-09-30 training set. Sampling: 5 seeds × 5
diffusion samples, 10 recycles, top-ranked structure._

**Provenance, and it matters.** The AlphaFold3, Boltz-1, Chai-1, HelixFold3 and
Protenix-v0.2.0 rows were **not re-run** by Protenix-v1 — they were recomputed
from the per-instance prediction logs those models' authors published, with the
intersection filter applied. The Protenix-v0.5.0 and Protenix-v1 rows are the
authors' own runs. This is a table built by the maker of its best-performing
model, and it should be read with that in mind; what makes it usable anyway is
that the correction it applies works *against* convenience, and that it
publishes the uncorrected numbers alongside.

**What the table says.** Monomer prediction is saturated — every model between
0.85 and 0.89 lDDT, differences that no one should care about. Protein–protein
sits in a 7-point band. The spread that matters is **antibody–antigen, where the
same models range from 23 to 52 percent** — a factor of two, on the one target
class that §3–§7's design systems actually need their critics to get right. A
model leading on monomers and trailing on antibody–antigen is a weak critic for
this review's purposes, and only a split table reveals it.

**Every instrument here has a documented defect.** FoldBench's own aggregates do
not enforce the intersection this table imposes. PoseBusters' validity criterion
passes structures with distorted geometry, which is why Protenix-v2 extended it
with planarity checks. Boltz-2 is absent from this table because its 2023-06-01
training cutoff overlaps the benchmark window — a leakage flag raised
independently by Protenix-v1, Protenix-v2 and the ESMFold2 authors. Not one
benchmark in this field is uncontested.

______________________________________________________________________

## Exhibit 2 — The same model, the same task, three different numbers

Exhibit 1 is readable only alongside this one.

**AlphaFold3 on FoldBench antibody–antigen**, as reported in three papers:

| Reported as | By                                    | Why it differs                            |
| ----------: | ------------------------------------- | ----------------------------------------- |
|       47.90 | FoldBench's own leaderboard (n = 167) | no common-intersection filter             |
|       48.75 | Protenix-v1 (n = 160)                 | intersection of all compared models       |
|       0.488 | OpenDDE                               | its own re-run on the FoldBench-AB subset |

Three numbers, one model, one benchmark, one task. The spread is small here —
but it is the floor, not the ceiling, of how far this kind of disagreement goes.

**Chai-1 on antibody interfaces**, as reported in two papers:

| Reported as | By                 | Averaging unit                     |
| ----------: | ------------------ | ---------------------------------- |
|       0.529 | Chai-1's own paper | per 40%-identity interface cluster |
|       25.2% | FoldBench          | per interface                      |

**The same model on the same task, differing by roughly a factor of two,
entirely because of what gets averaged over.** Neither number is wrong.
Clustering at 40% identity prevents a heavily-represented antigen family from
dominating the mean; averaging per interface treats every measured interface as
one observation. They answer different questions and the papers report both as
"DockQ success rate."

A third averaging unit exists: Boltz-1 averages per interface *within* a complex
and then across complexes. Three papers, three statistics, one name.

**And the correction can reverse a published ranking.** Protenix-v1's worked
example on the FoldBench protein–protein subset: as reported, Boltz-1 scores
172/252 = 0.683 and Chai-1 scores 172/251 = 0.685, so Chai-1 leads. Restricted
to the 237 interfaces both models actually completed, Boltz-1 scores 162/237 =
0.684 and Chai-1 160/237 = 0.675 — and the order flips. The gap in both
directions is smaller than the noise, which is the real lesson: these two models
are indistinguishable on this task, and either published ordering is an
artifact.

______________________________________________________________________

## Exhibit 3 — How much of a reported score is the ranking, not the structure

Every model here generates several candidate structures and then picks one using
its own confidence head. A reported accuracy is therefore two things at once:
how good the best candidate was, and whether the model recognized it.

AtlasFold separates them, reporting every model under confidence-based selection
("rank", what you get in practice) and under best-of-25 selection against the
ground truth ("oracle", unavailable at inference time).

**FoldBench antibody–antigen, 172 targets, DockQ > 0.23 success rate (%):**

| Model               |   Rank | Oracle | Headroom lost to ranking |
| ------------------- | -----: | -----: | -----------------------: |
| AlphaFold3          | 49.285 | 66.168 |                     16.9 |
| Protenix-v1         | 44.945 | 65.818 |                 **20.9** |
| ESMFold2 (MSA)      | 52.270 | 63.427 |                     11.2 |
| ESMFold2 (seq only) | 48.602 | 61.489 |                     12.9 |
| AtlasFold-M         | 46.955 | 64.733 |                     17.8 |
| AF-Multimer v2.3    | 40.924 | 52.921 |                     12.0 |
| Boltz-1             | 34.967 | 39.505 |                      4.5 |

**FoldBench protein–protein, 278 targets, same metric:**

| Model               |   Rank | Oracle | Headroom lost to ranking |
| ------------------- | -----: | -----: | -----------------------: |
| AlphaFold3          | 73.006 | 78.028 |                      5.0 |
| Protenix-v1         | 74.445 | 81.572 |                      7.1 |
| ESMFold2 (MSA)      | 73.230 | 77.237 |                      4.0 |
| ESMFold2 (seq only) | 69.216 | 74.071 |                      4.9 |
| AtlasFold-M         | 63.358 | 71.560 |                      8.2 |
| AF-Multimer v2.3    | 65.206 | 68.615 |                      3.4 |
| Boltz-1             | 71.120 | 76.632 |                      5.5 |

_Mean across 252 five-seed subsets drawn from 10 seeds; error bars in the source
are one standard deviation of the acceptable-or-better rate across those
subsets._

**On antibody–antigen, every model is leaving 11 to 21 points on the table
because it cannot tell which of its own samples is right.** On protein–protein
the same gap is 3 to 8 points. The structure modules are markedly better at
antibodies than their confidence heads can exploit — FoldBench states the
mechanism directly: a near-native CDR-H3 is necessary but not sufficient, and
"per-sample confidence scores do not reliably identify near-native
conformations."

This is the quantitative case for §3's trained critic. Replacing a confidence
head with a model trained to answer "will this bind" is not a refinement; it
addresses the largest single source of lost performance in the table above. It
is also why inference-time scaling works at all: AlphaFold3's antibody figures
were ranked across 1,000 seeds rather than the 5 used elsewhere in its own
paper, and OpenDDE's oracle success on FoldBench-AB rises from about 66% at one
seed to above 90% at hundreds.

______________________________________________________________________

## Exhibit 4 — Design campaigns, grouped by what was actually measured

The design half cannot be tabulated the way Exhibit 1 tabulates prediction, and
the reason is the finding. Per-target design budgets in this corpus run from **5
designs to 9,000**. Hit definitions range from a statistical enrichment in a
phage pool to a binding curve reproduced in a second assay format. Some papers
headline a target-level success rate, others a per-design rate, and the two
differ by two orders of magnitude within a single paper.

Sorting such rows by hit rate would be the leaderboard error in its purest form.
They are grouped here by **evidence tier** — what the paper required before
calling something a binder — and only within a tier by designs tested. A number
in a lower band is not worse science; it is a different measurement, and often
of a different thing.

### Band A — binding reproduced in a second assay format

| System          | Modality, targets               |                                Tested | Outcome                                                                                   | Best affinity                                       |
| --------------- | ------------------------------- | ------------------------------------: | ----------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **BoltzProt-1** | VHH, 10 low-homology targets    |                       15/target (150) | **12 confirmed binders, 8.0%**; BoltzGen on the same candidate pools and budget, 5 = 3.3% | not reported anywhere in the paper                  |
| **Germinal**    | VHH, 4 targets                  |            101 / 46 / 43 / 52 ordered | 7 / 2 / 4 / 5 confirmed by BLI after a split-luciferase screen                            | 170 nM (PDL1); 42 nM after Legobody rescaffolding   |
| **Germinal**    | scFv (tested as Fab), 2 targets |                             48/target | 3/48 PDL1 and 1/48 IL-3 confirmed on **both** SPR and BLI                                 | 360 nM SPR / 650 nM BLI (PDL1 H5)                   |
| **Latent-X1**   | Mini-binders, 5 targets         | 100/target HT-BLI, 88/target mDisplay | 10–64% per target, cross-validated on two platforms (Pearson r = 0.68–0.79)               | < 0.01 nM (below quantitation) on IL-7Rα and SC2RBD |

BoltzProt-1's confirmed tier is the strictest in the corpus: a clean sensorgram,
a flipped-orientation re-assay, and independent re-testing by the vendor. It is
the only paper that formally separates **screening hits** from **confirmed
binders**, and it says why — "much of the literature reports such cases as
binders."

Two cautions on this band. Germinal quotes its fractions against the BLI
sub-denominator (25/11/11/20), not against the 101/46/43/52 designs it actually
ordered; both denominators are above, and the second is the honest one. And
Latent-X1's orthogonal platform failed to discriminate on two of its five
targets, which the paper states.

### Band B — single assay format, with a stated numeric threshold

| System                | Modality, targets                     |                                          Tested | Hit rate (wet-lab)                                     | Best affinity                                       |
| --------------------- | ------------------------------------- | ----------------------------------------------: | ------------------------------------------------------ | --------------------------------------------------- |
| **AlphaProteo**       | Mini-binders, 8 targets               |                                   54–172/target | 9% (TrkA) to 88% (BHRF1); **0/54 on TNFα**             | **82 pM** (IL-7Rα)                                  |
| **Chai-2**            | Mini-binders, 5 targets               |                                    20–25/target | **68% (75/111)**, 5/5 targets                          | 18.3 pM (IL-7Rα, not avidity-flagged)               |
| **Chai-2**            | scFv + VHH, 52 targets                |                               ≤20/target/format | 13.7% scFv (68/496), 20.0% VHH (41/205); 26/52 targets | < 1 nM (EFNA5 scFv)                                 |
| **ESMFold2 campaign** | Mini-binders, 5 targets               |                                       84/cohort | 36–88%, mean 70.0% at high compute                     | 68 pM (target not stated in text)                   |
| **ESMFold2 campaign** | scFv, 5 targets                       |                                       84/cohort | 15–29%, mean 21.0% at high compute                     | —                                                   |
| **PXDesign**          | Mini-binders, 6 targets               |                                     9–17/target | 20–73% on five targets; **0/16 on TNFα**               | "multiple nanomolar" — no value in text             |
| **Protenix-v2**       | VHH-Fc, 14 soluble targets            |                                     figure only | 2–48% per target; 100% target-level                    | figure only                                         |
| **Protenix-v2**       | VHH-Fc and mAb, 4 GPCRs               |                                    16–30/target | VHH-Fc 16/62/40/88%; mAb 0/17/50/44%                   | 112 pM (GPRC5D, avidity)                            |
| **BindCraft**         | Mini-binders, 12 targets              |                                     6–53/target | 10–100%, mean 46.3%                                    | < 1 nM (PD-1, bivalent Fc); 5 nM monovalent (CbAgo) |
| **BoltzGen**          | VHH and mini-binders, 9 novel targets |                                       15/target | 6/9 targets both modalities                            | 6.1 nM VHH (PMVK); 9.8 nM protein (MZB1)            |
| **BoltzGen**          | VHH and proteins, 5 benchmark targets |                                    15–20/target | 4/5 targets                                            | 0.81 nM (PDGFR)                                     |
| **Latent-X1**         | Macrocycles, 3 targets                |        11–17/target after a 700→30→11–17 funnel | 91 / 100 / 94%                                         | 5.35 µM (MDM2)                                      |
| **Latent-X2**         | VHH and scFv, 18 targets              | 4–24/target/format, **not reported per target** | 9/18 targets; "up to 25% of designs"                   | **26.2 pM** (HDAC8 scFv)                            |
| **Latent-X2**         | Macrocycles, 2 targets                |                                       10/target | 9/10 and 8/10                                          | 1.54 nM (PHD2)                                      |
| **RFdiffusion**       | Mini-binders, 5 targets               |                                       95/target | 19% pooled over 475                                    | 28 nM (influenza HA)                                |
| **RFpeptides**        | Macrocycles, 4 targets                |              6–14 synthesised of 11–27 selected | 2–4 hits per target                                    | 6 nM (GABARAP)                                      |

**Three systematic distortions run through this band.**

_Avidity._ Chai-2 asterisks four of its ten headline affinities; Protenix-v2's
112 pM is explicitly measured under avidity and its VHHs are bivalent Fc fusions
throughout; BindCraft's sub-nanomolar PD-1 figure is a bivalent Fc construct
whose true KD "could not be determined." The cleanest picomolar claims in the
corpus are Chai-2's unasterisked 18.3 pM on IL-7Rα, AlphaProteo's 82 pM by HTRF,
and Latent-X2's 26.2 pM.

_Attrition between "designed" and "tested."_ RFpeptides selected 27 macrocycles
for MCL1 and could test 14; selected 26 for RbtA and could test 11. Latent-X1's
macrocycle hit rates of 91–100% are computed over the 11–17 peptides that
survived synthesis out of 30 submitted out of 700 generated. PXDesign is the
only paper that reports both denominators explicitly — "bind over tested" and
"bind over designed" — and for PD-L1 they are 72.7% and 47.1% respectively, the
gap being six designs that failed to express.

_Target-level versus per-design success._ BoltzGen headlines 6/9 targets,
Protenix-v2 headlines 100% of targets, Latent-X2 headlines 9/18 targets; Chai-2
and PXDesign headline per-design rates. These are not the same claim, and a
reader comparing "100%" to "15.5%" is comparing nothing.

### Band C — display or enrichment signal only, no affinity measured

| System         | Modality, targets               |                            Tested | Outcome                                                                                                                             |
| -------------- | ------------------------------- | --------------------------------: | ----------------------------------------------------------------------------------------------------------------------------------- |
| **mBER**       | VHH, 145 of 436 targets assayed |         1,153,241 designs, pooled | 45% of targets statistically elevated; **per-design rate 0.02–8%, median ≈0.4%**; up to 38% (8/21) in one ipTM-filtered epitope bin |
| **RFantibody** | VHH, 4 targets                  | **9,000/target** by yeast display | 0–2% per target, at least one target at 0%                                                                                          |
| **RFantibody** | VHH, 3 targets                  |                  95/target by SPR | same 0–2% envelope                                                                                                                  |
| **BoltzGen**   | VHH, 2 targets                  |                          7/target | 1/7 and 7/7 showing signal; "at best 2 µM", no EC50 computable                                                                      |

mBER measures no affinities at all and says so: phage display "does not permit
precise quantification of binding affinities." Its headline 45% is a
target-level figure; the per-design rate on the same campaign is around 0.4%.
RFantibody is the honest baseline the review's collapsing-budget argument is
measured against — it pairs design with 9,000-design yeast-display screening per
target and states that the screen "is currently necessary due to the quite low
design success rate."

### Band D — functional readout only, no binding assay

| System       | Modality, target             |    Tested | Outcome                                                                                                        |
| ------------ | ---------------------------- | --------: | -------------------------------------------------------------------------------------------------------------- |
| **BoltzGen** | Antimicrobial peptides, GyrA | **1,808** | 352 (19.5%) inhibited growth ≥4-fold; 54 lost activity on alanine substitution of the three interface residues |
| **BoltzGen** | Peptides, NPM1               |         5 | 1/5 showed nucleolar co-localization in live cells                                                             |

Growth inhibition is not binding. The paper's own alanine-substitution control
recovers only 54 of 352 as plausibly interface-dependent, and it says of the
NPM1 result that the experiment "does not definitely confirm that the binding
occurs specifically at the disordered region."

### Band E — no wet-lab validation

**BoltzDesign1** and **RFOptimization** report in-silico success rates only.
RFOptimization improves AF3-refolded success from 6.73% to 22.31% on
protein–protein interfaces and from 1.25% to 12.57% on cyclic peptides, with AF3
held out of its optimization loop as an independent check — a careful design,
and still a claim about refolding statistics rather than about binders. It
cannot be a row in any band above because it has no designs-tested denominator
and no hit definition.

______________________________________________________________________

## Exhibit 5 — What each paper means by "hit"

Quoted criteria, which is the reason Exhibit 4 is banded rather than sorted.

| Paper                                                    | A design counts as a binder when                                                                                                                                   |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **BoltzProt-1**                                          | a clean sensorgram confirms binding, ambiguous cases resolved by a flipped-orientation assay and independent vendor re-testing; screening hits reported separately |
| **Latent-X2**                                            | reference-subtracted single-point BLI > 0.1 nm, **and** binding reproduces on 5-point BLI or SPR with R² > 0.95                                                    |
| **ESMFold2 campaign**                                    | target-specific stringent cutoffs of 0.25–0.4 nm, borderline cases manually inspected; an inclusive >0.1 nm figure reported alongside                              |
| **Chai-2**                                               | BLI signal > 0.1 nm above background **and** > 300% of background                                                                                                  |
| **PXDesign**                                             | BLI response > 0.06 nm at 1 µM, then measured K<sub>D</sub> < 1000 nM                                                                                              |
| **Protenix-v2**                                          | BLI response > background + 0.05 nm; "most" such hits went on to show K<sub>D</sub> < 1000 nM                                                                      |
| **AlphaProteo**                                          | yeast-display flow-cytometry signal > 0.2, raised to 1.3 for IL-17A to account for background                                                                      |
| **BoltzGen**                                             | a quantifiable sensorgram, or association signal ≥ 300% of negative control where fitting failed                                                                   |
| **RFdiffusion**                                          | single-point BLI at 10 µM ≥ 50% of the positive control's response                                                                                                 |
| **Germinal**                                             | expression luminescence > 150,000 RLU **and** a rising binding ratio between two timepoints, then detectable BLI binding                                           |
| **mBER**                                                 | per-sequence order statistic across replicate wells exceeding threshold, tuned so expected false positives per target < 1                                          |
| **BindCraft**, **RFpeptides**, **Latent-X1 macrocycles** | **no numeric threshold stated** — "binding observed on SPR", "a binding signal at 100 µM", "measurable binding signal"                                             |

Three of these papers report a hit rate without publishing the threshold that
produced it.

______________________________________________________________________

## What the two halves say together

Exhibits 1 and 4 are built the way they are because the evidence underneath them
differs in kind, and that difference is this section's finding.

**The prediction half is measured in common.** FoldBench, PoseBusters, PXMeter
and Runs N' Poses are instruments that several groups actually ran against, the
disagreements are about aggregation and leakage rather than about what was
measured, and the corpus contains genuine third-party re-measurement:
Protenix-v2 ran OpenFold3 itself, OpenDDE built a benchmark postdating every
baseline and ran all of them, AtlasFold re-ran seven models including a
competitor whose published margin it reverses, and Protenix-v1 recomputed five
models' published outputs under one intersection rule. Papers in this half
contest each other's numbers in public, by name.

**The design half is not measured in common at all.** Not one campaign in
Exhibit 4 was evaluated against any benchmark another campaign in it used. Each
chose its own targets, its own epitopes, its own assay, its own threshold, and
its own denominator. No paper used a blinded or third-party-held target set; the
strongest constraints anyone applied were self-administered novelty filters,
further narrowed by which proteins were in a vendor's catalogue.

Designing against another paper's published targets is nevertheless routine —
PD-L1, IL-7Rα, InsulinR, TrkA, TNFα and SC2RBD recur across RFdiffusion,
AlphaProteo, Chai-2, PXDesign, BoltzGen and Latent-X — but reusing a target is
not reproducing a measurement. Only three papers re-measured a competitor's
actual molecules:

- **AlphaProteo** downloaded RFdiffusion's published designs, resynthesized
  them, and ran them through its own yeast-display assay. It recovered 16% where
  RFdiffusion published 33% on IL-7Rα, and 0% where RFdiffusion published 6% on
  TrkA — and attributed the gap to assay environment and a 10–20× lower target
  concentration. This is the only re-run in the corpus that includes a
  competitor's **non-binders**, and therefore the only one that independently
  produces a competitor's hit rate.
- **Latent-X1** resynthesized RFpeptides' two best published macrocycles and
  measured them beside its own. They came out 4.4× and 5× weaker than published.
  On MDM2 Latent-X's best (5.35 µM) beat RFpeptides' replicated 8.38 µM; **on
  MCL-1 RFpeptides' replicated 10.0 µM beat Latent-X's own best of 18.4 µM.**
  The paper's abstract nonetheless describes the comparison as "definitive
  evidence of Latent-X's leading performance," and its hit-rate contrast —
  91–100% against RFpeptides' 21–38% — is its own assay against RFpeptides'
  published figures, not a matched comparison.
- **Latent-X2** resynthesized two RaPID mRNA-display macrocycles, under a
  different cyclization chemistry than its own designs.

In all three cases only the best *binders* were re-measured. **No design
method's hit rate has been independently reproduced by anyone.**

That asymmetry — a prediction literature that argues about its instruments in
public, and a design literature where every number is its author's own — is the
strongest empirical support the review's disclosure argument has, and two
adjacent exhibits demonstrate it in a way no paragraph can.

______________________________________________________________________

## Gaps in this section, stated

- **AlphaFold3's own per-class figures are not in this draft.** They exist only
  in Extended Data Table 1 and Fig. 1c of its paper, which the PDF parser did
  not capture as text. Every AF3 number above is a third-party measurement,
  under settings that differ from AF3's own. Boltz-1, Boltz-2 and RoseTTAFold2's
  headline figures are figure-only for the same reason.
- **Protenix-v2's headline antibody result is figure-only**, as are its
  soluble-panel denominators and affinities. The three per-epitope ratios quoted
  anywhere in this corpus (2/50 and 13/27 on two AMBP epitopes, 12/50 on IDI2)
  come from BoltzProt-1's reading of that figure, not from Protenix-v2's prose.
- **BoltzProt-1's screening-hit rate is internally contradictory.** Its Table 1
  assigns 7 revised hits (4.7%) to BoltzGen and 14 (9.3%) to BoltzProt-1; its
  prose assigns 14 (9.3%) to BoltzGen and 24 (16.0%) to BoltzProt-1. The
  confirmed-binder figures — 5 (3.3%) and 12 (8.0%), a 2.4× improvement — agree
  in both places, so only the confirmed tier is quoted above.
- **OpenFold3 has no publication.** Its figures come from a repository and a
  technical report covering superseded weights; Protenix-v2's run of
  OpenFold3-preview2 is the only version anyone outside the project has checked,
  and Protenix-v2 reports its own MSA pipeline differs from the official one by
  about 1.5 points on protein–protein.
- Per-target denominators remain unrecoverable without the source PDFs for:
  RFdiffusion's per-target rates, RFantibody's per-target success table,
  BoltzProt-1's per-target ratios, Protenix-v2's Figures 1 and 4A, and the
  ESMFold2 campaign's per-target breakdown.
