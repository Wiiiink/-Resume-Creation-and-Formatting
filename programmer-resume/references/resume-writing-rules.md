# Resume Writing Rules

Use this reference when drafting or optimizing resume content.

## Fact Rules

- Use user-provided facts or the old resume as the only factual source.
- Never invent employers, dates, degrees, awards, metrics, projects, technologies, phone numbers, emails, or links.
- When a local project directory is provided, use `collect_project_facts.py` output only as evidence for project names, modules, README descriptions, and dependency-derived technologies.
- Do not turn repository evidence into unsupported claims about company ownership, employment dates, team size, user scale, performance gains, revenue, or production deployment.
- If a useful metric is missing, write the bullet without a fake number or ask for the missing metric.
- Treat template names, sample people, sample phone numbers, sample schools, and sample companies as formatting examples only.
- Remove obvious template placeholders such as `XX`, `姓名`, `学校`, `手机号`, `TBD`, and sample contact values.

## Programmer Resume Structure

Common programmer templates use:

1. Header: name, target role, phone, email, city, optional GitHub/blog.
2. Profile summary: 1-3 lines matching years of experience and target role.
3. Professional skills: grouped by language, framework, database, tooling, operating system.
4. Work experience: company, role, dates, and responsibility/result bullets.
5. Project experience: project name, role, dates, stack, context, responsibilities, results.
6. Education: school, major, degree, dates.
7. Certificates/awards: include only if provided.

## Bullet Style

- Start bullets with concrete actions: 负责, 参与, 设计, 实现, 优化, 编写, 推动.
- Prefer action + object + method + result.
- Keep each bullet to one main idea.
- Use technology names only when supplied by the user or old resume.
- For Chinese resumes, keep wording direct and work-focused.

## Optimization Rules

- Convert vague responsibilities into sharper statements without adding facts.
- Preserve dates, company names, education, and project facts from the old resume.
- If only repository evidence exists, write project bullets as implementation work (`负责/实现/参与`) and omit dates or metrics that were not supplied.
- Replace template sample sections with equivalent user sections.
- If the user's facts do not support a section, omit the section rather than filling it with sample text.
