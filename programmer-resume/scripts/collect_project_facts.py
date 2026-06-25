#!/usr/bin/env python3
"""Collect conservative resume facts from local software project directories."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "target",
}
MANIFEST_NAMES = {"pom.xml", "package.json"}
IDENTITY_NAMES = {"README.md", "readme.md", "AGENTS.md", "pom.xml", "package.json"}
README_NAMES = {"README.md", "readme.md"}
RELEVANT_NAMES = MANIFEST_NAMES | README_NAMES

POM_TECH_MAP = [
    ("spring-boot", "Spring Boot"),
    ("spring-cloud", "Spring Cloud"),
    ("spring-security", "Spring Security"),
    ("mybatis-plus", "MyBatis-Plus"),
    ("mybatis", "MyBatis"),
    ("mysql", "MySQL"),
    ("postgresql", "PostgreSQL"),
    ("redis", "Redis"),
    ("nacos", "Nacos"),
    ("sentinel", "Sentinel"),
    ("seata", "Seata"),
    ("dubbo", "Dubbo"),
    ("rabbitmq", "RabbitMQ"),
    ("amqp", "RabbitMQ"),
    ("kafka", "Kafka"),
    ("elasticsearch", "Elasticsearch"),
    ("knife4j", "Knife4j"),
    ("swagger", "Swagger"),
    ("jjwt", "JWT"),
    ("jwt", "JWT"),
    ("lombok", "Lombok"),
    ("hutool", "Hutool"),
]

PACKAGE_TECH_MAP = {
    "vue": "Vue",
    "react": "React",
    "vite": "Vite",
    "typescript": "TypeScript",
    "element-plus": "Element Plus",
    "element-ui": "Element UI",
    "pinia": "Pinia",
    "vue-router": "Vue Router",
    "axios": "Axios",
    "echarts": "ECharts",
    "ant-design-vue": "Ant Design Vue",
    "@dcloudio/uni-app": "uni-app",
    "uni-app": "uni-app",
    "tailwindcss": "Tailwind CSS",
}


def walk_project(root: Path) -> Iterable[Path]:
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in EXCLUDED_DIRS and not name.startswith("."))
        for filename in sorted(filenames):
            if filename not in RELEVANT_NAMES:
                continue
            path = Path(current) / filename
            yield path


def relative_depth(path: Path, root: Path) -> int:
    try:
        return len(path.relative_to(root).parts)
    except ValueError:
        return 999


def has_identity(root: Path) -> bool:
    return any((root / name).exists() for name in IDENTITY_NAMES)


def has_project_markers(root: Path, max_depth: int = 3) -> bool:
    if has_identity(root):
        return True
    for path in walk_project(root):
        if path.name in MANIFEST_NAMES and relative_depth(path, root) <= max_depth:
            return True
    return False


def expand_roots(roots: list[Path]) -> list[Path]:
    projects: list[Path] = []
    for root in roots:
        root = root.resolve()
        if has_identity(root):
            projects.append(root)
            continue
        children = [child for child in sorted(root.iterdir()) if child.is_dir() and has_project_markers(child)]
        projects.extend(children or [root])
    return projects


def xml_text(element: ElementTree.Element, tag: str) -> list[str]:
    values = []
    for node in element.iter():
        if node.tag.split("}")[-1] == tag and node.text:
            values.append(node.text.strip())
    return values


def parse_pom(path: Path) -> tuple[list[str], list[str]]:
    try:
        root = ElementTree.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except ElementTree.ParseError:
        return [], []
    tokens = [value.lower() for value in xml_text(root, "groupId") + xml_text(root, "artifactId")]
    technologies: list[str] = ["Java", "Maven"]
    for needle, label in POM_TECH_MAP:
        if any(needle in token for token in tokens):
            technologies.append(label)
    artifacts = [value for value in xml_text(root, "artifactId") if value]
    return unique(technologies), artifacts[:12]


def parse_package(path: Path) -> tuple[list[str], list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return [], []
    deps = {}
    for key in ["dependencies", "devDependencies"]:
        deps.update(data.get(key, {}) or {})
    technologies: list[str] = []
    for package_name, label in PACKAGE_TECH_MAP.items():
        if package_name in deps:
            technologies.append(label)
    if technologies:
        technologies.append("Node.js")
    return unique(technologies), sorted(deps.keys())[:18]


def read_evidence(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    evidence: list[str] = []
    for line in lines:
        text = line.strip().strip("#").strip()
        if not text or text.lower() in {"readme", "todo"}:
            continue
        evidence.append(text)
        if len(evidence) >= 4:
            break
    return evidence


def unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def collect_project(project_root: Path) -> dict:
    technologies: list[str] = []
    modules: list[str] = []
    evidence: list[str] = []
    files = {"pom": [], "package_json": [], "readme": []}
    dependency_signals: list[str] = []

    for path in walk_project(project_root):
        rel = path.relative_to(project_root).as_posix()
        lower_name = path.name.lower()
        if path.name == "pom.xml":
            tech, artifacts = parse_pom(path)
            technologies.extend(tech)
            dependency_signals.extend(artifacts)
            modules.append(str(path.parent.relative_to(project_root)) or ".")
            files["pom"].append(rel)
        elif path.name == "package.json":
            tech, deps = parse_package(path)
            technologies.extend(tech)
            dependency_signals.extend(deps)
            modules.append(str(path.parent.relative_to(project_root)) or ".")
            files["package_json"].append(rel)
        elif lower_name == "readme.md":
            files["readme"].append(rel)
            evidence.extend(read_evidence(path))

    return {
        "name": project_root.name,
        "path": str(project_root),
        "technologies": sorted(unique(technologies)),
        "modules": sorted(unique(module.replace("\\", "/") for module in modules)),
        "evidence": unique(evidence)[:10],
        "dependency_signals": sorted(unique(dependency_signals))[:40],
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", required=True, type=Path, help="Project root or container directory. Repeatable.")
    parser.add_argument("--out", required=True, type=Path, help="JSON output path.")
    args = parser.parse_args()

    roots = expand_roots(args.root)
    projects = [collect_project(root) for root in roots if root.exists()]
    payload = {
        "source_roots": [str(path.resolve()) for path in args.root],
        "projects": projects,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"collected {len(projects)} project(s) into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
