# Target venue

> Checked 2026-11-19 against the journals' public pages (URLs inline). This file
> records what the venue demands; `WRITING.md` carries what the review says. If
> the venue changes, only the budget table in `WRITING.md` changes with it.

## Recommendation: PLOS Computational Biology, article type **Review**

Scope fits: the journal publishes work applying computational methods —
including AI and machine learning — to living systems at all scales, and
protein/peptide binder design is squarely in its territory
(`journals.plos.org/ploscompbiol/s/journal-information`). Open access, indexed
everywhere, no page charges for length.

**What a Review is there** (`.../s/other-article-types`):

- Reflects a rapidly advancing, topical area of broad interest to the whole
  biology community, not covered significantly by other journals.
- **Aim for 3,000–6,000 words and two or three figures or other display items.**
- "Should not be a mere summary of the field; it should be a critique with new
  points of view which are supported by existing literature from a variety of
  authors." — our angle (the coupling-level taxonomy of generator–critic
  architectures, and the disclosure limit on the field's evidence) is the point
  of view; the families-and-concepts exposition is the vehicle.
- **Structure: Title, Authors, Affiliations, Abstract, Introduction, Main Text
  (subsections as appropriate), Conclusions, Acknowledgments, References.**
  Figure captions and tables are inserted immediately after the first paragraph
  that cites them.
- Reviews sit in the front section and are peer-reviewed. The page marks only
  Collection Overviews as pre-approval-only; confirm with the editorial office
  (ploscompbiol@plos.org) that an unsolicited Review on this topic is welcome
  before submission.

**General submission rules that shape the manuscript**
(`.../s/submission-guidelines`):

- Initial submission as a single PDF including text and figures; DOC/DOCX/RTF
  accepted; double-spaced; single column; English.
- No hard word limit at submission, but "present and discuss your findings
  concisely" — the 3,000–6,000-word Review aim is the operative budget.
- **Maximum 3 heading levels.**
- Title page first: title, authors, affiliations; the Abstract follows it.
- **References numbered in order of appearance, cited in square brackets
  ([19])** — Vancouver-style numbering, not author–year.
- Tables placed immediately after the first paragraph citing them.
- Required statements: Data Availability, Financial Disclosure ("The author(s)
  received no specific funding for this work." if unfunded), Competing Interests
  (declared on behalf of all authors), author contributions, ORCID for the
  corresponding author.
- Preprints encouraged; PLOS can auto-compile a bioRxiv PDF from the submission.

**AI-use policy (PLOS-wide, applies to this manuscript).** AI tools may assist
but can never be listed as authors. Any AI contribution to the article's content
must be disclosed — tool name, what it influenced, and how the output was
checked — in a dedicated part of Methods or in Acknowledgements. This review is
written with AI assistance under human verification of every claim against the
parsed sources; the disclosure statement is a submission-time to-do, and the
verification discipline in `AGENTS.md` ("second look") is what makes that
disclosure true.

## Alternatives considered

| Venue                                | Article type         | Length guidance                                    | Notes                                                                                                                 |
| ------------------------------------ | -------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **PLOS Comput Biol** (recommended)   | Review               | 3,000–6,000 words, 2–3 display items               | OA; AI/ML in scope; numbered refs; critique-with-viewpoint expected                                                   |
| Briefings in Bioinformatics (Oxford) | Review               | no hard cap published; graphical abstract required | reviews often commissioned; proposals welcome; higher-visibility venue                                                |
| Bioinformatics (Oxford)              | Review               | 3–8 pages ≈ 3,000–6,000 words excl. figures        | mostly commissioned; proposals welcome                                                                                |
| Comput Struct Biotechnol J (CSBJ)    | Review / Mini-review | no strict cap                                      | open access (APC); already ran an AI binder-design review in 2026 (doi:10.34133/csbj.0070), so novelty must be argued |

If a longer treatment is wanted later (the map supports ~13k words), CSBJ or
Briefings in Bioinformatics are the fallback; switching venue then only means
re-scaling the budget table in `WRITING.md`.

## What this changes in the writing plan

- The review is **Abstract (~250 words) + Introduction + Main Text +
  Conclusions, ≤ 3 heading levels, 3,000–6,000 words of main text, 2–3 display
  items**.
- The metrics primer stops being a standalone section: at this length,
  definitions sit beside the thing defined at first use (already a rule in
  `WRITING.md`); the primer draft remains as the vocabulary source.
- The five exhibits compress to **2–3 display items**: one families/coupling
  table, one prediction-accuracy table, one wet-lab campaigns table.
- Citations in the final manuscript are numbered in order of appearance; the bib
  keys in `refs.bib` remain the internal citation keys and are mapped to numbers
  at assembly.
- Submission-time checklist: title page, abstract, data availability, funding,
  competing interests, contributions, ORCID, AI-use disclosure, preprint opt-in.
