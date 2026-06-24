#!/usr/bin/env python3
"""Build a JSON index of the bundled programmer resume templates."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def infer_role(relative_path: str, extension: str) -> str:
    path = relative_path.lower()
    if extension == ".jpg" or "图片目录" in relative_path:
        return "visual-catalog"
    if any(token in relative_path for token in ["制作教程", "写作", "面试技巧", "怎么写"]):
        return "writing-guide"
    if extension in {".zip", ".rar"}:
        if "前端" in relative_path or "web" in path:
            return "frontend"
        if "java" in path or "后端" in relative_path:
            return "java-backend"
        return "archive"
    if "前端" in relative_path or "web" in path or "html" in path or "css" in path:
        return "frontend"
    if "java" in path or "后端" in relative_path or "javaee" in path:
        return "java-backend"
    return "general-programmer"


def infer_page_family(relative_path: str) -> str:
    if "单页" in relative_path:
        return "one-page"
    if "二页" in relative_path or "双页" in relative_path:
        return "two-page"
    if "三页" in relative_path:
        return "three-page"
    if "四页" in relative_path:
        return "four-page"
    if "封面" in relative_path:
        return "cover"
    return "unknown"


def infer_package_group(path: Path) -> str:
    if path.suffix.lower() in {".zip", ".rar"}:
        return path.stem
    parent = path.parent.name
    if parent and parent not in {"template", ""}:
        return parent
    return path.stem


def build_index(template_root: Path) -> dict:
    files = []
    extension_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    page_counts: Counter[str] = Counter()

    for file_path in sorted(template_root.rglob("*")):
        if not file_path.is_file():
            continue
        extension = file_path.suffix.lower()
        relative_path = file_path.relative_to(template_root).as_posix()
        role = infer_role(relative_path, extension)
        page_family = infer_page_family(relative_path)
        extension_counts[extension] += 1
        role_counts[role] += 1
        page_counts[page_family] += 1
        files.append(
            {
                "path": relative_path,
                "extension": extension,
                "size": file_path.stat().st_size,
                "role": role,
                "page_family": page_family,
                "package_group": infer_package_group(file_path),
            }
        )

    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "template_root": template_root.as_posix(),
        "summary": {
            "total_files": len(files),
            "extensions": dict(sorted(extension_counts.items())),
            "roles": dict(sorted(role_counts.items())),
            "page_families": dict(sorted(page_counts.items())),
        },
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    template_root = args.template_root.resolve()
    if not template_root.exists():
        parser.error(f"template root does not exist: {template_root}")

    data = build_index(template_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"indexed {data['summary']['total_files']} template files -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
