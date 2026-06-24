# Programmer Resume Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a template-grounded programmer resume Skill that helps agents generate or optimize resumes and export DOCX/PDF outputs.

**Architecture:** The repository keeps the source `template/` corpus, a `programmer-resume/` Skill folder, and tests. Scripts provide deterministic template indexing, text extraction, DOCX generation, PDF export, and package validation; the Skill tells agents how to combine those scripts with careful LLM drafting.

**Tech Stack:** Markdown Skill files, Python standard library, `python-docx` when available, local Office/LibreOffice/Word automation when available for PDF conversion, and `unittest` for no-extra-dependency tests.

---

## File Structure

- Create `tests/test_resume_skill_contract.py`: contract tests for required files, frontmatter, index generation, validation behavior, and sample generation.
- Create `tests/fixtures/sample_resume_facts.json`: structured sample facts used by generation tests.
- Create `programmer-resume/SKILL.md`: concise cross-agent Skill entry point.
- Create `programmer-resume/agents/openai.yaml`: Codex UI metadata.
- Create `programmer-resume/references/template-corpus.md`: template families and selection rules.
- Create `programmer-resume/references/resume-writing-rules.md`: content and anti-hallucination rules derived from templates.
- Create `programmer-resume/references/output-workflow.md`: DOCX/PDF output workflow and fallback behavior.
- Create `programmer-resume/scripts/build_template_index.py`: scan template corpus and emit JSON index.
- Create `programmer-resume/scripts/extract_template_archives.py`: safely extract `.zip`/`.rar` template packages into sibling folders and delete archives only after successful extraction.
- Create `programmer-resume/scripts/extract_resume_text.py`: extract inspectable text from template samples and old resumes.
- Create `programmer-resume/scripts/generate_resume_docx.py`: generate a DOCX from structured facts and a selected template profile.
- Create `programmer-resume/scripts/export_pdf.py`: convert DOCX to PDF or provide a clear diagnostic.
- Create `programmer-resume/scripts/validate_resume_package.py`: validate generated outputs for existence, placeholders, and required facts.
- Generate `programmer-resume/assets/template-index.json`: committed template index.
- Create `programmer-resume/assets/template-samples/`: copied inspectable text samples from representative templates.

---

### Task 1: Contract Tests

**Files:**
- Create: `tests/test_resume_skill_contract.py`
- Create: `tests/fixtures/sample_resume_facts.json`

- [ ] **Step 1: Write the failing contract tests**

Create `tests/test_resume_skill_contract.py` with tests that assert required files exist, validate Skill frontmatter, run template indexing, reject generated packages containing placeholders, and generate a sample DOCX.

Create `tests/fixtures/sample_resume_facts.json` with a Chinese Java backend engineer sample using clearly fake but realistic user-provided facts.

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_resume_skill_contract
```

Expected: FAIL because `programmer-resume/` and its scripts do not exist.

- [ ] **Step 3: Commit and push RED tests**

Run:

```powershell
git add tests
git commit -m "test: add programmer resume skill contract tests"
git push
```

---

### Task 2: Template Archive Extraction

**Files:**
- Create: `programmer-resume/scripts/extract_template_archives.py`
- Modify: `programmer-resume/references/template-corpus.md`
- Modify: `programmer-resume/references/output-workflow.md`

- [ ] **Step 1: Write the failing archive contract**

Update tests so the template corpus cannot contain `.zip` or `.rar` files, and `template-index.json` must not include archive extensions.

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'
```

Expected: FAIL while compressed template packages still exist.

- [ ] **Step 3: Implement `extract_template_archives.py`**

Implement safe extraction:

- Resolve every archive under `template/`.
- Extract each archive into a sibling folder named after the archive stem.
- Prevent path traversal by ensuring every output path remains inside the destination folder.
- Use Python `zipfile` for `.zip`.
- Use local `7z` for `.rar` if available.
- Delete an archive only after extraction succeeds and at least one output file exists.

- [ ] **Step 4: Extract archives and remove originals**

Run:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' programmer-resume/scripts/extract_template_archives.py --template-root template --delete-archives
```

Expected: `.zip` and extractable `.rar` files are gone, and their contents exist as ordinary files.

- [ ] **Step 5: Commit and push**

Run:

```powershell
git add programmer-resume template tests docs
git commit -m "feat: extract template archives"
git push
```

---

### Task 3: Template Indexing And Extraction

**Files:**
- Create: `programmer-resume/scripts/build_template_index.py`
- Create: `programmer-resume/scripts/extract_resume_text.py`
- Generate: `programmer-resume/assets/template-index.json`
- Create: `programmer-resume/assets/template-samples/`

- [ ] **Step 1: Implement `build_template_index.py`**

Implement a standard-library script that walks `template/`, records each file's relative path, extension, size, inferred role (`frontend`, `java-backend`, `general-programmer`, `visual-catalog`, `archive`, `writing-guide`), inferred page family (`one-page`, `two-page`, `three-page`, `four-page`, `cover`, `unknown`), and package group for zip siblings.

- [ ] **Step 2: Implement `extract_resume_text.py`**

Implement a script that extracts text from `.txt`, `.html`, `.docx`, and `.pdf` with graceful degradation. For `.doc` and unsupported PDFs, emit a diagnostic entry rather than crashing.

- [ ] **Step 3: Generate the template index**

Run:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' programmer-resume/scripts/build_template_index.py --template-root template --out programmer-resume/assets/template-index.json
```

Expected: JSON file includes at least 300 files and summary counts for `.docx`, `.doc`, `.zip`, `.pdf`, `.html`, `.txt`, and `.jpg`.

- [ ] **Step 4: Run tests to verify partial GREEN**

Run the unit tests. Expected: file/frontmatter tests may still fail until Skill docs exist, but index-related tests pass.

- [ ] **Step 5: Commit and push**

Commit scripts and generated index:

```powershell
git add programmer-resume/scripts programmer-resume/assets tests
git commit -m "feat: add template index and extraction scripts"
git push
```

---

### Task 4: Skill Documentation And Metadata

**Files:**
- Create: `programmer-resume/SKILL.md`
- Create: `programmer-resume/agents/openai.yaml`
- Create: `programmer-resume/references/template-corpus.md`
- Create: `programmer-resume/references/resume-writing-rules.md`
- Create: `programmer-resume/references/output-workflow.md`

- [ ] **Step 1: Write `SKILL.md`**

Write YAML frontmatter with:

```yaml
---
name: programmer-resume
description: Use when creating, rewriting, optimizing, formatting, or exporting programmer resumes from user facts or an existing resume, especially for Chinese IT, Java backend, frontend, software engineer, DOCX, PDF, template-based resume, or resume polishing requests.
---
```

The body must instruct agents to use the templates as the authoritative source for structure/style, use user facts as the only factual source, run the scripts, and validate DOCX/PDF outputs.

- [ ] **Step 2: Write references**

Create concise references for template selection, resume writing rules, and output workflow. Include the exact anti-hallucination rule: never invent employers, dates, degrees, awards, metrics, or technologies.

- [ ] **Step 3: Write `agents/openai.yaml`**

Create:

```yaml
interface:
  display_name: "Programmer Resume"
  short_description: "Generate template-grounded programmer resumes with DOCX/PDF output."
  default_prompt: "Use $programmer-resume to create or optimize my programmer resume from my facts and the bundled templates."

policy:
  allow_implicit_invocation: true
```

- [ ] **Step 4: Run tests**

Expected: frontmatter and metadata tests pass.

- [ ] **Step 5: Commit and push**

Run:

```powershell
git add programmer-resume/SKILL.md programmer-resume/agents programmer-resume/references
git commit -m "feat: add programmer resume skill instructions"
git push
```

---

### Task 5: DOCX Generation And Package Validation

**Files:**
- Create: `programmer-resume/scripts/generate_resume_docx.py`
- Create: `programmer-resume/scripts/validate_resume_package.py`
- Modify: `tests/test_resume_skill_contract.py`

- [ ] **Step 1: Implement `generate_resume_docx.py`**

Implement a CLI that accepts `--facts tests/fixtures/sample_resume_facts.json`, `--template-index programmer-resume/assets/template-index.json`, `--out-dir build/sample-resume`, and optional `--language zh-CN`. Generate a DOCX with sections matching common template structure: header, profile summary, professional skills, work experience, project experience, education, and certificates/awards when supplied.

- [ ] **Step 2: Implement `validate_resume_package.py`**

Validate that generated files exist, are non-empty, include required sample facts, and do not contain sample placeholders such as `XX`, `TBD`, `姓名`, `学校`, or `138-0138-0000`.

- [ ] **Step 3: Run sample generation**

Run:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' programmer-resume/scripts/generate_resume_docx.py --facts tests/fixtures/sample_resume_facts.json --template-index programmer-resume/assets/template-index.json --out-dir build/sample-resume --language zh-CN
```

Expected: `build/sample-resume/resume.docx` exists and is non-empty.

- [ ] **Step 4: Run package validation**

Run:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' programmer-resume/scripts/validate_resume_package.py --facts tests/fixtures/sample_resume_facts.json --package-dir build/sample-resume --allow-missing-pdf
```

Expected: PASS when DOCX exists and PDF has not yet been attempted.

- [ ] **Step 5: Run tests**

Expected: generation and validation tests pass.

- [ ] **Step 6: Commit and push**

Run:

```powershell
git add programmer-resume/scripts tests
git commit -m "feat: generate and validate programmer resume docx"
git push
```

---

### Task 6: PDF Export And Final Verification

**Files:**
- Create: `programmer-resume/scripts/export_pdf.py`
- Modify: `programmer-resume/references/output-workflow.md`
- Modify: `tests/test_resume_skill_contract.py`

- [ ] **Step 1: Implement `export_pdf.py`**

Implement a CLI that accepts `--docx build/sample-resume/resume.docx --out build/sample-resume/resume.pdf`. Try local conversion tools in this order: LibreOffice/soffice, Microsoft Word COM automation on Windows, then clear diagnostic JSON when no converter is available.

- [ ] **Step 2: Run PDF export**

Run:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' programmer-resume/scripts/export_pdf.py --docx build/sample-resume/resume.docx --out build/sample-resume/resume.pdf
```

Expected: either a non-empty PDF exists or the command exits with a diagnostic that names the missing converter.

- [ ] **Step 3: Run final validation**

Run:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_resume_skill_contract
```

Expected: PASS, allowing PDF diagnostic when local conversion tooling is absent.

- [ ] **Step 4: Commit and push**

Run:

```powershell
git add programmer-resume/scripts programmer-resume/references tests
git commit -m "feat: add pdf export workflow"
git push
```

---

### Task 7: Completion Audit

**Files:**
- Inspect all files above.

- [ ] **Step 1: Verify requirement coverage**

Check:

- Skill supports Codex and Claude Code compatible `SKILL.md`.
- Skill uses templates as style/source corpus.
- Skill supports structured facts and old-resume optimization workflow.
- Skill can generate DOCX.
- Skill attempts PDF export and clearly diagnoses missing tooling.
- Tests pass.
- All completed steps have been committed and pushed to GitHub.

- [ ] **Step 2: Final commit if docs changed**

If any audit notes modify files, commit and push with:

```powershell
git add .
git commit -m "docs: complete programmer resume skill audit"
git push
```
