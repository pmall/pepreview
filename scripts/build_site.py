#!/usr/bin/env python3
"""Build a clean, single-column, print-ready HTML article in `site/`.

Uses only the Python standard library so both local builds and GitHub Actions
can run `python3 scripts/build_site.py` with zero external dependencies.
"""

from __future__ import annotations

import html
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT_DIR = ROOT / "draft"
MANUSCRIPT_PATH = DRAFT_DIR / "manuscript.md"
BIB_PATH = ROOT / "literature" / "refs.bib"
SITE_DIR = ROOT / "site"

STATIC_ASSETS = [
    "wada-kujaku.css",
    "article.css",
    "fig1_cofolding_architecture.svg",
    "fig2_design_workflows.svg",
]

# Proportional column widths summing to 100% for clean wrapping on screen and PDF.
TABLE_COL_WIDTHS: dict[int, list[str]] = {
    1: ["16%", "15%", "15%", "25%", "16%", "13%"],
    2: ["14%", "18%", "13%", "30%", "25%"],
}

# ---------------------------------------------------------------------------
# BibTeX parsing & LaTeX accent decoding
# ---------------------------------------------------------------------------

LATEX_COMBINING: dict[str, str] = {
    "`": "\u0300",
    "'": "\u0301",
    "^": "\u0302",
    '"': "\u0308",
    "~": "\u0303",
    "=": "\u0304",
    ".": "\u0307",
    "u": "\u0306",
    "v": "\u030c",
    "H": "\u030b",
    "c": "\u0327",
    "r": "\u030a",
}


def decode_latex(text: str) -> str:
    """Decode common BibTeX/LaTeX diacritics and dashes into clean Unicode."""
    s = text

    def _combine(accent: str, char: str) -> str:
        comb = LATEX_COMBINING.get(accent)
        return unicodedata.normalize("NFC", char + comb) if comb else char

    s = re.sub(
        r"\{\\([`'^\"~=.uvHcr])\{([A-Za-z])\}\}",
        lambda m: _combine(m.group(1), m.group(2)),
        s,
    )
    s = re.sub(
        r"\{\\([`'^\"~=.uvHcr])\s*([A-Za-z])\}",
        lambda m: _combine(m.group(1), m.group(2)),
        s,
    )
    s = re.sub(
        r"\\([`'^\"~=.uvHcr])\{([A-Za-z])\}",
        lambda m: _combine(m.group(1), m.group(2)),
        s,
    )
    s = re.sub(
        r"\\([`'^\"~=.])([A-Za-z])",
        lambda m: _combine(m.group(1), m.group(2)),
        s,
    )

    s = s.replace(r"\&", "&").replace(r"\%", "%").replace(r"\_", "_")
    s = s.replace(" --- ", " \u2013 ").replace("---", "\u2013").replace("--", "\u2013")
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def _split_top_level_and(raw_authors: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    buf: list[str] = []
    i = 0
    n = len(raw_authors)
    while i < n:
        ch = raw_authors[i]
        if ch == "{":
            depth += 1
            buf.append(ch)
            i += 1
        elif ch == "}":
            depth = max(0, depth - 1)
            buf.append(ch)
            i += 1
        elif depth == 0 and raw_authors[i : i + 5].lower() == " and ":
            parts.append("".join(buf).strip())
            buf = []
            i += 5
        else:
            buf.append(ch)
            i += 1
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _format_single_author(raw: str) -> str:
    stripped = raw.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        depth = 0
        matched_whole = True
        for idx, ch in enumerate(stripped):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and idx < len(stripped) - 1:
                    matched_whole = False
                    break
        if matched_whole:
            return decode_latex(stripped[1:-1])

    decoded = decode_latex(stripped)
    if "," in decoded:
        family, given = [p.strip() for p in decoded.split(",", 1)]
        initials_parts: list[str] = []
        for token in re.split(r"\s+", given):
            token_clean = token.replace(".", "").strip()
            if not token_clean:
                continue
            initials_parts.extend(sub[0].upper() for sub in token_clean.split("-") if sub)
        return f"{family} {''.join(initials_parts)}".strip()

    tokens = decoded.split()
    if len(tokens) >= 2:
        return f"{tokens[-1]} {''.join(t[0].upper() for t in tokens[:-1] if t)}"
    return decoded


def format_vancouver_authors(raw_authors: str, max_authors: int = 6) -> str:
    normalized = re.sub(r"\s+", " ", raw_authors).strip()
    authors = [_format_single_author(a) for a in _split_top_level_and(normalized)]
    if len(authors) > max_authors:
        return ", ".join(authors[:max_authors]) + ", et al."
    return ", ".join(authors)


def parse_bibtex(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    i = 0
    n = len(text)

    while i < n:
        at = text.find("@", i)
        if at == -1:
            break
        m = re.match(r"@([A-Za-z]+)\s*\{\s*([^,\s]+)\s*,", text[at:])
        if not m:
            i = at + 1
            continue
        entry_type = m.group(1).lower()
        key = m.group(2).strip()
        pos = at + m.end()

        depth = 1
        start_body = pos
        while pos < n and depth > 0:
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
            pos += 1
        body = text[start_body : pos - 1]
        i = pos

        fields: dict[str, str] = {"entry_type": entry_type, "key": key}
        fp = 0
        bn = len(body)
        while fp < bn:
            while fp < bn and body[fp] in " \t\r\n,":
                fp += 1
            if fp >= bn:
                break
            fm = re.match(r"([A-Za-z0-9_-]+)\s*=\s*", body[fp:])
            if not fm:
                break
            fname = fm.group(1).lower()
            fp += fm.end()
            if fp >= bn:
                break
            if body[fp] == "{":
                fp += 1
                fstart = fp
                fdepth = 1
                while fp < bn and fdepth > 0:
                    if body[fp] == "{":
                        fdepth += 1
                    elif body[fp] == "}":
                        fdepth -= 1
                    fp += 1
                fval = body[fstart : fp - 1]
            elif body[fp] == '"':
                fp += 1
                fstart = fp
                while fp < bn and body[fp] != '"':
                    fp += 2 if body[fp] == "\\" and fp + 1 < bn else 1
                fval = body[fstart:fp]
                fp += 1
            else:
                fstart = fp
                while fp < bn and body[fp] not in ",\r\n":
                    fp += 1
                fval = body[fstart:fp].strip()
            fields[fname] = fval.strip()

        entries[key] = fields
    return entries


def format_vancouver_entry(entry: dict[str, str]) -> str:
    authors = format_vancouver_authors(entry.get("author", ""))
    title = decode_latex(entry.get("title", "")).rstrip(".")
    year = decode_latex(entry.get("year", ""))
    etype = entry.get("entry_type", "misc")
    doi = entry.get("doi", "").strip()

    if etype == "article":
        journal = html.escape(decode_latex(entry.get("journal", "")))
        vol = decode_latex(entry.get("volume", ""))
        num = decode_latex(entry.get("number", ""))
        pages = decode_latex(entry.get("pages", ""))
        if pages and "-" in pages and "\u2013" not in pages:
            pages = pages.replace("-", "\u2013")

        bib_tail = year
        if vol:
            bib_tail += f";{html.escape(vol)}"
            if num:
                bib_tail += f"({html.escape(num)})"
            if pages:
                bib_tail += f":{html.escape(pages)}"
        elif pages:
            bib_tail += f":{html.escape(pages)}"
        venue_html = f"<em>{journal}</em>. {bib_tail}."
    elif etype == "inproceedings":
        booktitle = html.escape(decode_latex(entry.get("booktitle", "")))
        series = decode_latex(entry.get("series", ""))
        vol = decode_latex(entry.get("volume", ""))
        extra = f" ({html.escape(series)} {html.escape(vol)})" if series and vol else ""
        venue_html = f"In: <em>{booktitle}</em>{extra}; {html.escape(year)}."
    else:
        howpub = decode_latex(entry.get("howpublished", ""))
        archive = decode_latex(entry.get("archiveprefix", ""))
        eprint = decode_latex(entry.get("eprint", ""))
        if "biorxiv" in howpub.lower():
            venue_html = f"<em>bioRxiv</em> [Preprint]. {html.escape(year)}."
        elif archive.lower() == "arxiv" and eprint:
            venue_html = f"<em>arXiv</em>:{html.escape(eprint)} [Preprint]. {html.escape(year)}."
        elif "zenodo" in howpub.lower():
            venue_html = f"<em>Zenodo</em> [Software]. {html.escape(year)}."
        elif howpub:
            venue_html = f"<em>{html.escape(howpub)}</em>. {html.escape(year)}."
        else:
            venue_html = f"Preprint. {html.escape(year)}."

    parts = [
        f"{html.escape(authors.rstrip('.'))}.",
        f"{html.escape(title)}.",
        venue_html,
    ]
    if doi:
        doi_esc = html.escape(doi)
        parts.append(
            f'<a class="doi-link" href="https://doi.org/{doi_esc}" '
            f'target="_blank" rel="noopener noreferrer">doi:{doi_esc}</a>'
        )
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Citations & inline Markdown
# ---------------------------------------------------------------------------


class CitationManager:
    def __init__(self, bib: dict[str, dict[str, str]]) -> None:
        self.bib = bib
        self.key_to_num: dict[str, int] = {}
        self.ordered_keys: list[str] = []

    def register(self, key: str) -> int:
        if key not in self.bib:
            raise KeyError(f"Citation key @{key} not found in {BIB_PATH}")
        if key not in self.key_to_num:
            num = len(self.ordered_keys) + 1
            self.key_to_num[key] = num
            self.ordered_keys.append(key)
        return self.key_to_num[key]

    def render_bracket(self, keys: list[str]) -> str:
        nums = sorted({self.register(k) for k in keys})
        groups: list[list[int]] = []
        for num in nums:
            if not groups or num != groups[-1][-1] + 1:
                groups.append([num])
            else:
                groups[-1].append(num)

        pieces: list[str] = []
        for grp in groups:
            if len(grp) >= 3:
                a, b = grp[0], grp[-1]
                pieces.append(
                    f'<a class="cite-link" href="#ref-{a}">{a}</a>'
                    f"\u2013"
                    f'<a class="cite-link" href="#ref-{b}">{b}</a>'
                )
            else:
                for num in grp:
                    pieces.append(f'<a class="cite-link" href="#ref-{num}">{num}</a>')
        return f'<span class="cite">[{", ".join(pieces)}]</span>'


def _render_math(expr: str) -> str:
    e = expr.strip()
    if e == "20^L":
        return '<span class="math">20<sup><em>L</em></sup></span>'
    if e == "K_D":
        return '<span class="math"><em>K</em><sub>D</sub></span>'
    m_sup = re.fullmatch(r"([A-Za-z0-9]+)\^\{?([A-Za-z0-9+-]+)\}?", e)
    if m_sup:
        base, sup = m_sup.group(1), m_sup.group(2)
        base_html = f"<em>{base}</em>" if base.isalpha() else base
        sup_html = f"<em>{sup}</em>" if sup.isalpha() else sup
        return f'<span class="math">{base_html}<sup>{sup_html}</sup></span>'
    m_sub = re.fullmatch(r"([A-Za-z0-9]+)_\{?([A-Za-z0-9+-]+)\}?", e)
    if m_sub:
        base, sub = m_sub.group(1), m_sub.group(2)
        base_html = f"<em>{base}</em>" if base.isalpha() else base
        return f'<span class="math">{base_html}<sub>{sub}</sub></span>'
    return f'<span class="math">{html.escape(e)}</span>'


def unescape_mdformat(text: str) -> str:
    return (
        text.replace(r"\[", "[")
        .replace(r"\]", "]")
        .replace(r"\<", "<")
        .replace(r"\>", ">")
    )


def render_inline(text: str, cites: CitationManager) -> str:
    s = unescape_mdformat(text)
    placeholders: list[str] = []

    def _stash(fragment: str) -> str:
        idx = len(placeholders)
        placeholders.append(fragment)
        return f"\x00PH{idx}\x00"

    def _cite_sub(m: re.Match[str]) -> str:
        keys = re.findall(r"@([A-Za-z0-9_:-]+)", m.group(1))
        return _stash(cites.render_bracket(keys)) if keys else m.group(0)

    s = re.sub(r"\[(@[A-Za-z0-9_:-]+(?:\s*;\s*@[A-Za-z0-9_:-]+)*)\]", _cite_sub, s)
    s = re.sub(r"\$([^$\n]+)\$", lambda m: _stash(_render_math(m.group(1))), s)
    s = re.sub(
        r"`([^`\n]+)`",
        lambda m: _stash(f"<code>{html.escape(m.group(1))}</code>"),
        s,
    )
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+?)\*", r"<em>\1</em>", s)

    for idx, frag in enumerate(placeholders):
        s = s.replace(f"\x00PH{idx}\x00", frag)
    return s


# ---------------------------------------------------------------------------
# Manuscript parsing & HTML generation
# ---------------------------------------------------------------------------


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"


def parse_table_rows(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    def split_row(line: str) -> list[str]:
        stripped = line.strip()
        if stripped.startswith("|"):
            stripped = stripped[1:]
        if stripped.endswith("|"):
            stripped = stripped[:-1]
        return [cell.strip() for cell in stripped.split("|")]

    headers = split_row(lines[0])
    rows = [split_row(ln) for ln in lines[2:] if ln.strip()]
    return headers, rows


def build_html() -> tuple[str, dict[str, int]]:
    bib = parse_bibtex(BIB_PATH)
    cites = CitationManager(bib)
    raw_lines = MANUSCRIPT_PATH.read_text(encoding="utf-8").splitlines()

    blocks: list[dict[str, object]] = []
    i = 0
    n = len(raw_lines)
    while i < n:
        stripped = raw_lines[i].strip()
        if not stripped:
            i += 1
            continue

        hm = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if hm:
            blocks.append(
                {"type": "heading", "level": len(hm.group(1)), "text": hm.group(2).strip()}
            )
            i += 1
            continue

        im = re.match(r"^!\[(.*?)\]\((.*?)\)$", stripped)
        if im:
            blocks.append(
                {"type": "image", "alt": im.group(1).strip(), "src": im.group(2).strip()}
            )
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < n and re.match(
            r"^\|[\s:|-]+\|$", raw_lines[i + 1].strip()
        ):
            tlines: list[str] = []
            while i < n and raw_lines[i].strip().startswith("|"):
                tlines.append(raw_lines[i])
                i += 1
            headers, rows = parse_table_rows(tlines)
            blocks.append({"type": "table", "headers": headers, "rows": rows})
            continue

        plines: list[str] = []
        while i < n:
            cur = raw_lines[i].strip()
            if (
                not cur
                or re.match(r"^#{1,4}\s+", cur)
                or re.match(r"^!\[.*?\]\(.*?\)$", cur)
                or cur.startswith("|")
            ):
                break
            plines.append(cur)
            i += 1
        blocks.append({"type": "paragraph", "text": " ".join(plines)})

    title = ""
    subtitle_note = ""
    start_idx = 0
    if blocks and blocks[0]["type"] == "heading" and blocks[0]["level"] == 1:
        title = str(blocks[0]["text"])
        start_idx = 1
        if (
            start_idx < len(blocks)
            and blocks[start_idx]["type"] == "paragraph"
            and str(blocks[start_idx]["text"]).startswith("*")
            and str(blocks[start_idx]["text"]).endswith("*")
        ):
            subtitle_note = str(blocks[start_idx]["text"])
            start_idx += 1

    body_parts: list[str] = []
    current_h2 = ""
    in_section = False
    fig_count = 0
    table_count = 0

    idx = start_idx
    while idx < len(blocks):
        blk = blocks[idx]
        btype = blk["type"]

        if btype == "heading":
            level = int(blk["level"])
            htext = str(blk["text"])
            slug = slugify(htext)

            if level == 2:
                if in_section:
                    body_parts.append("</section>")
                current_h2 = htext.lower()
                in_section = True
                sec_cls = (
                    "article-section abstract-section"
                    if current_h2 == "abstract"
                    else "article-section"
                )
                body_parts.append(f'<section id="{slug}" class="{sec_cls}">')
                body_parts.append(f"<h2>{html.escape(htext)}</h2>")
            elif level == 3:
                body_parts.append(f'<h3 id="{slug}">{html.escape(htext)}</h3>')
            else:
                body_parts.append(f'<h4 id="{slug}">{html.escape(htext)}</h4>')
            idx += 1
            continue

        if current_h2 == "references":
            idx += 1
            continue

        if btype == "image":
            fig_count += 1
            src = html.escape(str(blk["src"]))
            alt = html.escape(str(blk["alt"]))
            caption_html = ""
            if idx + 1 < len(blocks) and blocks[idx + 1]["type"] == "paragraph":
                next_text = str(blocks[idx + 1]["text"])
                if next_text.startswith("**Fig "):
                    caption_html = render_inline(next_text, cites)
                    idx += 1
            body_parts.append(
                f'<figure id="fig-{fig_count}" class="article-figure">'
                f'<div class="figure-plate">'
                f'<img src="{src}" alt="{alt}">'
                f"</div>"
                f"<figcaption>{caption_html}</figcaption>"
                f"</figure>"
            )
            idx += 1
            continue

        if (
            btype == "paragraph"
            and str(blk["text"]).startswith("**Table ")
            and idx + 1 < len(blocks)
            and blocks[idx + 1]["type"] == "table"
        ):
            table_count += 1
            cap_html = render_inline(str(blk["text"]), cites)
            tbl = blocks[idx + 1]
            headers = list(tbl["headers"])  # type: ignore[arg-type]
            rows = list(tbl["rows"])  # type: ignore[arg-type]
            ncols = len(headers)

            col_widths = TABLE_COL_WIDTHS.get(table_count, [])
            colgroup = (
                "<colgroup>"
                + "".join(f'<col style="width: {w};">' for w in col_widths)
                + "</colgroup>"
                if len(col_widths) == ncols
                else ""
            )

            thead_cells = "".join(
                f'<th scope="col">{render_inline(h, cites)}</th>' for h in headers
            )

            tbody_rows: list[str] = []
            stripe_idx = 0
            for r in rows:
                cells = r + [""] * (ncols - len(r))
                if (
                    cells[0].startswith("**")
                    and cells[0].endswith("**")
                    and all(not c.strip() for c in cells[1:])
                ):
                    group_label = cells[0][2:-2].strip()
                    tbody_rows.append(
                        f'<tr class="table-group-row">'
                        f'<td colspan="{ncols}">{html.escape(group_label)}</td>'
                        f"</tr>"
                    )
                    stripe_idx = 0
                else:
                    stripe_cls = "row-even" if stripe_idx % 2 == 1 else "row-odd"
                    stripe_idx += 1
                    td_html = []
                    for c_idx, cell in enumerate(cells[:ncols]):
                        cls = ' class="col-system"' if c_idx == 0 else ""
                        td_html.append(f"<td{cls}>{render_inline(cell, cites)}</td>")
                    tbody_rows.append(
                        f'<tr class="data-row {stripe_cls}">{"".join(td_html)}</tr>'
                    )

            body_parts.append(
                f'<div id="table-{table_count}" class="table-block">'
                f'<p class="table-caption">{cap_html}</p>'
                f'<table class="data-table">'
                f"{colgroup}"
                f"<thead><tr>{thead_cells}</tr></thead>"
                f"<tbody>{''.join(tbody_rows)}</tbody>"
                f"</table>"
                f"</div>"
            )
            idx += 2
            continue

        if btype == "paragraph":
            body_parts.append(f"<p>{render_inline(str(blk['text']), cites)}</p>")
            idx += 1
            continue

        idx += 1

    if current_h2 == "references":
        ref_items = [
            f'<li id="ref-{num}" value="{num}">{format_vancouver_entry(bib[key])}</li>'
            for num, key in enumerate(cites.ordered_keys, start=1)
        ]
        body_parts.append(f'<ol class="reference-list">{"".join(ref_items)}</ol>')

    if in_section:
        body_parts.append("</section>")

    subtitle_html = (
        f'<p class="article-subtitle">{render_inline(subtitle_note, cites)}</p>'
        if subtitle_note
        else ""
    )

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="wada-kujaku.css">
  <link rel="stylesheet" href="article.css">
</head>
<body>
  <article class="article">
    <header class="article-header">
      <h1>{html.escape(title)}</h1>
      {subtitle_html}
    </header>
    {"".join(body_parts)}
  </article>
</body>
</html>
"""
    return document, {
        "figures": fig_count,
        "tables": table_count,
        "references": len(cites.ordered_keys),
    }


def main() -> int:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    html_text, stats = build_html()
    (SITE_DIR / "index.html").write_text(html_text, encoding="utf-8")
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")

    for asset in STATIC_ASSETS:
        src = DRAFT_DIR / asset
        if not src.exists():
            print(f"ERROR: Missing asset {src}", file=sys.stderr)
            return 1
        shutil.copy2(src, SITE_DIR / asset)

    print(
        f"Built {SITE_DIR / 'index.html'} "
        f"({stats['figures']} figures, {stats['tables']} tables, {stats['references']} references)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
