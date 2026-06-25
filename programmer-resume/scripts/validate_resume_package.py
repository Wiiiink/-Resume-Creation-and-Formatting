#!/usr/bin/env python3
"""Validate a generated programmer resume package."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PLACEHOLDER_PATTERNS = [
    r"\bXX\b",
    r"XXXXX?",
    r"TBD",
    r"毛向军",
    r"南华大学",
    r"138-0138-0000",
    r"13718812xxx",
    r"Xxx@163\.com",
    r"service@qiaobutang\.com",
]


def docx_to_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    return "\n".join(node.text or "" for node in root.iter(f"{WORD_NS}t"))


def package_text(package_dir: Path) -> str:
    parts = []
    txt = package_dir / "resume.txt"
    if txt.exists():
        parts.append(txt.read_text(encoding="utf-8", errors="replace"))
    docx = package_dir / "resume.docx"
    if docx.exists():
        parts.append(docx_to_text(docx))
    return "\n".join(parts)


def required_facts(facts: dict) -> list[str]:
    personal = facts.get("personal", {})
    values = [
        facts.get("target_role"),
        personal.get("name"),
        personal.get("phone"),
        personal.get("email"),
    ]
    return [value for value in values if value]


def validate(facts_path: Path, package_dir: Path, allow_missing_pdf: bool) -> list[str]:
    errors: list[str] = []
    facts = json.loads(facts_path.read_text(encoding="utf-8"))
    if not package_dir.exists():
        return [f"package directory does not exist: {package_dir}"]

    docx_path = package_dir / "resume.docx"
    txt_path = package_dir / "resume.txt"
    if not docx_path.exists() and not txt_path.exists():
        errors.append("package must contain resume.docx or resume.txt")
    if docx_path.exists() and docx_path.stat().st_size < 1024:
        errors.append("resume.docx is unexpectedly small")

    pdf_path = package_dir / "resume.pdf"
    diagnostic_path = package_dir / "pdf-export-diagnostic.json"
    if not allow_missing_pdf and not pdf_path.exists() and not diagnostic_path.exists():
        errors.append("resume.pdf is missing and no PDF diagnostic was produced")
    if pdf_path.exists() and pdf_path.stat().st_size < 1024:
        errors.append("resume.pdf is unexpectedly small")

    text = package_text(package_dir)
    for fact in required_facts(facts):
        if fact not in text:
            errors.append(f"required fact missing from generated resume: {fact}")
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"placeholder detected: {pattern}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facts", required=True, type=Path)
    parser.add_argument("--package-dir", required=True, type=Path)
    parser.add_argument("--allow-missing-pdf", action="store_true")
    args = parser.parse_args()

    errors = validate(args.facts, args.package_dir, args.allow_missing_pdf)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("resume package validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
