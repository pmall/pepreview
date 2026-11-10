# The conclusion

No exhibit above measures what a successful design was used for — the field's
own placement, not the review's: the systems say what they are for. BoltzGen
opens on "de-novo binder design" and its "considerable potential for automating
drug discovery"; Chai-2 optimizes designs "for specific therapeutic requirements
such as species cross-reactivity"; BindCraft carries its IgE reduction to birch
allergen "in patient-derived samples"; Latent-X2 reports developability profiles
"that match or exceed those of approved antibody therapeutics"; and mBER places
binder discovery as "a critical step" in "the development of protein
therapeutics". The therapeutic endpoint is the stated goal of this field, not a
standard imported to judge it.

Whether any of this reached a patient is the one question the corpus cannot
answer; the source that speaks to it is not a benchmark: sixteen authors in
_Nature Reviews Drug Discovery_ weigh a decade of AI in drug development against
delivering "safer and more efficacious medicines to patients faster", and report
that "evidence of their clinically relevant impact is, so far, disappointingly
limited", while "progress with AI-based technological capabilities is much more
encouraging". Its organizing distinction is model validation against process
validation: a model is judged on held-out data inside its own box, a process by
whether the decision downstream got better. AlphaFold, its clearest success, is
successful "in the context of model validation — in this case, protein folding —
and not necessarily process validation in a drug discovery setting". Every
result in §§1–8 is model validation in that sense, the wet-lab campaigns
included: a measured hit rate validates the generator; no campaign is followed
into the decision it was meant to improve. That is the sentence the five gaps
below are particular cases of. Its evidence base is small molecules and the
clinical pipeline; it establishes what the field has not been asked to show, not
how far any system here falls short.

The first gap is the endpoint itself. Every system in §§1–7 generates, filters
and reports on binding; one line of the corpus says why that stops short:
campaigns fail "not because they lack binding, but because binding alone is
insufficient when clinical success demands developability and low
immunogenicity" — and the line belongs to Latent-X2, the one system in the
review that optimizes past binding. It reports what it calls the first
low-immunogenicity demonstration for any de novo generated antibody. It
publishes no mechanism: generation withheld, its two models "two variants of the
same foundational model architecture" — so the one result past binding sits
outside the checking §§1–7 open on everything else.

The second gap is strength. The filters are binary: BindCraft says so of its own
score, which predicts whether a design binds and "does not correlate with the
interaction affinity" — and the corpus's one affinity module, Boltz-2's, is
protein–ligand and states of itself that it "does not explicitly handle such
cofactors, including ions, water, or multimeric binding partners". So the field
ranks designs by whether they are expected to bind, not how tightly; what a
binding is worth enters the exhibits only afterwards, measured by a wet lab. The
third gap sits upstream: how far design success depends on the quality of the
antigen model "remains an open question", in Germinal's phrasing, and every
campaign in Exhibit 4 designed against structures solved already or confidently
predicted. What these methods do on the targets that most need them is not in
the corpus.

The fourth gap is measurement, and its first half is Exhibit 4's: no two design
campaigns in the review were measured against a common benchmark. The one
blinded benchmark the field has built did not close that gap, because it is not
a design benchmark. It is an antibody-engineering challenge — 511 antibodies
from 29 organizations, expressed as IgGs, measured by independent laboratories
under one protocol — and on its ranking task, ordering HCDR3-cluster sequences
by affinity, every organization but one fell below the baseline of picking
clones at random. The systems this review is about were not in it — the
challenge notes "the absence of several prominent groups that have publicly
reported strong computational antibody design capabilities". Targets recur
between papers; their measurements do not. Only once did someone else re-run
another paper's designs, non-binders included: AlphaProteo re-synthesized
RFdiffusion's published set and measured it by yeast display, recovering 16%
against a published 33% on IL-7Rα and zero against 6% on TrkA. That is the
corpus's only independently produced hit rate for another method.

The fifth gap is the filter on the individual design. Two papers state its limit
from opposite directions: Germinal reports "many nonbinders also exceeded these
thresholds", while the mBER study, at million-design scale, finds hit rates
climbing as its ipTM filter tightens. Both hold. Across a population a
confidence score enriches; on any one design it does not discriminate. The
cross-lab test sharpens rather than settles it: a meta-analysis pooling 3,766
tested designs from six published studies across 15 targets re-scored every
design under one pipeline; the best single score, AlphaFold3's ipSAE, had
average precision running from 0.1 to 1 depending on the target. And re-scoring
reaches the designs, not the assays or the hit definitions — the filter
standardized, each denominator left as its campaign reported it.

What stands unanswered is short, and none of it new. The disclosure question
closes neither way: independent assessment finds that "open-source models in the
area of co-folding have largely caught up with closed-source developments",
while the systems at the top of the performance curves "offer few technical
details and hence do not allow independent verification of the results
obtained". Two threads run through the review and stop where they were paid off,
not concluded. The divide between statistics retrieved at inference and
statistics carried in a language model's weights closed in §7 on the word
"matching" — the margin inside the error bars, an independent re-run reversed
the ordering — and what survived is that the search for related sequences is no
longer the price of accuracy on the class this review designs for. What counts
as a hit stayed a choice: the same 150 designs sit at 8.0% under BoltzProt-1's
confirmed-binder definition and 16.0% under its looser screening definition;
Exhibit 5 records the criteria as each paper states them. Beneath both runs is
the number the introduction made the review's spine — how many designs must be
physically made before one binds — here 5 to 9,000 per target, counted campaign
by campaign under instruments no two papers shared. The exhibits are where
measurement stops — short of what a successful design was used for — and the
review ends there.
