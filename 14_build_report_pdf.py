#!/usr/bin/env python3
"""Render docs/FIRE_FISCAL_FULL_REPORT.md -> a styled PDF via Chrome headless.

No LaTeX/pandoc needed: markdown -> HTML (figures inlined as base64) -> Chrome --print-to-pdf.
    python 14_build_report_pdf.py [docs/SOME_OTHER.md]
Outputs outputs/<doc-stem>.{html,pdf}. Requires the `markdown` package
(pip install markdown) and a Chromium/Chrome binary.
"""
import base64, re, shutil, subprocess, sys
from pathlib import Path
import markdown

REPO = Path(__file__).resolve().parent
MD = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO / "docs" / "FIRE_FISCAL_FULL_REPORT.md"
HTML = REPO / "outputs" / f"{MD.stem}.html"
PDF = REPO / "outputs" / f"{MD.stem}.pdf"

CHROME = next((p for p in [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome"), shutil.which("chromium"),
    "/opt/pw-browsers/chromium"] if p and Path(p).exists()), None)

CSS = """
@page { size: letter; margin: 0.85in 0.8in; }
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: -apple-system,'Helvetica Neue',Arial,sans-serif; font-size:10.5pt; line-height:1.5; color:#1a1a1a; }
h1 { font-size:22pt; line-height:1.2; margin:0 0 4px; color:#1d3557; }
h2 { font-size:14pt; color:#1d3557; border-bottom:2px solid #d8d2c4; padding-bottom:3px; margin-top:22px; page-break-after:avoid; }
h3 { font-size:11.5pt; color:#2a4a63; margin-top:16px; }
h4 { font-size:10.5pt; color:#2a4a63; margin:12px 0 4px; }
hr { border:none; border-top:1px solid #d8d2c4; margin:14px 0; }
blockquote { border-left:4px solid #457b9d; background:#f6f4ee; margin:12px 0; padding:8px 14px; color:#2a4a63; }
blockquote em { color:#9c4221; font-style:italic; }
table { border-collapse:collapse; width:100%; margin:12px 0; font-size:9pt; }
th,td { border:1px solid #c8ccd0; padding:5px 8px; text-align:left; vertical-align:top; }
th { background:#e8eef3; color:#1d3557; font-weight:600; }
tr:nth-child(even) td { background:#fafbfc; }
figure { margin:14px 0; text-align:center; page-break-inside:avoid; }
figure img { max-width:100%; max-height:4.8in; width:auto; border:1px solid #e0e4e8; border-radius:3px; }
figcaption { font-size:8.5pt; color:#555; font-style:italic; margin-top:4px; }
code { background:#f0efe9; padding:1px 4px; border-radius:3px; font-size:8.8pt; color:#9c4221; }
pre { background:#1d3557; color:#eef2f6; padding:11px 13px; border-radius:5px; overflow-x:auto;
      font-size:8.4pt; line-height:1.42; page-break-inside:avoid; }
pre code { background:none; color:#eef2f6; padding:0; }
strong { color:#1d3557; }
/* generated TOC (markdown 'toc' extension) */
.toc { background:#f6f4ee; border:1px solid #d8d2c4; border-radius:6px; padding:10px 14px 10px 28px; font-size:9.5pt; }
.toc ul { margin:2px 0; padding-left:16px; }
.toc > ul { padding-left:6px; }
.toc a { color:#2a4a63; text-decoration:none; }
/* footnotes (markdown 'footnotes' extension) */
.footnote { font-size:8.6pt; color:#444; border-top:1px solid #d8d2c4; margin-top:20px; padding-top:6px; }
.footnote ol { padding-left:18px; }
.footnote li { margin:2px 0; }
sup a, a.footnote-ref { color:#9c4221; text-decoration:none; font-weight:600; }
"""


def embed(m):
    alt, src = m.group(1), m.group(2)
    p = (MD.parent / src).resolve()
    if not p.exists():
        return m.group(0)
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{b64}"/><figcaption>{alt}</figcaption></figure>'


def main():
    if CHROME is None:
        sys.exit("No Chromium/Chrome found — install it or adjust CHROME path.")
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', embed, MD.read_text())
    body = markdown.markdown(text, extensions=[
        "tables", "fenced_code", "attr_list", "footnotes", "toc"])
    HTML.write_text(f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--no-pdf-header-footer", f"--print-to-pdf={PDF}", HTML.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"wrote {PDF} ({PDF.stat().st_size//1024} KB) and {HTML.name}")


if __name__ == "__main__":
    main()
