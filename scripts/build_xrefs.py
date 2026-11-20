#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the corpus cross-reference map: which cataloged publications cite which.

Edges are found by searching each paper's parsed Markdown for the identifiers of
every other cataloged paper — DOI, preprint DOI, arXiv id, and normalized title.
Nothing is fetched from the network; the parsed corpus is the only source.
"""

from __future__ import annotations

import re
from argparse import ArgumentParser
from collections import defaultdict
from datetime import date
from pathlib import Path

ENTRY_RE = re.compile(r"@(\w+)\{([^,]+),(.*?)\n\}\n", re.S)
# map.md uses one "# " heading per top-level section (skipping the document title)
SECTION_RE = re.compile(r"^# (?!Literature Map\b)(.+)$", re.M)
# a map line that *defines* an entry, e.g. "- **Boltz-1** (`boltz1`..." or "- **Boltz-1** ([@boltz1]..."
DEFINITION_RE = re.compile(r"^\s*[-*]\s+\*\*.*?(?:`([a-z0-9_]+)`|\[@([a-z0-9_]+)\])", re.M)


def norm(text: str) -> str:
    """Collapse to comparable form: lowercase alphanumerics only."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def field(body: str, name: str) -> str:
    # the trailing newline is optional: the last field of an entry has none
    match = re.search(r"\n  %s = \{(.*?)\},(?=\n|$)" % name, body, re.S)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def short_name_pattern(keywords: list[str], key: str) -> re.Pattern[str]:
    """Regex matching how a paper is named in prose ("Boltz-1", "boltz 1", ...).

    Prefers the keyword that matches the bib key once separators are ignored,
    since the first keyword is often a family tag too generic to count with
    (`boltz` would match BoltzGen and BoltzDesign1 as well).
    """
    exact = [k for k in keywords if norm(k) == norm(key)]
    pool = exact or keywords
    chosen = max(pool, key=lambda k: (k.count("-"), len(k)))
    pattern = re.escape(chosen).replace(r"\-", "[-\\s]?")
    pattern = re.sub(r"(?<=[a-zA-Z])(?=\d)", "[-\\\\s]?", pattern)
    return re.compile(r"\b" + pattern + r"\b", re.I)


def load_catalog(repo_root: Path) -> dict[str, dict]:
    bib = (repo_root / "literature" / "refs.bib").read_text()
    papers: dict[str, dict] = {}
    for _kind, key, body in ENTRY_RE.findall(bib):
        doi = field(body, "doi")
        note = field(body, "note")
        keywords = [k.strip() for k in field(body, "keywords").split(",") if k.strip()]

        aliases = {doi.lower()}
        # a citing paper often references the preprint, whose DOI we keep in the note
        aliases |= {d.lower().rstrip(".") for d in re.findall(r"10\.\d{4,5}/[^\s,;)]+", note)}
        aliases |= {"arxiv:" + a for a in re.findall(r"arXiv:([\d.]+)", note)}
        eprint = re.search(r"\n  eprint = \{([^}]+)\}", body)
        if eprint:
            aliases.add("arxiv:" + eprint.group(1))

        papers[key] = {
            "doi": doi,
            "title": field(body, "title"),
            "year": int(field(body, "year")),
            "aliases": {a for a in aliases if a},
            "pattern": short_name_pattern(keywords, key),
        }
    return papers


def load_sections(repo_root: Path, papers: dict[str, dict]) -> None:
    """Tag each paper with the map section(s) that define an entry for it."""
    text = (repo_root / "literature" / "map.md").read_text()
    bounds = [(m.start(), m.group(1).strip()) for m in SECTION_RE.finditer(text)]
    for paper in papers.values():
        paper["sections"] = []

    def label_at(pos: int) -> str | None:
        return next((lab for start, lab in reversed(bounds) if start < pos), None)

    for match in DEFINITION_RE.finditer(text):
        key = match.group(1) or match.group(2)
        label = label_at(match.start())
        if key in papers and label and label not in papers[key]["sections"]:
            papers[key]["sections"].append(label)

    # fallback to first mention for entries cited inline rather than at bullet start
    for key, paper in papers.items():
        if paper["sections"]:
            continue
        first = re.search(r"(?:`%s`|@%s\b)" % (re.escape(key), re.escape(key)), text)
        label = label_at(first.start()) if first else None
        if label:
            paper["sections"].append(label)


def build_edges(papers: dict[str, dict], corpus: Path) -> dict[str, dict[str, int]]:
    """src -> {dst: mentions}. Mentions count prose uses, not reference-list rows."""
    texts = {}
    for key, paper in papers.items():
        path = corpus / (paper["doi"].replace("/", "__") + ".md")
        if path.exists():
            texts[key] = path.read_text()

    edges: dict[str, dict[str, int]] = defaultdict(dict)
    for src, text in texts.items():
        lowered = text.lower()
        collapsed = norm(text)
        for dst, paper in papers.items():
            if dst == src:
                continue
            cited = any(alias in lowered for alias in paper["aliases"])
            if not cited:
                title = norm(paper["title"])
                cited = len(title) > 25 and title in collapsed
            if cited:
                edges[src][dst] = len(paper["pattern"].findall(text))
    return edges


def section_of(paper: dict) -> str:
    return paper["sections"][0] if paper["sections"] else "-"


def render(papers: dict[str, dict], edges: dict[str, dict[str, int]], missing: list[str]) -> str:
    cited_by: dict[str, dict[str, int]] = defaultdict(dict)
    for src, targets in edges.items():
        for dst, mentions in targets.items():
            cited_by[dst][src] = mentions

    total = sum(len(t) for t in edges.values())
    this_year = date.today().year
    out: list[str] = []
    add = out.append

    add("# Corpus cross-references")
    add("")
    add("**What this file is for:** finding which paper to read when writing about")
    add("another. If A names B forty times, A is where B is argued with, and that")
    add(f"passage is what a draft needs. Covers all {len(papers)} entries in")
    add("`literature/refs.bib`. Generated by `uv run scripts/build_xrefs.py` from the")
    add("parsed Markdown in `literature/corpus/`; regenerate after adding a publication.")
    add("**Do not edit by hand.**")
    add("")
    add(f"{total} edges. A number in parentheses is how often the citing paper *names* the")
    add("cited one in its prose — a reference-list row scores 1, a paper argued with")
    add("scores much higher. That gap is usually the interesting part.")
    add("")
    add("## Read this before quoting any number here")
    add("")
    add("- **Citation is not comparison, and neither is endorsement.** That A cites B says")
    add("  nothing about whether A benchmarks against B, agrees with it, or refutes it.")
    add("  Only reading the passage settles that.")
    add("- **In-degree is confounded by age.** A recent publication has had no time to")
    add("  be cited, so a low count means *too new*, not *minor*. Never size a section or")
    add("  set a tier from these counts.")
    add("- **This is corpus-internal.** Counts are citations from within these")
    add(f"  {len(papers)} publications, not from the literature. A work the field leans on")
    add("  heavily will still score low here if the corpus does not happen to contain")
    add("  the papers citing it.")
    add("- **Years are the cataloged version's.** An entry upgraded from preprint to")
    add("  journal carries the journal year, so a paper may legitimately cite something")
    add("  that looks newer than itself — it cited the preprint.")
    add("")

    older = sorted(k for k in papers if not cited_by.get(k) and papers[k]["year"] < this_year)
    add("## Uncited despite having had time")
    add("")
    add(f"Nothing in the corpus cites these {len(older)}, and they are not new enough for")
    add("that to be an artifact of publication date — worth a sentence in the draft that")
    add("covers them. Papers from this year are omitted: their zero carries no signal.")
    add("")
    add("".join(f"- `{k}` ({section_of(papers[k])}, {papers[k]['year']})\n" for k in older) or "- none\n")

    add("## Per publication")
    add("")
    for key in sorted(papers, key=lambda k: (section_of(papers[k]), k)):
        paper = papers[key]
        add(f"### `{key}` — {section_of(paper)}, {paper['year']}")
        add("")
        add(f"*{paper['title']}* · `{paper['doi']}`")
        add("")
        for label, table in (("Cites", edges.get(key, {})), ("Cited by", cited_by.get(key, {}))):
            if table:
                listed = ", ".join(
                    f"`{k}`" + (f" ({n})" if n > 1 else "")
                    for k, n in sorted(table.items(), key=lambda kv: (-kv[1], kv[0]))
                )
                add(f"- **{label} ({len(table)}):** {listed}")
            else:
                add(f"- **{label} (0):** —")
        add("")

    if missing:
        add("## Not analysed")
        add("")
        add("Cataloged but with no parsed Markdown in `literature/corpus/`, so they")
        add("neither cite nor are counted as citing:")
        add("")
        add("".join(f"- `{k}`\n" for k in missing))

    return "\n".join(out)


def main() -> int:
    parser = ArgumentParser(description="Build literature/xrefs.md from the parsed corpus.")
    parser.add_argument(
        "--stdout", action="store_true", help="print the result instead of writing the file"
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    corpus = repo_root / "literature" / "corpus"
    if not corpus.is_dir():
        parser.error(f"corpus directory not found: {corpus}")

    papers = load_catalog(repo_root)
    load_sections(repo_root, papers)
    missing = sorted(
        key
        for key, paper in papers.items()
        if not (corpus / (paper["doi"].replace("/", "__") + ".md")).exists()
    )
    edges = build_edges(papers, corpus)
    rendered = render(papers, edges, missing)

    if args.stdout:
        print(rendered)
    else:
        out = repo_root / "literature" / "xrefs.md"
        out.write_text(rendered)
        total = sum(len(t) for t in edges.values())
        print(f"wrote {out.relative_to(repo_root)}: {len(papers)} publications, {total} edges")
        if missing:
            print(f"  {len(missing)} cataloged without parsed text: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
