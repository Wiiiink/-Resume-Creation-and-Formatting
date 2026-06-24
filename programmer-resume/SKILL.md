---
name: programmer-resume
description: 当用户要创建、改写、优化、排版或导出程序员简历时使用，尤其适用于中文 IT、Java 后端、前端、软件工程师、DOCX、PDF、基于模板的简历生成、旧简历润色和简历格式化请求。
---

# 程序员简历

## 核心规则

必须把 `template/` 当作简历结构、样式、章节节奏和表达范式的来源。用户填写的信息或旧简历才是事实来源。不得编造公司、日期、学历、奖项、指标、项目、技术栈、手机号、邮箱或链接。

## 工作流

1. 判断输入模式：用户给了结构化基本信息、旧简历，还是两者都有。
2. 如果 `template/` 里还有 `.zip` 或 `.rar`，先运行 `scripts/extract_template_archives.py --template-root template --delete-archives`，把压缩包解压成普通文件并删除压缩包。
3. 如果 `assets/template-index.json` 缺失或过期，运行 `scripts/build_template_index.py` 重新建立模板索引。
4. 根据目标岗位、经验年限、语言和期望篇幅，从索引里选择模板画像。
5. 按需读取参考文档：
   - `references/template-corpus.md`：模板族、岗位方向和样式选择。
   - `references/resume-writing-rules.md`：内容改写规则和不得编造规则。
   - `references/output-workflow.md`：DOCX/PDF 生成、导出和验证流程。
6. 用模板里的章节顺序、标题、项目 bullet 节奏和排版习惯组织内容。
7. 用 `scripts/generate_resume_docx.py` 生成 DOCX。
8. 用 `scripts/export_pdf.py` 导出 PDF；如果本机没有转换器，必须生成清楚的诊断文件。
9. 回复前用 `scripts/validate_resume_package.py` 验证输出包。

## 常用命令

解压模板压缩包并刷新索引：

```bash
python programmer-resume/scripts/extract_template_archives.py --template-root template --delete-archives
python programmer-resume/scripts/build_template_index.py --template-root template --out programmer-resume/assets/template-index.json
```

根据规范化事实生成 DOCX：

```bash
python programmer-resume/scripts/generate_resume_docx.py --facts resume-facts.json --template-index programmer-resume/assets/template-index.json --out-dir output/resume --language zh-CN
```

导出 PDF：

```bash
python programmer-resume/scripts/export_pdf.py --docx output/resume/resume.docx --out output/resume/resume.pdf
```

验证输出：

```bash
python programmer-resume/scripts/validate_resume_package.py --facts resume-facts.json --package-dir output/resume
```

## 输出要求

最终回复必须给出生成的 DOCX/PDF 路径、所选模板来源、缺失信息和必要假设。如果 PDF 因缺少本机转换器无法导出，要明确说明原因，并仍然返回 DOCX 路径。
