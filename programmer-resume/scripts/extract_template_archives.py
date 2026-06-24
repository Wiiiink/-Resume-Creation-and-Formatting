#!/usr/bin/env python3
"""Extract template archives and optionally delete the compressed originals."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


ARCHIVE_EXTENSIONS = {".zip", ".rar"}


def ensure_inside(child: Path, parent: Path) -> None:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    if parent_resolved != child_resolved and parent_resolved not in child_resolved.parents:
        raise ValueError(f"archive member escapes destination: {child}")


def unique_destination(archive: Path) -> Path:
    base = archive.with_suffix("")
    if not base.exists():
        return base
    index = 1
    while True:
        candidate = archive.with_name(f"{archive.stem}-{index}")
        if not candidate.exists():
            return candidate
        index += 1


def find_7z() -> str | None:
    for name in ("7z", "7z.exe", "7za", "7za.exe"):
        found = shutil.which(name)
        if found:
            return found
    common = Path(r"C:\Program Files\NVIDIA Corporation\NVIDIA App\7z.exe")
    if common.exists():
        return str(common)
    return None


def extract_zip(archive: Path, destination: Path) -> int:
    count = 0
    with zipfile.ZipFile(archive, metadata_encoding="gb18030") as zf:
        for member in zf.infolist():
            target = destination / member.filename
            ensure_inside(target, destination)
        zf.extractall(destination)
        count = sum(1 for item in zf.infolist() if not item.is_dir())
    return count


def extract_rar(archive: Path, destination: Path) -> int:
    seven_zip = find_7z()
    if not seven_zip:
        raise RuntimeError("7z is required to extract .rar files but was not found")
    destination.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [seven_zip, "x", "-y", f"-o{destination}", str(archive)],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"7z failed for {archive}")
    return sum(1 for path in destination.rglob("*") if path.is_file())


def extract_archive(archive: Path, delete_archive: bool) -> dict:
    destination = unique_destination(archive)
    destination.mkdir(parents=True, exist_ok=True)
    try:
        if archive.suffix.lower() == ".zip":
            files = extract_zip(archive, destination)
        elif archive.suffix.lower() == ".rar":
            files = extract_rar(archive, destination)
        else:
            return {"archive": str(archive), "status": "skipped", "message": "not an archive"}
        if files < 1:
            raise RuntimeError("archive produced no files")
        if delete_archive:
            archive.unlink()
        return {
            "archive": str(archive),
            "destination": str(destination),
            "files": files,
            "deleted": delete_archive,
            "status": "ok",
        }
    except Exception as exc:
        return {
            "archive": str(archive),
            "destination": str(destination),
            "status": "error",
            "message": str(exc),
        }


def find_archives(template_root: Path) -> list[Path]:
    return sorted(
        path
        for path in template_root.rglob("*")
        if path.is_file() and path.suffix.lower() in ARCHIVE_EXTENSIONS
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-root", required=True, type=Path)
    parser.add_argument("--delete-archives", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    template_root = args.template_root.resolve()
    if not template_root.exists():
        parser.error(f"template root does not exist: {template_root}")

    archives = find_archives(template_root)
    results = [extract_archive(archive, args.delete_archives) for archive in archives]
    payload = {"template_root": str(template_root), "archive_count": len(archives), "results": results}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text)
    errors = [item for item in results if item["status"] != "ok"]
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
