# job-autoapply — a Claude Code skill that job-hunts for you

An end-to-end job application agent built as a [Claude Code](https://claude.com/claude-code) skill.
Give it your resume once; it searches job boards and company career pages, scores every match,
asks you for **one** batch approval, then tailors your resume per job description and fills +
submits the applications in your own Chrome — logging everything so it never applies twice.

## How it works

```
resume ──► profile (one-line prefs) ──► search ──► score 0-100 ──► ONE approval table
                                                                      │
             applications.jsonl ◄── submit ◄── fill form ◄── tailor resume per JD
```

1. **Setup (once)** – reads your resume, builds an editable `master.json` + PDF, infers your profile, and asks for the rest in a single fill-in line (roles, locations, CTC, notice period, deal-breakers…).
2. **Search** – LinkedIn, Naukri, Instahyre, Wellfound, Cutshort, Hirist, plus company ATS boards (Greenhouse, Lever, Ashby) via their public JSON APIs (`ats_search.py`). Pre-filters by title/seniority/location *before* opening any JD to save tokens.
3. **Score** – title & seniority 30 · skills 30 · location 15 · experience 15 · company 10. Deal-breakers score 0.
4. **Approve** – one compact table, best match first; you reply `all` / `1-5` / `all except 3`.
5. **Tailor** – a small edit spec per JD (new summary, bullet order, rewrites, skill order). `tailor.py` **rejects any number or skill not in your master resume**, so tailoring can't invent experience. Renders a one-page PDF via headless Chrome/Edge.
6. **Apply** – fills forms from profile → learned answers bank → resume, uploads a recruiter-friendly `Firstname_Lastname_Resume.pdf`, verifies required fields, submits, confirms the success page.
7. **Log & report** – `tracker.py` dedups across sites and runs (`check | seen | status | bulk | report`).

## Guardrails

- Never invents facts: every answer comes from the resume, profile, answers bank or the user.
- Submits only what you approved; never re-applies to anything already in the log.
- Never handles passwords, CAPTCHAs, OTPs or legal-consent checkboxes on your behalf — those are handed back to you.
- Keeps a human pace and a daily cap (LinkedIn ≤ ~15/day).
- Your personal data lives outside the skill, in `~/.claude/job-autoapply/` (never committed).

## Layout

```
SKILL.md                     # the agent's playbook
references/
  profile-schema.md          # preferences schema
  resume-tailoring.md        # master.json schema + tailoring process
  sites.md                   # search URLs and per-site apply quirks
scripts/
  ats_search.py              # Greenhouse / Lever / Ashby public-API search
  tailor.py                  # spec -> fact-checked tailored resume PDF
  render_resume.py           # resume JSON -> 1-page PDF (headless browser)
  tracker.py                 # application log, dedup and reports
```

## Install

```bash
git clone https://github.com/Psrijith/job-autoapply ~/.claude/skills/job-autoapply
```

Then in Claude Code (with the Claude in Chrome extension connected) run `/job-autoapply`.

## Disclaimer

Use responsibly and within each job site's terms of service. You stay accountable for every application sent under your name — review the approval table carefully.
