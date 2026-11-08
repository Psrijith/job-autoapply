# profile.json schema

Write this file at `~/.claude/job-autoapply/profile.json`. Leave a field `null` if unknown rather than guessing — a null means "ask the user when a form needs it".

```json
{
  "updated_at": "2026-11-08",
  "personal": {
    "full_name": "",
    "email": "",
    "phone": "+91-",
    "current_city": "",
    "linkedin_url": "",
    "github_url": null,
    "portfolio_url": null,
    "gender": null,
    "date_of_birth": null
  },
  "career": {
    "current_title": "",
    "current_company": "",
    "total_experience_years": 0,
    "relevant_experience_years": 0,
    "skills": [{"name": "Java", "years": 5}],
    "highest_education": {"degree": "", "field": "", "institution": "", "year": 0, "score": null},
    "summary": "2-3 line pitch used for short 'about you' fields"
  },
  "compensation": {
    "currency": "INR",
    "current_ctc": 0,
    "expected_ctc": 0,
    "minimum_ctc": 0,
    "unit": "LPA",
    "negotiable": true
  },
  "availability": {
    "notice_period_days": 0,
    "serving_notice": false,
    "last_working_day": null,
    "can_join_by": null
  },
  "targets": {
    "titles": ["Senior Software Engineer", "Backend Engineer"],
    "seniority": ["mid", "senior"],
    "locations": ["Bangalore", "Hyderabad"],
    "work_mode": ["remote", "hybrid"],
    "willing_to_relocate": false,
    "experience_range_ok": [3, 8],
    "countries": ["IN"]
  },
  "work_authorization": {
    "IN": "citizen",
    "US": "needs_sponsorship"
  },
  "preferences": {
    "include_companies": [],
    "exclude_companies": [],
    "company_stage": ["series_b_plus", "public"],
    "industries_avoid": [],
    "deal_breakers": ["contract roles", "night shift"]
  },
  "run_settings": {
    "daily_cap": 25,
    "score_threshold": 70,
    "sites_logged_in": [],
    "sites_disabled": []
  },
  "resume_files": {"default": "resume/resume.pdf"},
  "cover_letter_style": null
}
```

## answers.json

Key = normalized question (lowercase, strip punctuation, collapse synonyms like k8s→kubernetes). Store the original wording too so you can match similar phrasings.

```json
{
  "years of experience with kubernetes": {"answer": "3", "asked_as": ["How many years have you worked with Kubernetes?"], "added": "2026-11-08"},
  "are you comfortable working from office 5 days a week": {"answer": "No", "asked_as": ["..."], "added": "..."}
}
```

Reuse an answer only when the question really means the same thing. "Years of Python" ≠ "years of Python in production ML" — when in doubt, ask.
