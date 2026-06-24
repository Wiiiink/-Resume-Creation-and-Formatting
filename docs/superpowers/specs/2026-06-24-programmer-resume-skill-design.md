# Programmer Resume Skill Design

Date: 2026-06-24

## Goal

Create a reusable programmer-resume Skill for Codex, Claude Code, and other agent runtimes. The Skill must guide an agent to generate or optimize a programmer resume from either structured user facts or an existing resume, then export professional `.docx` and `.pdf` artifacts.

The `template/` directory is the authoritative style and example corpus. The agent may use the user's facts and prior resume as factual input, but resume structure, section choices, visual style, example phrasing, and formatting patterns must be derived from the bundled templates.

## Current Evidence

The workspace contains `template/.程序员简历模板互联网IT行业程序员自动发货/` with:

- 164 `.docx` files and 88 `.doc` files.
- 39 `.zip` packages, each typically containing a PDF, Word file, text file, and HTML version.
- 5 `.jpg` visual catalogs for single-page, two-page, three-page, four-page, and cover templates.
- Frontend templates with `.txt`, `.html`, `.doc`, and `.pdf` examples.
- Backend Java resume examples grouped by years of experience and location/example quality.

One template note says each package includes PDF for best print output, Word for local editing, text for information editing, and HTML for viewing style. This supports a workflow that extracts text/structure from examples and preserves Word/PDF layout as output formats.

## Proposed Approaches

### Recommended: Template-Corpus Skill With Deterministic Scripts

Build a Skill folder in this repository with concise `SKILL.md`, targeted references, template assets, and Python scripts for indexing, extracting, selecting, and rendering resumes. The agent uses the Skill to choose a template profile, map user facts into template sections, draft content under strict factual constraints, then export `.docx` and `.pdf`.

Trade-off: more upfront scripting, but much better agent reliability and less free-form drift.

### Alternative: Instruction-Only Skill

Create a short Skill that tells agents to inspect the `template/` directory manually and produce resumes from those files.

Trade-off: faster to write, but weak harnessing. Different agents will inspect different files, miss style patterns, and produce inconsistent outputs.

### Alternative: Full Resume Web App

Build an interactive resume generator with template picker, preview, editing, and export.

Trade-off: richer UX, but too broad for the first Skill. It delays the core agent harness and introduces frontend complexity not required by the current request.

## Skill Architecture

Create a root Skill folder named `programmer-resume`:

```text
programmer-resume/
  SKILL.md
  agents/openai.yaml
  references/
    template-corpus.md
    resume-writing-rules.md
    output-workflow.md
  scripts/
    build_template_index.py
    extract_resume_text.py
    generate_resume_docx.py
    export_pdf.py
    validate_resume_package.py
  assets/
    template-index.json
    template-samples/
```

`SKILL.md` stays compact and tells agents when to use the Skill, how to choose input mode, how to load references only when needed, and which scripts to run.

`references/template-corpus.md` documents the available template families and when to choose each one: frontend, Java/backend, general programmer, one-page, two-page, multi-page, and visual catalog usage.

`references/resume-writing-rules.md` captures the content rules learned from the templates: common sections, Chinese resume conventions, project bullet style, skill taxonomy, experience-level patterns, and strict anti-hallucination rules.

`references/output-workflow.md` describes DOCX/PDF rendering, template preservation, validation, and what to do when Word/PDF conversion tools are missing.

## Script Responsibilities

`build_template_index.py` scans `template/`, classifies files by path, extension, role, page count hints, job direction, and package membership, then writes `programmer-resume/assets/template-index.json`.

`extract_resume_text.py` extracts text from `.txt`, `.html`, `.docx`, `.doc`, and `.pdf` where possible. It prefers text and HTML from zip packages because those are easy to inspect and align with Word/PDF companions.

`generate_resume_docx.py` accepts normalized resume facts plus a selected template profile and generates a `.docx`. It must preserve the selected template's section order and visual conventions as much as practical.

`export_pdf.py` converts a generated `.docx` to `.pdf` using available local office/document tooling. If PDF conversion is unavailable, it must report a clear actionable error.

`validate_resume_package.py` checks that generated outputs exist, are non-empty, include required user facts, do not contain obvious placeholders such as `XX`, `TBD`, or sample names, and include both DOCX and PDF when PDF export succeeds.

## Agent Workflow

1. Determine whether the user supplied structured facts, an old resume, or both.
2. Extract or ask for missing critical facts: target role, name/contact, years of experience, education, skills, work history, projects, and desired language.
3. Choose a template profile from `template-index.json` based on target role, experience level, resume length, and visual preference.
4. Read only the relevant template samples and references.
5. Draft or optimize the resume using user-provided facts only. Do not invent employers, dates, awards, metrics, degrees, or technologies.
6. Use template-derived section order, section names, bullet rhythm, and formatting.
7. Generate DOCX, export PDF, and validate the output package.
8. Return the output paths plus a short summary of assumptions and any missing facts.

## Data Rules

The templates provide:

- Style and layout.
- Section structure.
- Resume-writing examples.
- Common programmer skill categories.
- Example phrasing patterns and bullet density.

The user or old resume provides:

- Personal identity and contact information.
- Education, employment, project facts, technologies actually used, dates, awards, and metrics.

The agent must not fabricate missing factual details. If a template contains sample facts, use them only as formatting and phrasing examples, not as facts for the user's resume.

## Cross-Agent Compatibility

The Skill must avoid platform-specific assumptions in the core instructions. It should work for:

- Codex skills via `SKILL.md` and `agents/openai.yaml`.
- Claude Code skills via the same `SKILL.md` folder structure.
- Other agent harnesses that can read Markdown instructions and run scripts.

Tool names in the Skill should be generic: read files, run scripts, inspect generated outputs, and render/convert documents. Platform-specific notes belong in references, not in the main trigger description.

## Testing And Validation

Validation starts before implementation:

- Baseline scenarios document what an agent would likely do without this Skill, such as inventing facts, ignoring templates, or generating Markdown only.
- Script tests cover template indexing, text extraction, placeholder detection, and output package validation.
- A sample structured input test generates DOCX and attempts PDF export.
- A prior-resume optimization test ensures old resume facts are preserved while template style changes.

Completion requires:

- Valid Skill frontmatter and metadata.
- Generated `template-index.json`.
- Working extraction/index scripts.
- At least one generated DOCX from sample facts.
- PDF export attempted and either successful or clearly diagnosed.
- Validation command passing.
- Git commits and GitHub pushes after each completed step.

## First Implementation Slice

1. Initialize and push the repository with this design spec.
2. Create failing validation scenarios and basic script tests.
3. Scaffold `programmer-resume/` using the Skill creator pattern.
4. Implement template indexing and extraction.
5. Write references and `SKILL.md`.
6. Implement DOCX/PDF generation workflow.
7. Validate with a sample programmer resume package.

