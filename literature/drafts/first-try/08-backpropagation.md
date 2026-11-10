# §5 — Design by backpropagation

The first designs the field made by running a predictor backwards. Each system
here takes a structure predictor it did not train, picks a point inside it to
backpropagate from, and builds machinery to turn that gradient into a sequence:
loss, soft representation, hardening schedule, aftermath. Where these
arrangements hold and where they come apart depends mostly on where the gradient
attaches.

The loop is told once; nearly every system below shares it. A predictor is held
at its trained weights; a differentiable loss — confidence or contact terms, or
a match against a wanted interface — is read off its outputs; the gradient flows
into an *L*×20 simplex for the sequence. An annealing schedule hardens it into
one-hot letters; other tools tidy what the loop leaves. Nearly all of it runs
through one library, ColabDesign, which owns input preparation, losses and the
annealing; each group supplies the difference. AfCycDesign, the earliest here,
is the smallest modification — AlphaFold2's relative positional encoding made
cyclic — but its binders are known motifs grafted onto hallucinated scaffolds,
not loop output; the real test comes from the system that filled the loop out.

BindCraft runs the loop in its fullest form on AlphaFold2-multimer, gradient
through the whole network into an *L*×20 error gradient over amino-acid choices.
The five trained weight sets swap between iterations, so no trajectory overfits
one. The target is repredicted every iteration, so its backbone and side chains
mould to the binder — Cα r.m.s.d. of 0.5–5.5 Å across designs. The simplex
hardens in four stages, continuous logits to discrete search, with a
straight-through phase showing one-hot while gradients still flow. Afterwards
ProteinMPNN-soluble redesigns everything beyond 4 Å of the interface,
AF2-monomer single-sequence repredicts, Rosetta relaxes and scores. In the wet
lab, passing designs succeeded 10–100% across twelve targets, averaging 46.3%.
Two caveats. AF2 reads the designed chain single-sequence, off-distribution,
which annealing and the weight-set swap appear to compensate for; and the ipTM
it ranks on predicts *whether* a design binds, not how tightly. BindCraft2
widens the modalities without changing the loop; no benchmark yet backfills the
numbers.

A diffusion module cannot be unrolled for a gradient, so the loss attaches
elsewhere. BoltzDesign1, on Boltz-1, stops the gradient before the diffusion
module and reads the loss off the trunk's distogram — contact losses over its 64
distance bins — betting that optimizing the distogram optimizes the distribution
the sampler draws from, not one draw from it. On BindCraft's own 212 successful
binders across 13 protein targets, distogram contacts match the diffusion
module's at precision at *K* above 0.5 for 76% of designs — the substitution,
checked. For nucleic-acid targets it fails; the confidence module carries the
loss. The sequence update reuses BindCraft's four stages after a softmax warm-up
— raw logits start off-distribution here — and LigandMPNN optionally redesigns
the surface. One caveat: it shares senior authors with BindCraft, so the
protein-target half is one programme porting one method, not two independent
data points.

RFOptimization never relaxes the sequence and does not design from scratch: it
takes a finished design and improves it with RF3 gradients off the confidence
heads and distogram. Mutations are proposed from the negative normalized
gradient and accepted or rejected by Metropolis–Hastings, keeping the sequence
chemically valid: a continuous relaxation, the paper says, is an attack surface
the optimizer would exploit. Half the time it instead cycles through Boltz and
LigandMPNN, with AF3 held out as an independent check — the review's only
optimizer-side answer to single-predictor agreement. Its cost case against
BindCraft is the numbers unit's to carry; its limit here is being entirely in
silico, with no designs-tested denominator.

Confidence does not say a designed sequence is natural, so the antibody systems
add a language model; the difference is whether that prior moves. Germinal runs
the loop on AlphaFold-Multimer with a second gradient merged into the first:
AF-M's structural confidence and IgLM's CDR-naturalness score, a weighted sum,
MGDA or PCGrad. Framework positions are pinned so only the CDRs move, and AF-M
gets the framework as a template with every CDR atom masked — anchoring the
prediction without biasing the loops. A straight-through estimator feeds IgLM
its one-hot; the sequence lives in a PSSM through logit and softmax phases and
ten semigreedy iterations of five candidates, then AbMPNN tidies the rest. The
arrangement this entry carries: a live prior merged with the structural gradient
— §7 reaches it with one model. Its filters do not separate it from failure:
nonbinders clear its ipSAE threshold alongside binders. Its antigens are AF3
predictions, their quality's hold on design success left open. OpenGerminal
reimplements it Apache-2.0 on an open stack.

mBER keeps the ColabDesign loop — `design_3stage`, BindCraft's pAE-centred
losses — unchanged and adds ESM2's logits, run once over the masked VHH
framework, as a fixed bias: the prior never moves, it tilts the space the
optimizer walks. Templates — a NanoBodyBuilder2 framework, a hotspot-truncated
target — answer the off-distribution problem the others handle with annealing.
mBER-2 is so far a company technical report extending the method to
microbinders. The diffusion wall gets a third answer in §6: Protenix shortens
the trajectory instead of reading the loss before the sampler.
