# Model Families: From Predictors to Design Systems

Tracing each model family from structure prediction to binder generation shows
how architectural choices, training data, and release policies shape downstream
design workflows. **Table 1** compares the major lineages side by side, while
**Table 2** compiles per-target prediction benchmarks and wet-lab campaign
results.

## AlphaFold and open reproductions

AlphaFold2 [@alphafold2] demonstrated experimental-level single-chain structure
prediction at CASP14 (median 0.96 Å r.m.s.d.95, 95% CI 0.85–1.16 Å, versus 2.8 Å
for the next best method) by combining an MSA-driven Evoformer trunk and
distogram head with an end-to-end differentiable Invariant Point Attention (IPA)
structure module. Because coordinates emerge from a single differentiable
regression pass, AlphaFold2 served both as a standard post-hoc refolding filter
[@rfdiffusion; @alphaproteo] and as a substrate for gradient-based sequence
design [@bindcraft]. Its documented weakness is a sharp accuracy drop when MSA
depth shrinks, making single-sequence input its weakest regime [@alphafold2].
AlphaFold-Multimer [@alphafold_multimer], released as a bioRxiv preprint without
peer review, retrained the network on protein complexes and introduced
interchain confidence scores (ipTM and interchain PAE) that became standard
design filters; gradient-based complex design tools such as BindCraft
[@bindcraft], Germinal [@germinal], and mBER [@mber] invert AlphaFold-Multimer
rather than the monomer model. OpenFold [@openfold] provided an open-source
retraining of AlphaFold2 alongside a structural distillation dataset later used
to train Boltz-1 [@boltz1].

AlphaFold3 [@alphafold3] generalized co-folding to complexes of proteins,
nucleic acids, small-molecule ligands, and ions by replacing the Evoformer with
a simplified Pairformer trunk and substituting an all-atom diffusion module for
IPA. On the 428-structure PoseBusters benchmark, it outperformed AutoDock Vina
and RoseTTAFold All-Atom without requiring solved pocket coordinates
[@alphafold3]. For antibody–antigen complexes, however, reported accuracy relied
on selecting the top-ranked sample across 1,000 random seeds rather than the
five seeds used for other classes, with accuracy still improving at 1,000 seeds
[@alphafold3]. Multi-step diffusion also prevents direct end-to-end
backpropagation through coordinates and introduces documented physical-validity
artifacts: a 4.4% chirality violation rate on PoseBusters despite a chirality
ranking penalty, residual steric clashes, and hallucinated secondary structure
in intrinsically disordered regions (mitigated via cross-distillation from
AlphaFold-Multimer v2.3) [@alphafold3]. Predictions remain static PDB-like
structures rather than conformational ensembles, and shallow MSAs still degrade
accuracy [@alphafold3].

AlphaFold3's restricted weights prompted open reproductions including Boltz-1
[@boltz1], Protenix [@protenix_v1], and OpenFold3 [@openfold3]. OpenFold3
distributes Apache-2.0 weights, training code, and its full training corpus,
including a reproduction of AlphaFold3's 13-million-sequence MGnify distillation
set, enabling retraining from scratch [@openfold3]. As a software release rather
than a peer-reviewed paper, OpenFold3 relies on self-reported benchmarks, and
its technical report evaluates superseded `preview2` weights rather than the
newer `OpenBind-0` default [@openfold3].

## RoseTTAFold, RFdiffusion, and inverse folding

Developed independently of AlphaFold at the Baker Lab and the Institute for
Protein Design, this family spans structure predictors, diffusion generators,
inverse folding models, and modality-specific tools. Two similarly named recent
releases serve opposite roles: RoseTTAFold3 (RF3) [@rosettafold3] is an all-atom
structure predictor that denoises coordinates for a known sequence, whereas
RFdiffusion3 (RFD3) [@rfdiffusion3] is a generative model that denoises
coordinates with sequence unknown before inverse folding.

The predictor branch began with RoseTTAFold (RF1) [@rosettafold], a three-track
(1D sequence, 2D pairwise distance, 3D coordinate) network contemporaneous with
AlphaFold2 in which complex prediction emerged via discontinuous two-segment
cropping without dedicated multimer training; superseded as a predictor, RF1
supplied the weights fine-tuned into RFdiffusion [@rfdiffusion]. RoseTTAFold2
(RF2), an unreviewed bioRxiv preprint, ablated AlphaFold2 and showed that FAPE
loss, recycling, distillation, and depth drove accuracy while IPA and triangle
attention were unnecessary: RF2 matched AlphaFold2 on monomers and
AlphaFold-Multimer on complexes without either module, scaled better past 1,000
residues, and kept an input-to-output 3D coordinate track suited to spatial
design constraints [@rosettafold2]. Built on RF2, RoseTTAFold All-Atom (RFAA)
added nucleic acids, small molecules, and metals two months before AlphaFold3
[@rosettafold_all_atom]. RoseTTAFold3 (RF3) subsequently adopted a BSD-licensed
all-atom diffusion architecture that learns ligand chirality from geometric
features rather than inference-time guidance, predicting 88% of ligand chiral
centers correctly versus 84% for AlphaFold3 and 76% for Boltz-2 without
guidance, and achieving 1.74 Å mean backbone RMSD on mixed L/D peptides versus
1.88 Å for AlphaFold3 and 2.24 Å for Boltz-1x [@rosettafold3]. Its authors
caution that inference-time modifications may shift diffusion networks outside
their training distribution [@rosettafold3].

On the generative side, RFdiffusion (RFD1) fine-tuned RF1 for equivariant frame
diffusion over each residue's Cα position and N–Cα–C frame orientation,
outperforming earlier RoseTTAFold hallucination and establishing the backbone
diffusion, ProteinMPNN, and AlphaFold2 refolding workflow [@rfdiffusion]. Its
authors note that reported in silico success measures agreement with AlphaFold2
confidence and self-consistency RMSD filters rather than experimental binding
[@rfdiffusion]. RFdiffusion2 (RFD2), also fine-tuned from RoseTTAFold, enabled
sequence-agnostic, atom-level enzyme active-site scaffolding from
functional-group coordinates [@rfdiffusion2]. RFdiffusion3 (RFD3) departed from
predictor initialization by pre-training an all-atom transformer U-Net modeled
on AlphaFold3's diffusion module directly on PDB structures and AlphaFold2
distillation data; reducing the Pairformer from 48 to 2 layers (168 million
trainable parameters) with 100-step sampling makes RFD3 roughly an order of
magnitude faster than earlier versions [@rfdiffusion3].

Because backbone generators omit amino-acid identities, inverse folding models
assign sequences. ProteinMPNN [@proteinmpnn], an autoregressive message-passing
neural network for fixed backbones, became the standard sequence-design
component across RFdiffusion [@rfdiffusion], RFpeptides [@rfpeptides], BindCraft
surface redesign [@bindcraft], and PXDesign [@pxdesign], though its authors
caution that native sequence recovery does not necessarily correlate with
accurate folding [@proteinmpnn]. LigandMPNN [@ligandmpnn] conditions sequence
design on non-protein context including small molecules, nucleic acids, and
metal ions, while AlphaDesign's Autoregressive Diffusion Model (ADM)
[@alphadesign] benchmarks comparably to ProteinMPNN with complementary
structural preferences.

Two modality extensions adapted this framework to antibodies and cyclic
peptides. RFantibody [@rfantibody] fine-tuned RFdiffusion for epitope-specific
VHH, scFv, and antibody design, testing 9,000 designs per target by yeast
display (four targets) and 95 per target by *E. coli* expression with SPR (three
targets); confirmed hit rates of 0–2% (best SPR affinities 78 nM on influenza
hemagglutinin and 1.4 µM on RSV site III) led the authors to note that
experimental library screening remains necessary [@rfantibody]. RFpeptides
[@rfpeptides] added a cyclic relative positional encoding to RFdiffusion and RF2
for head-to-tail macrocycles, pairing ProteinMPNN with AfCycDesign
[@afcycdesign] and Rosetta interface filtering to obtain
crystal-structure-verified binders across all four targets from fewer than 20
synthesized designs each. A separate tool in this family, RFOptimization
[@rfoptimization], uses RF3 gradients for training-free discrete refinement and
is covered under gradient-based design.

## Boltz

Boltz-1 [@boltz1], the first MIT-licensed AF3-class all-atom co-folder, was
trained partly on OpenFold distillation structures [@openfold] and supported
external design tools such as BoltzDesign1 [@boltzdesign1] (covered under
gradient-based design). Boltz-1x added Boltz-steering, using Feynman-Kac
steering potentials at inference time to reduce chirality violations and steric
clashes [@boltz1]. Boltz-2 [@boltz2] maintained essentially unchanged
structure-prediction accuracy while adding conditioning controls and a
small-molecule affinity module. That module achieved a mean Pearson correlation
of 0.66 on the four-target FEP+ subset at over 1,000-fold lower compute than
free-energy perturbation and exceeded 0.55 on three of eight blinded industrial
assays (weaker on the other five), but because it is trained on single-protein
ligand assays, it does not predict protein–protein binding affinity [@boltz2].
Its June 1, 2023 training cutoff also overlaps the standard FoldBench window
(January 13, 2023 to November 1, 2024), causing temporal leakage noted in later
benchmarks [@protenix_v1; @protenix_v2; @esmc].

BoltzGen [@boltzgen] introduced an MIT-licensed (weights, training code, and
data) all-atom diffusion model trained jointly for structure prediction
(matching Boltz-2 on its test set) and de novo binder design across proteins,
peptides, and nanobodies against targets from disordered proteins to small
molecules, excluding full antibodies from training and filtering candidates with
Boltz-2 refolding. Across eight wet-lab campaigns covering 26 targets, testing
at most 15 designs per target yielded nanomolar binders on 6 of 9 novel targets
(\<30% PDB sequence identity in a bound context) in both nanobody and
miniprotein formats, and 15–20 designs per target yielded binders on 4 of 5
benchmark targets in each format (down to 0.81 nM on PDGFR) [@boltzgen].
Disclosed caveats include diversity collapse into ubiquitin at binder lengths
73–76 (attributed to more than 900 PDB ubiquitin entries) and a `BoltzGenv0`
refolding bug that mis-assigned fixed binder residues to the target chain
(yielding 0/7 hits on two targets versus 1/7 and 7/7 once fixed); the authors
caution that binder design is not plug-and-play and advise manual structural
inspection and reruns [@boltzgen].

BoltzProt-1 [@boltzprot1] paired a refined BoltzGen generator with BoltzPPI, a
classifier trained directly on experimental binding outcomes rather than
structure-confidence heads. Across 10 low-homology targets using identical
candidate pools and 15 designs per target (150 total), switching from BoltzGen's
confidence ranking to BoltzPPI raised confirmed binders from 3.3% (5/150; 2/10
targets) to 8.0% (12/150; 4/10 targets) [@boltzprot1]. The study separated
initial screening hits from confirmed binders verified by flipped assay
orientations and independent vendor re-testing [@boltzprot1]. Unlike earlier
MIT-licensed Boltz releases, BoltzProt-1 is offered only via commercial API and
platform access without released weights [@boltzprot1].

## Chai

Chai-1 [@chai1] is an AF3-class diffusion co-folder with both an MSA track and a
protein language model track usable independently or together, plus optional
experimental restraints (pocket, contact, or docking) that deliver double-digit
accuracy gains. It matched AlphaFold3 on PoseBusters (77% versus 76% ligand RMSD
success), and on antibody–protein interfaces, single-sequence Chai-1 matched
MSA-enabled Chai-1 while both outperformed AlphaFold-Multimer v2.3 with MSAs,
which the authors attribute to weak evolutionary signal in antibodies [@chai1].
Model weights carry a non-commercial license (commercial use via web server),
and commercial use restrictions prevented benchmarking against AlphaFold3 or
ESM-3, confining comparison to AlphaFold-Multimer v2.3 on CASP15 [@chai1].

Chai-2 [@chai2] built on Chai-1 (via an intermediate `Chai-1d` prototype) for
zero-shot scFv, VHH, and minibinder design without library screening or affinity
maturation. Testing at most 20 designs per target per format across 52 novel
targets produced 13.7% scFv (68/496) and 20.0% VHH (41/205) hit rates (16%
combined; binders on 26/52 targets), while five minibinder targets (20–25
designs each) achieved a 68% hit rate (75/111; best affinity 18.3 pM on IL-7Rα)
[@chai2]. The paper describes only the folding submodule (`Chai-2f`, similar in
architecture to Chai-1) and withholds the generative architecture [@chai2]. A
commercial successor, Chai-3 (2026), runs via Chai Discovery's web platform
without an accompanying publication.
