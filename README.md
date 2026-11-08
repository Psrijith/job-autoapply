# 🤖 job-autoapply

**A Claude Code skill that runs your job hunt end-to-end — search → score → one approval → a resume tailored to *each* JD → fill & submit → log.**

You give it your resume **once**. After that, one command finds matching jobs across job boards and company career pages, ranks them, asks you a single "which ones?", writes a fresh one-page resume for every job description, fills the application forms in *your own* Chrome and submits them — without ever inventing a fact about you, and without ever applying to the same job twice.

> Built for [Claude Code](https://claude.com/claude-code) + the Claude in Chrome extension. Type `/job-autoapply` (or just say *"apply to some backend roles in Bangalore for me"*).

---

## ✨ What it actually does

| Phase | What happens | You do |
|---|---|---|
| **0. Setup** (first run only) | Reads your resume (PDF/DOCX), converts it word-for-word into an editable `master.json` + a clean 1-page `master.pdf`, and pre-fills your profile from it (name, title, years, skills, education, city). | Send the resume path, then answer **one fill-in line**: roles, locations, CTC, notice period, deal-breakers, daily cap. |
| **1. Browser check** | Opens each job site in a new tab and checks you're logged in (reads the page as text, no screenshots). | Log in to any site it lists — it never touches passwords. |
| **2. Search** | Searches LinkedIn, Naukri, Instahyre, Indeed, Wellfound, Cutshort, Hirist, Foundit, IIMJobs **and** company ATS boards (Greenhouse, Lever, Ashby, Workday) filtered to the last 7–14 days. | Nothing. |
| **3. Score** | Ranks every survivor 0–100 against your profile. | Nothing. |
| **4. Approve** | Shows **one compact table** — the only checkpoint. | Reply `all`, `1-10`, or `all except 4,7`. |
| **5. Tailor** | Builds a **JD-specific resume** for each approved job (see below), fact-checked against your master resume. | Nothing (first tailored copy shows a 3-line before/after so you can OK the style). |
| **6. Apply** | Fills each form from profile → learned answers → resume, uploads the right PDF, checks required fields, submits, confirms the success page. | Only things a human must do: CAPTCHAs, OTP/email codes, legal-consent boxes. |
| **7. Report** | `Applied N · Needs input N · Failed N · Skipped N` + links. | Read it. 🎉 |

Example approval table:

```
#  Sc Company    Role                         Loc        Site        Apply  Note
1  92 Zscaler    SDE – Java + Distributed     Hyderabad  Greenhouse  form   Java/Redis/AWS match
2  88 Stripe     Software Engineer, New Grad  Bangalore  Greenhouse  form   ≤18 mo exp – eligible
3  79 GitLab     Intermediate Backend Eng     Remote-IN  Greenhouse  form   Ruby/Go preferred (gap)
Which ones? (all / 1-10 / all except 4,7)
```

---

## 📄 A new resume for every job description

This is the core feature. Recruiters and ATS filters skim for the JD's own words in the first few lines — so every application gets its own version of your resume.

**How a tailored resume is built**

1. **Map the JD → your evidence.** Pull 8–15 key requirements/keywords from the JD and map each one to a real line in `master.json` (or mark it a *gap*, which shows up as a note in the approval table).
2. **Write a tiny edit spec, not a new resume.** ~10 lines of JSON:
   ```json
   {
     "summary": "Backend engineer building secure Java/Go services: HMAC-authenticated relay ...",
     "bullets": {"0": [1, 0, "r:Built a relay integration service with per-API credential handling ...", 3, 2]},
     "skills":  {"Languages": ["Java", "Go", "Python"], "Data & Infrastructure": ["Redis", "Kafka"]},
     "section_order": ["experience", "skills", "projects", "achievements", "education"]
   }
   ```
   - **Summary** rewritten in the JD's vocabulary
   - **Bullets reordered** so the most relevant achievement is first under each role
   - **Optional `r:` rewrites** that re-phrase a bullet with JD terms (same facts)
   - **Skills regrouped & reordered** to mirror the JD's stack (only skills you already list)
   - **Projects / achievements** picked and ordered per role (e.g. new-grad roles lead with competitive-programming ranks)
3. **Fact-check (hard gate).** `tailor.py` **rejects the spec** if the output contains *any number* (%, latency, counts, years) or *any skill* that isn't already in your master resume. Tailoring can sharpen the story — it can't invent experience.
4. **Render to exactly one page.** `render_resume.py` prints via headless Chrome/Edge and reports the page count; if it's ≠ 1 the weakest bullets are dropped.
5. **Upload a recruiter-friendly file** named `Firstname_Lastname_Resume.pdf` (some ATSs show the filename to recruiters), while the dated per-job copy is kept locally: `tailored/2026-11-08_<company>.pdf`.

Typical per-role angles it produces from the same master resume:

| JD type | What gets pushed to the top |
|---|---|
| Distributed-systems / Java backend | high-throughput APIs, caching, Kafka/Redis, latency numbers |
| Data-integration / connectors | third-party API integrations, auth/token handling, DB migrations |
| Security platform | HMAC auth, credential isolation, security training |
| New-grad programs | GPA, competitive-programming rank, internships, fundamentals |
| Platform / DevEx | test coverage, observability, production ownership, AI tooling |

---

## ⚡ Built to be cheap on tokens

A naive agent that opens every job page, screenshots every form and rewrites whole resumes burns huge context. This skill is designed around not doing that:

| Technique | Saving |
|---|---|
| **Public ATS JSON APIs** (`ats_search.py`) for Greenhouse / Lever / Ashby — no browser, no login, one compact TSV line per job | Search dozens of companies for a few hundred tokens |
| **Pre-filter on the results list** (title, seniority, location, company) *before* opening any JD | The biggest saver — most jobs are dropped without reading them |
| **Batch dedup** — `tracker.py bulk` checks a whole results page in one call | One call instead of one per job |
| **Text over pixels** — `get_page_text` / `find` / `read_page`; screenshots only when text fails | Screenshots are the most expensive thing an agent can read |
| **Resume tailoring as a ~10-line diff spec** instead of regenerating the resume | ~a few hundred tokens per tailored resume |
| **Fetch form questions from the ATS API** before opening the form, so unknowns are batched up front | Fewer round-trips with you |
| **Lazy-loaded references** — site quirks and schemas are only read at the step that needs them | Small base prompt |
| **One-line chat updates**; page contents are never pasted back | Keeps the conversation lean |

---

## 🧠 Gets smarter every run

- **Answers bank (`answers.json`)** — every screening answer you give once (notice period, work authorization, "how did you hear", relocation, 5-day WFO…) is saved and reused on every future form.
- **Batched questions** — unknown questions mark the job `needs_input`, and after ~5 jobs you get *all* pending questions in one message, not one at a time.
- **Format matching** — answers are converted to what each form expects (LPA vs ₹, days vs months, dropdown wording).
- **Per-family resumes** — if you target different role families (e.g. backend vs AI/ML), it keeps a base version per family; jobs scoring 90+ get a fully per-JD copy.

---

## 🛡️ Guardrails (non-negotiable)

- **Never invents facts.** Every resume line and form answer comes from your resume, profile, answers bank or you — enforced in code for numbers and skills.
- **Submits only what you approved.** The approval table is the authorization; nothing else goes out.
- **Never applies twice.** URLs are normalized (tracking params stripped, job IDs like `gh_jid` kept) and checked against the log across all sites and runs; cross-site duplicates (same company + title + city) are collapsed to the easiest apply path.
- **Hands blockers back to you.** CAPTCHAs, OTP / email verification codes, passwords and legal-consent / arbitration checkboxes are never bypassed or ticked on your behalf.
- **Protects sensitive documents.** e.g. won't upload marksheets containing national ID numbers; strips documents to only the pages a form actually asks for.
- **Human pace + daily cap** (default 25/day, LinkedIn ≤ ~15/day to avoid anti-automation restrictions).
- **Your data stays local** in `~/.claude/job-autoapply/` and is never part of this repo.

---

## 📊 Scoring

| Factor | Weight |
|---|---|
| Title & seniority fit | 30 |
| Skills overlap | 30 |
| Location / work mode | 15 |
| Experience range vs. yours | 15 |
| Company preference | 10 |
| Any deal-breaker | → 0 |

Search stops once it has ~2× your daily cap above your threshold (default 70).

---

## 🗂️ Repo layout

```
SKILL.md                     # the agent's playbook (phases, rules, token budget)
references/
  profile-schema.md          # preferences schema (roles, CTC, notice, caps…)
  resume-tailoring.md        # master.json schema + tailoring process
  sites.md                   # search URLs + per-site apply quirks (Greenhouse, Lever, Ashby, Workday, Naukri…)
scripts/
  ats_search.py              # Greenhouse / Lever / Ashby public-API search → compact TSV
  tailor.py                  # spec → fact-checked, tailored 1-page resume PDF
  render_resume.py           # resume JSON → 1-page PDF via headless Chrome/Edge
  tracker.py                 # append-only application log: check | seen | status | bulk | report
```

Your local data (created on first run, git-ignored):

```
~/.claude/job-autoapply/
  profile.json               # your preferences
  answers.json               # learned screening answers
  applications.jsonl         # every job seen / applied / skipped, with notes
  resume/original.*  master.json  master.pdf  tailored/
```

---

## 🚀 Install & use

```bash
git clone https://github.com/Psrijith/job-autoapply ~/.claude/skills/job-autoapply
```

Requirements: Claude Code, the **Claude in Chrome** extension, Python 3.9+, and Chrome or Edge (for PDF rendering).

```
/job-autoapply                          # full run: search → approve → apply
"status" / "what did I apply to?"       # report from the log, no browser
"continue"                              # finish pending / needs-input jobs
"tailor my resume for <JD>"             # just produce a tailored PDF
"change my notice period to 30 days"    # profile edits
```

Useful scripts on their own:

```bash
python scripts/ats_search.py companies.txt --title "engineer|sde" --loc "india|bangalore|remote"
python scripts/tailor.py master.json spec.json out.pdf
python scripts/tracker.py report --since 2026-11-01
```

---

## ⚠️ Disclaimer

Use responsibly and within each site's terms of service. Applications go out under your name — review the approval table and the first tailored resume carefully.
