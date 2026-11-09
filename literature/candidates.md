# Candidates and exclusions — the decision log

Everything the review considered and did not take. `literature/map.md` holds
what is in; this file holds what is out, and why, so no decision is
re-litigated.

**Nothing here is part of the review.** No section of the map is built on any of
it, and nothing here is drafted. Two states:

- **Undecided** — surfaced while reading the corpus, not yet judged. Not in
  `refs.bib` and not in `corpus/`.
- **Excluded** — retrieved, parsed and then judged out. These _stay_ in
  `refs.bib` and `corpus/`: the catalog records what was obtained, the map
  records what is in scope. An excluded work can still be quoted in the review —
  the exclusion is from the argument's structure, not from the bibliography.

Undecided entries are **DOI-verified** — the identifier resolves and its
metadata matches the description — but **the paper has not been read**.
Everything stated in that part is from the citing paper or the abstract, not
from the source itself. Excluded entries have been read.

**To accept an undecided work:** read it, write it into its section in
`literature/map.md`, then run the `map-to-bib` skill. Delete it from this file.
**To reject one:** move it down to _Excluded_ with a stated reason.

______________________________________________________________________

# UNDECIDED

_Nothing undecided._

______________________________________________________________________

# EXCLUDED

Judged out, with the reason stated. Recorded rather than deleted: an exclusion
with a stated reason is part of the review's method, and keeping them prevents
re-litigating the same decision later.

_Scope rule applied:_ in scope = generates a **protein or peptide binder
conditioned on a target**, or predicts the structure such a system designs
against. Out of scope = a different modality (small molecules), or sequence
generation with no target conditioning. A work can also be in scope and still be
out, for carrying no claim the review leans on, or for belonging to no lineage
the review follows.

Every work here that has a publication was retrieved and parsed before being
judged, so it is in `refs.bib` and `literature/corpus/` and may still be quoted
— its bib key stands in front of its DOI. What it may not do is carry a claim
the review leans on; the review is not obliged to re-cite what a work it cites
already cites.

- **ProtDBench** — `protdbench` · `10.48550/arXiv.2605.04118` — _excluded: not a
  third party, and its head-to-head is in-silico only._ ICML 2026 (PMLR 306); a
  standardized, throughput-aware evaluation framework for binder design, with
  fixed targets, hotspots, filters and success criteria. Considered for Table B
  alongside the Overath meta-analysis and fails on both counts the map would
  have needed. _Not a third party:_ every author is ByteDance Seed or ex-Seed,
  corresponding author Wenzhi Xiao, who is also corresponding author on PXMeter,
  Protenix and PXDesign (§6) — and its verifier study concludes that Protenix
  and Protenix-Mini enrich best, then adopts Protenix-Mini as ProtDBench's own
  structural-consistency verifier. _Not a Table B row, and no help to the ones
  there:_ the seven-method comparison (RFdiffusion-3, BoltzGen, Protpardelle-1c,
  ODesign, PXDesign, BindCraft, BoltzDesign1) is scored entirely in silico —
  AF2-IG-Easy filter pass rate, successful backbones per 24 h on one A100,
  Foldseek cluster diversity, Protenix-Mini recapitulation. No assay, no
  designs-tested denominator, no hit definition, which is the same exclusion
  that keeps RFOptimization (§5) out of the table. Re-scoring seven systems'
  computed output does not make their wet-lab campaigns comparable, so Table B's
  claim stands unchanged. Two things in it bear on the map and are cited from
  here rather than given an entry: **(a)** the retrospective on RFdiffusion's
  released wet-lab outcomes (Appendix B.5, Table 10) — six targets, 139
  confirmed binders against 432 non-binders, already AF2-IG-prefiltered, AF2-IG
  precision 0.252 / recall 0.754, Protenix-Mini precision 0.479 / recall 0.420 —
  which is a cross-lab discrimination measurement on someone else's designs; and
  **(b)** the finding that verifiers recover largely distinct subsets of true
  binders under identical filtering, with recall collapsing as more of them are
  required to agree, which is PXDesign's filter-ensembling result (§6) extended
  to seven verifiers and checked against wet-lab labels. _Also worth not
  re-deriving:_ it excludes Latent-X, AlphaProteo, Chai-2 and SeedProteo from
  the head-to-head outright, for shipping no code or weights.

- **Gauss-Seidel projection** — `gauss_seidel_projection` ·
  `10.48550/arXiv.2510.08946` — _excluded: nothing in the review uses it._ ICLR
  2026; a differentiable projection mapping provisional diffusion coordinates
  onto the nearest physically valid configuration, enforcing validity as a
  strict constraint rather than a bias, with a 2-step model reported at the
  accuracy of 200-step baselines. A real and peer-reviewed result, from a group
  with no other presence in the corpus and adopted by no system here. Held a
  **mention** whose only job was to be the fourth option in a physical-validity
  thread that has since been cut as too low-level for a field review.

- **ColabFold** — `colabfold` · `10.1038/s41592-022-01488-1` — _excluded: a
  tool, carrying no claim the review leans on._ MMseqs2 homology search in front
  of unmodified AF2 / AlphaFold-Multimer weights, plus the ColabFoldDB
  environmental database and the Colab notebooks. Held a **meat** entry in the
  instruments unit on two jobs, and neither survived the tier test: the
  off-distribution claim it was credited with naming in 2022 is stated
  independently by AlphaFold2's own paper, BindCraft, mBER and ESMFold2, so
  ColabFold contributes a date; and its provenance fact is a table footnote
  rather than an entry. That footnote is kept under Table A — the AF2 cells and
  Table B's AF2 filters are ColabFold runs.

- **DrugFlow** — `drugflow` · `10.48550/arXiv.2508.17815` · and **FLOWR** —
  `flowr` · `10.1038/s43588-026-00998-8` — _excluded: wrong modality._ Both are
  pocket-conditioned **small-molecule** generators, producing 3D atom types,
  coordinates and bond topology for a ligand. Structure-based drug design rather
  than binder design; the overlap is the flow-matching machinery, not the
  problem.

- **OpenBind, first release** — `openbind` · `10.64898/2026.08.27.747600` —
  _excluded: wrong modality._ An open experimental structure-affinity dataset
  and benchmark: 925 crystallographic binding events from 699 compounds against
  enteroviral 2A protease, affinities for 601, from one antiviral campaign.
  Protein-**ligand** throughout; it generates no binder, and its one model
  result is fine-tuning OpenFold3-p2 on that target's 79 fragment-bound
  structures. Same exclusion as DrugFlow, FLOWR and BoltzMol-1. _Named here
  because the name misleads:_ Anthropic's release presents it among folding
  models, but its kit is `openfold3_ob0` — OpenFold3 0.5.0 on the **OpenBind-0
  checkpoint** — so the model is OpenFold3 and OpenBind is the data initiative
  behind its weights. _Not a Table A row, and the near miss is worth recording:_
  it runs a genuine third-party head-to-head of six co-folders here —
  AlphaFold3, Boltz-1, Boltz-2, OpenFold3-p2, Protenix-v1, RoseTTAFold3 — on one
  shared precomputed MSA with stated cutoffs, which is exactly the provenance
  Table A asks for, and Protenix-v1 leads at both Top-25 and Top-1. It still
  does not earn the row: **one target**, on the target class §3–§7 do not design
  for, and the authors say the ordering may not generalise. A protein-ligand row
  needs a multi-target benchmark.

- **BoltzMol-1** — `boltzmol1` · `10.64898/2026.07.04.736485` — _excluded: wrong
  modality._ Small-molecule hit discovery over an optimized Boltz-2, API-only
  with no weights. It **screens catalogue compounds** rather than generating
  binders, so it fails the scope rule twice over — the same exclusion that keeps
  DrugFlow and FLOWR out. Its one pull toward the map is that it is a second
  closed Boltz model, but §3's open→closed fork is established by BoltzProt-1
  alone.

- **ProtFlow** — `protflow` · `10.64898/2026.02.14.705870` — _excluded: not
  binder design._ Rectified flow matching in sequence space for general protein
  engineering; learns the global semantic distribution of protein space. The
  words "binder" and "binding" do not appear anywhere in the paper, and there is
  no target conditioning.

- **moPPIt** — `moppit` · `10.1101/2024.07.31.606098` — _excluded: no lineage._
  A genetic algorithm iterating a pool from the PepMLM peptide language model,
  scored by BindEvaluator (an ESM-2 binding-site predictor) plus perplexity. No
  diffusion, no flow matching, no structure input at all; AlphaFold2-Multimer
  appears only as retrospective validation. Target-conditioned, so it passes the
  scope rule, but it shares no machinery with anything else here and is cited by
  no other corpus paper. _Recorded error, do not reintroduce:_ an earlier
  version of this map described moPPIt as discrete flow matching. That was
  wrong.

- **SaProt** — `saprot` · `10.1101/2023.10.01.560349` — _excluded: neither half
  of the review._ A structure-aware protein language model (Foldseek 3Di
  alphabet, 441 tokens) with no folding head and no generative binder
  capability. It neither predicts 3D structure nor designs binders, and belongs
  to no lineage tracked here. Cited by one corpus paper.

- **Genie 3** — `genie3` · `10.64898/2026.05.01.722168` — _excluded: no lineage
  in the review, and its dispute is not the review's._ An SE(3)-equivariant
  all-atom backbone diffusion model (AlQuraishi lab), target-conditioned and so
  in scope by the rule, reporting the most successful designs on 7 of 10 of
  AlphaProteo's binder problems at a fixed 200-structure budget against
  BindCraft, RFdiffusion, BoltzGen and Proteina-Complexa, and holding that lead
  normalized by GPU-hours. _Why it is out:_ the review is organized as predictor
  lineages followed to the design systems built on them, and Genie descends from
  none of the six. Admitting it on its benchmark result alone would make the
  review a scoreboard between generation and hallucination — the log of disputes
  `GOAL.md` rules out — and the coupling levels are an ordering of the material,
  not a claim that tighter coupling wins, so there is no beat here for it to
  overturn. _Reopen when:_ the Adaptyv Nipah competition is written up as
  material in its own right; §5's joltz/mosaic line is the map's only Nipah
  entry today, and it is in-silico only. Genie 3 is the wet-lab side of the same
  competition — 1 binder in 8 designs at KD ≈ 92 nM — and reports RFdiffusion
  3/60, BindCraft 1/100 and BoltzGen 2/288 there too. _How far that goes:_ the
  assay is shared, the method attribution is not. Those three rates are scraped
  from the competition site's self-reported method tags, which the paper says
  may be missing and may reflect the entrants' choices rather than the models'.
  So it is a common assay, not the controlled cross-method comparison the corpus
  lacks. That is a different job from a section entry and needs no decision now.
  Two numbers in it bear on the conclusion without an entry — the in-silico
  oracles' precision ceiling (maximum 12%, and no binder found at all for H3,
  TGFβ and TIE2) for the fifth gap, and the Nipah rates above, carrying that
  caveat. _Provisional claim corrected on reading:_ the Genie 3 / BindCraft
  design overlap is reported qualitatively in a figure, not as the \<10% this
  file previously recorded. _Preprint; re-check for a journal version._

- **AlphaDesign** — `alphadesign` · `10.1038/s44320-025-00119-z` — _excluded:
  below the weight the review spends a line on._ AF2 confidence scores as a
  fitness function searched by an evolutionary algorithm, with an autoregressive
  diffusion model of its own redesigning the surviving sequences. Held a
  **mention** in §5 until Sep 2026, as the non-gradient version of the same
  arrangement. _Why it is out:_ the field does not remember it — no system in
  the corpus builds on it, and §5 is about the gradient, which this replaces
  with a search. _What it still carries:_ ProteinMPNN's entry (§2) cites it as
  the corpus's one alternative sequence designer, so it stays in `refs.bib` and
  the corpus and may still be quoted there.

- **joltz / mosaic** — _no publication, no DOI; not cataloguable_ — _excluded:
  its only claim on the review is a leaderboard score._ `joltz` ports Boltz-1/2
  to JAX and makes them differentiable; `mosaic` (Escalante Bio) optimizes
  against them — the Boltz counterpart to ColabDesign. Held a _map-only_ mention
  in §5 until Sep 2026. _Why it is out:_ what put it there was the top
  **in-silico** score in Adaptyv's Nipah binder competition (Jan 2026),
  descending a Boltz-2 loss directly with no inverse-folding stage, and a
  leaderboard result with no wet-lab outcome is not weight the review should
  spend a line on. _What removing it cost, recorded so it is not rediscovered:_
  it was the second group inverting Boltz, independent of BoltzDesign1's — the
  only loss in §5 of a group, not of an attachment point. _Reopen when:_ the
  Adaptyv Nipah competition is written up, where it is the in-silico entrant
  beside Genie 3's wet-lab one. Cannot enter `refs.bib` in any case, so it comes
  back as a map-only line or not at all.

- **Protein Hunter** — `protein_hunter` · `10.1101/2025.10.10.681530` —
  _excluded: cycling, not gradient, and no room at that weight._ Hallucination
  inside a diffusion co-folder: starting from an all-X sequence, Boltz-2
  hallucinates a plausible structure, improved through _"iterative sequence
  re-design and structure re-prediction"_ with SolubleMPNN. It never
  backpropagates into the design variable — the paper's own contrast is with
  BindCraft and BoltzDesign1, whose _"reliance on gradient decent leads to slow
  convergence"_ — so it cannot join the Level-2 roster without blurring the axis
  §5–§7 escalate along, and as a cycling method it would enter §5 at a weight
  the section does not have room for beside BindCraft, BoltzDesign1 and
  Germinal. Its one remaining claim was being RFOptimization's only external
  baseline, and that comparison is RFOptimization's own and cited there; §2 and
  §5 carry the lineage's optimizer completely without it. _Preprint; re-check
  for a journal version._

- **HalluDesign** — `halludesign` · `10.1101/2025.11.08.686881` — _excluded:
  same ground as Protein Hunter above._ The same move on an AlphaFold3-style
  predictor, _"fine-tune free, forward-pass only"_, which the paper sets against
  the _"gradient-based backpropagation methods"_ it classifies the field into.
  _What its existence establishes, and the map does not need it to say:_
  cycling-based hallucination is an independently developed family rather than
  an RFOptimization idiosyncrasy — this is the Cao lab's, independent of
  Ovchinnikov's. _Preprint; re-check for a journal version._

- **Caliby** — `caliby` · `10.1101/2025.09.30.679633` — _out by the scope rule,
  and no lineage in the review._ A sequence designer: ProteinMPNN's architecture
  rewired to emit a Potts model — per-position and per-pair amino-acid scores,
  sampled for a low-energy sequence — so that several backbone conformers can be
  averaged into one scoring function, the ensemble generated by partially
  re-diffusing the input with Protpardelle-1c. It writes sequences with no
  target conditioning, which the scope rule above excludes, and it descends from
  no predictor lineage the review follows: Protpardelle is not in the map, and
  there is no wet lab. §2 presents ProteinMPNN's standing as adoption rather
  than necessity through AlphaDesign already. _Surfaced 18 Sep 2026 from
  Anthropic's inference-optimization release
  (`anthropics/uplifting-biomolecular-modeling`), whose kit table lists the open
  models the field runs; sweeping it left Caliby as the only design-side name
  not already judged — `ef2inv` is the ESMFold2 campaign in §7, `esm_if1` is
  covered by ProteinMPNN's entry, `mosaic` (with `joltz`) is excluded above._
  _Preprint; re-check for a journal version._

- **Proteina-Complexa** — `proteina_complexa` · `10.48550/arXiv.2603.27950` —
  _excluded: no lineage in the review._ ICLR 2026; atomistic binder design by
  partially latent flow matching, extending La-Proteina, pretrained on
  _Teddymer_, a synthetic binder-target dataset built from domain-domain
  contacts in predicted monomers, then optimized at inference time over that
  generative prior. Out for the same reason as Genie 3 above: it descends from
  no predictor lineage the review follows, and the background covers the
  formalism through FrameFlow already. It also has **no wet lab** — the paper
  states its evaluations are in-silico only and names experimental validation as
  future work — so it cannot carry a beat the design sections rest on.
  _Provisional claim corrected on reading:_ this file previously credited the
  wet-lab campaign behind it to Manifold Bio, with mBER (§5) carrying the group.
  That was wrong on both counts — the work is NVIDIA, Mila, Oxford and Seoul
  National, and there is no campaign.
