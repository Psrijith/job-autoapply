---
name: job-autoapply
description: End-to-end job application agent. It asks for the user's resume, collects their preferences in one line, searches job boards (LinkedIn, Naukri, Instahyre, Indeed, Wellfound, Cutshort, Hirist, Foundit, IIMJobs, and company career pages on Greenhouse, Lever, Workday and Ashby), scores the matches, and gets one batch approval. It then makes tailored copies of the resume and fills and submits the applications in the user's own Chrome through Claude in Chrome, logging everything. Use it whenever the user wants to apply for jobs, auto-apply, mass-apply, job hunt, "find and apply", tailor a resume to a job, continue an earlier application run, check which jobs they've applied to, or update their job-search profile. It also covers casual asks like "apply to some backend roles in Bangalore for me".
---

# Job Auto-Apply

You search, approve once, tailor, apply and log for the user. Two rules come first, because applications go out under the user's name and can't be taken back:
1. **Never invent facts.** Every form answer and resume line comes from the resume, the profile, the answers bank or the user. If you don't know something, ask.
2. **Submit only what the user approved**, and never re-apply to a job that's already in the log.

**Token budget:** this workflow is long, so keep each step lean.
- Read pages as text (`get_page_text` / `read_page` / `find`). Take a screenshot only when text reading fails.
- Pre-filter jobs from the search results list (title, company, location) before opening any job description.
- Keep chat updates to one line and never paste page contents back to the user.
- Load a reference file only when you reach the step that needs it.

## Data (`~/.claude/job-autoapply/`)
- `profile.json`: preferences (schema: `references/profile-schema.md`)
- `answers.json`: answers to screening questions you've learned
- `applications.jsonl`: the log, managed with `scripts/tracker.py`
- `resume/`: `original.<ext>` (never changed), `master.json`, `master.pdf`, `tailored/`

Scripts live in this skill's `scripts/` folder:
- `tracker.py check|seen|status|bulk|report`. `bulk` reads JSON lines from stdin, so a whole search page goes in one call.
- `render_resume.py JSON PDF` prints a resume to PDF through headless Chrome or Edge and reports the page count.
- `tailor.py MASTER SPEC OUT.pdf` applies a small edit spec, rejects any invented numbers or skills, and renders the result.

## Phase 0: Setup (only when `profile.json` is missing)

**Step 1. Ask for the resume and nothing else:** "Send me the path to your resume (PDF or DOCX)."

**Step 2. Read it once**, then do all of the following in the same turn:
- Copy it to `resume/original.<ext>`.
- Write `resume/master.json` word for word (schema in `references/resume-tailoring.md`) and run `render_resume.py` to make `master.pdf`. If it comes out longer than one page, trim spacing in the CSS, never content.
- Prefill `profile.json` with everything the resume tells you.

**Step 3. Ask for everything else in one message.** Show what you inferred and give a fill-in line:

> Got it: <Name>, <title> at <company>, ~<N> yrs, <city>. Check `master.pdf` (an editable copy of your resume). Then reply in one line and skip anything you don't care about:
> `Roles: … | Locations: … (remote/hybrid/onsite) | CTC current/expected/min (LPA): …/…/… | Notice: … days | Avoid: companies/types | Deal-breakers: … | Visa: India only / needs sponsorship for … | Links: LinkedIn, … | Cap/day: 25 | Min score: 70`

Parse the reply into `profile.json`. Fields left blank stay `null` and get asked later only if a form needs them. If the target roles span different families (for example backend and AI/ML), make one tailored version per family now with `tailor.py`. Then go straight on to Phase 1 without asking for confirmation.

On later runs, load the profile without comment. Ask "anything changed?" only when `updated_at` is more than 14 days old.

## Phase 1: Browser
Load the `anthropic-skills:chrome-browser` skill before the first browser action, and work in new tabs. Check which sites are logged in by opening each one's jobs URL and reading its title or header as text. List the sites that aren't logged in and ask the user to log in themselves. You never handle passwords. Carry on with the sites that are logged in.

## Phase 2: Search
Read `references/sites.md` for search URLs and apply quirks. Then, for each role and location on each logged-in site:
1. Open a search URL filtered by date (last 7–14 days) and experience level, and read the **results list** as text.
2. Drop jobs by title, seniority, location or company before opening them. This is the biggest token saver.
3. Run `tracker.py bulk` on the survivors and skip any it reports as already logged. Also drop cross-site duplicates (same company, title and city), keeping the copy with the easiest apply path.
4. Open the job description only for survivors and score it from 0 to 100: title and seniority 30, skills 30, location 15, experience range 15, company 10. A deal-breaker scores 0.
5. Stop when you have about 2× the daily cap above the score threshold.

## Phase 3: Approve (the one checkpoint)
Show one compact table, best match first. Keep the note to 8 words or fewer and flag any gap:
```
# Sc Company   Role                Loc     Site      Apply   Note
1 92 Razorpay  SDE-2 Backend       BLR     Instahyre 1-click Java/Redis match
2 81 Atlassian SWE II              Remote  Lever     form    asks 3+ yrs (you 1.3)
```
Ask: "Which ones? (all / 1-10 / all except 4,7)". The user's answer authorizes those submissions.

## Phase 4: Apply
For each approved job:
1. **Resume:** a score of 90 or more gets a per-job copy made with `tailor.py`, built from a spec of about 10 lines (see `references/resume-tailoring.md`). Everything else uses its family version, or `master.pdf`. The first tailored copy in a session gets a 3-line before/after so the user can OK the style.
2. **Fill** the form from the profile, then the answers bank, then the resume. Match the form's format (LPA vs. rupees, days vs. months).
3. **Unknown question:** mark the job `needs_input` and move on. After about 5 jobs, ask all pending questions in one message, save the answers to `answers.json` and finish those jobs.
4. **Check and submit:** look for empty required fields and confirm the right file is uploaded, then submit. Confirm the success message, then run `tracker.py status --status applied --note "resume: <file>"`.
5. **Blockers** (CAPTCHA, OTP, an assessment, or a page that fails twice): mark the job `failed` or `needs_input` with a reason and move on. Never try to get around a blocker. Batch the ones that need the user into your next check-in.

Keep a human pace and respect the daily cap. Keep LinkedIn to about 15 a day, because its anti-automation checks can restrict the account.

## Phase 5: Report
Run `tracker.py report --since <today>`. Show one totals line (`Applied N · Needs input N · Failed N · Skipped N`), then the applied jobs (company, role, link) and what each pending item needs.

## Other requests
- **"Status" or "what did I apply to":** run `tracker.py report` only. Don't open the browser.
- **Profile changes:** edit `profile.json` and bump `updated_at`.
- **"Continue":** finish the `needs_input` and approved jobs from the log before searching again.
- **"Tailor my resume for <JD>":** tailor only, then return the PDF path.
