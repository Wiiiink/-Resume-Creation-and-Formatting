---
name: programmer-resume
description: Use when creating, rewriting, optimizing, formatting, or exporting programmer resumes from user facts or an existing resume, especially for Chinese IT, Java backend, frontend, software engineer, DOCX, PDF, template-based resume, or resume polishing requests.
---

# Programmer Resume

## Core Rule

Use `template/` as the source for resume structure, style, section rhythm, and example wording. Use the user's facts or old resume as the only source for factual claims. Never invent employers, dates, degrees, awards, metrics, projects, technologies, phone numbers, emails, or links.

## Workflow

1. Identify the input mode: structured facts, an existing resume, or both.
2. If `template/` contains `.zip` or `.rar` files, run `scripts/extract_template_archives.py --template-root template --delete-archives` before indexing.
3. Run `scripts/build_template_index.py` if `assets/template-index.json` is missing or stale.
4. Select a template profile from the index by target role, experience level, language, and desired length.
5. Read the relevant reference:
   - `references/template-corpus.md` for template families and selection.
   - `references/resume-writing-rules.md` for content rules and anti-hallucination rules.
   - `references/output-workflow.md` for DOCX/PDF generation and validation.
6. Draft or optimize content using template-derived section order and bullet style.
7. Generate DOCX with `scripts/generate_resume_docx.py`.
8. Export PDF with `scripts/export_pdf.py`.
9. Validate outputs with `scripts/validate_resume_package.py` before replying.

## Commands

Build or refresh the template index:

```bash
python programmer-resume/scripts/extract_template_archives.py --template-root template --delete-archives
python programmer-resume/scripts/build_template_index.py --template-root template --out programmer-resume/assets/template-index.json
```

Generate a DOCX package from normalized facts:

```bash
python programmer-resume/scripts/generate_resume_docx.py --facts resume-facts.json --template-index programmer-resume/assets/template-index.json --out-dir output/resume --language zh-CN
```

Export PDF:

```bash
python programmer-resume/scripts/export_pdf.py --docx output/resume/resume.docx --out output/resume/resume.pdf
```

Validate:

```bash
python programmer-resume/scripts/validate_resume_package.py --facts resume-facts.json --package-dir output/resume
```

## Output Contract

Return the generated DOCX/PDF paths, the selected template source, and any missing facts or assumptions. If PDF export cannot run because no converter is installed, say that clearly and still return the DOCX path.
