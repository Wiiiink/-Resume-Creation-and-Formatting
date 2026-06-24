#!/usr/bin/env python3
"""Extract text from resume templates or old resumes."""

from __future__ import annotations

import argparse
import html
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def read_text_file(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8", "gb18030", "gbk"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def html_to_text(path: Path) -> str:
    text = read_text_file(path)
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    return normalize_space(text)


def docx_to_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    parts = []
    for node in root.iter(f"{WORD_NS}t"):
        if node.text:
            parts.append(node.text)
    return normalize_space("\n".join(parts))


def normalize_space(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.replace("\r", "\n").split("\n")]
    return "\n".join(line for line in lines if line)


def extract(path: Path) -> dict:
    extension = path.suffix.lower()
    try:
        if extension == ".txt":
            text = normalize_space(read_text_file(path))
        elif extension in {".html", ".htm"}:
            text = html_to_text(path)
        elif extension == ".docx":
            text = docx_to_text(path)
        elif extension == ".pdf":
            text = ""
            return {"path": str(path), "status": "unsupported", "text": text, "message": "PDF text extraction is not enabled in this lightweight extractor."}
        elif extension == ".doc":
            text = ""
            return {"path": str(path), "status": "unsupported", "text": text, "message": "Legacy .doc extraction requires Word or conversion tooling."}
        else:
            text = ""
            return {"path": str(path), "status": "unsupported", "text": text, "message": f"Unsupported extension: {extension}"}
    except Exception as exc:
        return {"path": str(path), "status": "error", "text": "", "message": str(exc)}

    return {"path": str(path), "status": "ok", "text": text, "chars": len(text)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    results = [extract(path) for path in args.paths]
    payload = {"results": results}
    output = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0 if all(item["status"] in {"ok", "unsupported"} for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
