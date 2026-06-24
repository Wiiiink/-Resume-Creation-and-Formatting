import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "programmer-resume"
PYTHON = sys.executable


class ProgrammerResumeSkillContractTests(unittest.TestCase):
    def test_required_skill_files_exist(self):
        required = [
            SKILL_DIR / "SKILL.md",
            SKILL_DIR / "agents" / "openai.yaml",
            SKILL_DIR / "references" / "template-corpus.md",
            SKILL_DIR / "references" / "resume-writing-rules.md",
            SKILL_DIR / "references" / "output-workflow.md",
            SKILL_DIR / "scripts" / "build_template_index.py",
            SKILL_DIR / "scripts" / "extract_resume_text.py",
            SKILL_DIR / "scripts" / "generate_resume_docx.py",
            SKILL_DIR / "scripts" / "export_pdf.py",
            SKILL_DIR / "scripts" / "validate_resume_package.py",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]

        self.assertEqual(missing, [])

    def test_skill_frontmatter_targets_programmer_resume_requests(self):
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertTrue(skill_text.startswith("---\n"))
        self.assertIn("name: programmer-resume", skill_text)
        self.assertIn("description:", skill_text)
        self.assertIn("programmer", skill_text.lower())
        self.assertIn("DOCX", skill_text.upper())
        self.assertIn("PDF", skill_text.upper())
        self.assertIn("template", skill_text.lower())
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
            self.assertGreaterEqual(data["summary"]["total_files"], 300)
            self.assertGreaterEqual(data["summary"]["extensions"][".docx"], 160)
            self.assertGreaterEqual(data["summary"]["extensions"][".doc"], 80)
            self.assertGreaterEqual(data["summary"]["extensions"][".zip"], 30)
            self.assertTrue(any(item["role"] == "frontend" for item in data["files"]))
            self.assertTrue(any(item["role"] == "java-backend" for item in data["files"]))

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


if __name__ == "__main__":
    unittest.main()
