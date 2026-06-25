#!/usr/bin/env python3
"""Export a DOCX resume to PDF when local conversion tooling is available."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import textwrap
from pathlib import Path
from xml.etree import ElementTree
import zipfile


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
BLUE = "#0070C0"
GOLD = "#C8A96A"


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


def wrap_by_width(text: str, font_name: str, font_size: int, max_width: float, pdfmetrics) -> list[str]:
    lines: list[str] = []
    current = ""
    tokens = re.findall(r"\s+|[A-Za-z0-9_./:+#-]+|[\u4e00-\u9fff]|[^\s]", text)
    for token in tokens:
        candidate = current + token
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current.rstrip())
            current = token.lstrip()
    if current:
        lines.append(current.rstrip())
    return lines or [""]


def try_canonical_reportlab_pdf(docx: Path, out: Path) -> bool:
    render_path = docx.parent / "resume-render.json"
    if not render_path.exists():
        return False
    try:
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
    except Exception:
        return False

    payload = json.loads(render_path.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True, exist_ok=True)
    font_name = "STSong-Light"
    for font_path in [
        Path("C:/Windows/Fonts/Deng.ttf"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/NotoSansSC-VF.ttf"),
    ]:
        if font_path.exists():
            try:
                pdfmetrics.registerFont(TTFont("ResumeFont", str(font_path), subfontIndex=0))
                font_name = "ResumeFont"
                break
            except Exception:
                continue
    if font_name == "STSong-Light":
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    page_width, page_height = A4
    margin_x = 58
    y = page_height - 62
    pdf = canvas.Canvas(str(out), pagesize=A4)
    pdf.setTitle(payload.get("title", docx.stem))

    def new_page_if_needed(height: float) -> None:
        nonlocal y
        if y - height < 48:
            pdf.showPage()
            y = page_height - 58

    def draw_title() -> None:
        nonlocal y
        pdf.setFont(font_name, 18)
        pdf.setFillColor(black)
        title = payload.get("title", "")
        width = pdfmetrics.stringWidth(title, font_name, 18)
        pdf.drawString((page_width - width) / 2, y, title)
        y -= 28
        pdf.setFillColor(HexColor(BLUE))
        pdf.rect(margin_x, y, 300, 10, stroke=0, fill=1)
        pdf.setFillColor(HexColor(GOLD))
        pdf.rect(margin_x + 305, y, page_width - margin_x * 2 - 305, 10, stroke=0, fill=1)
        y -= 24

    def draw_section(label: str) -> None:
        nonlocal y
        new_page_if_needed(34)
        pdf.setFillColor(HexColor(BLUE))
        pdf.rect(margin_x + 14, y - 13, 94, 18, stroke=0, fill=1)
        pdf.setFillColor(white)
        pdf.setFont(font_name, 12)
        pdf.drawCentredString(margin_x + 61, y - 8, label)
        pdf.setStrokeColor(HexColor(BLUE))
        pdf.setLineWidth(0.8)
        pdf.line(margin_x + 104, y - 13, page_width - margin_x, y - 13)
        pdf.setFillColor(black)
        y -= 28

    def draw_key_values(rows: list[list[str]]) -> None:
        nonlocal y
        pdf.setFont(font_name, 10)
        max_width = (page_width - margin_x * 2) / 2 - 12
        for index in range(0, len(rows), 2):
            new_page_if_needed(18)
            pair = rows[index : index + 2]
            for col, row in enumerate(pair):
                label, value = row
                x = margin_x + 45 + col * ((page_width - margin_x * 2) / 2)
                pdf.drawString(x, y, f"{label}：{value}")
            y -= 18
        y -= 4

    def draw_bullets(lines: list[str], font_size: int = 9) -> None:
        nonlocal y
        pdf.setFont(font_name, font_size)
        max_width = page_width - margin_x * 2 - 74
        for line in lines:
            wrapped = wrap_by_width(line, font_name, font_size, max_width, pdfmetrics)
            new_page_if_needed(len(wrapped) * 14 + 4)
            pdf.setFillColor(black)
            path = pdf.beginPath()
            path.moveTo(margin_x + 50, y + 3)
            path.lineTo(margin_x + 57, y)
            path.lineTo(margin_x + 50, y - 3)
            path.close()
            pdf.drawPath(path, stroke=0, fill=1)
            for part in wrapped:
                pdf.drawString(margin_x + 68, y, part)
                y -= 14
            y -= 2

    def draw_project(item: dict) -> None:
        nonlocal y
        title = "    ".join(part for part in [item.get("period", ""), item.get("name", ""), item.get("role", "")] if part)
        new_page_if_needed(30)
        pdf.setFont(font_name, 10)
        pdf.setFillColor(black)
        pdf.drawString(margin_x + 34, y, title)
        y -= 18
        lines = []
        technologies = item.get("technologies", [])
        if technologies:
            lines.append(f"技术栈：{'、'.join(technologies)}")
        lines.extend(item.get("bullets", []))
        draw_bullets(lines, font_size=8)

    draw_title()
    if payload.get("basics"):
        draw_section("基本信息")
        draw_key_values(payload["basics"])
    if payload.get("intent"):
        draw_section("求职意向")
        draw_key_values(payload["intent"])
    if payload.get("skills"):
        draw_section("开发技能")
        draw_bullets([f"{row['label']}：{row['value']}" for row in payload["skills"]], font_size=9)
    if payload.get("work_experience"):
        draw_section("工作经历")
        for item in payload["work_experience"]:
            draw_project(item)
    if payload.get("projects"):
        draw_section("项目经历")
        for item in payload["projects"]:
            draw_project(item)
    if payload.get("summary") and not payload.get("projects") and not payload.get("work_experience"):
        draw_section("自我评价")
        draw_bullets([payload["summary"]], font_size=9)

    pdf.save()
    return out.exists() and out.stat().st_size > 0


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

    if (
        try_canonical_reportlab_pdf(args.docx, args.out)
        or try_libreoffice(args.docx, args.out)
        or try_word_com(args.docx, args.out)
        or try_reportlab_pdf(args.docx, args.out)
    ):
        print(f"exported {args.out}")
        return 0

    diagnostic = write_diagnostic(args.out, args.docx)
    print(f"PDF export unavailable; wrote diagnostic {diagnostic}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
