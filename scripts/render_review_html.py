#!/usr/bin/env python3
"""Render draft/manuscript.md into an interactive sentence-coded HTML review sheet.

Usage:
    .venv/bin/python scripts/render_review_html.py [--done P01 ...] [--undone P01 ...]
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

SKIP_SECTIONS = {"acknowledgments", "references"}

# Abbreviations whose trailing period does not terminate a sentence.
ABBREVIATIONS = {
    "al.",
    "e.g.",
    "i.e.",
    "vs.",
    "fig.",
    "figs.",
    "eq.",
    "eqs.",
    "no.",
    "dr.",
    "prof.",
    "cf.",
    "ca.",
    "approx.",
    "ref.",
    "refs.",
    "sec.",
    "st.",
    "mr.",
    "mrs.",
    "ms.",
}


@dataclass
class Paragraph:
    code: str
    raw_text: str
    sentences: list[tuple[str, str]]  # (sentence_code, sentence_text)
    word_count: int


@dataclass
class Subsection:
    title: str
    anchor: str
    paragraphs: list[Paragraph] = field(default_factory=list)


@dataclass
class Section:
    title: str
    anchor: str
    paragraphs: list[Paragraph] = field(default_factory=list)
    subsections: list[Subsection] = field(default_factory=list)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def split_sentences(text: str) -> list[str]:
    """Split an unwrapped prose paragraph into individual sentences."""
    normalized = text.replace(r"\[", "[").replace(r"\]", "]").replace(r"\<", "<").replace(r"\>", ">")

    sentences: list[str] = []
    start = 0
    n = len(normalized)
    i = 0

    while i < n:
        ch = normalized[i]
        if ch in ".?!":
            end = i + 1
            while end < n and normalized[end] in "\"')]}":
                end += 1

            if end < n and not normalized[end].isspace():
                i += 1
                continue

            if ch == ".":
                token_match = re.search(r"([A-Za-z.]+)$", normalized[start : i + 1])
                if token_match:
                    token = token_match.group(1).lower()
                    if token in ABBREVIATIONS or re.fullmatch(r"(?:[a-z]\.){2,}", token):
                        i += 1
                        continue

            nxt = end
            while nxt < n and normalized[nxt].isspace():
                nxt += 1

            if nxt >= n:
                sentences.append(normalized[start:end].strip())
                start = n
                break

            if normalized[nxt].isupper() or normalized[nxt] in "\"'(*$0123456789":
                sentences.append(normalized[start:end].strip())
                start = nxt
                i = nxt
                continue

        i += 1

    if start < n:
        tail = normalized[start:].strip()
        if tail:
            sentences.append(tail)

    return sentences


def count_words(text: str) -> int:
    cleaned = re.sub(r"\\?\[@[^\]]+\\?\]", "", text)
    return len(cleaned.split())


def format_inline_html(text: str) -> str:
    """Convert light Markdown/LaTeX/Pandoc-citation syntax in a sentence to clean HTML."""
    escaped = html.escape(text)

    def render_math(match: re.Match[str]) -> str:
        expr = match.group(1)
        expr = re.sub(r"\^\{([^}]+)\}", r"<sup>\1</sup>", expr)
        expr = re.sub(r"\^([A-Za-z0-9+-])", r"<sup>\1</sup>", expr)
        expr = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", expr)
        expr = re.sub(r"_([A-Za-z0-9+-])", r"<sub>\1</sub>", expr)
        return f'<span class="math">{expr}</span>'

    escaped = re.sub(r"\$([^$]+)\$", render_math, escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"(\[@[^\]]+\])",
        r'<span class="cite">\1</span>',
        escaped,
    )

    return escaped


def parse_manuscript(md_text: str) -> tuple[str, list[Section]]:
    """Parse manuscript Markdown into sections, subsections, and coded paragraphs."""
    lines = md_text.splitlines()
    title = "Manuscript Review"
    sections: list[Section] = []
    current_section: Section | None = None
    current_subsection: Subsection | None = None
    skip_section = False

    para_idx = 0
    buf: list[str] = []

    def flush_paragraph() -> None:
        nonlocal para_idx, buf
        if not buf or skip_section or current_section is None:
            buf = []
            return

        joined = " ".join(line.strip() for line in buf if line.strip())
        buf = []
        if not joined:
            return

        if (
            joined.startswith("**Fig ")
            or joined.startswith("**Table ")
            or joined.startswith("![")
            or joined.startswith("|")
            or (joined.startswith("*") and joined.endswith("*") and "Draft Review Manuscript" in joined)
        ):
            return

        para_idx += 1
        p_code = f"P{para_idx:02d}"
        raw_sentences = split_sentences(joined)
        coded_sentences = [(f"{p_code}.{s_idx}", s) for s_idx, s in enumerate(raw_sentences, start=1)]
        para = Paragraph(
            code=p_code,
            raw_text=joined,
            sentences=coded_sentences,
            word_count=count_words(joined),
        )
        if current_subsection is not None:
            current_subsection.paragraphs.append(para)
        else:
            current_section.paragraphs.append(para)

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            title = stripped[2:].strip()
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            sec_title = stripped[3:].strip()
            if sec_title.lower() in SKIP_SECTIONS:
                skip_section = True
                current_section = None
                current_subsection = None
            else:
                skip_section = False
                current_section = Section(title=sec_title, anchor=slugify(sec_title))
                current_subsection = None
                sections.append(current_section)
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            if not skip_section and current_section is not None:
                sub_title = stripped[4:].strip()
                current_subsection = Subsection(
                    title=sub_title,
                    anchor=f"{current_section.anchor}-{slugify(sub_title)}",
                )
                current_section.subsections.append(current_subsection)
            continue

        if stripped.startswith("|"):
            flush_paragraph()
            continue

        buf.append(stripped)

    flush_paragraph()
    return title, sections


def load_done_set(status_path: Path) -> set[str]:
    if not status_path.exists():
        return set()
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return {code.upper() for code in data.get("done", [])}


def save_done_set(status_path: Path, done_set: set[str]) -> None:
    def sort_key(code: str) -> tuple[int, str]:
        m = re.fullmatch(r"P(\d+)", code)
        return (int(m.group(1)), code) if m else (10**9, code)

    payload = {"done": sorted(done_set, key=sort_key)}
    status_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def render_paragraph_html(para: Paragraph, is_done: bool) -> str:
    rows = []
    for s_code, s_text in para.sentences:
        s_html = format_inline_html(s_text)
        rows.append(
            f'      <div class="sentence-row" id="{s_code}">\n'
            f'        <button class="code sentence-code" data-copy="{s_code}" title="Copy {s_code}">{s_code}</button>\n'
            f'        <div class="sentence-text">{s_html}</div>\n'
            f"      </div>"
        )
    rows_html = "\n".join(rows)
    s_label = "sentence" if len(para.sentences) == 1 else "sentences"
    done_cls = " is-done" if is_done else ""
    checked_attr = " checked" if is_done else ""
    status_badge = '<span class="done-badge">Reviewed</span>' if is_done else ""

    return (
        f'    <article class="paragraph-block{done_cls}" id="{para.code}">\n'
        f'      <header class="paragraph-header">\n'
        f'        <div class="para-left">\n'
        f'          <input type="checkbox" class="para-checkbox" aria-label="Review status for {para.code}"{checked_attr} disabled />\n'
        f'          <button class="code para-code" data-copy="{para.code}" title="Copy {para.code}">{para.code}</button>\n'
        f"          {status_badge}\n"
        f"        </div>\n"
        f'        <span class="para-meta">{len(para.sentences)} {s_label} &middot; ~{para.word_count} words</span>\n'
        f"      </header>\n"
        f'      <div class="sentences">\n'
        f"{rows_html}\n"
        f"      </div>\n"
        f"    </article>"
    )


def paragraph_range(paragraphs: list[Paragraph]) -> str:
    if not paragraphs:
        return ""
    if len(paragraphs) == 1:
        return paragraphs[0].code
    return f"{paragraphs[0].code}&ndash;{paragraphs[-1].code}"


def render_html(
    title: str,
    sections: list[Section],
    source_path: str,
    done_set: set[str],
) -> str:
    all_paras = [
        p
        for sec in sections
        for p in ([*sec.paragraphs] + [sp for sub in sec.subsections for sp in sub.paragraphs])
    ]
    total_paras = len(all_paras)
    done_count = sum(1 for p in all_paras if p.code in done_set)
    total_sentences = sum(len(p.sentences) for p in all_paras)
    total_words = sum(p.word_count for p in all_paras)

    toc_items: list[str] = []
    body_parts: list[str] = []

    for sec in sections:
        sec_all_paras = [*sec.paragraphs] + [sp for sub in sec.subsections for sp in sub.paragraphs]
        sec_range = paragraph_range(sec_all_paras)
        sec_done = all(p.code in done_set for p in sec_all_paras) and bool(sec_all_paras)
        sec_done_cls = " toc-done" if sec_done else ""
        toc_items.append(
            f'        <li class="toc-sec{sec_done_cls}"><a href="#{sec.anchor}">'
            f'<span>{html.escape(sec.title)}</span>'
            f'<span class="toc-range">{sec_range}</span></a>'
        )
        if sec.subsections:
            toc_items.append('          <ul class="toc-sub-list">')
            for sub in sec.subsections:
                sub_range = paragraph_range(sub.paragraphs)
                sub_done = all(p.code in done_set for p in sub.paragraphs) and bool(sub.paragraphs)
                sub_done_cls = " toc-done" if sub_done else ""
                toc_items.append(
                    f'            <li class="toc-sub{sub_done_cls}"><a href="#{sub.anchor}">'
                    f'<span>{html.escape(sub.title)}</span>'
                    f'<span class="toc-range">{sub_range}</span></a></li>'
                )
            toc_items.append("          </ul>")
        toc_items.append("        </li>")

        sec_chunks = [f'  <section class="manuscript-section" id="{sec.anchor}">']
        sec_chunks.append(f'    <h2>{html.escape(sec.title)}</h2>')
        for p in sec.paragraphs:
            sec_chunks.append(render_paragraph_html(p, p.code in done_set))
        for sub in sec.subsections:
            sec_chunks.append(f'    <div class="manuscript-subsection" id="{sub.anchor}">')
            sec_chunks.append(f'      <h3>{html.escape(sub.title)}</h3>')
            for p in sub.paragraphs:
                sec_chunks.append(render_paragraph_html(p, p.code in done_set))
            sec_chunks.append("    </div>")
        sec_chunks.append("  </section>")
        body_parts.append("\n".join(sec_chunks))

    toc_html = "\n".join(toc_items)
    sections_html = "\n\n".join(body_parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)} — Sentence Review</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --surface: #ffffff;
      --border: #dfe3ea;
      --border-soft: #eef1f5;
      --text: #1c2430;
      --muted: #606d80;
      --accent: #1d4ed8;
      --accent-bg: #eff4ff;
      --para-bg: #1e293b;
      --para-fg: #ffffff;
      --done: #15803d;
      --done-bg: #f0fdf4;
      --done-border: #bbf7d0;
      --cite-fg: #3b5998;
      --cite-bg: #f1f5fb;
      --hover-row: #f8fafc;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
      --serif: Georgia, "Times New Roman", serif;
    }}

    * {{
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: var(--sans);
      line-height: 1.6;
    }}

    .layout {{
      display: grid;
      grid-template-columns: 300px minmax(0, 1fr);
      min-height: 100vh;
    }}

    .sidebar {{
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
      background: var(--surface);
      border-right: 1px solid var(--border);
      padding: 1.25rem 1rem 2rem;
    }}

    .sidebar-title {{
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin: 0 0 0.75rem;
    }}

    .stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-bottom: 1rem;
      padding-bottom: 0.9rem;
      border-bottom: 1px solid var(--border-soft);
      font-size: 0.78rem;
      color: var(--muted);
    }}

    .stat-pill {{
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.15rem 0.55rem;
      font-family: var(--mono);
    }}

    .stat-pill.progress {{
      background: var(--done-bg);
      border-color: var(--done-border);
      color: var(--done);
      font-weight: 600;
    }}

    .toc-list, .toc-sub-list {{
      list-style: none;
      margin: 0;
      padding: 0;
    }}

    .toc-sec > a, .toc-sub > a {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 0.5rem;
      text-decoration: none;
      color: var(--text);
      padding: 0.32rem 0.45rem;
      border-radius: 6px;
      font-size: 0.85rem;
    }}

    .toc-sec > a {{
      font-weight: 600;
      margin-top: 0.25rem;
    }}

    .toc-sub-list {{
      padding-left: 0.75rem;
    }}

    .toc-sub > a {{
      font-weight: 400;
      color: var(--muted);
      font-size: 0.8rem;
    }}

    .toc-done > a {{
      color: var(--done);
    }}

    .toc-sec > a:hover, .toc-sub > a:hover {{
      background: var(--accent-bg);
      color: var(--accent);
    }}

    .toc-range {{
      font-family: var(--mono);
      font-size: 0.72rem;
      color: var(--muted);
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .main {{
      max-width: 960px;
      width: 100%;
      margin: 0 auto;
      padding: 2rem 2.25rem 5rem;
    }}

    .doc-header {{
      margin-bottom: 2rem;
      padding-bottom: 1.25rem;
      border-bottom: 2px solid var(--border);
    }}

    .doc-header h1 {{
      margin: 0 0 0.5rem;
      font-size: 1.75rem;
      line-height: 1.25;
      letter-spacing: -0.01em;
    }}

    .doc-note {{
      margin: 0;
      font-size: 0.88rem;
      color: var(--muted);
    }}

    .manuscript-section {{
      margin-top: 2.25rem;
    }}

    .manuscript-section > h2 {{
      font-size: 1.35rem;
      margin: 0 0 1rem;
      padding-bottom: 0.35rem;
      border-bottom: 1px solid var(--border);
      color: #0f172a;
    }}

    .manuscript-subsection {{
      margin-top: 1.65rem;
    }}

    .manuscript-subsection > h3 {{
      font-size: 1.05rem;
      margin: 0 0 0.85rem;
      color: #334155;
    }}

    .paragraph-block {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      margin-bottom: 1.15rem;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
      overflow: hidden;
    }}

    .paragraph-block.is-done {{
      border-color: var(--done-border);
    }}

    .paragraph-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.55rem 0.9rem;
      background: #f8fafc;
      border-bottom: 1px solid var(--border-soft);
    }}

    .paragraph-block.is-done .paragraph-header {{
      background: var(--done-bg);
      border-bottom-color: var(--done-border);
    }}

    .para-left {{
      display: flex;
      align-items: center;
      gap: 0.55rem;
    }}

    .para-checkbox {{
      appearance: none;
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      margin: 0;
      border: 2px solid #94a3b8;
      border-radius: 4px;
      background: #ffffff;
      display: inline-grid;
      place-content: center;
      flex-shrink: 0;
      cursor: default;
    }}

    .para-checkbox:checked {{
      background: var(--done);
      border-color: var(--done);
    }}

    .para-checkbox:checked::after {{
      content: "";
      width: 5px;
      height: 9px;
      border: solid #ffffff;
      border-width: 0 2.2px 2.2px 0;
      transform: rotate(45deg) translate(-0.5px, -1px);
    }}

    .done-badge {{
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--done);
      background: #dcfce7;
      padding: 0.12rem 0.45rem;
      border-radius: 999px;
    }}

    .para-meta {{
      font-size: 0.78rem;
      color: var(--muted);
      font-family: var(--mono);
    }}

    .code {{
      font-family: var(--mono);
      border: none;
      cursor: pointer;
      border-radius: 5px;
      transition: background 0.12s ease, transform 0.08s ease;
    }}

    .code:active {{
      transform: scale(0.96);
    }}

    .para-code {{
      background: var(--para-bg);
      color: var(--para-fg);
      font-size: 0.8rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      letter-spacing: 0.03em;
    }}

    .para-code:hover {{
      background: var(--accent);
    }}

    .sentences {{
      padding: 0.35rem 0;
    }}

    .sentence-row {{
      display: grid;
      grid-template-columns: 74px minmax(0, 1fr);
      gap: 0.75rem;
      align-items: baseline;
      padding: 0.45rem 0.9rem;
      border-bottom: 1px solid var(--border-soft);
    }}

    .sentence-row:last-child {{
      border-bottom: none;
    }}

    .sentence-row:hover {{
      background: var(--hover-row);
    }}

    .sentence-code {{
      background: var(--accent-bg);
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 600;
      padding: 0.16rem 0.42rem;
      text-align: center;
      justify-self: start;
      user-select: all;
    }}

    .sentence-code:hover {{
      background: var(--accent);
      color: #ffffff;
    }}

    .sentence-text {{
      font-family: var(--serif);
      font-size: 1.02rem;
      line-height: 1.62;
      color: var(--text);
    }}

    .cite {{
      font-family: var(--mono);
      font-size: 0.78em;
      color: var(--cite-fg);
      background: var(--cite-bg);
      padding: 0.05rem 0.32rem;
      border-radius: 4px;
      white-space: nowrap;
    }}

    .math {{
      font-family: var(--serif);
      font-style: italic;
    }}

    .toast {{
      position: fixed;
      bottom: 1.25rem;
      right: 1.25rem;
      background: #0f172a;
      color: #ffffff;
      font-family: var(--mono);
      font-size: 0.8rem;
      padding: 0.45rem 0.8rem;
      border-radius: 7px;
      opacity: 0;
      pointer-events: none;
      transform: translateY(6px);
      transition: opacity 0.15s ease, transform 0.15s ease;
    }}

    .toast.show {{
      opacity: 1;
      transform: translateY(0);
    }}

    @media (max-width: 900px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .sidebar {{
        position: static;
        height: auto;
        border-right: none;
        border-bottom: 1px solid var(--border);
      }}
      .main {{
        padding: 1.25rem 1rem 3rem;
      }}
    }}
  </style>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-title">Review Map</div>
      <div class="stats">
        <span class="stat-pill progress">{done_count} / {total_paras} done</span>
        <span class="stat-pill">{total_sentences} sentences</span>
        <span class="stat-pill">~{total_words} words</span>
      </div>
      <nav>
        <ul class="toc-list">
{toc_html}
        </ul>
      </nav>
    </aside>

    <main class="main">
      <header class="doc-header">
        <h1>{html.escape(title)}</h1>
        <p class="doc-note">
          Source: <code>{html.escape(source_path)}</code> &middot; Figures and tables omitted &middot; Click any paragraph (<code>P01</code>) or sentence (<code>P01.1</code>) badge to copy its code.
        </p>
      </header>

{sections_html}
    </main>
  </div>

  <div class="toast" id="toast">Copied</div>

  <script>
    const toast = document.getElementById("toast");
    let toastTimer = null;

    function showToast(msg) {{
      toast.textContent = msg;
      toast.classList.add("show");
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove("show"), 1100);
    }}

    document.addEventListener("click", (event) => {{
      const btn = event.target.closest("button[data-copy]");
      if (!btn) return;
      const code = btn.getAttribute("data-copy");
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(code).then(() => showToast("Copied " + code));
      }} else {{
        showToast(code);
      }}
    }});
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render sentence-coded HTML review view.")
    parser.add_argument("--input", type=Path, default=Path("draft/manuscript.md"))
    parser.add_argument("--output", type=Path, default=Path("draft/review.html"))
    parser.add_argument("--status", type=Path, default=Path("draft/review_status.json"))
    parser.add_argument("--done", nargs="*", default=[], help="Mark paragraph code(s) as done (e.g. P01)")
    parser.add_argument("--undone", nargs="*", default=[], help="Unmark paragraph code(s) as done")
    args = parser.parse_args()

    done_set = load_done_set(args.status)
    for code in args.done:
        done_set.add(code.upper())
    for code in args.undone:
        done_set.discard(code.upper())
    save_done_set(args.status, done_set)

    md_text = args.input.read_text(encoding="utf-8")
    title, sections = parse_manuscript(md_text)
    rendered = render_html(title, sections, str(args.input), done_set)
    args.output.write_text(rendered, encoding="utf-8")

    total_paras = sum(
        len(sec.paragraphs) + sum(len(sub.paragraphs) for sub in sec.subsections)
        for sec in sections
    )
    print(f"Wrote {args.output} ({len(done_set)}/{total_paras} paragraphs marked done).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
