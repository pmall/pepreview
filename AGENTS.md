## Goal

I'm building a systematic literature review, using reproducible tooling to turn
primary sources into a structured, verifiable corpus. Three things stay in sync
— a **map** of the field, a **catalog** of the publications behind it, and a
**corpus** of those publications parsed to text — and the **drafts** are written
from all three. The map is the thinking; the catalog and corpus keep the
thinking honest.

**What the review is about, what it is for, and the test every claim must pass
are in `WRITING.md`.** Read it before proposing anything that adds, cuts or
moves material; this file stays about the tooling.

## Knowledge cutoff

Your training data is already old news to a moving field. Two cases: things you
don't know at all, and things you do know that may have moved on without you.
Both are worth checking — trust fresh information from the internet over your
own memory.

## Workflow

1. **Map first.** A publication enters the review as an entry in `map.md`,
   placed in the section where it belongs, written as a layout line — name, bib
   key, DOI, a sentence of role. Analysis does not go here.
1. **Formalize with `map-to-bib`** (`.agents/skills/map-to-bib/SKILL.md`).
   Verify the source is what the map says it is, prefer the peer-reviewed
   version over the preprint, fetch metadata from Crossref/DataCite, never
   invent a field. `refs.bib` is only ever edited through this skill.
1. **I download, you parse.** Getting the PDF is mine — I hand you the file or
   drop it in `literature/corpus/`. Parsing is yours: run it as soon as a PDF
   lands, without asking, since it costs seconds. Say what is missing, and wait
   only when the PDF itself is missing.
1. **Second look.** Once a publication is parsed, re-read it and check every
   claim you wrote into the map against the source. Correct what does not hold
   and say what changed. Claims taken from abstracts, search results or page
   summaries are **provisional** until checked against the parsed text, and they
   are frequently wrong in exactly the details a review depends on — numbers,
   method identity, what a metric measures.
1. **Refresh the cross-references.** Run `build_xrefs.py` whenever the corpus
   grows; a stale `xrefs.md` makes the newest publications look uncited.
1. **Draft.** Write drafts into `literature/drafts/` when I ask for one.

## Invariants

- **Every publication named in the map resolves to a `refs.bib` entry** — by bib
  key, or by a `keywords` tag on the entry whose paper describes it. Concepts
  with no citable publication are marked _map-only_ with the reason.
- **The map holds only what is in the review.** Undecided and excluded works
  live in `candidates.md` with their reason, so no decision is re-litigated. An
  included work carries its own caveats, borderline calls and scope reasoning in
  its entry.
- **Excluded is not uncited.** A work excluded from the argument stays in
  `refs.bib` and the corpus and may still be quoted — the catalog records what
  was obtained, the map what is in scope.
- **Preprints are re-checked for a journal version** on every catalog pass.
- **Every map entry carries a tier**, written after its DOI as `· **backbone**`.

## Two tests

Everything in the map — a section opening, an entry, a caveat, a clause inside
an entry — passes both, and they are re-applied on every pass over the file,
because material that passed when the argument was shaped one way often stops
passing once it moves.

1. **Does it serve a reader of the review?** If it serves the map, the catalog
   or the drafter instead, it belongs in an entry's decision record, in the
   writing plan, or nowhere. The recurring failures are _the map auditing
   itself_ — defending a tier count, a section's length, its own shape — and
   _process residue_: what a claim said before it was corrected, which pass
   found the error.
1. **Does it answer a question the review has already raised?** Material that
   settles a dispute no reader is having, or that arrives before the question it
   answers, moves to where the question gets asked, or is cut. A passage that
   argues with an imagined objector is usually answering nothing.

Failing test 1 means cutting. Failing test 2 usually means moving — the content
is right and its position wrong. Neither test is about length: a long entry that
earns its place stays, a single clause that fails goes.

## Tiers

The tier answers **how much of the review's argument rests on this work** —
nothing else. It keeps the intended writing weight visible in the layout instead
of rediscovered each time a section is drafted.

| Tier         | Test                                                                                                       | Consequence when drafting                                                     |
| ------------ | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **backbone** | Remove it and a beat of the argument, or a section's organizing fact, collapses                            | Analysed in full: mechanism, numbers, caveats, and what it is contrasted with |
| **meat**     | It supplies evidence a backbone claim rests on, but that claim survives if another work substitutes for it | Described and cited; its numbers may be quoted; no mechanism walkthrough      |
| **mention**  | It establishes that a category exists, or is a date on a timeline                                          | One sentence. No numbers, no mechanism                                        |

- **Tier is not quality, novelty or citation count.** A famous paper the
  argument does not lean on is a _mention_; an obscure one that anchors a
  section is _backbone_. Never derive a tier from `xrefs.md` — in-degree there
  is confounded by publication age and is corpus-internal.
- **Structural weight is read as importance in the field, so it is weighed
  separately from the tier.** A row in a taxonomy table looks like a category of
  the field; the last rung of a ladder looks like where the field currently
  ends. The test is whether the field will still remember the work in a few
  months — a very recent short preprint with no wet lab will not, so it gets no
  structural position, however distinct its idea. Keep the substance in its home
  section and demote it in overview material to a clause or a named variant.
- **Tier is per-claim, so state which claim.** Where it is not self-evident from
  the entry, name the beat or organizing fact the work carries. That is what
  makes a tier checkable, and re-derivable when the argument moves.
- **Tier is a property of the argument, not of the paper**, so it changes when
  the argument changes. Re-check tiers when a beat is rewritten or a section
  reordered, not when a new paper arrives.
- **The count per section is not a target.** A tier is wrong when two backbone
  entries carry the _same_ claim, or when a section has no backbone at all.
- **Map-only concepts are tiered too.** Having no publication does not make a
  concept argumentatively light.

## Files

- `WRITING.md` — the field, the goal and register of the review, the test every
  claim is weighed against, and the rules for turning a map unit into a section
  draft.
- `literature/map.md` — the living map of the field: the layout of the review,
  its sections in the order they will read, and every publication placed in one
  of them. The default working file and the entry point of the system.
- `literature/refs.bib` — the catalog, one BibTeX entry per publication, keys
  matching the map's entry slugs. Every entry carries a DOI and a `keywords` tag
  list, so map concepts resolve by key or by tag. Sources without a resolvable
  DOI are not cataloged.
- `literature/corpus/` — the publication artifacts, named by DOI: source PDFs
  alongside their parsed Markdown, same name, different extension.
- `literature/candidates.md` — the decision log for everything outside the
  review: works surfaced but not yet judged, and works read and then judged out
  of scope, each with its reason. Accepting one means writing it into the map
  and running `map-to-bib`; rejecting one means moving it to the excluded part
  of the file.
- `literature/xrefs.md` — the citation network among the cataloged publications:
  who cites whom, how often each is named in prose, what nothing cites, which
  sections talk to each other. Generated, never hand-edited. Material for
  drafts, not a source of truth — a citation is not a comparison or an
  endorsement, in-degree is confounded by publication age, and the counts are
  internal to the corpus rather than to the field.
- `literature/drafts/` — intermediate drafts on the way to the final review.
  Filenames are free-form and named for their subject.
- `.agents/skills/` — project-local, tool-agnostic skills for repeatable
  workflows.

DOI-based filenames replace each `/` with `__`, since `/` cannot appear in a
filename: `10.1234/example` becomes `10.1234__example.pdf` and `.md`.

## Scripts

`uv` manages dependencies — run `uv sync` when the environment needs updating.
Run scripts with `uv run scripts/<name>.py` from the repo root. You run all of
them yourself, unprompted, including parsing; I never touch the command line.

- `uv run scripts/parse_pdf.py <path/to/file.pdf>` — parse one PDF into
  `literature/corpus/<stem>.md` (Markdown only, no images). Errors if the output
  already exists.
- `uv run scripts/parse_all_pdf.py [--dry-run]` — parse every PDF in
  `literature/corpus/` that lacks a `.md` beside it. `--dry-run` only lists
  them.
- `uv run scripts/build_xrefs.py [--stdout]` — rebuild `literature/xrefs.md`
  from `refs.bib`, `map.md` and the parsed corpus. Offline and quick; safe to
  re-run any time. It matches papers by DOI, preprint DOI, arXiv id and title,
  and counts prose mentions using each entry's `keywords`, so a misspelled
  keyword silently produces a zero mention count.

## Formatting

**Never hand-wrap Markdown.** After editing any `.md` file, run
`uv run mdformat --wrap 80 <files>` and move on. Line width, wrapping, table
padding and emphasis markers are the formatter's business, never a thing to fix
by hand or to raise as a review finding. Do not format `literature/xrefs.md`; it
is generated — rebuild it instead.
