# Background

## The founding bet, and how a co-folder is built

Design needed prediction first, and got it on a single wager: that coevolution
between two positions in a multiple sequence alignment is a usable proxy for the
two residues being close in space. AlphaFold2 cashed it — a median backbone
accuracy of 0.96 Å r.m.s.d.95 on the CASP14 domains, against 2.8 Å for the next
best method — and AlphaFold3 carried the result to arbitrary complexes of
proteins, nucleic acids, ligands and ions.

Every co-folder is two stages, and they do different jobs — the anatomy the rest
of the review reads through. **Stage 1 — the trunk. Sequences in, pairwise
reasoning out.** What comes out is principally a distogram: per residue pair, a
probability distribution over how far apart they are. The stage is
differentiable throughout, and cashes the bet. The divide among co-folders is
over what feeds it:

- **An MSA**, retrieved from sequence databases at inference time. AlphaFold2
  and AlphaFold3, RoseTTAFold, Boltz and Protenix are built around one.
- **A protein language model**, which internalizes the same statistics, so a
  single sequence is enough. ESM-2 with ESMFold, then ESMC with ESMFold2.

The divide is not a wall — Chai-1 carries both tracks — but which a model is
built around is the thread this review follows longest: it settles not accuracy
so much as how tightly a generator can later couple.

**Stage 2 — the structure stage. Pairwise reasoning in, atomic coordinates
out.** The variation here is the generative formalism, and what it decides is
how many forward passes one sample costs:

- **A single regression pass — AlphaFold2.** The structure module with invariant
  point attention, trained end to end. AF2's ablation includes a "no end-to-end
  structure gradients" run among the mechanisms its results credit.
- **Diffusion — AlphaFold3, and everything built in its image.** Coordinates are
  sampled along a long stochastic denoising trajectory. FrameFlow puts the
  inference cost at "∼1000 model forward passes … to produce high-quality
  samples".
- **Flow matching — an ODE rather than an SDE, straighter trajectories.** Fewer
  steps buy the same sample: FrameFlow recasts FrameDiff this way at twofold
  better designability and five-times fewer steps — on unconditional monomers,
  not binders. Several target-conditioned generators exist on the formalism,
  cited once in the corpus, in passing, or not at all.

Both formalisms are borrowed from image generation — what differs is only what
gets noised: AF3 calls its structure stage "a relatively standard diffusion
approach", "trained to receive 'noised' atomic coordinates and then predict the
true coordinates". The formalism is borrowed, the purpose is not — the module
replaced AF2's structure module and runs whether or not anything is being
designed. Image generation made the same move for its own reasons of speed —
hence these papers present flow matching as diffusion's successor, not an
alternative.

That is the machine. Its limit is where the next question starts: a predictor
tells you what a _given_ sequence folds into, never which sequence to try.

## Prediction and generation are the same machinery

What separates a predictor from a generator is only which sequences you hold
fixed. Fill every chain, it predicts a structure; leave one blank — the short
binder being invented — and the same model fills that chain against the rest,
designing binder and complex in one pass. BoltzGen states it outright: "a single
all-atom diffusion model capable of performing both structure prediction and
protein design".

RFdiffusion reached the same place from the other direction, fine-tuning
RoseTTAFold — a predictor — into a generator of backbones, design recast as
denoising. It works because RoseTTAFold's 3D track runs all the way to the
input, so a design constraint enters as coordinates, not pairwise distances. The
two halves of this review are one technology used two ways.

Why the predictor alone was not enough is arithmetic. It answers a question you
must already have asked — how does _this_ sequence fold against the target? —
and the candidates run to twenty choices per position over a chain tens of
residues long. The established way around it was a library, still how most
binders are found; its limit is not scale but aim. RFantibody puts it plainly:
"no method currently exists to design novel, epitope-specific antibodies
entirely in silico". A library cannot be aimed at the site you care about: it
returns binders to whichever part is accessible or immunogenic.

What generation bought is measured in one number: how many designs before one of
them binds. Chai-2's characterisation of prior work: it required "thousands to
millions of designs to reliably identify hits"; its own campaign prompts for
twenty or fewer designs per target, and on 52 targets with no antibody binder
already in the PDB it finds a hit for half from one round. That number is the
measure of progress, and the eight sections are, read one way, a history of it
falling.

The percentages do not all count the same event. BoltzProt-1 separates initial
_screening hits_ — "what prior binder design model literature typically reports
as binders" — from _confirmed binders_, which it validates in a second assay;
under it the headline confirmed-binder rate is 8.0%, where the looser definition
would score the same 150 designs, over 10 low-homology targets, at 16.0%.

And the one campaign that did not choose its targets: mBER — more than 1.1
million VHH binders against 436 human cell-surface proteins, hotspots drawn at
random from exposed residues, read out by phage display in one all-against-all
sweep. Its median per-design hit rate lands at 0.4% — roughly two orders of
magnitude below the headline rates, same coupling level, same predictor as
Germinal — while its best epitopes come back up into everyone else's range,
reaching 38% for individual hotspots under a strict confidence filter. The
spread inside that single campaign is the finding: target and epitope selection
alone move a hit rate across the full width of the literature's spread. Its hits
are phage-display enrichments — the looser event BoltzProt-1's split warns
about.

Image generation has no AlphaFold: nothing scores whether an image is _correct_,
so they are judged by human preference and cannot close a loop on their own
objective. Protein design can — it has a predictor to grade against, and how
tightly that loop closes is the next beat's subject.

## How tightly the generator is coupled to its critic

Every system in this review pairs a proposer with a judge; what separates them
is how tightly the two are bound — it orders §5–§7.

**Level 0** — the generator _is_ a predictor, weights reused. **Level 1** —
generate, then filter with a critic, no gradient: either the predictor's own
confidence scores — the field's default — or a critic trained to answer whether
a design binds. **Level 2** — backpropagate the predictor's loss into the
sequence being designed, held as a blurred distribution over amino acids, an
_L_×20 simplex annealed to one-hot.

The standard success criterion comes from Level 1, the field's default route:
AlphaProteo's phrasing of an older benchmark's rule — "interchain AF2 pAE < 10,
binder-aligned binder RMSD < 1 Å, pLDDT > 80" — quoted whole; the metrics primer
defines its units. What Level 1's "then filter" is read as, three systems have
questioned. BoltzProt-1 holds generator and testing budget fixed and changes
only the judge: BoltzGen's confidence metrics become a trained-to-bind
interaction model, and the confirmed-binder rate lifts from 3.3% to 8.0%.
RFOptimization treats agreement with a single predictor as the failure mode
itself, holding one out as an independent check on the others — never relaxing
the sequence, using the gradient only to rank discrete point mutations. PXDesign
finds a Protenix filter and an AF2-based one keep designs that overlap only
slightly, each holding true positives the other discards.

What makes Level 2 possible is that a sequence relaxes: every point of the
_L_×20 simplex is a valid prediction input, so a loop can hand the predictor a
blurred sequence, read how wrong the structure is, and step downhill — BindCraft
through AlphaFold2, Germinal over its merged AF-Multimer and
antibody-language-model gradients, ESMFold2 through a language model and a
folding head at once. Level 2 is not a training trick; it is what this
representation permits and a discrete encoding does not.

Why MSA emancipation was the precondition. An MSA is a database lookup on a
sequence that does not exist yet — neither differentiable nor even defined for a
binder still being invented — so any Level-2 loop runs its predictor
single-sequence on the designed chain. AlphaFold2's own paper documents where
that hurts: accuracy decreases substantially once median alignment depth drops
below about 30 sequences — and a designed chain has none, exactly where
BindCraft operates, hallucinating through AF2. ESMC is natively single-sequence,
so ESMFold2 backpropagates through a 6-billion-parameter language model without
leaving its training distribution. MSA emancipation is not an accuracy story; it
sets the ceiling on how tightly a generator can couple to its critic.

Where the gradient attaches is the mechanical half of the same claim. AF2 is
differentiable end to end, so a design loop backpropagates through the whole
network. AF3-class models replaced the structure module with diffusion and broke
that attachment: RFOptimization's account is that its diffusion module "is
inherently non-differentiable", backprop through it "computationally
prohibitive", so the loop blocks the gradient at the diffusion module and reads
its objectives from the trunk's heads. The corpus holds three answers to that
fact, and they are the substance of §5–§6.

## The disclosure limit

There is a limit on what a literature review can establish, reached wherever the
strongest claimed results come from systems that publish benchmarks and withhold
mechanisms. AlphaProteo describes its generator in one sentence — trained on PDB
structures and a distillation set of AlphaFold predictions. Latent-X credits its
architecture with two words: "our proprietary". Chai-2 gives its design
submodule a paragraph that names the framework it extends — the strongest
antibody result in the corpus is the one the review can say least about. IsoDDE
has no publication — visible only as the top point on a competitor's scaling
curves.

The sharpest version is not IsoDDE — it is Boltz. The lineage enters as the open
answer to AlphaFold3's closed weights and exits with its own frontier closed:
Boltz-1 and BoltzGen release code and weights under MIT, Boltz-2
permissive-open, BoltzProt-1 API-only with no weights — still publishing a paper
and wet-lab numbers. The review holds its before and after, both with papers.

One more fact: a hit rate is a self-report from the party whose assay,
definition and method you cannot inspect. That is why §8 sits outside the
argument — the closed systems are evidence about the field's evidence, not its
strongest results.

The eight sections follow from all this. §1 holds the AF2 and AF3 poles and the
open reproductions that join them, prediction only — everything later
reproduces, reacts to, or replaces the choice. §2 fine-tunes a predictor into a
generator — Level 0 in its historical form, then the Level 1 pipeline it
established — §3 reuses a diffusion predictor's weights as a generator, Level 0
stated outright, and §4 sits past where coupling can be inspected. Then the
coupling ladder climbs: §5 is Level 2 assembled from parts, §6 makes the levels
configuration on a predictor of its own, §7 fuses language model, folding head
and design loop into one system. §8 stands outside on the disclosure limit. What
§1–§8 quote their numbers in is defined next.
