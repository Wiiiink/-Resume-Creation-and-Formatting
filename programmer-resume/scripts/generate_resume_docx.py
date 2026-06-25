#!/usr/bin/env python3
"""Generate a programmer resume DOCX from normalized facts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt


SECTION_ORDER = ["个人优势", "专业技能", "工作经历", "项目经历", "教育背景", "证书与奖项"]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def select_template(index: dict, target_role: str) -> dict:
    target = target_role.lower()
    preferred_role = "java-backend" if "java" in target or "后端" in target else "frontend" if "前端" in target or "web" in target else "general-programmer"
    candidates = [item for item in index.get("files", []) if item.get("role") == preferred_role and item.get("extension") in {".docx", ".doc", ".html", ".txt"}]
    if not candidates:
        candidates = [item for item in index.get("files", []) if item.get("extension") in {".docx", ".doc"}]
    candidates.sort(key=lambda item: (item.get("page_family") != "two-page", item.get("size", 0)))
    return candidates[0] if candidates else {}


def configure_document(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Cm(1.4)
    section.bottom_margin = Cm(1.4)
    section.left_margin = Cm(1.6)
    section.right_margin = Cm(1.6)
    normal = document.styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal.font.size = Pt(9)


def add_heading(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    run = paragraph.add_run(text)
    run.bold = True
    run.font.size = Pt(11)
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(3)


def add_bullet(document: Document, text: str) -> None:
    paragraph = document.add_paragraph(style=None)
    paragraph.paragraph_format.left_indent = Cm(0.3)
    paragraph.paragraph_format.first_line_indent = Cm(-0.3)
    paragraph.paragraph_format.space_after = Pt(1)
    paragraph.add_run("• ").bold = True
    paragraph.add_run(text)


def add_line(document: Document, text: str, bold: bool = False) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(1)
    run = paragraph.add_run(text)
    run.bold = bold


def compact_join(parts: list[str], separator: str = "    ") -> str:
    return separator.join(part for part in parts if part)


def date_range(item: dict) -> str:
    start = item.get("start", "")
    end = item.get("end", "")
    if start and end:
        return f"{start}-{end}"
    return start or end


def meaningful_items(items: list[dict]) -> list[dict]:
    return [
        item
        for item in items
        if any(value for value in item.values() if isinstance(value, str))
        or any(item.get(key) for key in ["bullets", "technologies"])
    ]


def render_resume(facts: dict, selected_template: dict, out_dir: Path) -> Path:
    document = Document()
    configure_document(document)

    personal = facts.get("personal", {})
    name = personal.get("name", "")
    target_role = facts.get("target_role", "")

    header = document.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_run = header.add_run(name)
    name_run.bold = True
    name_run.font.size = Pt(18)

    role = document.add_paragraph()
    role.alignment = WD_ALIGN_PARAGRAPH.CENTER
    role_run = role.add_run(f"求职意向：{target_role}")
    role_run.bold = True

    contacts = [
        personal.get("phone"),
        personal.get("email"),
        personal.get("city"),
        personal.get("github"),
    ]
    contact_line = " | ".join(item for item in contacts if item)
    if contact_line:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run(contact_line)

    if facts.get("summary"):
        add_heading(document, SECTION_ORDER[0])
        add_bullet(document, facts.get("summary", ""))

    skills = facts.get("skills", {})
    labels = {
        "languages": "编程语言",
        "backend": "后端框架",
        "frontend": "前端技术",
        "databases": "数据库",
        "tools": "工具平台",
    }
    if any(skills.get(key) for key in labels):
        add_heading(document, SECTION_ORDER[1])
        for key, label in labels.items():
            values = skills.get(key)
            if values:
                add_bullet(document, f"{label}：{'、'.join(values)}")

    work_items = meaningful_items(facts.get("work_experience", []))
    if work_items:
        add_heading(document, SECTION_ORDER[2])
    for item in work_items:
        add_line(document, compact_join([date_range(item), item.get("company", ""), item.get("role", "")]), bold=True)
        for bullet in item.get("bullets", []):
            add_bullet(document, bullet)

    project_items = meaningful_items(facts.get("projects", []))
    if project_items:
        add_heading(document, SECTION_ORDER[3])
    for item in project_items:
        stack = "、".join(item.get("technologies", []))
        add_line(document, compact_join([item.get("period", ""), item.get("name", ""), item.get("role", "")]), bold=True)
        if stack:
            add_bullet(document, f"技术栈：{stack}")
        for bullet in item.get("bullets", []):
            add_bullet(document, bullet)

    education_items = meaningful_items(facts.get("education", []))
    if education_items:
        add_heading(document, SECTION_ORDER[4])
    for item in education_items:
        add_line(document, compact_join([date_range(item), item.get("school", ""), item.get("major", ""), item.get("degree", "")]), bold=True)

    certificates = facts.get("certificates", [])
    if certificates:
        add_heading(document, SECTION_ORDER[5])
        add_bullet(document, "、".join(certificates))

    out_dir.mkdir(parents=True, exist_ok=True)
    docx_path = out_dir / "resume.docx"
    document.save(docx_path)

    text_path = out_dir / "resume.txt"
    text_path.write_text(render_plain_text(facts, selected_template), encoding="utf-8")

    metadata = {
        "selected_template": selected_template,
        "section_order": SECTION_ORDER,
        "style_source": "template corpus",
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return docx_path


def render_plain_text(facts: dict, selected_template: dict) -> str:
    personal = facts.get("personal", {})
    contact_line = " | ".join(filter(None, [personal.get("phone"), personal.get("email"), personal.get("city"), personal.get("github")]))
    lines = [
        personal.get("name", ""),
        f"求职意向：{facts.get('target_role', '')}",
    ]
    if contact_line:
        lines.append(contact_line)
    lines.extend(["", f"模板来源：{selected_template.get('path', 'template corpus')}"])
    if facts.get("summary"):
        lines.extend(["", "个人优势", facts.get("summary", "")])
    skills = facts.get("skills", {})
    if any(skills.values()):
        lines.extend(["", "专业技能"])
        for values in skills.values():
            if values:
                lines.append("、".join(values))
    for section, key in [("工作经历", "work_experience"), ("项目经历", "projects"), ("教育背景", "education")]:
        items = meaningful_items(facts.get(key, []))
        if not items:
            continue
        lines.extend(["", section])
        for item in items:
            if key == "work_experience":
                lines.append(compact_join([date_range(item), item.get("company", ""), item.get("role", "")], " "))
            elif key == "projects":
                lines.append(compact_join([item.get("period", ""), item.get("name", ""), item.get("role", "")], " "))
            elif key == "education":
                lines.append(compact_join([date_range(item), item.get("school", ""), item.get("major", ""), item.get("degree", "")], " "))
            for bullet in item.get("bullets", []):
                lines.append(f"- {bullet}")
    if facts.get("certificates"):
        lines.extend(["", "证书与奖项", "、".join(facts["certificates"])])
    return "\n".join(line for line in lines if line is not None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facts", required=True, type=Path)
    parser.add_argument("--template-index", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--language", default="zh-CN")
    args = parser.parse_args()

    facts = load_json(args.facts)
    index = load_json(args.template_index)
    selected_template = select_template(index, facts.get("target_role", ""))
    docx_path = render_resume(facts, selected_template, args.out_dir)
    print(f"generated {docx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
