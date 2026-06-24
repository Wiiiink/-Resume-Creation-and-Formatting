#!/usr/bin/env python3
"""Export a DOCX resume to PDF when local conversion tooling is available."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import textwrap
from pathlib import Path
from xml.etree import ElementTree
import zipfile


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def try_libreoffice(docx: Path, out: Path) -> bool:
    executable = shutil.which("soffice") or shutil.which("libreoffice")
    if not executable:
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [executable, "--headless", "--convert-to", "pdf", "--outdir", str(out.parent), str(docx)],
        text=True,
        capture_output=True,
    )
    produced = out.parent / f"{docx.stem}.pdf"
    if result.returncode == 0 and produced.exists():
        if produced != out:
            produced.replace(out)
        return True
    return False


def try_word_com(docx: Path, out: Path) -> bool:
    try:
        import win32com.client  # type: ignore
    except Exception:
        return False

    word = None
    document = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        document = word.Documents.Open(str(docx.resolve()))
        out.parent.mkdir(parents=True, exist_ok=True)
        document.SaveAs(str(out.resolve()), FileFormat=17)
        return out.exists()
    except Exception:
        return False
    finally:
        if document is not None:
            document.Close(False)
        if word is not None:
            word.Quit()


def docx_to_text(docx: Path) -> str:
    with zipfile.ZipFile(docx) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    lines = []
    for paragraph in root.iter(f"{WORD_NS}p"):
        texts = [node.text or "" for node in paragraph.iter(f"{WORD_NS}t")]
        line = "".join(texts).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def try_reportlab_pdf(docx: Path, out: Path) -> bool:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfgen import canvas
    except Exception:
        return False

    text = docx_to_text(docx)
    out.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    page_width, page_height = A4
    margin = 42
    line_height = 15
    y = page_height - margin
    pdf = canvas.Canvas(str(out), pagesize=A4)
    pdf.setTitle(docx.stem)
    pdf.setFont("STSong-Light", 10)

    for raw_line in text.splitlines():
        wrapped = textwrap.wrap(raw_line, width=52) or [""]
        for line in wrapped:
            if y < margin:
                pdf.showPage()
                pdf.setFont("STSong-Light", 10)
                y = page_height - margin
            pdf.drawString(margin, y, line)
            y -= line_height
    pdf.save()
    return out.exists() and out.stat().st_size > 0


def write_diagnostic(out: Path, docx: Path) -> Path:
    diagnostic = out.parent / "pdf-export-diagnostic.json"
    diagnostic.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "unavailable",
        "docx": str(docx),
        "requested_pdf": str(out),
        "message": "No PDF converter was available. Install LibreOffice/soffice or Microsoft Word with COM automation.",
    }
    diagnostic.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return diagnostic


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    if not args.docx.exists():
        parser.error(f"DOCX does not exist: {args.docx}")

    if try_libreoffice(args.docx, args.out) or try_word_com(args.docx, args.out) or try_reportlab_pdf(args.docx, args.out):
        print(f"exported {args.out}")
        return 0

    diagnostic = write_diagnostic(args.out, args.docx)
    print(f"PDF export unavailable; wrote diagnostic {diagnostic}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
