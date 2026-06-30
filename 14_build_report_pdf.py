#!/usr/bin/env python3
"""Render docs/FISCAL_PRODUCTIVITY_REPORT.md -> a styled PDF via Chrome headless.

No LaTeX/pandoc needed: markdown -> HTML (figures inlined as base64) -> Chrome --print-to-pdf.
    python 14_build_report_pdf.py
Outputs outputs/FISCAL_PRODUCTIVITY_REPORT.{html,pdf}. Requires the `markdown` package
(pip install markdown) and Google Chrome.
"""
import base64, re, shutil, subprocess, sys
from pathlib import Path
import markdown

REPO = Path(__file__).resolve().parent
MD = REPO / "docs" / "FISCAL_PRODUCTIVITY_REPORT.md"
HTML = REPO / "outputs" / "FISCAL_PRODUCTIVITY_REPORT.html"
PDF = REPO / "outputs" / "FISCAL_PRODUCTIVITY_REPORT.pdf"

CHROME = next((p for p in [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome"), shutil.which("chromium")] if p), None)

CSS = """
@page { size: letter; margin: 0.85in 0.8in; }
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: -apple-system,'Helvetica Neue',Arial,sans-serif; font-size:10.5pt; line-height:1.5; color:#1a1a1a; }
h1 { font-size:21pt; line-height:1.2; margin:0 0 4px; color:#0f2b46; }
h2 { font-size:14pt; color:#0f2b46; border-bottom:2px solid #d0d7de; padding-bottom:3px; margin-top:22px; page-break-after:avoid; }
h3 { font-size:11.5pt; color:#244; margin-top:16px; }
hr { border:none; border-top:1px solid #d0d7de; margin:14px 0; }
table { border-collapse:collapse; width:100%; margin:12px 0; font-size:9pt; }
th,td { border:1px solid #c8ccd0; padding:5px 8px; text-align:left; vertical-align:top; }
th { background:#eef2f6; color:#0f2b46; font-weight:600; }
tr:nth-child(even) td { background:#fafbfc; }
figure { margin:14px 0; text-align:center; page-break-inside:avoid; }
figure img { max-width:100%; max-height:4.6in; width:auto; border:1px solid #e0e4e8; border-radius:3px; }
figcaption { font-size:8.5pt; color:#555; font-style:italic; margin-top:4px; }
code { background:#f3f4f6; padding:1px 4px; border-radius:3px; font-size:9pt; }
strong { color:#0f2b46; }
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
        sys.exit("Google Chrome not found — install it or adjust CHROME path.")
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', embed, MD.read_text())
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list"])
    HTML.write_text(f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={PDF}", HTML.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"wrote {PDF} ({PDF.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
