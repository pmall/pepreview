# Conclusions and Open Challenges

## From in vitro binding to therapeutic utility

Most binder-design papers motivate their methods through therapeutic
development, citing goals such as automating drug discovery [@boltzgen], tuning
species cross-reactivity [@chai2], reducing IgE binding in patient-derived
samples [@bindcraft], matching approved-antibody developability [@latentx2], and
accelerating protein therapeutics [@mber]. Evaluating a decade of artificial
intelligence in pharmaceutical R&D, Bender et al. report substantial technical
progress alongside limited evidence of clinical impact so far
[@bender_perspective]. They distinguish *model validation* (accuracy on held-out
benchmarks or isolated in vitro assays, including structure prediction and
binding hit rates) from *process validation* (improved downstream clinical
decisions), noting that AlphaFold exemplifies model validation for folding
rather than process validation for drug discovery [@bender_perspective].

Although biologics have aided recent approval gains through higher clinical
success rates and stronger intellectual-property protection than small
molecules, Bender et al.'s review of protein-design methods (citing RFdiffusion,
ProteinMPNN, BoltzGen, and Chai-2) notes that binding remains easier to predict
than functional activity and developability [@bender_perspective]. This mirrors
small-molecule discovery, where ChEMBL and PubChem catalog over 10⁶ bioactive
ligands versus roughly 10³ marketed drugs [@bender_perspective]. They also
emphasize matching evaluation metrics to the decision task (selection,
deselection, or quantification), local generalization outside training
distributions, and verifiability: open-source co-folding models have largely
caught up with closed alternatives, whereas proprietary systems such as IsoDDE
disclose too little detail for independent evaluation [@bender_perspective].
Because their Perspective draws mainly on small-molecule and clinical-pipeline
evidence, relying on one benchmark preprint (FLAb2) for biologic developability,
these conclusions provide context rather than a direct audit of protein design
[@bender_perspective].

## Open technical and methodological limitations

Five technical and methodological limitations recur across current binder-design
pipelines. First, nearly all open systems generate, filter, and report solely on
binding. Latent-X2 notes that therapeutic campaigns often fail not for lack of
binding, but because binding alone is insufficient when clinical success demands
developability and low immunogenicity [@latentx2]; Latent-X2 reports such
measurements for designed antibodies, yet its generative architecture is
undisclosed [@latentx2]. Second, current scoring functions act mainly as binary
binding indicators rather than quantitative affinity estimators. BindCraft
reports that AlphaFold2 ipTM predicts whether a design binds rather than its
dissociation constant ($K_D$) [@bindcraft], and Boltz-2's affinity module covers
small-molecule ligands on single-protein targets rather than multimeric
protein–protein interfaces [@boltz2], leaving affinity to experimental
measurement. Third, most wet-lab campaigns condition on experimentally solved or
high-confidence predicted structures, and Germinal notes that how strongly
design success depends on predicted antigen-model accuracy remains an open
question [@germinal].

Fourth, no shared, blinded prospective benchmark exists for de novo binder
design, and independent replication of a full published campaign has occurred
only once, when AlphaProteo re-tested RFdiffusion's published designs (including
nonbinders) by yeast display [@alphaproteo; @rfdiffusion]. The closest
prospective standard is the AIntibody challenge, which evaluated 511 antibodies
from 29 organizations across three tasks, expressed as full IgGs and assayed
independently under one protocol combining high-throughput surface plasmon
resonance (HT-SPR), kinetic exclusion assays (KinExA), and a five-assay
developability panel with explicit pass thresholds [@aintibody]. The top
computational design (95 pM) was statistically indistinguishable from the best
wet-lab antibody (113 pM), and the Challenge 1 winner used an open-code
Protenix-derived pairformer with a direct preference optimization (DPO) fitness
head, yet a non-ML consensus of selection data ranked third [@aintibody]. On
Challenge 2 (within-HCDR3-cluster affinity ranking), only 1 of 26 groups
outperformed random clone selection; on the out-of-library task, 30.4% of
designs were nonbinders, and the highest-affinity winner (2.9 pM) failed to
elute from the hydrophobic interaction chromatography (HIC) column [@aintibody].
AIntibody also has clear scope limits: it tested one extensively characterized
antigen (SARS-CoV-2 RBD, described as "deliberately primed for success"),
captures a Q1 2025 snapshot missing several prominent de novo antibody-design
groups, and evaluated library-conditioned engineering with provided affinities
in Challenges 2 and 3 rather than target-conditioned de novo design
[@aintibody].

Fifth, structure-prediction confidence scores remain unreliable for per-design
selection. Metrics such as ipTM and ipSAE enrich hit rates across large pools,
as observed at million-design scale in mBER [@mber], yet often fail to separate
individual binders from nonbinders, as seen in Germinal where nonbinders cleared
the same ipSAE threshold as binders [@germinal]. Pooling 3,766 experimentally
tested designs from six published campaigns across 15 targets under one
re-scoring pipeline, Overath et al. found AlphaFold3 ipSAE to be the strongest
single predictor of binding overall, yet its average precision spanned 0.1–1.0
across targets [@overath_meta]. Uniform re-scoring also leaves each campaign's
heterogeneous wet-lab assays and binding cutoffs unchanged and reflects
earlier-generation designs rather than the newest 2025–2026 models
[@overath_meta].

Current co-folding and generative models can produce epitope-targeted protein
and peptide binders across several structural formats while often testing tens
rather than thousands or millions of sequences per target. Quantitative
protein–protein affinity prediction, joint control of functional activity,
developability, and immunogenicity in inspectable architectures, reliable
per-design filtering on structurally uncharacterized targets, and comparative
performance under shared blinded wet-lab benchmarks remain to be demonstrated.
