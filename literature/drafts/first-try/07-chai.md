# §4 — Chai

Chai-1 is the lineage's predictor: an all-atom co-folding model whose
architecture "largely follows" AlphaFold3's, run at inference as trunk samples
and diffusion samples — AF3's two stages by another name. Inference takes any
combination of MSAs, templates and protein-language-model embeddings; the two
trunk inputs are alternatives the same model can run alone, and single-sequence
mode passes only sequence and embeddings. On antibody–protein interfaces the
choice is free of measurable cost — single-sequence Chai-1 matches Chai-1 given
full MSAs, and both outperform AlphaFold 2.3 run with MSAs, which the paper
attributes to the weak evolutionary signal in antibody sequences. Second is
prompting: pocket, contact and docking constraint features that "boost
performance by double-digit percentage points" when supplied — one to four
epitope residues are all the campaign below asks for. Its comparison against
AlphaFold3 is a number rather than a run: ligands pose within 2 Å RMSD on 77.05%
of the PoseBusters benchmark against AF3's reported 76.34%, AF3's values taken
from its publicly released predictions — "we did not run AF3 ourselves" — and
its direct comparisons run against AlphaFold 2.3, head-to-heads against AF3 or
ESM3 having been impossible "due to commercial use restrictions". Weights are
non-commercial; the web server is free for commercial use.

That prompting is what Chai-2 turns into a design campaign. Across 52 novel
antigens — none with an antibody or nanobody binder already in the PDB, and
excluded against any antigen in the structural antibody database at 70% sequence
identity and 80% coverage before the training cutoff — up to 20 designs per
target go to the bench in a single round, and at least one comes back binding
for 26 of the 52: a hit rate the abstract reports as 16%, 15.5% averaged across
all designed antibodies, all inside a two-week loop from epitope to
biolayer-interferometry validation. A hit is a positive BLI curve signature
above 0.1 nm of signal and 300% of background; the designs are novel by the
paper's own checks, none within 2 Å of any solved antibody structure or within
ten CDR edits of the nearest. What the campaign claims is the screen's absence.
RFantibody (§2) ships its designs alongside a 9,000-design screen and states the
screen as still necessary; Chai-2 reports no successive rounds of wet-lab
experimentation and calls its results "the blind performance of running Chai-2
once in a new setting" — the claim §2 stops short of.

What does not travel with it is the generator. The paper describes Chai-2 as one
end-to-end model with two named submodules — the folding submodule Chai-2f
follows "a similar architecture as Chai-1", while the design submodule Chai-2d,
"trained to generate one or more protein chains that bind to arbitrary,
prespecified protein targets", gets a paragraph naming "an all-atom generative
protein model framework" and two citations. The generative mechanism itself —
which formalism proposes the candidate binders — is nowhere stated, and the
architectural improvement the paper does quote, antibody–antigen complexes
predicted above DockQ 0.8 for 34% against Chai-1's 17%, belongs to the folding
submodule. Opening that coupling — building the generator where the predictor's
internals stay readable — is where the review goes next.
