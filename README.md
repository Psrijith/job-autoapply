# 🤖 job-autoapply

**A Claude Code skill that applies to jobs for you — with a resume tailored to every job description.**

Give it your resume once. Then one command:

1. **Searches** LinkedIn, Naukri, Instahyre, Wellfound, Cutshort, Hirist + company career pages (Greenhouse, Lever, Ashby, Workday)
2. **Scores** every job 0–100 against your profile
3. **Asks you once** — a single table, you reply `all` / `1-5` / `all except 3`
4. **Writes a new resume for each JD**
5. **Fills and submits** the applications in your own Chrome
6. **Logs everything** so it never applies to the same job twice

```
#  Score  Company   Role                      Location   Note
1  92     Zscaler   SDE – Java + Distributed  Hyderabad  Java/Redis/AWS match
2  88     Stripe    Software Engineer (Grad)  Bangalore  eligible
3  79     GitLab    Backend Engineer          Remote     Go preferred (gap)
Which ones? → all
```

---

## 📄 A tailored resume for every job

For each job it reads the JD, picks out the key skills, and builds a one-page resume that:

- rewrites the **summary** in the JD's own words
- puts your **most relevant bullet first** under each role
- reorders **skills** to match the JD's stack
- picks the right **projects / achievements** (e.g. coding ranks for new-grad roles)
- uploads it as `Firstname_Lastname_Resume.pdf`

**It can't lie.** `tailor.py` rejects any resume that contains a number or skill not already in your original resume. It sharpens your story — it never invents one.

---

## ⚡ Uses very few tokens

- Searches company job boards through their **public APIs** — no browser needed
- **Filters by title/location first**, opens only the jobs worth reading
- **Reads pages as text**, screenshots only as a last resort
- Tailors a resume with a **~10-line edit**, not a full rewrite
- **Saves your answers** (notice period, CTC, work auth…) and reuses them on every form

---

## 🛡️ Safe by default

- Applies **only** to jobs you approved
- **Never** handles passwords, CAPTCHAs, OTPs or legal-consent boxes — hands them to you
- Daily cap and human pace (LinkedIn ≤ 15/day)
- Your personal data stays on your machine in `~/.claude/job-autoapply/` — never in this repo

---

## 🚀 Get started

```bash
git clone https://github.com/Psrijith/job-autoapply ~/.claude/skills/job-autoapply
```

Needs: Claude Code, the Claude in Chrome extension, Python 3.9+, Chrome or Edge.

Then in Claude Code:

| Say | It does |
|---|---|
| `/job-autoapply` | full run: search → approve → apply |
| `status` | shows what you applied to |
| `continue` | finishes pending applications |
| `tailor my resume for <JD>` | just makes the tailored PDF |

---

## 📁 What's inside

| File | Purpose |
|---|---|
| `SKILL.md` | the agent's step-by-step playbook |
| `scripts/ats_search.py` | fast job search via Greenhouse / Lever / Ashby APIs |
| `scripts/tailor.py` | builds a fact-checked tailored resume |
| `scripts/render_resume.py` | resume → one-page PDF |
| `scripts/tracker.py` | application log + duplicate check |
| `references/` | site quirks, profile & resume formats |

---

*Use responsibly and within each site's terms. Every application goes out under your name.*
