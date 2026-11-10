# §6 — Protenix

A Level-2 gradient stops short of an AF3-class predictor because its structure
stage diffuses. Protenix replaced the 200-step diffusion decoder with a two-step
ODE sampler, and the gradient runs through the whole network. ByteDance Seed's
v1 is an open AF3-class predictor, and its results against AlphaFold3 carry
their conditions: the same training-data cutoff, model scale and inference
budget. Matched conditions split the results — ahead of AF3 on protein–protein
and antibody–antigen, behind it on protein–ligand and protein–DNA — and accuracy
rises roughly log-linearly with the sampling budget, a behaviour AF3 has and
prior open models lacked. The controlled claim covers the strict-cutoff model;
the variant recommended for applied use trains past it and stands outside that
comparison.

PXDesign attaches to that sampler. The hallucination arm, PXDesign-h, relaxes
sequences over amino-acid distributions and optimizes them against five Protenix
models resampled each step — BindCraft's five-weight-set defence against
overfitting one critic, carried in. The diffusion arm, PXDesign-d, generates
Cartesian coordinates from a diffusion-transformer backbone rather than the
SE(3)-equivariant or frame representations RFdiffusion and AlphaProteo use. What
§1–§5 treated as competing couplings become two modes of one product, chosen per
target: diffusion for volume, more successful designs per 24 hours;
hallucination for small, targeted campaigns. The wet lab ran on the diffusion
arm.

Against BindCraft and BoltzDesign1 the two couplings are compared under
identical settings — a matched head-to-head few studies had run, by the system
being promoted, so under Exhibit 4's self-reported band. The wet lab is
stronger: six targets, hits defined by BLI affinity measurement as below 1 µM,
20–73% on five of six targets and 2–6× AlphaProteo's rates on those five, with
TNF-α at zero for both. Its filter analysis adds a critic-side caveat:
confidence thresholds do not transfer across targets, and a Protenix-Mini pTM
cutoff raised to help FGFR2 drove SC2RBD's success rate to zero.

Protenix-v2 pushes both halves. On prediction it gains 9–13 points of
antibody–antigen success over v1 at the DockQ success cutoff across three
benchmark collections, and five seeds surpass v1's thousand-seed accuracy. On
design it moves from miniproteins to antibody formats — a novelty-controlled
VHH-Fc panel with at least one BLI-confirmed binder for every antigen, at hit
rates of 2–48%, and on four GPCRs, small flexible extracellular epitopes
conventional antibody discovery struggles with, 16–88% in VHH-Fc and up to 50%
in mAb at 16–30 designs tested per target. Its targets were in stock to assay
and its epitopes were chosen, the opposite of mBER's control; the paper repeats
the lesson itself — 4% against 48% for two epitopes on one antigen — and then
adopts Chai-2's practice of native ligand-binding interfaces. BoltzGen and
Chai-2 are compared in the panel, built from their target-selection regimes
rather than a shared assay; unlike Chai-2, the mechanism is described and the
predictor is downloadable.

The lineage ships the ruler too. PXMeter, an open evaluation toolkit with a
hand-curated PDB benchmark first run against Chai-1 and Boltz-1, is where this
section states the physical-validity thread once. AlphaFold3's diffusion stage
samples coordinates that can be chemically impossible — inverted chirality,
steric clashes — that geometric accuracy metrics do not penalize, which is what
PB-valid was built to test. Four groups answered: AF3 with a chirality penalty
in its ranking; Boltz-1x by steering diffusion inference; RF3 by training
chirality in as a feature; this lineage twice — training-free guidance variants
that constrain chirality, planarity, torsion and pairwise distances, and PXMeter
v1.1's planarity checks, which catch twisted amides a steered model can produce
while passing the original validity filter. The answers barely meet: guidance
against steering is what the corpus holds, 60.5% against Boltz-1x's 54.0% —
validity counted jointly with pocket-aligned ligand RMSD under 2 Å, on the
2022-to-2025 PXMeter ligand set. The one part still composed from outside the
predictor is the sequence prior — the piece §7 folds away into a single model.
