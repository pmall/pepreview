# Repository Guide

## Goal

This repository supports a descriptive scientific review of co-folding and
generative methods for **de novo binder design** targeting protein–protein
interactions. The primary focus is on designed peptides, macrocyclic peptides,
and compact protein binders (minibinders) as candidate drug precursors; antibody
and nanobody (VHH, scFv, mAb) systems are covered accurately where relevant as
part of the field, rather than serving as the main lens. Small-molecule ligand
generation is out of scope.

The review is written from a drug-discovery and protein-engineering perspective
for a curious scientific reader, emphasizing underlying mechanisms and
architectural trade-offs rather than ranking models or arguing a thesis. Key
topics include how replacing non-differentiable MSA lookups with a protein
language model trunk (e.g., ESMC/ESMFold2) enables native single-sequence
inference and end-to-end gradient backpropagation all the way back to the
sequence, coordinate-generation strategies, design workflows, and the gap
between in vitro binding hits and drug leads. Prose should read smoothly and
draw selectively on illustrative examples from `literature/map.md` instead of
enumerating every paper in the catalog. Never use em-dashes (`—`) in manuscript
prose: reaching for an em-dash signals a poorly structured sentence that should
be structured cleanly from the start. Never compress prose afterward to reduce
word count: manuscripts are drafts, and if a draft or abstract is too long or
dense, that is an outline and scope problem to solve by removing content rather
than squeezing the text.

Three core artifacts stay in sync:

- `literature/map.md` — a neutral, verified reference knowledge base distilled
  from the examined literature (concepts, model mechanisms, verified numbers,
  caveats, and `[@bibkey]` citations). Drafts draw selectively from it to
  illustrate ideas rather than exhaustively covering every entry.
- `literature/refs.bib` — the verified BibTeX catalog (every entry carries a
  resolvable DOI and `keywords` tags).
- `literature/corpus/` — primary publications stored by DOI (`/` replaced by
  `__`, e.g., `10.1234__example.pdf` and `10.1234__example.md`).

Target venue guidelines live in `VENUE.md` (PLOS Computational Biology Review).

## Workflow

1. **Knowledge cutoff:** Always verify facts against the parsed corpus or fresh
   web sources rather than relying on memory.
1. **Map first:** Add publications to `literature/map.md` under the appropriate
   section using plain domain terminology from the cited papers (avoid invented
   taxonomies or meta-commentary). Cite publication-derived facts inline with
   Pandoc-style keys (`[@bibkey]`).
1. **Formalize with `map-to-bib`** (`.agents/skills/map-to-bib/SKILL.md`):
   Verify the source, prefer the peer-reviewed journal version over the
   preprint, and fetch metadata from Crossref/DataCite. Only edit
   `literature/refs.bib` through this skill.
1. **Parse PDFs immediately:** When a PDF lands in `literature/corpus/`, run
   `uv run scripts/parse_all_pdf.py` without asking.
1. **Fact-check against parsed text:** Claims from abstracts or search snippets
   are provisional until verified against the parsed `.md` file in
   `literature/corpus/`. Correct inaccuracies and note when a source figure is
   image-only.
1. **Refresh cross-references:** Run `uv run scripts/build_xrefs.py` after
   updating the corpus or `literature/map.md`.
1. **Draft:** Write prose drafts into `literature/drafts/` when requested,
   following `VENUE.md` constraints and drawing selectively from
   `literature/map.md` as a reference knowledge base.

## Invariants

- Every publication cited in `literature/map.md` resolves to a
  `literature/refs.bib` entry via its `[@bibkey]` key. Non-publication sources
  (code repositories, blog posts, commercial platforms) are noted plainly
  inline.
- Undecided and excluded works live in `literature/candidates.md` with their
  exclusion reasons so decisions are not repeated. Excluded works may remain in
  `refs.bib` and `corpus/`.
- Re-check preprints for peer-reviewed journal versions during catalog passes.

## Files

- `literature/map.md` — neutral, verified literature knowledge base and fact
  reference.
- `literature/refs.bib` — verified BibTeX catalog.
- `literature/corpus/` — PDFs and parsed Markdown files named by DOI.
- `literature/candidates.md` — decision log for undecided and excluded works.
- `literature/xrefs.md` — generated corpus-internal citation network (never
  hand-edited).
- `literature/drafts/` — prose drafts.
- `VENUE.md` — target journal submission and formatting guidelines.
- `.agents/skills/map-to-bib/SKILL.md` — workflow for updating `refs.bib`.

## Scripts

Run scripts with `uv run scripts/<name>.py` from the repository root (`uv sync`
updates dependencies):

- `uv run scripts/parse_pdf.py <path/to/file.pdf>` — parse one PDF into
  `literature/corpus/<stem>.md` (Markdown only, no images).
- `uv run scripts/parse_all_pdf.py [--dry-run]` — parse all PDFs in
  `literature/corpus/` that lack a corresponding `.md` file.
- `uv run scripts/build_xrefs.py [--stdout]` — rebuild `literature/xrefs.md`
  from `refs.bib`, `map.md`, and `literature/corpus/`.

## Formatting

Never hand-wrap Markdown. After editing any `.md` file (except the generated
`literature/xrefs.md`), run:

```bash
uv run mdformat --wrap 80 <files>
```
