# §3 — Boltz

This is the lineage that publishes its mechanism, and the section spends that
publication twice: once to show design and prediction sharing one set of
diffusion weights, once to hold a generator fixed and swap the critic that ranks
what it proposes. The second is the controlled comparison the rest of the review
reaches for — same candidate pools, same testing budget, only the selection
changed — and the confirmed-binder rate moves 2.4-fold.

The lineage opens by publishing what AlphaFold3 closed. Boltz-1 reimplements the
AF3-class co-folding architecture and releases everything — training and
inference code, weights, datasets, benchmarks — under MIT, the first fully
accessible model at AF3-reported accuracy. Its accuracy claim is the
reproduction one: across the protein–protein and protein–ligand metrics of its
benchmark test set, the differences from AlphaFold3 and Chai-1 sit well within
the confidence intervals. The paper's own addition is physical validity, entered
through the gap between a geometry score and a usable pose: the afflictions
AF3-class output carries — steric clashes, wrong stereochemistry, non-planar
rings, chains on top of chains — are barely penalized in geometric accuracy
measures like DockQ, and 57% of Boltz-1's top-1 poses on the test set fail the
physical checks, with Chai-1 passing all of them for around 27% of poses and
AlphaFold3 58%. Boltz-1x adds the fix: Feynman-Kac steering, which tilts the
diffusion trajectory with flat-bottom potentials over chirality, bond
stereochemistry, ring planarity and internal geometry, and resamples among
particle proposals every third step. On the same test set it brings 97% of poses
through the checks while holding the accuracy of the unconstrained model.

Boltz-2 keeps the predictor and adds the corpus's only binding-affinity model. A
PairFormer pass — trained after structure training, trunk gradients detached —
operates on the model's own predicted structure, over protein–ligand and
intra-ligand pairs, feeding two heads: a binding likelihood and a regressed
affinity value, interpretable only approximately, as an IC50-like general
measure of binding strength. The training data set the boundary: single-protein
assays only, standardized to a logarithmic µM scale, the mixture of Ki, Kd and
IC50 values tolerated because the pairwise within-assay losses cancel the assay
terms. On the four-target FEP+ subset, where physical baselines exist, it
reaches a mean Pearson correlation of 0.66 while running over 1,000× faster than
FEP+; on eight blinded industrial assays it clears 0.55 on three and is weak on
the other five. The structure it reads affinities off has moved less than the
affinity module has: structure accuracy "does not significantly deviate" from
its predecessors', and the module does not explicitly handle cofactors, ions,
water — or multimeric binding partners, protein–protein binding in other words,
outside its trained competence. What the design models in this section filter
with is the refolding on top of this architecture: predicted structure and
confidence out of the same weights.

BoltzGen is Level 0 in its published form: the same diffusion model designs and
predicts. The trick that makes joint training work is a representation choice —
residues are not drawn from a discrete label at all, but encoded through the
geometry of the 14-atom representation, so the model runs entirely in a
continuous space and trains together on folding, binder design and
motif-scaffolding tasks, with the Boltz-2 trunk preserved underneath. The claim
that design and prediction are one machinery is evidenced rather than asserted:
the same weights fold at the predictor's level, matching Boltz-2 on Boltz-2's
own test set — best lDDT over five diffusion samples, less the 187 complexes
that did not fit a 40 GB GPU. The wet lab then tests design across platforms:
eight campaigns with functional and affinity readouts over 26 targets, from
disordered proteins to small molecules. On nine novel targets — candidates with
less than 30% sequence identity to any bound structure in the PDB — 15 designs
per target give nanomolar binders for 6 of 9 in both nanobody and miniprotein
format — 8.8 nM against RFK in nanobody form, 9.8 nM against MZB1 as a
miniprotein. On five established targets — PD-L1, TNFα, PDGFR, IL-7Rα, InsulinR
— each modality hits 4 of 5, down to 0.81 nM on PDGFR, with the paper's own
warning about what that counts: these targets have known binders in the training
data, so the results give only "marginal evidence toward" generalization, and
TNFα, the one failure, is a target prior work succeeded on.

Two caveats, both disclosed by the paper itself. At designed binder lengths of
73–76, generation diversity collapses and the model samples ubiquitin almost
exclusively — a memorization artefact of ubiquitin's 900+ PDB entries. And an
earlier version, BoltzGenv0, produced an accidental ablation of the critic: a
template bug mis-assigned the design's fixed residues to the target, so
refolding could only recapitulate the generated design and the ranking scores
carried "close-to-random" filtering power — zero hits across two targets where
the fixed version gets 1 of 7 and 7 of 7. The generator was untouched in that
failure; the hit rate left with the critic, which points the same way as the
trained critic below. The paper declines the field's usual framing — nothing
here is "zero-shot" or "plug-and-play" — and tells users to inspect the
structures and rerun.

Then the trained critic, in a comparison the paper designs to be unconfounded.
BoltzPPI is a protein–protein interaction head co-trained with the confidence
head on the Boltz-2 base, reading the pairwise interaction features and
predicted coordinates, restricted to a slice concentrated on the predicted
interface, and supervised as a binary answer to whether the proposed complex
binds — positives from PDB and patent-derived complexes, negatives from
synthetically generated pairs. Its binding-confidence score replaces BoltzGen's
own confidence metrics as the primary rank signal. The evaluation holds
everything else fixed: the selections are drawn from the published BoltzGen
candidate pools at the BoltzGen testing budget — 15 nanobody designs per target,
150 across the ten low-homology targets — and BoltzPPI's picks exclude the
sequences BoltzGen itself selected. Confirmed binders rise from 3.3% to 8.0% of
designs, 5 of 150 to 12, with coverage moving from 2 of 10 targets to 4 of 10;
the fourth, MZB1, is credited to the improved generator and kept out of the
ranking claim. Confirmation is an orthogonal flipped-orientation assay,
reversing which binding partner sits immobilized to blunt format and avidity
artifacts, run by Adaptyv Bio and Sino Biological. On the ten-target panel
Chai-2 published, the full BoltzProt-1 pipeline takes screening hits on 7 of 10
targets, against 6 of 10 for Chai-2 and 3 for BoltzGen — broadest coverage, but
a full-pipeline number that does not isolate ranking. Developability is measured
too: 58% of the confirmed binders pass every criterion — stability, aggregation,
purity, polyspecificity, hydrophobicity — against 40% of BoltzGen-selected
binders and 21–25% for the clinical-stage VHH and IgG controls. All of it is
measured and published; almost none of it is inspectable. The pipeline is
reachable through the Boltz API and the Boltz Lab platform, with no weights —
the disclosure beat's fork, landing inside the lineage that opened it.

§4 is the strongest design system the corpus holds, from a lineage whose
generator mechanism is never stated — which is why this section met the reader
first, every part of it inspectable.
