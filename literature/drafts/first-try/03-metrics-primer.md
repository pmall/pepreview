# The metrics primer

The numbers the review quotes from here on are one of two kinds, and the
difference decides what each can measure. The first family is judged from
outside — a prediction against a solved structure, or against physics. **lDDT**
compares local interatomic distances between model and reference without
superposing either — atom pairs within its inclusion radius are scored for how
well their reference distances are reproduced, over four tolerance thresholds —
so a correct domain in a wrong overall pose still scores well. **TM-score**
measures overall fold similarity, weighting each aligned residue's error by a
scale that grows with protein length, so its value means the same thing for
short and long proteins. **RMSD** is the plain ångström deviation between two
sets of atom positions after the best superposition, which Kabsch's algorithm
computes; which two sets is the whole question — against a solved structure it
measures accuracy, but design pipelines also call RMSD the comparison of a
designed backbone against a re-prediction of its own sequence, where nothing
experimental is involved.

**DockQ** condenses protein–protein interface quality into a single number
between 0 and 1, combining the fraction of native interface contacts preserved
with two interface RMSDs; its scoring cutoffs sit well below 1, with the
conventional success reading at 0.23 and high quality at 0.8.

**PoseBusters** answers a different, prior question: not where a predicted pose
sits, but whether the molecule in it is physically possible. The checks run in
the RDKit cheminformatics toolkit, in three groups. Chemical validity and
consistency require the output to load and still be the input's molecule — same
formula, bonds, chirality. Geometry tests bound bond lengths and angles, keep
aromatic rings and double bonds planar, and reject internal clashes; an energy
test bounds the conformation's force-field energy against what unconstrained
conformations of the same molecule reach. Intermolecular tests bound
protein–ligand distances against van der Waals radii and cap volume overlap. A
prediction passing every test is **PB-valid** — a verdict, not a score, and
orthogonal to placement: a physically valid but mispositioned ligand passes, a
correctly placed ligand with inverted chirality fails, and a method can clear an
RMSD threshold while its poses are physically impossible. It shipped with its
own benchmark set — complexes published from 2021, outside the training data of
the methods it was built to test — and the AF3-class predictors report its
verdict on their protein–ligand predictions.

The second family needs no solved structure, because these are the model's
estimates of itself. AlphaFold2 introduced three alongside its accuracy and
published each fit against the quantity it estimates, on 10,795 recent PDB
chains: r = 0.76 for pLDDT against its own lDDT-Cα, r = 0.85 for pTM against its
own TM-score. **pLDDT** is the first, per residue, from a small network reading
the final representation; **pTM** is the second, whole-prediction, from a
pairwise error projection off the same representation. **PAE** differs in kind:
not a score but a matrix — for every ordered pair of residues, the expected
error, in ångströms, in the position of residue *j*'s Cα once residue *i*'s
backbone frame is superposed onto its true counterpart. It predicts a
distribution over 64 half-ångström bins spanning 0 to 32 Å and reports its
expectation.

AlphaFold-Multimer added the interface versions, over interchain residue pairs
only. **ipTM** is pTM restricted that way — the TM-style error of residue *j*
scored through an alignment centred on residue *i*, averaged over the other
chains' residues, maximized over *i*, with the length normalization set by the
whole complex — ranking models on 0.8·ipTM + 0.2·pTM, so the rank keeps some
intra-chain confidence. The interchain reduction of the PAE matrix, **iPAE**, is
the other half: the success criterion quoted in the background, interchain AF2
pAE < 10, is ten ångströms of expected aligned error across binder–target
residue pairs.

**ipSAE** exists because ipTM's restriction is not tight enough. Averaged over
whole chains, ipTM moves when the input does: add disordered sequence to one
chain and the score rises, because the length normalization *d*₀ grows with it;
add disordered sequence to both chains and the score falls, because residue
pairs with high PAE enter the average — in both cases with the predicted
interface unchanged. ipSAE restricts ipTM once more, to interchain pairs whose
PAE sits below a cutoff, recomputes the length normalization from those residues
alone, and takes the pairwise scores from the PAE values rather than the
predicted distributions — so it computes from the PAE matrix alone, on
AlphaFold2 or AlphaFold3 output, for every chain pair in a complex. The cutoff
is the user's to choose, with the paper finding 10–15 Å the useful range, and
the floor the normalization needs for very short peptides is flagged by the
author as somewhat arbitrary. What it measures is still ipTM's question, put
only to the residues the interface involves — and the design half of the review
runs on it: Germinal reports its binders against a suggested ipSAE threshold,
and the Overath meta-analysis found it the best single predictor of measured
binding among the AlphaFold output scores. The families divide the sections to
come: predictors are read against the first, designed binders against the second
— the only comparison available to a design, since it has no solved structure.

| Unit           | Compared to      | What it measures                                                                                | Introduced by      |
| -------------- | ---------------- | ----------------------------------------------------------------------------------------------- | ------------------ |
| **lDDT**       | a real structure | local interatomic distances, no superposition                                                   | lDDT               |
| **TM-score**   | a real structure | global fold similarity, length-normalized                                                       | TM-score           |
| **RMSD**       | whatever it says | Å deviation between two sets of atom positions — accuracy only when one set is a real structure | Kabsch             |
| **DockQ**      | a real structure | interface quality as one 0–1 number                                                             | DockQ              |
| **PB-valid**   | nothing          | physical plausibility, pass/fail                                                                | PoseBusters        |
| **pLDDT**      | itself           | per-residue guess at its own lDDT                                                               | AlphaFold2         |
| **pTM**        | itself           | guess at its own TM-score                                                                       | AlphaFold2         |
| **PAE**        | itself           | predicted error in Å per residue pair — a matrix, not a score                                   | AlphaFold2         |
| **ipTM**       | itself           | pTM over interchain pairs only                                                                  | AlphaFold-Multimer |
| **pAE / iPAE** | itself           | PAE over interchain pairs only                                                                  | AlphaFold-Multimer |
| **ipSAE**      | itself           | ipTM over the well-predicted interchain pairs only                                              | ipSAE              |
