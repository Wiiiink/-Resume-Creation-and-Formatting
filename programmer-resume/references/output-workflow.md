# Output Workflow

Use this reference when creating final resume artifacts.

## Normal Output Flow

1. Build or refresh `assets/template-index.json`.
2. Normalize user facts into JSON.
3. Generate DOCX with `scripts/generate_resume_docx.py`.
4. Export PDF with `scripts/export_pdf.py`.
5. Validate with `scripts/validate_resume_package.py`.
6. Return paths and the selected template source.

## DOCX Rules

- Preserve template-derived section order.
- Use compact programmer resume spacing.
- Use Chinese font-friendly defaults for Chinese output.
- Include a plain text companion file when generating a package; it helps validation and review.

## PDF Rules

`scripts/export_pdf.py` tries:

1. LibreOffice or `soffice`.
2. Microsoft Word COM automation on Windows.
3. Diagnostic JSON if no converter is available.

PDF export failure is acceptable only when the diagnostic clearly names the missing converter. Always validate and return the DOCX.

## Validation Rules

Validation must confirm:

- The package directory exists.
- `resume.docx` exists and is non-empty.
- Required user facts appear in generated text.
- Obvious placeholders and sample contact values are absent.
- `resume.pdf` exists unless the command was run with `--allow-missing-pdf`.
