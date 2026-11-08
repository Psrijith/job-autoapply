# Resume tailoring

The user's original resume is never modified. Tailored versions are **new copies** built from a structured master.

## Files

```
~/.claude/job-autoapply/resume/
├── original.pdf             # untouched copy of what the user gave you
├── master.json              # structured, complete, truthful source of everything on the resume
├── master.pdf               # render of master.json — should look like the original
└── tailored/
    ├── backend.json / .pdf  # role-family variants (reused across many jobs)
    └── 2026-11-08_razorpay_senior-backend.json / .pdf   # per-job variants for top matches
```

## Building master.json (first run)

Read the original PDF and transcribe it into the schema below **verbatim** — same bullets, same numbers, same bold emphasis (`**...**`), and links as `[text](url)`. If the PDF hides link URLs behind text like "LinkedIn", ask the user for those URLs. Then render it with
`python scripts/render_resume.py master.json master.pdf`. Ask the user to check that master.pdf matches the original before you tailor anything from it.

```json
{
  "name": "",
  "contact": [{"text": "email@x.com", "url": "mailto:email@x.com"}, {"text": "LinkedIn", "url": "https://..."}],
  "summary": "",
  "section_order": ["experience", "skills", "projects", "achievements", "education"],
  "experience": [{"title": "", "company": "", "company_url": null, "dates": "", "location": "", "bullets": [""]}],
  "skills": [{"group": "Languages", "items": ["Java"]}],
  "projects": [{"name": "", "stack": "", "bullets": [""]}],
  "projects_footer": "More deployed projects: [github.com/x](https://github.com/x)",
  "achievements": [""],
  "education": [{"degree": "", "institution": "", "dates": "", "score": ""}]
}
```

`master.json` can also hold extra true material that didn't fit on one page, such as more projects or bullets the user mentions, under `"reserve": {"bullets": {...}, "projects": [...]}`. Tailored copies can pull from it.

## When to tailor

- **Role-family variants**: when targets span different families (e.g. backend vs. ML/AI vs. full-stack), make one variant per family and use it as the default for that family's jobs. This gives most of the benefit for little cost.
- **Per-job variants**: for jobs scoring 85+ or where the JD stresses things the family variant buries. Make these during Phase 4, just before applying.
- Otherwise, upload the closest variant (or master.pdf).

Record which file was uploaded in the tracker note (`--note "resume: tailored/backend.pdf"`).

## What tailoring may and may not change

The guiding rule is that a recruiter who later interviews the user should find every line true. Tailoring changes **emphasis**, never **facts**.

Allowed:
- Rewrite the summary to lead with what the JD cares about, using only skills and experience in master.json.
- Reorder bullets within a job, reorder skill groups and items, and reorder sections (e.g. projects above skills for ML roles).
- Reword a bullet to use the JD's vocabulary for the *same* work (e.g. "relay service" → "API integration service", "OpenSearch" can be noted as "OpenSearch (Elasticsearch-compatible)").
- Bold different keywords.
- Drop low-relevance bullets, skills or projects to keep one page, and swap in items from `reserve`.

Not allowed:
- Adding a skill, tool, employer, title, certification or responsibility the user doesn't have.
- Changing any number, date, metric, GPA, ranking or job title.
- Stretching scope ("contributed to" → "led") or claiming JD requirements the user doesn't meet.

If a JD requires something the user lacks, leave it off the resume and mention the gap in the shortlist notes instead.

## Process (keep it cheap: write a spec, not a resume)

1. Pull 8–15 key requirements and keywords from the JD, and map each one to evidence in master.json (or mark it "gap").
2. Write a small spec JSON (format in the `scripts/tailor.py` docstring). It holds the new summary, the bullet order by index, a few `"r:"` rewrites, and the skill order. Don't copy unchanged text into it.
3. Run `python scripts/tailor.py master.json spec.json tailored/<name>.pdf`. It rejects any number or skill that isn't in master.json; fix the spec and run it again. If `pages` ≠ 1, drop the weakest bullets.
4. The **first time** you tailor in a session, show the user a short before/after of the summary and the 2–3 most-changed bullets, and get their OK on the style. After that, tailor without asking.

File names: `YYYY-MM-DD_<company>_<role-slug>.pdf`, lowercase with hyphens. Some ATS forms show the file name to recruiters, so if the site shows it, upload a copy named `<Firstname>_<Lastname>_Resume.pdf` instead.
