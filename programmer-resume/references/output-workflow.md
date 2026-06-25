# 输出流程

创建最终简历文件时读取本文件。

## 标准流程

1. 确认 `template/` 只保留 `优秀简历汇总/xxx.doc`。
2. 运行 `scripts/build_template_index.py` 建立或刷新单模板 `assets/template-index.json`。
3. 如果用户提供本地项目目录，运行 `scripts/collect_project_facts.py --root <project-dir> --out <output>/project-facts.json`。
4. 将用户信息、旧简历内容和项目事实整理成 JSON 事实；缺少的联系方式、学校、日期、指标必须留空或省略。
5. 用 `scripts/generate_resume_docx.py` 生成 DOCX。
6. 用 `scripts/export_pdf.py` 导出 PDF。
7. 用 `scripts/validate_resume_package.py` 验证输出。
8. 返回输出路径和所选模板来源。

## DOCX 规则

- 保留 `xxx.doc` 的蓝金色视觉系统、章节顺序和紧凑间距。
- `scripts/generate_resume_docx.py` 必须同时生成 `resume-render.json`，供 PDF 使用同一套样式渲染。
- 中文输出要使用适合中文显示的默认字体。
- 同时生成 `resume.txt`，便于验证和人工检查。

## PDF 规则

`scripts/export_pdf.py` 会按顺序尝试：

1. 如果同目录有 `resume-render.json`，使用 ReportLab 按 canonical 蓝金样式直接渲染 PDF。
2. LibreOffice 或 `soffice`。
3. Windows 上的 Microsoft Word COM 自动化。
4. 使用 ReportLab 从 DOCX 文本渲染 PDF。
5. 如果都不可用，生成诊断 JSON。

只有诊断文件清楚说明缺少哪个转换器时，PDF 导出失败才可接受。无论 PDF 是否成功，都必须返回 DOCX。

## 验证规则

验证必须确认：

- 输出目录存在。
- `resume.docx` 存在且非空。
- 必要用户事实出现在生成文本中。
- 没有明显占位符和模板样例联系方式。
- 除非使用 `--allow-missing-pdf`，否则必须存在 `resume.pdf` 或 PDF 诊断文件。
