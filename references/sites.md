# Job sites: search and apply notes

Search every site that is relevant to the user's countries/roles. Site UIs change often — treat these notes as a starting point, read the actual page, and adapt. If a URL pattern stops working, use the site's search box.

## Contents
- India-focused boards: Naukri, Instahyre, Foundit, Cutshort, Hirist, IIMJobs, Hirect, Apna (non-tech)
- Global boards: LinkedIn, Indeed, Wellfound, Glassdoor, Y Combinator Work at a Startup, Otta/Welcome to the Jungle
- ATS career pages: Greenhouse, Lever, Ashby, Workday, SmartRecruiters, others
- Discovery tricks

---

## India-focused

### Naukri (naukri.com)
- Search: `https://www.naukri.com/<role-slug>-jobs-in-<city>?experience=<yrs>&jobAge=7`
- Apply: "Apply" on the job page often submits instantly using the Naukri profile. Some jobs open a chatbot-style questionnaire (drawer on the right) — answer from profile/answers bank.
- "Apply on company site" → follow to the external ATS and handle it there.
- Keep the user's Naukri profile fresh — it's what recruiters see. Don't edit it unless asked.
- Daily apply limits exist; stop on any "limit reached" message.

### Instahyre (instahyre.com)
- Primarily curated "opportunities" feed: `https://www.instahyre.com/candidate/opportunities/` — also has search with filters for role/location/experience.
- Apply = "Interested" button; it's 1-click using the Instahyre profile. Very low friction — good yield.

### Foundit (foundit.in, ex-Monster India)
- Search: site search with role + location + experience filters; sort by date.
- Apply is usually 1-click with profile; some redirect externally.

### Cutshort (cutshort.io)
- Search jobs filtered by skill/location. Apply asks for a short note sometimes — use profile summary or ask.

### Hirist (hirist.tech) / IIMJobs (iimjobs.com)
- Same company (InfoEdge-style). Hirist = tech roles, IIMJobs = management/business roles. 1-click apply with profile; some recruiters attach screening questions.

### Hirect / Apna
- Chat-based hiring apps. Only use if the user is targeting roles posted there; applying usually starts a recruiter chat — tell the user rather than auto-chatting.

---

## Global

### LinkedIn (linkedin.com/jobs)
- Search: `https://www.linkedin.com/jobs/search/?keywords=<title>&location=<loc>&f_TPR=r604800&f_AL=true` (`f_AL=true` = Easy Apply only, `f_TPR=r604800` = past week, `f_WT=2` remote).
- Easy Apply: multi-step modal. Check each step; uncheck "Follow company" unless the user wants it. Review page before Submit.
- LinkedIn restricts accounts that behave like bots. Keep LinkedIn volume modest (suggest ≤10–15/day) and spaced out; tell the user this once.
- Non–Easy Apply jobs: follow to the company ATS.

### Indeed (indeed.com / in.indeed.com)
- Search with `q`, `l`, `fromage=7`. "Apply now" (Indeed Apply) vs "Apply on company site".
- Indeed Apply flows often include employer screening questions — route unknowns to the answers bank flow.

### Wellfound (wellfound.com, ex-AngelList)
- Startup roles. Apply needs a short note to the founder — draft one per job from JD + profile (show the style once, then reuse).

### Glassdoor, YC Work at a Startup (workatastartup.com), Welcome to the Jungle / Otta
- Use for discovery; many apply through external ATS.

---

## ATS career pages (company sites)

These carry the least account risk and are often the "real" posting behind board listings. Prefer them when the same job appears on a board.

- **Greenhouse** (`boards.greenhouse.io/<co>` or `job-boards.greenhouse.io`): single page form. Resume upload often auto-parses — verify parsed fields afterwards. Custom questions at the bottom; EEO section is optional (decline-to-answer unless profile says otherwise).
- **Lever** (`jobs.lever.co/<co>`): single page. "Additional information" free text is optional — leave blank or add 1–2 lines.
- **Ashby** (`jobs.ashbyhq.com/<co>`): single page, similar to Greenhouse.
- **Workday** (`<co>.wd*.myworkdayjobs.com`): requires creating an account per company. That needs an email + password the user must choose — ask the user to create/sign in themselves, then you fill the multi-page flow. Slow; batch these last.
- **SmartRecruiters, iCIMS, Taleo, SuccessFactors, Zoho Recruit, Keka, Darwinbox, Freshteam**: varied. Many need accounts — same rule as Workday.

## Discovery tricks

- Google: `site:boards.greenhouse.io OR site:jobs.lever.co OR site:jobs.ashbyhq.com "<title>" "<city or Remote>"` surfaces fresh ATS postings that never appear on boards.
- Company include list from the profile: visit each company's careers page directly.
- After an apply on a board, if it redirects externally, record the final ATS URL in the log too (for dedup).
