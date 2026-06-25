import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "programmer-resume"
PYTHON = sys.executable
CANONICAL_TEMPLATE_NAME = "xxx.doc"
CANONICAL_TEMPLATE_HINT = "优秀简历汇总"


class ProgrammerResumeSkillContractTests(unittest.TestCase):
    def test_required_skill_files_exist(self):
        required = [
            SKILL_DIR / "SKILL.md",
            SKILL_DIR / "agents" / "openai.yaml",
            SKILL_DIR / "references" / "template-corpus.md",
            SKILL_DIR / "references" / "resume-writing-rules.md",
            SKILL_DIR / "references" / "output-workflow.md",
            SKILL_DIR / "scripts" / "extract_template_archives.py",
            SKILL_DIR / "scripts" / "build_template_index.py",
            SKILL_DIR / "scripts" / "extract_resume_text.py",
            SKILL_DIR / "scripts" / "collect_project_facts.py",
            SKILL_DIR / "scripts" / "generate_resume_docx.py",
            SKILL_DIR / "scripts" / "export_pdf.py",
            SKILL_DIR / "scripts" / "validate_resume_package.py",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]

        self.assertEqual(missing, [])

    def test_collect_project_facts_detects_stack_and_readme(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "sample-saas"
            frontend_dir = project_dir / "frontend"
            backend_dir = project_dir / "backend"
            frontend_dir.mkdir(parents=True)
            backend_dir.mkdir(parents=True)
            for index in range(120):
                (project_dir / f"note-{index:03d}.txt").write_text("not a manifest", encoding="utf-8")
            (project_dir / "README.md").write_text(
                "# Sample SaaS\n\nFull-stack project with low-code dashboards.",
                encoding="utf-8",
            )
            (backend_dir / "pom.xml").write_text(
                """<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>sample-backend</artifactId>
  <dependencies>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
    <dependency><groupId>com.mysql</groupId><artifactId>mysql-connector-j</artifactId></dependency>
  </dependencies>
</project>""",
                encoding="utf-8",
            )
            (frontend_dir / "package.json").write_text(
                json.dumps({"dependencies": {"vue": "^3.0.0", "vite": "^5.0.0"}}, indent=2),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    PYTHON,
                    str(SKILL_DIR / "scripts" / "collect_project_facts.py"),
                    "--root",
                    str(project_dir),
                    "--out",
                    str(Path(temp_dir) / "facts.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((Path(temp_dir) / "facts.json").read_text(encoding="utf-8"))
            project = data["projects"][0]
            self.assertEqual(project["name"], "sample-saas")
            self.assertIn("Spring Boot", project["technologies"])
            self.assertIn("Vue", project["technologies"])
            self.assertIn("MySQL", project["technologies"])
            self.assertIn("Full-stack project", " ".join(project["evidence"]))

    def test_skill_frontmatter_targets_programmer_resume_requests(self):
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertTrue(skill_text.startswith("---\n"))
        self.assertIn("name: programmer-resume", skill_text)
        self.assertIn("description:", skill_text)
        self.assertIn("programmer", skill_text.lower())
        self.assertIn("DOCX", skill_text.upper())
        self.assertIn("PDF", skill_text.upper())
        self.assertIn("template", skill_text.lower())
        self.assertIn("程序员简历", skill_text)
        self.assertIn("模板", skill_text)
        self.assertIn("不得编造", skill_text)
        self.assertNotIn("TODO", skill_text.upper())

    def test_template_index_script_builds_expected_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "template-index.json"
            result = subprocess.run(
                [
                    PYTHON,
                    str(SKILL_DIR / "scripts" / "build_template_index.py"),
                    "--template-root",
                    str(ROOT / "template"),
                    "--out",
                    str(out_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["total_files"], 1)
            self.assertEqual(data["summary"]["extensions"][".doc"], 1)
            self.assertEqual(data["summary"]["extensions"].get(".docx", 0), 0)
            self.assertEqual(data["summary"]["extensions"].get(".zip", 0), 0)
            self.assertEqual(data["summary"]["extensions"].get(".rar", 0), 0)
            self.assertEqual(data["files"][0]["path"].replace("\\", "/").split("/")[-1], CANONICAL_TEMPLATE_NAME)
            self.assertIn(CANONICAL_TEMPLATE_HINT, data["files"][0]["path"])

    def test_template_directory_contains_only_canonical_template(self):
        files = sorted(path for path in (ROOT / "template").rglob("*") if path.is_file())
        relative_files = [path.relative_to(ROOT).as_posix() for path in files]

        self.assertEqual(len(relative_files), 1, relative_files[:10])
        self.assertEqual(files[0].name, CANONICAL_TEMPLATE_NAME)
        self.assertIn(CANONICAL_TEMPLATE_HINT, relative_files[0])

    def test_template_archives_have_been_extracted_and_removed(self):
        archives = sorted(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "template").rglob("*")
            if path.is_file() and path.suffix.lower() in {".zip", ".rar"}
        )

        self.assertEqual(archives, [])

    def test_validate_package_rejects_placeholders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir)
            (package_dir / "resume.txt").write_text(
                "林晨\nJava 后端开发工程师\n这里残留 XX 占位符\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    PYTHON,
                    str(SKILL_DIR / "scripts" / "validate_resume_package.py"),
                    "--facts",
                    str(ROOT / "tests" / "fixtures" / "sample_resume_facts.json"),
                    "--package-dir",
                    str(package_dir),
                    "--allow-missing-pdf",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("placeholder", (result.stdout + result.stderr).lower())

    def test_validate_package_allows_field_labels(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            facts_path = Path(temp_dir) / "facts.json"
            facts_path.write_text(
                json.dumps(
                    {
                        "target_role": "全栈开发工程师",
                        "personal": {"name": "郑发炜"},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            package_dir = Path(temp_dir) / "package"
            package_dir.mkdir()
            (package_dir / "resume.txt").write_text(
                "姓名：郑发炜\n求职意向：全栈开发工程师\n专业背景：软件工程\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    PYTHON,
                    str(SKILL_DIR / "scripts" / "validate_resume_package.py"),
                    "--facts",
                    str(facts_path),
                    "--package-dir",
                    str(package_dir),
                    "--allow-missing-pdf",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generate_resume_docx_from_sample_facts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir) / "resume-package"
            result = subprocess.run(
                [
                    PYTHON,
                    str(SKILL_DIR / "scripts" / "generate_resume_docx.py"),
                    "--facts",
                    str(ROOT / "tests" / "fixtures" / "sample_resume_facts.json"),
                    "--template-index",
                    str(SKILL_DIR / "assets" / "template-index.json"),
                    "--out-dir",
                    str(out_dir),
                    "--language",
                    "zh-CN",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            docx_path = out_dir / "resume.docx"
            self.assertTrue(docx_path.exists())
            self.assertGreater(docx_path.stat().st_size, 5_000)
            metadata = json.loads((out_dir / "metadata.json").read_text(encoding="utf-8"))
            self.assertTrue(metadata["selected_template"]["path"].endswith(CANONICAL_TEMPLATE_NAME))
            self.assertIn(CANONICAL_TEMPLATE_HINT, metadata["selected_template"]["path"])
            self.assertEqual(metadata["style_source"], "canonical xxx.doc template")
            self.assertTrue((out_dir / "resume-render.json").exists())
            with zipfile.ZipFile(docx_path) as archive:
                document_xml = archive.read("word/document.xml")
            self.assertIn(b"0070C0", document_xml)
            self.assertIn(b"C8A96A", document_xml)

            pdf_result = subprocess.run(
                [
                    PYTHON,
                    str(SKILL_DIR / "scripts" / "export_pdf.py"),
                    "--docx",
                    str(docx_path),
                    "--out",
                    str(out_dir / "resume.pdf"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(pdf_result.returncode, 0, pdf_result.stderr)
            pdf_path = out_dir / "resume.pdf"
            self.assertTrue(pdf_path.exists())
            self.assertGreater(pdf_path.stat().st_size, 1_000)

    def test_generate_resume_omits_empty_optional_sections(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            facts_path = Path(temp_dir) / "facts.json"
            facts_path.write_text(
                json.dumps(
                    {
                        "target_role": "全栈开发工程师",
                        "personal": {"name": "郑发炜"},
                        "summary": "软件工程专业背景，面向全栈开发。",
                        "skills": {},
                        "work_experience": [],
                        "projects": [
                            {
                                "name": "Sample",
                                "role": "全栈开发",
                                "technologies": ["Spring Boot", "Vue"],
                                "bullets": ["实现前后端分离功能。"],
                            }
                        ],
                        "education": [{"major": "软件工程"}],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            out_dir = Path(temp_dir) / "resume-package"
            result = subprocess.run(
                [
                    PYTHON,
                    str(SKILL_DIR / "scripts" / "generate_resume_docx.py"),
                    "--facts",
                    str(facts_path),
                    "--template-index",
                    str(SKILL_DIR / "assets" / "template-index.json"),
                    "--out-dir",
                    str(out_dir),
                    "--language",
                    "zh-CN",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            text = (out_dir / "resume.txt").read_text(encoding="utf-8")
            self.assertNotIn("工作经历", text)
            self.assertIn("教育背景\n软件工程", text)


if __name__ == "__main__":
    unittest.main()
