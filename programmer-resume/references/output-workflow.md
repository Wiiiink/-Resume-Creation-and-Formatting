# 输出流程

创建最终简历文件时读取本文件。

## 标准流程

1. 如果 `template/` 仍有 `.zip` 或 `.rar`，运行 `scripts/extract_template_archives.py --template-root template --delete-archives`。
2. 运行 `scripts/build_template_index.py` 建立或刷新 `assets/template-index.json`。
3. 将用户信息或旧简历内容整理成 JSON 事实。
4. 用 `scripts/generate_resume_docx.py` 生成 DOCX。
5. 用 `scripts/export_pdf.py` 导出 PDF。
6. 用 `scripts/validate_resume_package.py` 验证输出。
7. 返回输出路径和所选模板来源。

## DOCX 规则

- 保留模板语料中的章节顺序。
- 使用紧凑的程序员简历间距。
- 中文输出要使用适合中文显示的默认字体。
- 同时生成 `resume.txt`，便于验证和人工检查。

## PDF 规则

`scripts/export_pdf.py` 会按顺序尝试：

1. LibreOffice 或 `soffice`。
2. Windows 上的 Microsoft Word COM 自动化。
3. 使用 ReportLab 从 DOCX 文本渲染 PDF。
4. 如果都不可用，生成诊断 JSON。

只有诊断文件清楚说明缺少哪个转换器时，PDF 导出失败才可接受。无论 PDF 是否成功，都必须返回 DOCX。

## 验证规则

验证必须确认：

- 输出目录存在。
- `resume.docx` 存在且非空。
- 必要用户事实出现在生成文本中。
- 没有明显占位符和模板样例联系方式。
- 除非使用 `--allow-missing-pdf`，否则必须存在 `resume.pdf` 或 PDF 诊断文件。
