# Literature Map

> **This file is the review minus its prose** — every publication and every
> claim the review makes, in the order the final review will read. Its
> conventions are defined once in `AGENTS.md`; what the drafter does with it is
> in `literature/writing-plan.md`; what is in scope is in `GOAL.md`.
>
> **Claims here, evidence in the corpus.** The map says _what the review
> asserts_; `literature/corpus/` holds what proves it. "Changing only the filter
> roughly doubles the confirmed-binder rate" is a claim and belongs in an entry;
> the figure, the cutoff, the assay and the caveat that travels with them are
> read out of the parsed paper at writing time. So a section draft that could
> have been written from the map alone has failed — and so has an entry that
> says only where a work sits and never what it claims.
>
> **Entry schema.** Every entry opens with name · bib key · DOI · tier, then one
> or two sentences of what the work is. Anything further uses these lines and no
> others, so that a missing one is visible rather than merely absent:
>
> | Line                     | Holds                                                                       | Required on                         |
> | ------------------------ | --------------------------------------------------------------------------- | ----------------------------------- |
> | _Carries:_               | the claim the tier rests on, named so the tier is checkable                 | **backbone**, **meat**              |
> | _Against:_               | what the work is contrasted with — the comparison the prose is built around | **backbone**                        |
> | _Caveat:_                | the limit that travels with the claim wherever it is cited                  | where one exists                    |
> | _Collision:_             | material this entry does **not** own, and where it is owned                 | where two units could both claim it |
> | _Level:_ / _Attachment:_ | how tightly it couples to its critic, and where its gradient stops          | design systems only                 |
>
> A **mention** carries none of these: a mention is one sentence, and if it
> needs a _Carries_ line it is not a mention.
>
> **One unit per `#` heading**, in the order they render. A `##` heading inside
> a unit is a **beat**: one piece of it, with its own sources.

______________________________________________________________________

# The introduction

One unit, one draft. The funnel — from why a binder matters at all down to what
this review covers. It names systems without explaining them; every mechanism
belongs to the background that follows.

**Binders are how biology is acted on.** Blocking a protein, detecting it,
tagging it, drugging it — each means having another molecule that binds it, and
for a protein target that molecule is usually itself a protein or a peptide: an
antibody, a nanobody, a minibinder, a macrocyclic peptide. That class of
molecule is a large share of modern medicine and of the reagents a lab runs on.

**Getting one has meant searching, not designing.** Immunize an animal, or
screen 10¹² or more random sequences by display and keep whatever sticks. That
works, and it is still how most binders are found. It also costs a wet lab from
the first step, runs once per target, and returns whatever the library happened
to contain rather than something proposed on purpose. The ambition behind
everything in this review is to propose instead — candidates for a named target,
computed, in whatever number you want.

**What changed is that structure prediction stopped being the open problem.**
AlphaFold2 closed a fifty-year-old question at CASP14, and AlphaFold3 carried
the result from single chains to arbitrary complexes. Prediction became
something other work is built on rather than something being argued about, and
the field's attention moved to design. _Collision:_ the wager that made it work,
its numbers and the anatomy of a co-folder are the founding bet beat's.

**Designing a binder is not the same problem.** A predictor is asked what a
known sequence folds into, and an experimental structure can say whether it was
right. A generator is asked to invent a sequence that does something chosen, and
nothing short of a wet lab says whether it did. That the two turn out to run on
one machinery is a finding the review arrives at, not a premise it starts from.
_Collision:_ that argument is the identity beat's.

**The last two years are an explosion, which is the reason for the review.**
Several predictor lineages, each openly reimplemented; design systems stacked on
every one of them; results published faster than anyone compares them; and
vendors paying for speed on these exact models — during one week of September
2026, NVIDIA, Anthropic and the ESM side each shipped optimized inference
kernels for Boltz, Chai-1, Protenix, OpenFold, RoseTTAFold3, RFdiffusion,
BindCraft, PXDesign and ESMFold2, reporting two- to fourfold throughput gains.
Nobody spends that on software nobody runs. A newcomer cannot see the shape of
any of this from the papers alone. _(map-only — blog posts and repository
releases, no publication.)_
[NVIDIA](https://developer.nvidia.com/blog/high-throughput-structure-prediction-with-bionemo-inference-runtime/)
·
[Anthropic](https://www.anthropic.com/research/claude-uplifts-biomolecular-modeling)
· [kits](https://github.com/anthropics/uplifting-biomolecular-modeling)

**The review is about one problem: given a target protein, design a new protein
or peptide that binds it.** Antibodies, nanobodies, VHHs, scFvs, minibinders and
macrocyclic peptides are one object here, because that is what they are to every
model in the review: a chain of amino acids, judged by how it folds against the
target. Small molecules are the other half of binder discovery and are out of
scope — a molecule is a variable-size graph under hard valence rules, not a
chain drawn from a fixed alphabet of twenty, so generating one takes different
machinery and is judged on different benchmarks.

**The models are followed lineage by lineage, from each predictor to the designs
built on it.** AlphaFold, RoseTTAFold, Boltz, Chai, Protenix, ESM — so an
architecture is met once and then traced to what it produces, with its results
and the caveats on them. §8 steps outside the open lineages to the closed
systems, read as evidence about the field's evidence rather than as its
strongest results. What comes before §1 is preparation for it: what a co-folder
is, why prediction and generation are one machinery, how tightly a generator
couples to its critic, what the field's disclosure limit does to its evidence,
and the vocabulary its numbers are quoted in.

**The thread through all of it, in one number.** How many designs must be
physically made before one binds. Screening-era and early computational work
needed thousands to millions of candidates per target; current systems report
tens. The measure of progress in this field is how few designs you must make to
get a binder, and §1–§8 are, read one way, a history of that number falling.
_Collision:_ the numbers, the table and the argument are the identity beat's;
the introduction says the number exists and what it measures.

______________________________________________________________________

# Background

## The founding bet, and how a co-folder is built

Design needed prediction first, and prediction was solved on a single wager:
**that coevolution between two positions in a multiple sequence alignment is a
usable proxy for the two residues being close in space.** AlphaFold2 cashed it —
median 0.96 Å backbone accuracy on CASP14, against 2.8 Å for the next best
method — and AlphaFold3 generalized it from single chains to arbitrary complexes
of proteins, nucleic acids, ligands and ions.

**Every co-folder in this review is two stages, and they do different jobs.**
This is the anatomy the rest of the review reads through, because almost every
disagreement between systems is a disagreement about one of the two.

**Stage 1 — the trunk. Sequences in, pairwise reasoning out.** What comes out is
principally a **distogram**: for each pair of residues, a probability
distribution over how far apart they are. The contact map _is_ the trunk's
output, so this is where the coevolution bet is cashed, and the stage is
differentiable throughout. The variation here is what feeds it, and the divide
runs the length of the review:

- **An MSA**, retrieved by searching sequence databases at inference time —
  evolutionary depth looked up on demand. AlphaFold2 and AlphaFold3,
  RoseTTAFold, Boltz, Protenix.
- **A protein language model**, which has the same statistics in its weights, so
  a single sequence is enough. ESM-2 with ESMFold, then ESMC with ESMFold2 (§7).

The divide is not a wall — Chai-1 (§4) carries both tracks and runs on either —
but which of the two a model is built around is the thread this review follows
longest, and what it settles is not accuracy so much as how tightly a generator
can later couple to it (the coupling beat).

**Stage 2 — the structure stage. Pairwise reasoning in, atomic coordinates
out.** The variation here is the generative formalism, and what it decides is
how many forward passes one sample costs:

- **A single regression pass — AlphaFold2.** The structure module with IPA,
  trained end to end; AF2's own ablation table lists _"no end-to-end structure
  gradients"_ as a measurable cost. Gradients traverse the entire network.
- **Diffusion — AlphaFold3, and everything built in its image.** Coordinates are
  sampled along a long stochastic denoising trajectory. FrameFlow, the paper
  that recast this problem as flow matching, puts the cost at _"∼1000 model
  forward passes ... to produce high-quality samples"_.
- **Flow matching — an ODE rather than an SDE**, with _"straighter sampling
  trajectories"_, so far fewer steps buy the same sample: FrameFlow —
  `frameflow` · `10.48550/arXiv.2310.05297` · **meat** — recasts FrameDiff this
  way and reports 2× designability at 5× fewer sampling steps, on unconditional
  monomers rather than binders. _Carries:_ the step-count premise quoted in the
  bullet above, which the coupling beat's Level-2 argument rests on. Four
  target-conditioned binder generators in the catalog are built on the formalism
  — PPIFlow (`ppiflow`), OriginFlow (`originflow`), AtomFlow (`atomflow`),
  D-Flow (`dflow`), each **mention** — and nothing in the corpus cites them, so
  it has traction as a method and none as a lineage.

**Both formalisms are borrowed from image generation, and what differs is only
what gets noised.** AF3 calls its structure stage _"a relatively standard
diffusion approach"_ and cites the image-generation literature for it; where an
image model denoises pixels, AF3's module is _"trained to receive 'noised'
atomic coordinates and then predict the true coordinates"_. The formalism is
borrowed, the purpose is not — that module replaced AF2's structure module and
runs whether or not anything is being designed. Image generation then made the
same diffusion → flow-matching move for the same reasons of speed and
simplicity, which is why these papers present flow matching as diffusion's
successor rather than as an alternative to it.

That is the machine. Its limit is where the identity beat starts: a predictor
tells you what a _given_ sequence folds into. It does not tell you which
sequence to try.

## Prediction and generation are the same machinery

**What separates them is only which sequences you hold fixed.** Give a co-folder
every chain in the complex and it predicts a structure. Leave one chain blank —
usually the short binder you are trying to invent — and ask the same model for a
chain that folds against the rest, and the same machine is a generator. BoltzGen
says so outright: _"a single all-atom diffusion model capable of performing both
structure prediction and protein design"_. RFdiffusion reached the same place
from the other direction, by fine-tuning RoseTTAFold — a predictor — into a
generator of backbones. That direction works because RoseTTAFold's 3D track runs
all the way to the input, so a design constraint — a target to bind, an active
site to hold — enters as coordinates rather than as pairwise distances. The two
halves of this review are one technology used two ways.

**Why the predictor alone was not enough.** A predictor answers a question you
must already have asked: how does _this_ sequence fold against the target? It
cannot tell you which sequence to try, and there are vastly more candidates than
anyone can test — twenty choices at every position of a chain tens of residues
long. The established way around that was to let a library do the searching:
immunize an animal, or screen 10¹² or more random sequences by display and keep
whatever sticks. This works, and it is still how most binders are found. Its
limit is not scale but aim. RFantibody states it plainly: _"no method currently
exists to design novel, epitope-specific antibodies entirely in silico. Instead,
antibody discovery currently relies on immunization, random library screening or
the isolation of antibodies directly from patients"_. A library returns binders
to whichever part of the target happens to be accessible or immunogenic; it
cannot be aimed at the site you care about.

**What generation bought is measured in one number: how many designs you have to
physically make before one of them binds.** That collapse is the review's
quantitative spine.

| Era                                             | Designs tested per target                                                                                | Source                                  |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Screening-based, and early computational design | _"thousands to millions of designs to reliably identify hits"_                                           | Chai-2's characterisation of prior work |
| Current generative + filtering                  | 16–30 (Protenix-v2), ≤20 (Chai-2), ≤20 (RFpeptides), 30–100 (Latent-X), 43–101 (Germinal), 84 (ESMFold2) | each system's own campaign              |

The hit rates in the same papers sharpen it: 16% for Chai-2 on de novo
antibodies, up to 48% and 16–88% on GPCRs for Protenix-v2's VHH-Fc designs, 70%
for ESMFold2's minibinders. **The measure of progress in this field is how few
designs you must make to get a binder**, and the eight sections are, read one
way, a history of that number falling.

Those percentages do not all count the same event. BoltzProt-1 separates
_screening hits_ from _confirmed binders_ and notes that screening hits are
_"what prior binder design model literature typically reports as binders"_; its
own confirmed-binder rate is 8.0%, where the looser definition would give a much
larger number.

**And the one campaign that did not choose its targets.** Every number above
comes from a campaign whose targets and epitopes its own authors selected. mBER
(§5) is the exception — a million-scale VHH campaign against hundreds of human
cell-surface proteins, hotspots drawn at random — and its median per-design hit
rate lands two orders of magnitude below the headline numbers, at the same
coupling level and on the same predictor as Germinal. The spread _inside_ that
single campaign is the finding: its best epitopes come back up into the range
everyone else reports. **Target and epitope selection alone move a hit rate
across the full width of the literature's spread**, and every hit rate the
review quotes is read against it. Its hits are phage-display enrichments —
BoltzProt-1's _screening hits_, not confirmed binders.

**Image generation has no AlphaFold.** Both formalisms in the structure stage
are borrowed from it (the founding bet), and that is where the resemblance
stops: nothing scores whether a generated image is _correct_, so image models
are judged by human preference and cannot close a loop on their own objective.
Protein design can, because it has a predictor to grade against — and how
tightly that loop is closed is the coupling beat. The borrowed machinery was the
easy half; the critic is the part with no counterpart in the source field.

## How tightly the generator is coupled to its critic

Every system in this review pairs something that proposes sequences with
something that judges them. What separates them is how tightly the two are
bound, and §5–§7 are ordered by it.

**Level 0** — the generator _is_ a predictor, with its weights reused. An
attribute of an entry rather than a section, marked _(inherits …)_. **Level 1**
— generate, then filter with a critic, no gradient: either the predictor's own
confidence scores, which is the field's default, or a critic trained to answer
whether a design binds (§3). **Level 2** — backpropagate the predictor's loss
into the sequence being designed, held as a blurred distribution over amino
acids. RFOptimization (§5) is the one system that leaves the sequence as real
amino acids and uses the gradient only to rank point mutations.

What follows is what each level costs and what it buys.

| Route                                                                 | What is optimized                                      | Where the critic sits | Corpus examples                                                                            |
| --------------------------------------------------------------------- | ------------------------------------------------------ | --------------------- | ------------------------------------------------------------------------------------------ |
| **Level 0** — the generator _is_ a predictor                          | the model's own sampling                               | inside the model      | BoltzGen (§3); RFdiffusion 1/2, fine-tuned from RF1 (§2) — the identity beat               |
| **Level 1** — backbone, then inverse folding, then a predictor judges | nothing is optimized; designs are sampled and filtered | after the fact        | RFdiffusion → ProteinMPNN → AF2 (§2); RFpeptides, BoltzGen, PXDesign-d, Protenix-v2 design |
| **Level 2** — descend a relaxed sequence                              | an *L*×20 simplex, annealed to one-hot                 | inside the loss       | BindCraft, Germinal, BoltzDesign1 (§5); PXDesign-h (§6); ESMFold2 (§7)                     |

Level 1 is still the field's default, and it is the origin of the standard
success criterion — AlphaProteo's _"interchain AF2 pAE < 10, binder-aligned
binder RMSD < 1 Å, pLDDT > 80"_ — quoted whole and left unpacked here; the
metrics primer, which follows this unit, defines its units.

**What makes Level 2 possible at all is that a sequence relaxes.** A chain still
being designed can be held as a probability distribution over the 20 amino acids
at each of _L_ positions, and every point in that space is still a valid input
to a structure predictor. So a design loop can hand the predictor a blurred
sequence, read how wrong the resulting structure is, and step downhill —
BindCraft through AlphaFold2, Germinal over antibody CDR logits, ESMFold2
through a language model and a folding head at once. Level 2 is not a training
trick; it is what this representation permits and a discrete one does not.

**Why MSA emancipation was the precondition for Level 2.** This is the one
genuinely non-obvious claim in this unit. **An MSA is a database lookup on a
sequence that does not exist yet.** It is neither differentiable nor even
defined for a binder still being invented, so any Level-2 loop has to run its
predictor single-sequence on the designed chain. That is why BindCraft,
hallucinating through AlphaFold2, operates the model in exactly the regime AF2's
own paper documents as its weakest — and why ESMC/ESMFold2, which is natively
single-sequence, can backpropagate through a 6-billion-parameter language model
without ever leaving distribution. MSA emancipation is not an accuracy story; it
sets the ceiling on how tightly a generator can couple to its critic.

**Where the gradient attaches is the mechanical half of the same claim**, and
the anatomy beat decides it. AlphaFold2 is differentiable end to end, so a
design loop can backpropagate through the whole network. AF3-class models
replaced the structure module with diffusion and broke that — not because
diffusion is undifferentiable, but because unrolling a thousand denoising steps
to get a gradient is impossible. The corpus holds three answers to that one
architectural fact, and they are the substance of §5; this unit's business is
that the question exists and that the anatomy beat's architecture is what raises
it.

**And the filter, not the generator, is where the hit rate lives.** Level 1 says
"filter", and the field long read that as the predictor's own confidence head.
Three systems say otherwise, which is why Level 1 has two forms above.
RFOptimization (§5) treats agreement with a single predictor as the failure mode
itself, mixing three predictor families across its loop and holding one of them
out as an independent check. PXDesign (§6) finds that Protenix and AF2-IG
filters retain _different_ true positives. And BoltzPPI (§3) replaces BoltzGen's
confidence metrics with a critic trained to answer "will this bind", roughly
doubling the confirmed-binder rate with the generator untouched — the same
designs, a different judge.

## The disclosure limit

The limit of what a literature review can establish. The strongest claimed
results increasingly come from systems that publish benchmarks and withhold
mechanisms — AlphaProteo, Latent-X, Chai-2's generator, and IsoDDE, which has no
publication at all and is visible only as the top point on a competitor's
scaling curve.

**The sharpest version of this is not IsoDDE — it is Boltz.** The lineage enters
the review as the open answer to AlphaFold3's closed weights and exits with its
own frontier closed: Boltz-1, Boltz-2 and BoltzGen stay MIT, while BoltzProt-1
ships API-only with no weights. It is the one lineage where the review holds the
before _and_ the after, both with papers.

The symmetry that gives §8 its force: **AlphaFold3 is a Google DeepMind _and
Isomorphic Labs_ paper**, so the review opens on the published half of that
organisation's work and closes on the half that stopped publishing.

**The published results do not make up for the withheld methods, because the
same labs supply them.** Every design campaign chose its own targets, assay and
hit definition, so a hit rate is self-reported by the party whose method cannot
be inspected. And the correlation runs backwards: the papers disclosing most are
not the ones reporting the highest numbers, so the most impressive result is
systematically the least checkable. That is this beat's finding rather than a
warning attached to it, and it is why §8 sits outside the argument instead of
inside it — the review reads the closed systems as evidence about the field's
evidence, not as its strongest results.

______________________________________________________________________

# The metrics primer

Renders between the background and §1, because §1–§8 quote lDDT, DockQ,
PB-valid, pLDDT, pAE and ipTM from the start. It defines those units and nothing
else, grouped by the publication that introduced them. The first three
paragraphs judge a prediction from outside — against a solved structure, or
against physics; the last three are the model's own estimates, which need no
solved structure — the only kind the design sections can use, since a designed
binder has none.

**lDDT** — `lddt` · `10.1093/bioinformatics/btt473` · **mention** — compares
local interatomic distances without superposing the two structures, so a correct
domain in the wrong pose still scores. **TM-score** — `tm_score` ·
`10.1002/prot.20264` · **mention** — measures overall fold similarity,
normalized for length. **RMSD** — `kabsch` · `10.1107/S0567739476001873` ·
**mention** — is the plain distance in ångströms between two sets of atom
positions after the best superposition, which Kabsch's algorithm computes; which
two sets is the whole question — against a solved structure it measures
accuracy, but design pipelines also call RMSD the comparison of a designed
backbone against a re-prediction of its own sequence, where nothing experimental
is involved.

**DockQ** — `dockq` · `10.1371/journal.pone.0161879` · **mention** — reduces
interface quality to one number between 0 and 1, with a conventional success
threshold well below 1.

**PoseBusters** — `posebusters` · `10.1039/D3SC04185A` · **backbone** —
introduced **PB-valid**, which is not accuracy but a pass/fail verdict on
physical plausibility, bundling chemical-validity, geometry, energy and clash
tests, with a benchmark set to run it on. AF3, Chai-1, Boltz-1 and Protenix all
report it. _Carries:_ the unit AF3-class physical validity is argued in.
_(PoseBusters V2 is a benchmark-set revision, not a separate publication;
map-only.)_

**AlphaFold2** introduced three self-estimates and published the fit between
each and the quantity it estimates. **pLDDT** guesses its own lDDT, per residue;
**pTM** guesses its own TM-score for the whole prediction; **PAE** is a matrix
rather than a score, predicting in ångströms how far off each residue pair will
land.

**AlphaFold-Multimer** added the interface versions, computed over interchain
residue pairs only: **ipTM**, which scores the interface rather than the chains,
and the **pAE / iPAE** reduction of the PAE matrix that gives the canonical
criterion its `< 10`.

**ipSAE** — `ipsae` · `10.1101/2025.02.10.637595` · **backbone** — restricts
ipTM to the well-predicted interchain pairs, which removes its dependence on how
the input was trimmed. _Carries:_ the unit the design half has converged on —
Germinal (§5) reports its threshold and the Overath meta-analysis (Table B)
scores designs with it.

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

______________________________________________________________________

# §1 — AlphaFold, and the open co-folding cluster

Prediction only. The forward problem — sequence / chemical input → 3D structural
state — and the reference every later section is defined against.

_Why it opens:_ AlphaFold is the elephant in the room — everything later
reproduces it, reacts to it, or replaces its evolutionary input, so the review
cannot begin anywhere else without the reader waiting for it. The open
reproductions join their pole here rather than getting sections of their own,
since neither has a design descendant to follow.

## The AF2 pole — AlphaFold2, and its open reproduction

- **AlphaFold2** — `alphafold2` · `10.1038/s41586-021-03819-2` · **backbone** —
  single-chain predictor at experimental accuracy, and the model that cashed the
  MSA-as-coevolution bet. _Carries:_ three facts the review is built on. The
  anatomy beat's **Stage 1** — trunk, distogram, coevolution wager — is AF2's
  design, and every co-folder in §3, §4, §6 and §8 is a variation on it. Its
  **single regression pass** is the structure stage everything after it
  replaced. And because the whole network is differentiable, it is the **only
  predictor a design loop can invert without choosing an attachment point** —
  the fact §5 is built on and the reason BindCraft exists. It is also the
  standard post-hoc filter across §2–§4 and §6: the review's first model and its
  most-used critic. _Against:_ the CASP14 field it displaced — which is why the
  coevolution bet is treated as settled rather than argued, and why every later
  contrast in the review is drawn with AF2 rather than with anything before it.
  _Caveat:_ it is weakest run single-sequence, which its own paper documents —
  the regime §5 then operates it in. _Collision:_ the anatomy beat owns the
  CASP14 margin and the statement of the bet; this entry owns the three
  consequences above.
- **AlphaFold-Multimer** — `alphafold_multimer` · `10.1101/2021.10.04.463034` ·
  **backbone** — AF2 retrained on complexes, and the complex predictor the
  review actually runs on: §5 does not invert AlphaFold2, it inverts this. Kept
  despite the pre-2025 rule under the active-lineage exception. _Carries:_
  **ipTM**, the unit half the review's numbers are denominated in — load-bearing
  for §2–§6 and for both benchmarking units, not only §5. Every "the field's
  standard filter" claim resolves to a metric this paper defined. _Against:_ AF2
  itself. It is the evidence that complex prediction needed its own training
  rather than following from single-chain accuracy — which is what makes the
  binder problem a distinct problem and not a corollary of folding. _Caveat:_
  never peer-reviewed. The field's most-used complex predictor has no journal
  version — a disclosure gap of a different kind from §8's.
- **OpenFold** — `openfold` · `10.1038/s41592-024-02272-z` · **mention** —
  AlQuraishi Lab's open retraining of AlphaFold2, and the source of the
  distillation set Boltz-1 trains on.
  [GitHub](https://github.com/aqlaboratory/openfold)

## The AF3 pole — AlphaFold3, and its open reproduction

- **AlphaFold3** — `alphafold3` · `10.1038/s41586-024-07487-w` · **backbone** —
  the generalization from single chains to arbitrary complexes of proteins,
  nucleic acids, ligands and ions, and the architecture the open lineages
  reproduce. _Carries:_ the review's second structural fact — replacing AF2's
  structure module with **diffusion** broke end-to-end differentiability, and
  the three answers to that one decision (attach to the trunk, attach to the
  confidence heads, shorten the trajectory) are what §2, §5 and §6 disagree
  about. It also carries the openness thread's opening: closed weights are the
  stated motivating gap behind Boltz-1, Protenix and OpenFold3, so §3 and §6
  exist as answers to this paper. And it opens the **seed-budget** thread: its
  antibody-antigen gain is reported from predictions top-ranked over **1,000
  seeds** rather than the usual 5, with quality still climbing at 1,000 — the
  behaviour Protenix-v1 (§6) reproduces in an open model and Protenix-v2 then
  collapses back to 5 seeds. _Against:_ AF2, on both counts — more modalities,
  at the cost of the property §5 depends on. The review's central trade, stated
  by the same lab in two papers. On the ligand half it is measured against
  classical docking instead: on PoseBusters' 428 structures it beats Vina and
  RoseTTAFold All-Atom while taking no structural input, where the docking tools
  are handed the solved pocket. _Caveat:_ diffusion brought failure modes AF2
  did not have, and this paper's own limitations section is where the review's
  physical-validity thread starts. Sampled coordinates can be chemically
  impossible — a 4.4% chirality violation rate on PoseBusters **after** a
  chirality penalty is added to the ranking, plus clashes that ranking reduces
  without eliminating — and "PB-valid" enters the literature here as the test
  for it. Generation also hallucinates order into disordered regions, which AF3
  answers by cross-distilling from AF2 predictions. Two limits carry further:
  predictions are static PDB-like structures, not conformational ensembles, and
  accuracy still falls with MSA depth exactly as AlphaFold-Multimer's does — the
  dependence §7 sets out to remove.
- **OpenFold3** — `openfold3` · `10.5281/zenodo.17485509` · **meat** —
  Apache-2.0 AF3 reproduction released with weights, training code and training
  data. _Carries:_ the far end of the openness axis. Boltz-1's openness is a
  downloadable model; OpenFold3 also releases the full training corpus —
  including its reproduction of AF3's MGnify-based 13M-sequence distillation set
  — making it the only co-folder in the review that can be retrained from
  scratch rather than only run. Downloadable and reproducible are different
  claims, and §8 weighs the closed systems against the second one. _Against:_
  AlphaFold3, which it targets bitwise. _Caveat:_ a software release, not a
  publication — its benchmark claims are self-reported, and the one technical
  report covers the superseded preview2 weights rather than the current
  OpenBind-0 default. [GitHub](https://github.com/aqlaboratory/openfold-3)

# §2 — RoseTTAFold → RFdiffusion

The Baker Lab / IPD line, kept whole: the predictors, the generative models
fine-tuned from them, the sequence-design stage the whole field borrowed, and
the modality arms and refinement stage built on top of those.

_Why it is second:_ it is the one lineage a reader can follow end to end —
prediction, the generative turn, inverse folding, antibodies, macrocycles,
gradient optimization, all inside one architecture family — and the one origin
in the review developed independently of AlphaFold.

**Section-defining fact:** it is the only lineage still shipping both tracks.
Its early predictors have left the conversation — nothing published since 2024
benchmarks against RF1 or RFAA, and the recent co-folding papers do not mention
them — while as _generators_ those same networks remain the reference the whole
field cites. But the predictor track never stopped: **RF3 (2025) is current**,
benchmarks directly against AF3, Boltz-2 and Chai-1, and is what RFOptimization
takes its gradients from.

_The two tracks' names collide:_ **RF3** (RoseTTAFold3) is the predictor,
**RFdiffusion3** (RFD3) the generator — siblings, not two versions of one model.
Both diffuse, but RF3 denoises coordinates for a **known** sequence while RFD3
invents a backbone with the sequence **unknown**, which is why RFD3 is followed
by ProteinMPNN and RF3 is not.

## The predictors — RF3, and the line behind it

- **RoseTTAFold3 (RF3)** — `rosettafold3` · `10.1101/2025.08.14.670328` ·
  **meat** — the lineage's current all-atom predictor, AF3-class with a
  diffusion structure stage, BSD with weights, benchmarked directly against AF3,
  Boltz-2 and Chai-1. _Carries:_ the evidence for the section-defining fact —
  this lineage never stopped shipping predictors — and it is the model
  RFOptimization takes its gradients from, so the review's one gradient
  optimizer that keeps the sequence discrete runs on something it can cite.
  _Carries:_ also the learned-features answer to AF3's physical-validity problem
  — more ligand chiral centres correct than AF3 or Boltz-2 without guidance,
  with the argument that Boltz-1x's inference-time steering _"may shift the
  network outside the training distribution"_. One clause, because it is an
  implementation difference rather than a fork in the field.
- **RoseTTAFold All-Atom (RFAA)** — `rosettafold_all_atom` ·
  `10.1126/science.adl2528` · **mention** — all-atom generalization published
  two months _before_ AF3 and independently of it: the date that makes the two
  origins a fact rather than a framing.
- **RoseTTAFold2 (RF2)** — `rosettafold2` · `10.1101/2023.05.24.542179` ·
  **meat** — RF1 rebuilt with AF2's ideas added one at a time, to find out which
  of them the accuracy actually needs. _Carries:_ the test behind §2's
  organizing fact. FAPE loss, recycling, distillation and depth mattered; AF2's
  two signature modules — invariant point attention and triangle attention — did
  not, and RF2 reaches AF2's accuracy on monomers and AF2-Multimer's on
  complexes without either, scaling better past 1,000 residues. Its conclusion
  is the one §2 is built on: _"excellent performance can be achieved with a
  broader class of models"_ than the AF2 architecture nearly everything else
  re-uses. Its discussion also gives the lineage's own reason why its predictors
  fine-tune into generators — a 3D track running all the way to the input lets a
  design constraint be encoded as coordinates rather than as pairwise distances.
  It is RFAA's base network and the network RFpeptides adds cyclic positional
  encoding to. _Caveat:_ never peer-reviewed, three years on.
- **RoseTTAFold (RF1)** — `rosettafold` · `10.1126/science.abj8754` ·
  **backbone** — three-track (1D/2D/3D) network developed independently of AF2;
  complex prediction emerged untrained from two-segment cropping. _Carries:_
  §2's organizing fact — the one architecture in the review not derived from
  AlphaFold, which is what makes this lineage a second origin rather than a
  fork. It is also the network RFdiffusion is fine-tuned from, so the identity
  beat's claim has its historical proof here. _Against:_ AF2, contemporaneously
  and on the same problem — the comparison that establishes there were two
  independent routes to the same result, and the reason the review has two
  lineage origins to place rather than one. _Caveat:_ as a _predictor_ it has
  left the conversation; nothing published since 2024 benchmarks against it. Its
  standing in the review is as an ancestor.

## The generators — RFdiffusion3, and the line behind it

- **RFdiffusion3 (RFD3)** — `rfdiffusion3` · `10.1126/science.aeh2982` ·
  **meat** — transformer-based all-atom diffusion, adopting AF3's
  non-equivariant approach. _Carries:_ the lineage's own break with Level 0 —
  unlike RFdiffusion 1/2 it is not fine-tuned from a predictor but trained from
  scratch, so the claim the identity beat rests on is weakest in the lineage
  that established it.
- **RFdiffusion2 (RFD2)** — `rfdiffusion2` · `10.1038/s41592-025-02975-x` ·
  **mention** _(inherits RF1)_ — atom-level enzyme active-site scaffolding from
  functional-group positions, sequence-agnostic.
- **RFdiffusion (RFD1)** — `rfdiffusion` · `10.1038/s41586-023-06415-8` ·
  **backbone** _(inherits RF1)_ — the generative turn itself, and the most-cited
  design model in the corpus. SE(3)-equivariant frame diffusion, fine-tuned from
  a predictor, filtered by AF2 pAE. _Carries:_ three beats. **The identity
  beat's claim** in its cleanest historical form — a predictor fine-tuned into a
  generator, with nothing else changed. **The coupling beat's Level 1**, the
  pipeline this paper established (backbone, then ProteinMPNN, then AF2 judges)
  which every section from §3 to §6 either runs or argues with. And its
  **verdict on hallucination** — the technique §5 runs on stronger predictors —
  which sent gradient design quiet for two years. _Against:_ hallucination
  through RoseTTAFold — the Baker lab's own predecessor, beaten on the Baker
  lab's own benchmark. RFOptimization below reopens exactly that comparison,
  which is why this lineage ends on a return to what it abandoned. _Caveat:_ its
  "in silico success" criterion is a confidence-metric filter, so the
  designs-tested numbers attached to it are in-silico rather than measured.
  [GitHub](https://github.com/RosettaCommons/RFdiffusion)

### The sequence stage — inverse folding

**ProteinMPNN** · `proteinmpnn` · `10.1126/science.add2187` · **backbone** —
**LigandMPNN** · `ligandmpnn` · `10.1038/s41592-025-02626-1` · **meat**

A generator makes geometry, not sequence — two separate problems — and these two
write the sequence onto the backbone the generator produced. ProteinMPNN is the
autoregressive message-passing network that does it for a fixed backbone;
LigandMPNN is the same network conditioned on ligand and nucleic-acid context:
the all-atom extension of the stage, and the variant RFOptimization's cycling
move runs alongside ProteinMPNN. They sit under the generators because that is
what they were built for, but they are not this lineage's alone: **ProteinMPNN
is the review's one piece of universally shared machinery**, run by §2–§6 across
nine labs and both coupling levels.

_Carries:_ the middle stage of the coupling beat's Level 1 — this is the paper
that stopped sequence design being the bottleneck. Every "generate, then filter"
pipeline in the review has this step in it, usually unremarked, and §5 exists
precisely because Level 2 removes it. _Against:_ AlphaDesign, which substitutes
a diffusion model of its own and benchmarks it as comparable — the corpus's one
alternative, and the evidence that the field's dependence is adoption rather
than necessity. _Caveat:_ ProteinMPNN's own paper notes that sequence recovery,
the metric it is scored on, may not track whether the sequence folds.
[GitHub](https://github.com/dauparas/ProteinMPNN)

## The arms — antibodies, macrocycles, and the optimizer

- **RFantibody** — `rfantibody` · `10.1038/s41586-025-09721-5` · **meat**
  _(inherits RFdiffusion)_ — the lineage's antibody arm: a fine-tuned
  RFdiffusion designing VHHs, scFvs and full antibodies against chosen epitopes.
  _Carries:_ the concession that **the screen remains**. It pairs design with
  yeast-display library screening and says so, which makes it the honest
  baseline the identity beat's collapsing-budget table is measured against — and
  the paper §3, §4 and §5 cite when claiming they no longer need library
  selection. _Against:_ immunization and random library screening, which it
  states cannot be aimed at a chosen epitope. That framing is what the whole
  design half inherits. _Collision:_ the identity beat quotes its statement of
  the epitope gap; this entry owns the concession, not the gap.
- **RFpeptides** — `rfpeptides` · `10.1038/s41589-025-01929-w` · **meat**
  _(inherits RFdiffusion)_ — the lineage's macrocycle arm: RFdiffusion and RF2
  extended with a **cyclic relative positional encoding** so the generated chain
  closes head-to-tail; sequences from ProteinMPNN, filtered by refolding with
  AfCycDesign — AlphaFold2 given a cyclic offset so the chain reads as closed,
  and where the cyclic thread starts (§5) — and by Rosetta interface metrics.
  _Level 1._ _Carries:_ the low end of the identity beat's budget — binders
  against every target from fewer than twenty synthesized designs each, with
  crystal structures — and the cyclic thread's **open** method. _Against:_
  Latent-X1 (§8), which designed against these targets and epitopes and
  re-synthesized these binders to measure in its own assays. The corpus's only
  third-party wet-lab comparison of two design methods runs through this entry.
  _Collision:_ that head-to-head is argued under Table B, where its limits
  belong.
- **RFOptimization (RFO)** — _see §5_ — the lineage's optimizer: training-free
  refinement of finished designs, with gradients taken from RF3 above.
  _Carries:_ this lineage's completion of the stack — predict, generate,
  inverse-fold, optimize, filter, all from one group — and the Baker lab
  returning, on its own AF3-class predictor, to the technique RFdiffusion
  displaced above. _Caveat:_ **in silico only.** No wet-lab validation, no
  designs-tested denominator, no Table B row — the ceiling on how far the review
  leans on it.

# §3 — Boltz

Diffusion, stated outright: BoltzGen is _"a single all-atom diffusion model
capable of performing both structure prediction and protein design"_ — Level 0
in its cleanest published form. The section also carries the **trained-critic**
refinement to Level 1, the **open→closed fork** the disclosure beat and §8 turn
on, and the corpus's only affinity model.

_Why it precedes Chai:_ this lineage publishes the mechanism of its generator
and §4's does not, so the reader meets a stated Level-0 design model before
meeting the strongest one the review cannot inspect.

**The fork** (argued in the disclosure beat, evidenced here): Boltz-1, Boltz-2
and BoltzGen are MIT with weights released; **BoltzProt-1 is API-only and
commercial**, yet still publishes a paper and wet-lab numbers.

- **Boltz-1** — `boltz1` · `10.1101/2024.11.19.624167` · **backbone** — the
  first fully open (MIT) AF3-class co-folder, and the paper that made AF3's
  architecture something the rest of the field could build on. _Carries:_ the
  openness thread's opening. §5's BoltzDesign1, §3's own BoltzGen and a good
  part of the design literature exist because these weights were downloadable —
  and the thread it opens is the one the disclosure beat closes on this same
  lineage. **Boltz-1x** adds Feynman-Kac inference-time steering, the corpus's
  first answer to AF3's physical-validity problem. _Against:_ AlphaFold3, which
  it reproduces and releases. The comparison is not about accuracy; it is about
  what a downloadable model makes possible downstream, and §3, §5 and §6 are the
  evidence. _Collision:_ RF3 (§2) owns the objection to inference-time steering
  and the learned-features alternative to it.
  [GitHub](https://github.com/jwohlwend/boltz)
- **Boltz-2** — `boltz2` · `10.1101/2025.06.14.659707` · **backbone** — adds a
  binding-affinity module and the corpus's most complete conditioning system;
  the refolding oracle BoltzGen and BoltzProt-1 filter with. _Carries:_ the
  corpus's only affinity prediction, and its boundary — average Pearson 0.66 on
  the FEP+ four-target subset at over 1,000× less compute, and protein-ligand
  only, trained on single-protein assays, which is why the conclusion's gaps can
  say no system here predicts protein-protein affinity. _Against:_ FEP, the
  corpus's one comparison against a method that is not learned. _Caveat:_
  temporal leakage in its benchmark numbers, flagged by ESMC, Protenix-v1 and
  Protenix-v2; structure accuracy that _"does not significantly deviate"_ from
  its predecessors', so the oracle §3's design models filter with is Boltz-1
  plus conditioning; and Pearson above 0.55 on three of eight blinded industrial
  assays, weak on the other five.
- **BoltzGen** — `boltzgen` · `10.1101/2025.11.20.689494` · **backbone**
  _(inherits Boltz)_ — unified generative design across proteins, peptides,
  nanobodies, antibodies and small molecules, filtered by refolding with
  Boltz-2, released MIT with weights, data and training code. _Level 1,
  confidence-as-critic._
  - _Carries:_ the identity beat's claim in its published form. RFdiffusion
    demonstrated it historically by fine-tuning; BoltzGen states it as a design
    principle — _"a single all-atom diffusion model capable of performing both
    structure prediction and protein design"_ — and is the cleanest Level 0 in
    the corpus. The claim is evidenced rather than asserted: the same weights
    that design also fold, matching Boltz-2 on Boltz-2's own test set. And it
    carries the corpus's broadest wet-lab evidence for that claim: eight
    campaigns over 26 targets, from disordered proteins to small molecules. On
    nine **novel** targets — nothing in the PDB with over 30% identity in a
    bound context — 15 or fewer designs per target give nanomolar binders for 6
    of 9, in both nanobody and miniprotein format. On five established targets,
    4 of 5 in each format, with picomolar hits on PDGFR. These are the rates
    BoltzProt-1's filter is swapped into.
  - _Against:_ BoltzProt-1 below, which beats it by changing only the critic.
    The two are the same generator, which is what makes the comparison worth the
    section.
  - _Caveat:_ two the paper discloses itself. Generation diversity collapses for
    binders of length 73–76, where it samples ubiquitin almost exclusively — a
    memorization artefact of ubiquitin's 900+ PDB entries. And an earlier
    version, BoltzGenv0, mis-assigned fixed binder residues to the target, so
    refolding could only recapitulate the design and the ranking scores carried
    no filtering power: hit rates of 0/7 on two targets where the fixed version
    gets 1/7 and 7/7. That is an accidental ablation of the critic with the
    generator untouched, and it points the same way as BoltzProt-1. It also
    declines the framing the rest of the field uses — binder design is not
    _"zero-shot"_ or _"plug-and-play"_, and users are told to inspect structures
    and rerun.
- **BoltzProt-1** — `boltzprot1` · `10.64898/2026.06.23.733997` · **backbone**
  _(inherits BoltzGen)_ — a refined BoltzGen ranked by **BoltzPPI**, a critic
  trained to answer "will this bind" rather than a confidence head reused as
  one. _Level 1, trained-critic regime._ _Carries:_ two beats at once. It is the
  **trained-critic** half of the coupling beat — changing only the filter
  roughly doubles the confirmed-binder rate with the generator untouched, the
  corpus's cleanest evidence that hit rate lives in the critic. And it is the
  corpus's first critic trained against experimental outcomes rather than a
  confidence metric reused as a filter. It also splits _screening hits_ from
  _confirmed binders_, the definition problem the identity beat and Table B
  inherit. _Against:_ BoltzGen, its own unmodified generator — the only
  controlled comparison of a filter in the corpus, and the reason the claim is
  not confounded. _Caveat:_ API-only, no weights — the closed half of the fork
  above, so the result cannot be independently reproduced. _(BoltzPPI is the
  critic itself, no separate publication — resolves to the `boltzppi` keyword on
  this entry.)_
- **BoltzDesign1** — _see §5_ — inverts the Boltz predictor for binder design.
  _Level 2_, beside BindCraft, whose loop it reuses at a different attachment
  point.

# §4 — Chai

Diffusion co-folding, then the strongest antibody-design result in the corpus
from a generator whose mechanism is never stated.

- **Chai-1** — `chai1` · `10.1101/2024.10.10.615955` · **backbone** —
  AF3-derivative carrying **both** of the anatomy beat's Stage-1 inputs: an MSA
  track and a protein-LM track, either usable alone; adds experimentally
  grounded constraint features (pocket, contact, docking), worth a
  double-digit-point gain when supplied. _Carries:_ the qualifier the anatomy
  beat needs — the MSA/PLM divide is a switch here, not a commitment, which is
  why the review can say the divide is not a wall, and the hinge §7 completes by
  removing the MSA entirely. On antibody-protein interfaces the switch costs
  nothing: single-sequence Chai-1 matches full-MSA Chai-1 and both beat AF2.3
  run with MSAs, which the paper puts down to antibodies' weak evolutionary
  signal — and which is why Chai-2 below can design them without an MSA.
  _Against:_ AlphaFold3, matched on PoseBusters, 77% ligand RMSD success against
  76%. _Caveat:_ weights are non-commercial and commercial use runs through the
  free web server — the middle of the openness axis, not Boltz's MIT. And the
  paper could not benchmark against AF3 or ESM3 at all _"due to commercial use
  restrictions"_, falling back to CASP15 against AF2.3: the disclosure limit
  reaching into a published methods section.
  [GitHub](https://github.com/chaidiscovery/chai-lab)
- **Chai-2** — `chai2` · `10.1101/2025.07.05.663018` · **backbone** _(inherits
  Chai-1, via a "Chai-1d" design prototype)_ — zero-shot antibody design at
  roughly one hit in six, on twenty or fewer designs per target, across dozens
  of targets. _Carries:_ the low end of the identity beat's collapsing budget,
  and the characterisation the table's top row quotes — that prior work needed
  _"thousands to millions of designs to reliably identify hits"_. It is the
  result the field measures antibody design against. _Against:_ library
  screening, explicitly and by the number. The paper's framing — zero-shot, no
  affinity maturation, small plate assays — is the sharpest statement in the
  corpus that the screen has been removed, and it is exactly the claim
  RFantibody (§2) declines to make. _Caveat, and the section's finding:_ the
  paper describes only the _folding_ submodule (Chai-2f, _"a similar
  architecture as Chai-1"_). **The generative mechanism is never stated.** The
  strongest antibody result in the corpus is the one the review can say least
  about — §8's argument arriving early, inside a lineage rather than in the
  coda.
- **Chai-3 (2026)** — high-throughput commercial 3D foundation model, no
  publication. _see §8_ [platform](https://lab.chaidiscovery.com/)

# §5 — Design by backpropagation

The first designs the field made by running a predictor backwards. Each system
here takes a structure predictor it did not train, picks a point inside it to
backpropagate from, and bolts on its own machinery for turning that gradient
into a sequence — the loss, the representation the sequence is held in while it
is still being designed, the schedule that hardens it into one-hot, and whatever
runs afterwards to tidy the result. Nothing in the assembly was built for the
other parts: someone else's predictor, someone else's sequence model, a loop
written by hand.

_Why it comes before §6 and §7:_ §6 ships the predictor and the design loop as
one product, §7 collapses them into a single model. The reader should meet the
parts bolted together before seeing them fused.

## The loop, on AlphaFold2

The canonical form, on the one predictor a design loop can invert without
choosing an attachment point: the library everything here calls, the smallest
modification anyone made to it, and the system that fills out every stage.

- **ColabDesign** — `colabdesign` · `10.5281/zenodo.13309080` · **mention** —
  the bolt-on half, as a library: input preparation for AlphaFold2, losses on
  its outputs, the gradient path back to the input sequence, and ready-made
  annealing schedules (`design_3stage`). Every system below runs on it except
  BoltzDesign1, which is why their loops match each other down to the stage
  boundaries. _(No paper; a versioned software release.)_
- **AfCycDesign** — `afcycdesign` · `10.1038/s41467-025-59940-7` · **meat** —
  the earliest loop here, and the smallest modification: AlphaFold2's relative
  positional encoding made cyclic, so the network reads a chain as closed
  head-to-tail, with ColabDesign's stock protocol run on top. Its macrocycles
  are where §2's cyclic thread starts.
  - _Gradient:_ whole network. Categorical cross-entropy between predicted and
    desired distogram for fixed-backbone redesign; for hallucination, the sum of
    1 − pLDDT, PAE/31 and a contact term rewarding interacting residues. On
    complexes the cyclic offset is applied to the peptide chain alone, the
    target keeping default encodings.
  - _Sequence update:_ ColabDesign's three-stage protocol unmodified, continuous
    representation annealed to one-hot. The paper changes the predictor, not the
    optimizer — which is the point: the loop was already a library call.
  - _Afterwards:_ 48,000 hallucinated models per length for 7–10 residue
    macrocycles, clustered on torsion bins and filtered on pLDDT and Rosetta
    energy landscapes. Eight crystal structures, all within 1.0 Å of their
    design model.
  - _Caveat:_ its binders do not come out of the loop. Hallucination makes
    monomeric scaffolds; the MDM2 and Keap1 binders are known motifs grafted
    onto those scaffolds, sequences from ProteinMPNN and Rosetta, filtered on
    AfCycDesign confidence — Level 1 downstream of a Level-2 scaffold. The paper
    names de novo hallucination of binders as future work.
- **BindCraft** — `bindcraft` · `10.1038/s41586-025-09429-6` · **backbone** —
  AlphaFold2-multimer, gradient taken through the whole network.
  - _Gradient:_ position-specific errors from a loss over AF2's own outputs
    (confidence terms, plus optional helicity and radius-of-gyration terms)
    backpropagated through the multimer weights into an *L*×20 error gradient
    over amino-acid choices. The five trained model weight sets are swapped at
    random between iterations so a trajectory cannot overfit one of them. The
    target is repredicted every iteration rather than held fixed, so backbone
    and side chains mould to the binder — target Cα r.m.s.d. of 0.5–5.5 Å across
    designs.
  - _Sequence update:_ four stages. 75 iterations in continuous logit space on
    (1 − _λ_)·logits + _λ_·softmax(logits/_T_) with _λ_ ramped over the run; 45
    iterations on softmax probabilities with the temperature, and the learning
    rate with it, decayed to 0.01; 5 iterations of straight-through estimation,
    the model seeing one-hot while the gradient flows through the softmax; 15
    iterations of discrete search, sampling 0.05·_L_ mutations per step from the
    previous stage's distribution and fixing the best. Trajectories with poor
    confidence are killed at iteration 50.
  - _Afterwards:_ ProteinMPNN soluble weights redesign everything beyond 4 Å of
    the interface, the complex is repredicted with AF2 monomer weights in
    single-sequence mode, and Rosetta relaxes and scores the interface.
    300–3,000 trajectories per 100 designs passing filters.
  - _Carries:_ the loop in its fullest form — the other entries here vary one of
    its parts — and it is the system PXDesign-h (§6) benchmarks against.
  - _Caveat:_ AF2 runs single-sequence on the designed chain, off-distribution
    for that model, which the annealing and the five-model swap appear to
    compensate for. Its own paper adds that the ipTM it ranks on predicts
    _whether_ a design binds but not _how tightly_.

## Where the gradient stops when the predictor diffuses

A diffusion structure stage cannot be unrolled for a gradient, so neither of
these takes one through it. Both read the loss off the trunk's distogram and the
confidence heads instead — the same wall, two escapes — and both have to argue
that optimizing the distribution the sampler draws from is optimizing the
structure.

- **BoltzDesign1** — `boltzdesign1` · `10.1101/2025.04.06.647261` · **meat** —
  the same arrangement on Boltz-1 (§3), gradient taken from the trunk only.
  - _Gradient:_ a stop-gradient is placed on the diffusion module and the loss
    is read from the Pairformer's distogram — inter-chain and intra-chain
    contact losses over its 64 distance bins — optionally with the confidence
    module in the loop as well, gradients running confidence → Pairformer →
    sequence. The distogram _"represents the probability distribution of atomic
    distances that the diffusion model later samples from"_, so this optimizes
    the distribution rather than one sampled structure. The paper checks the
    substitution: on BindCraft's own 212 binders, Pairformer contacts match the
    diffusion module's with P@K > 0.5 for 76% of designs, and contact loss
    tracks pLDDT and inter-pAE. For nucleic-acid targets it does not, and the
    confidence module carries the loss instead.
  - _Sequence update:_ BindCraft's four stages, reimplemented, with a softmax
    warm-up first because raw logits start off-distribution for this model.
  - _Afterwards:_ LigandMPNN optionally redesigns the surface with interface
    residues fixed, or initializes the logits before optimization.
  - _Caveat:_ it shares senior authors with BindCraft, so the two are one
    research programme porting one method, not two independent data points.
- **RFOptimization (RFO)** — `rfoptimization` · `10.64898/2026.09.04.749184` ·
  **meat** — the odd one out, twice over: it never relaxes the sequence, and it
  does not design from scratch. It takes a finished design and improves it,
  using gradients from RF3 (§2) only to rank point mutations on a sequence that
  stays discrete throughout.
  - _Gradient:_ the escape BoltzDesign1 did not take — the objectives are
    written as differentiable surrogates on the distogram and the confidence
    heads — iPAE, pLDDT, iPTM — whose path back to the input stays open when the
    coordinate path does not.
  - _Sequence update:_ mutation logits are built from the negative normalized
    gradient, the residue already present penalized so a proposal is a real
    substitution; the proposal is trimmed to a single position and accepted or
    rejected by Metropolis–Hastings under an annealed temperature, with
    gradients recomputed after each acceptance. The persistent state is always a
    chemically valid sequence, on the stated grounds that a continuous
    relaxation is an attack surface the optimizer will exploit. Every other
    system in §5–§7 relaxes it.
  - _Second move:_ with equal probability the optimizer instead cycles — the
    current sequence folded by Boltz, redesigned by LigandMPNN — so
    gradient-guided edits and structure-conditioned resampling interleave, and
    AF3 is held out as an independent check. Agreement with a single predictor
    is treated as the failure mode itself, and this is the only system in the
    review answering that in the optimizer rather than in the filter.
  - _Against:_ BindCraft, which it reports beating on cost per filter-passing
    design.
  - _Caveat:_ **in silico only.** No wet-lab validation, no designs-tested
    denominator, no Table B row — the ceiling on how far the review leans on it.

## A second prior on the sequence

Confidence alone does not say a designed sequence is a plausible protein, so
both of these add a language model to say it. The difference is whether that
prior moves: a live gradient merged with the structural one, or a fixed bias the
optimizer walks under.

- **Germinal** — `germinal` · `10.1038/s41587-026-03187-0` · **backbone** —
  AlphaFold-Multimer, whole network, with a second gradient merged into the
  first. Antibody CDRs on a user-supplied framework.
  - _Gradient:_ two objectives merged into one update direction — AF-M's
    structural confidence, and IgLM, an antibody language model, scoring how
    natural the CDR sequence is. The merge is a weighted sum, MGDA, or a
    weighted PCGrad. Framework positions are pinned to their one-hot encodings
    and only CDRs are designed; the framework structure is given to AF-M as a
    template with every CDR atom masked, so the prediction is anchored without
    the loops being biased toward the framework's natural ones. A paratope loss
    keeps contacts on the CDRs rather than the framework.
  - _Sequence update:_ a PSSM — initialized to uniform noise, Gumbel noise
    around the framework, or zeros — taken through a logit phase, a softmax
    phase, then 10 semigreedy iterations sampling five candidates each and
    fixing the best joint score. AF-M reads the PSSM directly; IgLM needs
    discrete tokens, so a straight-through estimator hands it one-hot.
  - _Afterwards:_ AbMPNN redesigns non-interface CDR residues; filtering and
    ranking leave 43–101 designs per antigen for testing.
  - _Carries:_ the arrangement where the sequence prior is a live gradient
    rather than a fixed bias, which §7 reaches with one model instead of two.
  - _Caveat:_ its nonbinders clear the ipSAE threshold alongside its binders, so
    that filter does not separate them — the conclusion's fifth gap. Its antigen
    structures are AF3 predictions, and it states that how far design success
    depends on antigen-model quality is open — the conclusion's
    structure-availability gap.
  - **OpenGerminal** — `opengerminal` · `10.64898/2026.06.25.734527` ·
    **mention** — Apache-2.0 reimplementation on an open stack.
- **mBER** — `mber` · `10.1101/2025.09.26.678877` · **meat** — Manifold Bio's
  VHH designer: AlphaFold-Multimer, whole network, loop taken from ColabDesign
  unchanged. What it adds is not in the gradient but in what the model is
  handed.
  - _Gradient:_ ColabDesign's `design_3stage` with BindCraft's pAE-centred
    losses, modified only to template target and binder separately while masking
    their inter-chain contact map.
  - _Sequence update:_ the design logits are descended as usual, but ESM2 is run
    once over the masked VHH framework and its logits are added as a **fixed
    bias** at every step, under their own temperature, with the mixing parameter
    rising and the sampling temperature falling over the run. The prior never
    moves; it tilts the space the optimizer walks.
  - _Templates:_ a VHH framework structure from NanoBodyBuilder2 and the target
    truncated around a hotspot, both supplied as templates, with no MSA at all.
    The paper ablates them: the sequence prior alone gives a VHH-ish fold with
    disordered loops, the template alone is insufficient, and the two together
    give confident docked folds. This is its answer to the off-distribution
    problem BindCraft handles with annealing.
  - _Afterwards:_ designs are refolded by an AF-M model initialized with the
    held-out weight set, three recycles, and scored on ipTM.
  - _Carries:_ scale and target choice. Million-design campaigns against
    hundreds of targets with hotspots drawn at random from exposed surface
    residues — the corpus's only campaign that did not choose its own epitopes,
    and the control for every hit rate in Table B. Epitope choice alone moves
    one target's rate from 0.4% overall to 7.5% at its best hotspot.
  - _Caveat:_ its hits are phage-display enrichments — screening hits, not
    confirmed binders, with no affinity quantification.

# §6 — Protenix

The first full assembly, and the lineage that made §5's technique affordable.
AlphaFold3-style models decode structure in a 200-step diffusion pass that
cannot be backpropagated through; Protenix replaces it with a **2-step ODE
sampler**, so a Level-2 gradient runs end to end through the whole predictor
instead of stopping at a trunk. On that one change the lineage ships a diffusion
arm and a hallucination arm as two modes of one product — the couplings of §1–5
stop being alternatives and become configuration, chosen per target — then
benchmarks them against §5's own systems on an instrument it built and published
itself. Boltz (§3) ships one coupling and varies the critic under it; here both
couplings are configuration, and the ruler is part of the delivery.

- **Protenix-v1** — `protenix_v1` · `10.64898/2026.02.05.703733` · **backbone**
  — ByteDance Seed's open all-atom model, the second answer to AF3's closed
  weights after Boltz-1, and the predictor every arm below attaches to.
  _Carries:_ three things. The **matched-conditions** framing — same training
  cutoff, model scale and inference budget as AF3 — which makes "matches AF3" a
  checkable claim rather than a leaderboard position, and whose verdict is
  split: ahead of AF3 on protein-protein and antibody-antigen interfaces, behind
  it on protein-ligand and protein-DNA. The **inference-time scaling** result —
  accuracy rising roughly log-linearly with sampling budget, a behaviour AF3 has
  and prior open models largely did not — which is the baseline v2's efficiency
  claim below is measured against. And the **common-intersection critique** of
  FoldBench, which lands in Table A's defect column: models fail or run out of
  memory on different targets, so the published aggregates score each model on a
  different subset — Boltz-1 on 252 interfaces, Chai-1 on 251, 237 shared — and
  restricting to the shared set flips which of the two leads. Its own bootstrap
  puts the 95% CI of a single 5×5 run at 49.3–56.3% DockQ success, wider than
  the gaps such tables are read for. _Against:_ AlphaFold3, under conditions it
  holds fixed — same cutoff, same scale, same inference budget — which is what
  makes this the section's organizing fact: the open/closed accuracy gap is a
  resourcing difference, not an architectural one, and §6's design arms are
  built on a predictor that has shown it. _Collision:_ Boltz-1 (§3) owns the
  openness thread's opening, the argument that downloadable weights are what
  made the design literature possible; this entry owns the accuracy claim, and
  only under matched conditions. _Caveat:_ that claim covers the strict-cutoff
  model only; the variant recommended for applied use, Protenix-v1-20250630,
  trains past that cutoff and is not the one in the controlled comparison.
  [GitHub](https://github.com/bytedance/Protenix)
- **PXDesign** — `pxdesign` · `10.1101/2025.08.15.670450` · **backbone** — the
  section's reason for existing: the first system to ship **both couplings as
  two modes of one product**, chosen per target rather than argued over.
  Nanomolar hit rates of 20–73% on five of six targets, 2–6× AlphaProteo's.
  - **PXDesign-d** — diffusion arm, generating Cartesian coordinates from a DiT
    backbone rather than the SE(3)-equivariant or frame representations
    RFdiffusion and AlphaProteo use. _Level:_ 1 _(inherits Protenix)_.
  - **PXDesign-h** — hallucination arm. _Level:_ 2, continuous. _Attachment:_
    end-to-end through the **2-step ODE sampler**, which replaces the 200-step
    diffusion decoder and is what makes the gradient affordable — the attachment
    no §5 system could take. Sequences are optimized against an ensemble of five
    Protenix models resampled each step, BindCraft's five-weight-set defence
    against overfitting one critic, carried into this lineage.
  - _Carries:_ the composition claim — everything §1–§5 presented as competing
    answers appears here as configuration — and the **filter-ensembling
    finding**: Protenix and AF2-IG filters retain _different_ true positives
    with surprisingly little overlap, the other half of the coupling beat's
    critic-quality argument alongside BoltzPPI.
  - _Against:_ BindCraft and BoltzDesign1, benchmarked head-to-head. That is the
    evidence §5 is a real category rather than the review's own grouping, and it
    is the corpus's clearest instance of the field arguing about where a Level-2
    gradient should attach.
  - _Caveat:_ the head-to-head is run by the system being promoted, so it
    belongs in Table B's self-reported column like every other in-house
    comparison. Its own filtering analysis adds that confidence thresholds do
    not transfer across targets — gains on one target cost gains on another.
- **Protenix-v2** — `protenix_v2` · `10.64898/2026.04.10.717613` · **backbone**
  — the platform's current state: the predictor improved, and the design half
  carried from PXDesign's miniproteins to antibodies. _Level:_ 1 _(inherits
  Protenix)_.
  - _Prediction:_ 9–13 point antibody-antigen success gains over v1 at DockQ >
    0.23 across three benchmark collections, and the payoff of v1's scaling
    result — v2 at 5 seeds beats v1 at 1,000. It also finds the PoseBusters
    criterion itself incomplete (Table A): predictions pass it with twisted
    amides and flat sp3 centres, which is why PXMeter v1.1.0 adds planarity
    checks, and under the stricter criterion almost every model scores lower.
  - _Design:_ target-conditioned generation with epitope-specific and
    site-agnostic modes, across miniproteins, VHH, Fv and full mAb. Every
    antigen in its novelty-controlled panel produced a confirmed binder, at
    BLI-confirmed hit rates of 2–48%; on four GPCRs — small, flexible
    extracellular epitopes that conventional antibody discovery struggles with —
    16–88% in VHH-Fc and up to 50% in mAb, at 16–30 designs tested per target.
  - _Carries:_ the second independent demonstration that zero-shot antibody
    design works at a two-dozen-design budget, and the one that closes the
    disclosure gap Chai-2 leaves open — the mechanism is described and the
    predictor is downloadable. It extends the regime past soluble monomers to
    GPCRs and past VHH to full mAb, which is the review's evidence that the
    collapsing budget is a property of the field rather than of one lab's
    targets. It also independently replicates mBER's (§5) epitope finding, from
    a group that then chose its epitopes anyway — two epitopes on the same
    antigen give hit rates of 4% and 48%, after which the paper adopts Chai-2's
    practice of targeting native ligand-binding interfaces.
  - _Against:_ Chai-2 and BoltzGen, whose target-selection regimes it built its
    own panel out of — BoltzGen's 30%-identity low-homology monomers and
    Chai-2's novelty filter on SAbDab — so the comparison is in the panel rather
    than in a shared assay.
  - _Collision:_ Chai-2 (§4) owns the collapsing budget's low end and the claim
    that the screen has been removed; this entry owns its corroboration, its
    extension to a hard target class, and the open-mechanism contrast.
  - _Caveat:_ its targets were drawn from what was in stock for immediate assay
    and its epitopes were selected, the exact opposite of mBER's control, so
    these rates sit at the self-chosen end of Table B. It reports no
    head-to-head against Chai-2 because the overlapping targets were published
    in a different antibody format, and its rankers are compared against a
    single human expert on one target.
- **PXMeter** — `pxmeter` · `10.1101/2025.07.17.664878` · **meat** — ByteDance
  Seed's open evaluation toolkit and hand-curated PDB benchmark set, basis of
  the PXM family, benchmarking Chai-1, Boltz-1 and Protenix. v1.1.0 extends
  PoseBusters with sp2-planarity, amide-planarity and sp3-non-planarity checks —
  the fourth response in the physical-validity thread. _Carries:_ the fact that
  makes this section a platform rather than a model line. The lineage ships the
  predictor, both design arms **and** the instrument its competitors are
  measured on, so §6's numbers are partly its own measurements of other people's
  models. _Against:_ FoldBench (Tables A and B), the other multi-model
  prediction benchmark — and Protenix-v1's common-intersection critique of it is
  this group arguing for its own instrument, which the review states rather than
  adjudicates. _Caveat:_ its uptake is real but narrow — OpenDDE (§8) benchmarks
  on PXMeter-AB and follows its data protocol to curate its own set, and that is
  the only third-party adoption in the corpus.
  [GitHub](https://github.com/bytedance/PXMeter)

# §7 — ESM

**The analytical climax, and the section that closes the review's longest
thread.** Two things land here at once: the MSA/PLM divide opened in the anatomy
beat and followed since §1 resolves in favour of the language model, and the
coupling axis reaches its limit case — language model, folding head and design
loop are one system, with nothing left to compose.

_Why it comes last in the argument:_ §5 met Level 2 as a predictor with an
optimizer bolted on, §6 as one mode of a platform. Here it is not a technique
applied to a predictor at all. The escalation has nowhere further to go, which
is why §8 is a coda rather than a ninth step.

- **ESM-2 & ESMFold** — `esm2` · `10.1126/science.ade2574` · **meat** — the
  founding single-sequence predictor: structure emerges from masked-LM scaling
  alone, with no MSA and no templates at inference. Enabled the ESM Metagenomic
  Atlas (a database, out of scope). _Carries:_ the other half of the anatomy
  beat's Stage-1 divide. AlphaFold2 established that evolutionary depth is
  _retrieved_ at inference; this paper established that it can live in the
  weights instead — and the coupling beat's precondition for Level 2 depends on
  that alternative existing. _Against:_ AlphaFold2 with an MSA, which it did not
  match. That is the point: the trade was accuracy for independence, and §7
  exists because ESMC later closed the gap rather than because this paper won.
  _Caveat:_ the gap it traded away is real and was the standing objection to
  single-sequence prediction for three years; the review should state it rather
  than read the lineage backwards from its conclusion.
- **ESM-3** — `esm3` · `10.1126/science.ads0018` · **meat** — the lineage's
  generative turn: sequence, structure and function as three tracks of discrete
  tokens in one masked-token model, so any track can be prompted and any track
  generated. Trained at 1.4B, 7B and 98B parameters over 2.78 billion natural
  proteins. _Carries:_ the PLM instance of the background beat's identity — one
  set of weights predicts and generates, with no design head bolted on — and the
  evidence that ESM-2's accuracy trade was already closing before ESMC closed
  it: at 98B it beats ESMFold at single-sequence prediction, 0.880 against 0.861
  LDDT on CAMEO. Its esmGFP is the corpus's only wet-lab-confirmed de novo
  protein whose function is not binding — prompted from six chromophore
  residues, 58% identity to the nearest known fluorescent protein, bright on the
  plate reader. _Caveat:_ only ESM3-open, the small model, is downloadable, and
  for academic use only; the 98B model is API-only, which is why Chai-1's paper
  could not benchmark against it (§4).
- **ESMC & ESMFold2** — `esmc` · `10.64898/2026.06.03.729735` · **backbone** —
  Biohub / EvolutionaryScale's ~2.8B-sequence LM, a folding head on its frozen
  representations, and a binder design campaign run through both — one release,
  no separate papers for ESMFold2, ESMFold2-Fast or the campaign. _Level:_ 2,
  continuous. _Attachment:_ the language model **and** the folding head, the
  tightest coupling in the corpus, with nothing left to compose.
  - _Prediction:_ single-sequence antibody-antigen accuracy **matching
    AF3-with-MSA**, with the MSA encoder detachable and kept only as a rescue
    path for high-perplexity sequences.
  - _Design:_ binders optimized by descending a relaxed sequence — a
    distribution over amino acids fed to a 6-billion-parameter language model,
    the far end of the relaxation RFOptimization (§5) refuses outright.
  - _Carries:_ one claim per half. The prediction half resolves the anatomy
    beat's divide: the retrieval step is no longer the price of accuracy, which
    is what licenses the design half. The design half carries the claim that the
    coupling penalty is gone — every §5 system inverts a predictor outside the
    regime it was trained in, and BindCraft runs AF2 single-sequence and
    compensates with annealing and ensembling, whereas single-sequence **is**
    ESMFold2's native regime, so the off-distribution problem the coupling beat
    opens does not arise. MSA emancipation was never an accuracy story — it set
    the ceiling on coupling, and this is the ceiling.
  - _Against:_ AF3 with an MSA, on antibody-antigen — the target class §3–§7
    actually design for, which is why the comparison settles the thread rather
    than scoring a point. For the design half, §5's composed systems and
    Germinal in particular: the same sequence prior, reached with one model
    instead of two.
  - _Caveat:_ it flags the temporal-leakage problem in Boltz-2's numbers, so its
    own comparisons should be read under Table A's defect note like everyone's —
    and its own margin over AF3 is inside the error bars, reversing sign when
    AtlasFold re-runs the same benchmark. "Matching" is the claim that survives
    both runs; "exceeding" is not. The campaign adds self-chosen targets and a
    self-reported hit rate, the corpus's highest outside §8, so Table B's
    provenance columns apply here as everywhere.
- **AtlasFold** — `atlasfold` · `10.64898/2026.09.04.749352` · **mention** — the
  route is not one lab's: a second group reaches single-sequence folding from a
  language model independently, and is the only one to release it whole —
  training code, training data, stage checkpoints and weights, all MIT. It is
  also the independent re-run behind the caveat above. _(Preprint, 7 Sep 2026 —
  too recent to have been taken up by anything else here.)_

# §8 — The closed frontier

A coda, not a step in the argument. Systems that publish benchmarks and withhold
mechanisms — placed last because they cannot be analysed the way §1–7 analyse
everything else. Nothing here is backbone: a coda carries no beat of the
argument, and where one of these works does carry one, it is carried in the
section that owns it.

## Published without a mechanism

Results, benchmarks and a paper; the generator described in a clause.

- **AlphaProteo** — `alphaproteo` · `10.48550/arXiv.2409.08022` · **meat** —
  DeepMind generative engine plus a multi-stage filter for picomolar/nanomolar
  binders. Describes its generator only as _"a generative model trained on
  structure and sequence data from the PDB and a distillation set of AlphaFold
  predictions"_. _Carries:_ the canonical statement of the Level-1 success
  criterion — _"interchain AF2 pAE < 10, binder-aligned binder RMSD < 1 Å, pLDDT
  \> 80"_ — quoted in the coupling beat, in the units the metrics primer defines.
  _Caveat:_ the criterion is the field's rather than this paper's; what is
  proprietary is the generator, and the filter it publishes is the part everyone
  already ran.
- **Latent-X1** — `latentx1` · `10.48550/arXiv.2507.19375` · **meat** · and
  **Latent-X2** — `latentx2` · `10.48550/arXiv.2512.20263` · **meat** — Latent
  Labs' atom-level binder design platform: macrocycles and minibinders (X1),
  then drug-like low-immunogenicity antibodies (X2). Architecture credited only
  as _"our proprietary architecture"_; filters on ipTM/pAE and self-consistency.
  The one design lineage in this map with no predictor parent in §1–§7.
  _Carries:_ §8's one checkable result, and the awkward direction the disclosure
  beat has to absorb. Latent-X1 designed macrocycles against **RFpeptides'** own
  targets and epitopes, re-synthesized RFpeptides' published best binders, and
  measured them in its own assays — the corpus's only third-party wet-lab
  comparison of two design methods. The mechanism-withholding system did the
  more disciplined experiment. _Against:_ RFpeptides (§2), which is why the
  entry exists here rather than as a line in Table B — and against the rest of
  §8, since it is the only mechanism-withholding system that can be checked
  against an open method at all. _Caveat:_ two, and they are what keep the
  comparison honest. Only the _binders_ were re-measured, while the hit rates it
  contrasts with are RFpeptides' literature-reported ones, so that half is not a
  matched-assay comparison; and it covers one pair of methods on one modality.
  Its own headline rates are self-reported and the corpus's highest.
  _Collision:_ the head-to-head is argued in full under Table B, where its
  limits belong. **Latent-X2 carries the conclusion's developability gap**, not
  this one.
- **Back-references:** **Chai-2**'s generator (§4) and **BoltzProt-1** (§3)
  belong here and are reviewed in their own lineages. Boltz is the most
  informative case, because the same lab's earlier models are open and in the
  corpus — the comparison the other entries do not permit.

## Not published at all

No paper, no weights, no mechanism: these exist in the review only as points on
somebody else's benchmark, which is why the model that ran the benchmark opens
the beat.

- **OpenDDE** — `opendde` · `10.48550/arXiv.2607.03787` · **meat** — the
  instrument this beat is written from, and an open model in its own right: an
  Apache-2.0 all-atom co-folder that builds on Protenix-v1 and OpenFold3 and
  scales past them — a Pairformer three times wider than AlphaFold3's, an
  atom-level refinement stage before diffusion, and prediction and design
  trained as one task. _Carries:_ what it _measured_. Its scaling curve is the
  only public evidence about IsoDDE, and its antibody-antigen head-to-head of
  AlphaFold3, Boltz-1, Chai-1, Protenix-v1 and OpenFold3 is the corpus's most
  complete third-party comparison, which Table A's "who measured it" column
  rests on. _Caveat:_ in its own words _"not as a complete drug-discovery
  system"_ — design is roadmap only, so it belongs to the prediction half
  throughout. And it is a competitor measuring competitors: the comparison is
  third-party but not disinterested.
  [GitHub](https://github.com/aurekaresearch/OpenDDE)
- **IsoDDE** (Isomorphic Labs) — the frontier reference at the top of OpenDDE's
  scaling curve. Everything the review can say about it was measured by a
  competitor, which OpenDDE itself states as a limit on what can be concluded.
  _(map-only — private, no publication.)_ · **mention**
- **Chai-3** and **SeedFold** — a commercial web platform and a point on
  OpenDDE's scaling curve respectively. _(map-only.)_ · **mention**

For everything in this beat, every number the review can cite was measured by a
competitor. The disclosure beat's symmetry lands here: Isomorphic authors are
core contributors on the AlphaFold3 paper, so the review opens on the published
half of that organisation's work and closes on the half that stopped publishing.

______________________________________________________________________

# Tables A and B — planned, not yet filled

Two tables close the review, gathering the numbers spread across §1–§8 so a
reader sees the whole field at once. **Numbers are deliberately not entered
here** — the map does not carry per-paper figures; they are gathered from the
corpus when the tables are written.

**The risk they carry.** Everything else in the benchmarking units argues these
numbers are _not_ comparable, and a tidy side-by-side table reads as a
leaderboard — the exact misreading they exist to prevent. The tables therefore
make their own construction visible: **the provenance columns are not
decoration, they are the point**, and a cell without a stated benchmark, cutoff
and measurer has no entry.

- **FoldBench** — `foldbench` · `10.1038/s41467-025-67127-3` · **backbone** —
  peer-reviewed all-atom prediction benchmark spanning monomers,
  protein-protein, antibody-antigen, protein-ligand and protein-nucleic
  interfaces, scored in lDDT, DockQ and RMSD. It is the shared evaluation set
  behind the AF3 / Protenix / Boltz / ESMFold2 / OpenDDE comparisons. _Carries:_
  the benchmark column of Table A.

## Table A — structure prediction accuracy

_Rows:_ the predictors of §1, §3, §4, §6, §7, §8 — AlphaFold2/3,
AlphaFold-Multimer, OpenDDE, OpenFold3, Boltz-1/2, Chai-1, Protenix-v1/v2,
ESMFold/ESMFold2, plus the RoseTTAFold pair from §2 as the historical baseline.
_Columns:_ model · benchmark and version · training cutoff · target class ·
metric · **who measured it**.

_Target class is the axis that matters,_ not a single aggregate — split at
minimum into monomer, protein-protein, **antibody-antigen**, protein-ligand,
protein-nucleic. Antibody-antigen carries the most weight: most systems in §3–§7
design antibodies or nanobodies, so that is the accuracy their critics actually
run on, and a model leading on monomers while trailing there is a weak critic
for this review's purposes. Only a split table shows it.

_The "who measured it" column earns its place_ because the corpus contains
genuine third-party measurement — OpenDDE's antibody-antigen head-to-head,
Protenix-v2's baseline runs of OpenFold3 and others. Make self-reported and
independently-run numbers visually distinguishable: that distinction is the
disclosure beat arriving early. **OpenFold3 is the hardest row to source**: it
has no publication, so its self-reported figures come from a repository and a
technical report covering superseded weights, and Protenix-v2's baseline run is
the only version of them anyone else has checked.

_Every instrument in this table has a documented defect, and the column is where
they land._ FoldBench's aggregates do not enforce a common intersection of
evaluated targets, PoseBusters' criterion passes structures with distorted
geometry, and Boltz-2's numbers carry a temporal-leakage flag raised by three
separate groups. Not one benchmark here is uncontested, and two numbers from two
papers were almost never produced under the same conditions — which is what this
table is built to show rather than hide.

_One provenance note the AF2 rows carry._ Where a paper reports "AF2" it has
almost always run ColabFold (`colabfold` · `10.1038/s41592-022-01488-1`) — same
weights, different homology search — so the AF2 cells here and the AF2 filters
in Table B are ColabFold runs, with the MSA depth and recycle count set
differently paper to paper.

## Table B — quality of generated binders

_Rows:_ the design systems — RFdiffusion, RFantibody, RFpeptides, BoltzGen,
BoltzProt-1, PXDesign-d/h, Protenix-v2 design, Chai-2, BindCraft, BoltzDesign1,
Germinal, mBER, the ESMFold2 campaign, AlphaProteo, Latent-X1/X2.
_RFOptimization cannot be one:_ in-silico success rates only, so no
designs-tested denominator and no hit definition. It sits beneath the table
instead — the corpus's first system to claim a design advance on refolding
statistics alone. _Columns:_ system · coupling level · target class and count ·
**designs tested per target** · **hit definition** · assay · hit rate · affinity
reached · targets self-chosen?

**Sorted by designs-tested, not hit rate.** The identity beat's thesis is that
the measure of progress is how few designs you must make to get a binder, so the
denominator is the argument; sorting by hit rate silently converts the table
into the leaderboard.

**The hit-definition column is mandatory, and is why this table is hard.**
BoltzProt-1 (§3) separates _screening hits_ from _confirmed binders_ and states
that screening hits are _"what prior binder design model literature typically
reports as binders"_. Its own percentages are confirmed-binder rates; most
others quoted in this map are on the looser definition. Without the column the
table compares two different events and calls it progress.

**The one documented exception.** Latent-X1 (§8) designed macrocycles against
RFpeptides' own targets and epitopes, re-synthesized RFpeptides' published best
binders, and measured them in its own assays alongside its own designs — the
corpus's only third-party wet-lab comparison of two design methods. Two limits
keep it honest: only the _binders_ were re-measured, while the hit rates it
contrasts with are RFpeptides' own literature-reported ones, so that half is not
a matched-assay comparison; and it covers one pair of methods on one modality.
It runs in the awkward direction for the disclosure beat: the
mechanism-withholding system did the more disciplined experiment.

**What the pair says together, and why they stay adjacent.** Table A has a
benchmark column that can be filled — FoldBench, PXM and PoseBusters are
instruments several groups actually ran against. Table B's is empty, and **the
claim is about these rows, not about the field's inventory: not one campaign in
this table was measured against any benchmark another campaign in it used.**
Each chose its own targets, assays and hit definition. The prediction half of
this field is measured in common, the design half self-reported, and two
adjacent tables demonstrate that as no paragraph can. That asymmetry is the
benchmarking units' finding and the disclosure beat's strongest empirical
support.

**The one common frame anyone built, and how far it reaches.** The **Overath
binder meta-analysis** — `overath_meta` · `10.1101/2025.08.14.670059` · **meat**
— comes from a group with no design system of its own. It pooled 3,766 tested
designs from six published campaigns across 15 targets, re-scored every one
under a single pipeline, and asked which in-silico score predicts wet-lab
binding; AF3's ipSAE came out the best single predictor. That is the corpus's
only cross-lab test of the **filters**, as Latent-X1 (§8) is its only
third-party wet-lab comparison of two **methods** — and it belongs here, after
the lineages whose designs it scores. _Carries:_ the cross-lab evidence under
the conclusion's fifth gap, which without it rests on three labs each reporting
on their own designs. _What it reaches and what it does not:_ re-scoring reaches
the designs, not the assays or the hit definitions, so it standardizes the
filter and leaves the denominator and the hit definition exactly as each
campaign reported them — its own source table lists a different binding
definition for nearly every campaign it pooled. Its designs are also the
generation before the one this review centres on.

**The one prospective instrument, and why it is not a row either.** The
**AIntibody challenge** — `aintibody` · `10.1038/s41587-026-03238-6` · **meat**
— is the field's one blinded, prospective benchmark: 511 antibodies from 29
organizations across three tasks, expressed as full IgGs and measured by
independent laboratories under one protocol — HT-SPR, KinExA, and a five-assay
developability panel with a stated pass threshold. It is the complement of
Overath: Overath standardizes the filter on designs already made, AIntibody
standardizes the assay and the hit definition, which is the half Overath leaves
untouched. Together they are the only two places in the corpus where anyone
other than a method's authors decided what counted. _Carries:_ the second half
of the conclusion's fourth gap, and the prospective version of its fifth —
challenge 2 asked participants to rank sequences by affinity within HCDR3
clusters, and only one group of 26 beat the baseline of picking clones at
random. _What it does to Table B's claim:_ nothing, and the paper states why —
it notes "the absence of several prominent groups that have publicly reported
strong computational antibody design capabilities", so the systems in this table
were measured neither here nor against each other. Its one contact with a map
lineage is the challenge-1 winner, a **Protenix**-derived pairformer (§6) with a
DPO fitness head, disclosed in the paper's Methods with code released. _What it
found:_ the best design, 95 pM, was statistically indistinguishable from the
best antibody the wet-lab campaign produced (113 pM), a non-ML consensus of the
selection data ranked third, and the out-of-library design task returned 30.4%
nonbinders and a winning 2.9 pM design that failed to elute from the HIC column.
_Caveat, and it bounds what the review can take:_ one antigen — SARS-CoV-2 RBD,
chosen because it is the best-characterized target available and the challenge
was "deliberately primed for success" — a Q1-2025 snapshot, organized by the
consortium that reports it, and blinded on organizer integrity rather than
informatically. Its tasks are also **library-conditioned antibody engineering,
not target-conditioned de novo binder design**: challenges 2 and 3 handed
participants measured affinities a real campaign does not have until the end. It
tests the review's design half on a neighbouring problem, which is why it sits
here and not in a section.

______________________________________________________________________

# The conclusion

**Where the review's open questions are gathered, not where new ones are
raised.** Everything it lands is already argued above and none of it is
resolved: the open-versus-closed question the disclosure beat opens and §8
leaves standing; the two threads, which are paid off in §7 and under Table B but
not closed; the identity beat's designs-tested number, whose trajectory is the
review's spine and has no shared instrument to measure it against; and the five
gaps below, which are the conclusion's material.

**Order of the beats, and how it ends, are not settled** — they follow from the
units above rather than preceding them, so they are decided once those exist.

## The outside view — the field is trying to make drugs

**Opens the conclusion.** The five gaps below are internal to the corpus: each
is a limit a paper in `refs.bib` states about its own work. This beat is the
frame they sit in, and it is the one question the review cannot answer from
inside its own sources — whether any of this has reached a patient.

**The systems say what they are for.** BoltzGen (§3) opens on it — _"de-novo
binder design offers considerable potential for automating drug discovery"_ —
and it is not alone: Chai-2 (§4) optimizes designs _"for specific therapeutic
requirements such as species cross-reactivity"_, BindCraft (§5) reduces IgE
binding to birch allergen _"in patient-derived samples"_, Latent-X2 (§8) reports
developability _"that match or exceed those of approved antibody therapeutics"_,
and mBER (§5) places binder discovery as _"a critical step"_ in _"the
development of protein therapeutics"_. The therapeutic endpoint is the stated
goal of this field, not an outside standard imported to judge it.

**Bender et al., _AI in drug discovery_** — `bender_perspective` ·
`10.1038/s41573-026-01496-2` · **backbone** — is where that goal is audited.
_Nature Reviews Drug Discovery_ Perspective, Aug 2026; sixteen authors across
academia, pharma and biotech, 221 references. It weighs a decade of AI in drug
R&D against the only endpoint it accepts — delivering _"safer and more
efficacious medicines to patients faster"_ — and finds that _"evidence of their
clinically relevant impact is, so far, disappointingly limited"_, while
_"progress with AI-based technological capabilities is much more encouraging"_.

_Carries the beat's organizing distinction:_ **model validation against process
validation**. A model is validated inside its own box, on a held-out split of
its training data; a process is validated by whether the decision downstream of
the model got better. AlphaFold is one of its few unambiguous successes, and it
is successful _"in the context of model validation — in this case, protein
folding — and not necessarily process validation in a drug discovery setting"_.
**Every result in §1–§8 is model validation in that sense**, including the
wet-lab ones: a measured hit rate validates the generator, and no campaign in
the corpus is followed into the decision it was meant to improve. That is the
sentence the five gaps below are particular cases of.

_And the review's half of the field is the favourable half, which sharpens the
charge rather than excusing it._ Bender et al. attributes part of the recent
rise in approval rates to _"increasing investment in the development of biologic
modalities that have higher average clinical success rates and superior
intellectual property protection status than small-molecule drugs"_ — the
modality §1–§8 design for. Its Table 3 states the limit for that modality
directly, in the row naming RFdiffusion, ProteinMPNN, BoltzGen and Chai-2:
_"although binding is relatively easier to predict, functional effects and
developability also remain challenges"_. **Gap 1 below is that sentence in the
corpus's own terms**, and its Box 1 — _"a ligand, too, is not a drug"_, >10⁶
bioactive ligands in ChEMBL and PubChem against ~10³ marketed drugs — is the
small-molecule statement of the same distance.

_Where else it meets the gaps._ **Box 2** splits model use into selection,
deselection and quantification settings and holds that the metric must match the
setting — every Level-1 filter in §5–§7 is a selection setting scored by a
generic threshold — which is **gap 5** in general form, reinforced by _"every
model is a local model"_ for out-of-distribution use. Its recommendation that
benchmarking _"move on from model validation and instead focus on their ability
to improve decision making"_ is **gap 4** asked of the whole field rather than
of this corpus. And it corroborates the disclosure beat from outside, reporting
that _"open-source models in the area of co-folding have largely caught up with
closed-source developments"_ while dismissing **IsoDDE** (§8, tier 2) in the
review's own terms, as an in-house development whose authors _"offer few
technical details and hence do not allow independent verification of the results
obtained"_.

_Caveats._ It is a **Perspective**, the catalog's only secondary source,
admitted because this question cannot be answered from inside the corpus. Its
evidence base is small molecules and the clinical pipeline; proteins and
peptides are one row of one table, and the developability half of that row rests
on a single benchmark preprint the corpus does not hold (FLAb2, undecided in
`candidates.md`). So it supplies the argument and not the measurement — it
establishes what the field has not been asked to show, not how far any system
here would fall short if it were.

## What the field has not shown

Five gaps, each a question §1–§8 raise and none of them answer. They sit here
rather than after §8 because three of the five rest on Tables A and B, which a
reader has not met before this point.

**Each entry is a limit the corpus states about itself** — no gap is asserted
here that a paper in `refs.bib` does not name, and each points at the entry
where the evidence sits. That rule is the conclusion's discipline for this
material, and what keeps it from becoming a wish list.

**1. Binding is not the endpoint, and almost nothing here optimizes past it.**
Every system in §1–§7 generates, filters and reports on _binding_. Latent-X2
(§8) states the problem directly: campaigns fail _"not because they lack
binding, but because binding alone is insufficient when clinical success demands
developability and low immunogenicity"_, and it reports developability profiles
and what it claims is the first low-immunogenicity demonstration for an
AI-generated antibody. _The awkward part, and the reason this is its own beat
rather than a caveat:_ the one system in the review that optimizes past binding
is a closed one. The disclosure beat's uncomfortable direction, arriving a
second time.

**2. No system here predicts protein-protein binding affinity.** The filters are
binary. BindCraft (§5) says so of its own: AF2 ipTM is a strong predictor of
_whether_ a design binds and does not track _how tightly_. The corpus's one
affinity module is Boltz-2's (§3), which is protein-ligand and whose own paper
states it does not handle multimeric binding partners. So the field designs
binders it cannot rank by strength, and affinity appears in Table B only as an
outcome measured in a wet lab after the fact.

**3. Design success against targets with no experimental structure is
untested.** Germinal (§5) names it: how far design success depends on the
quality of the antigen model _"remains an open question"_. Every campaign in
Table B designed against solved or confidently predicted structures. What the
methods do on the targets that most need them is not in the corpus.

**4. No two design campaigns in the review were measured against a common
benchmark, and the one blinded benchmark the field has built did not measure
them.** Both facts are established elsewhere — the first under Tables A and B,
the second under AIntibody there, which ran 29 organizations through one assay
suite and records that the groups publicly claiming the strongest design
capabilities did not enter. Inside the corpus the only third-party wet-lab
comparison of two design _methods_ remains Latent-X1's, in §2's RFpeptides entry
and §8's. The conclusion does not re-argue any of it; it collects them as what
they are, the measurement gap the review's caveats keep running into.

**5. The filters have not been shown to work on the individual design.** Every
Level-1 pipeline selects designs on a confidence metric, and two papers report
the same limit from opposite directions. Germinal (§5) finds its nonbinders
clearing the ipSAE threshold alongside its binders. mBER (§5) finds the opposite
at million-design scale, hit rates climbing with ipTM. Both hold: across a
population a confidence score enriches, on any one design it does not
discriminate. The Overath meta-analysis (Table B) is the only cross-lab test and
sharpens it — re-scoring 3,766 designs from six campaigns, the best single
score's average precision ranged from 0.1 to 1 depending on the target, so the
score that works on one target is not the one that works on the next. _Why this
is a gap and not a caveat:_ the identity beat's collapsing designs-tested number
is the move out of the regime where enrichment is enough and into the one where
it is not.

_What this subsection is not._ Not a wish list, not a speculation about what
comes next, and not a place for limitations already attached to an entry. A gap
enters here only when a publication in the catalog states it and no section owns
it.
