# §8 — The closed frontier

Outside the open lineages the field's evidence comes in two kinds. There are
systems that publish benchmarks and keep the model behind them — AlphaProteo,
Latent-X, and, inside otherwise open lineages, Chai-2's generator and
BoltzProt-1, which refines an open generator and releases no weights of its own.
And systems that publish nothing at all — IsoDDE, Chai-3, SeedFold — which the
review sees only where somebody else has measured them.

What a paper of the first kind lets a reader check is the filter half. Latent-X1
— whose successor Latent-X2 extends the platform to drug-like antibodies —
selects its generated designs with filters tuned by the procedure AlphaProteo
had published, a grid search over thresholds on interchain predicted-alignment
error and self-consistency; and because AlphaFold3 could not be run "due to
commercial restrictions", those filters are built on open predictors, Chai-1 and
Boltz-2, a choice the authors make explicitly to facilitate independent
verification. The generation half is where the checking stops: Latent-X1's
platform serves designs rather than weights, and on the page the machine making
them is a clause.

Where the molecules are public, the check can still be run. AlphaProteo
re-synthesised RFdiffusion's published binder designs — its non-binders included
— and re-measured them by yeast display under its own conditions, target
concentrations of 0.5–1 µM against the 10 µM of the published screen. PD-L1's
rate reproduced; IL-7Rα's came back at 16% against a published 33%, TrkA's at
zero against 6%. The paper puts the differences on the assay — the yeast-surface
environment, and lower concentrations it notes may exclude weaker hits. It is
the one re-measurement in the corpus running to a whole campaign rather than two
molecules. An independent rate measures the machine and the measurement
together.

The second kind has no paper to check against anything. IsoDDE, Chai-3 and
SeedFold exist in the record only as points on other systems' measurements —
Chai-3 as a commercial web platform, IsoDDE and SeedFold on OpenDDE's scaling
curve, with IsoDDE at its top. The curve is drawn by an open model: OpenDDE,
Apache-2.0, built on Protenix-v1 and OpenFold3, and its antibody–antigen
comparison — AlphaFold3, Chai-1, Boltz-1, OpenFold3, Protenix-v1 and ESMFold2
under one protocol over three benchmark collections — is the most complete
third-party comparison in the corpus. OpenDDE states what that comparison cannot
settle: with IsoDDE's training recipe, data mixture and inference procedures not
public, the measured differences cannot be attributed to architecture, data
processing, scaling, distillation or inference-time procedure — and the group
drawing the curve is also a point on it.

The symmetry the disclosure beat set up is one sentence here: Isomorphic Labs
authors are core contributors on AlphaFold3, and IsoDDE, without a publication,
is Isomorphic Labs' system at the top of the curve. The review reads that
organisation's published half as §1 and its unpublished half only here. What
this frontier contributes to the rest is conditions: every figure quoted below
carries the bench and the party that produced it, which is what the five
exhibits keep.
