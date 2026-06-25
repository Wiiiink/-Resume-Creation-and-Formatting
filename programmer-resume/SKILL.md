---
name: programmer-resume
description: 当用户要创建、改写、优化、排版或导出程序员简历时使用，尤其适用于中文 IT、Java 后端、全栈开发、DOCX、PDF、严格复刻内置 xxx.doc 蓝金模板样式、旧简历润色和求职简历格式化请求。
---

# 程序员简历

## 核心规则

必须只把 `template/.程序员简历模板互联网IT行业程序员自动发货/后端简历/java简历/java简历/优秀简历汇总/xxx.doc` 当作简历结构、样式、章节节奏和表达范式来源。用户填写的信息、旧简历或本地项目事实才是事实来源。不得编造公司、日期、学历、奖项、指标、项目、技术栈、手机号、邮箱或链接。

## 工作流

1. 判断输入模式：用户给了结构化基本信息、旧简历、本地项目目录，还是多种输入组合。
2. 如果用户给了项目目录，先运行 `scripts/collect_project_facts.py` 生成项目事实 JSON；项目目录只能用于提取项目名、模块、README 线索和依赖技术栈，不得推断公司、日期、指标或头衔。
3. 确认 `template/` 只保留 `优秀简历汇总/xxx.doc`，不得从其他模板取样式。
4. 如果 `assets/template-index.json` 缺失或过期，运行 `scripts/build_template_index.py` 重新建立单模板索引。
5. 固定使用 `xxx.doc` 的蓝色分区条、顶部蓝金横条、基本信息双栏、开发技能箭头列表和项目段落节奏。
6. 按需读取参考文档：
   - `references/template-corpus.md`：模板族、岗位方向和样式选择。
   - `references/resume-writing-rules.md`：内容改写规则和不得编造规则。
   - `references/output-workflow.md`：DOCX/PDF 生成、导出和验证流程。
7. 用 `xxx.doc` 的章节顺序、标题条、项目 bullet 节奏和排版习惯组织内容。
8. 用 `scripts/generate_resume_docx.py` 生成 DOCX。
9. 用 `scripts/export_pdf.py` 导出 PDF；如果本机没有转换器，必须生成清楚的诊断文件。
10. 回复前用 `scripts/validate_resume_package.py` 验证输出包。

## 常用命令

刷新单模板索引：

```bash
python programmer-resume/scripts/build_template_index.py --template-root template --out programmer-resume/assets/template-index.json
```

根据规范化事实生成 DOCX：

```bash
python programmer-resume/scripts/collect_project_facts.py --root D:/Projects --out output/project-facts.json
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
