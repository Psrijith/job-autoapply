"""Search public ATS job feeds (Greenhouse, Lever, Ashby) without a browser or login.
usage: python ats_search.py companies.txt  [--title REGEX] [--loc REGEX] [--exclude REGEX]
companies.txt: one 'ats:slug' per line (greenhouse:phonepe, lever:cred, ashby:notion).
Prints one compact TSV line per match: ats  company  title  location  url"""
import argparse, json, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "job-search-script"}), timeout=20) as r:
            return json.load(r)
    except Exception:
        return None

def fetch(entry):
    ats, slug = entry.split(":", 1)
    out = []
    if ats == "greenhouse":
        d = get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
        for j in (d or {}).get("jobs", []):
            out.append((slug, j["title"], (j.get("location") or {}).get("name", ""), j["absolute_url"]))
    elif ats == "lever":
        for j in get(f"https://api.lever.co/v0/postings/{slug}?mode=json") or []:
            cat = j.get("categories", {})
            out.append((slug, j["text"], cat.get("location", "") or ", ".join(cat.get("allLocations", []) or []), j["hostedUrl"]))
    elif ats == "ashby":
        d = get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
        for j in (d or {}).get("jobs", []):
            loc = j.get("location", "") + (" Remote" if j.get("isRemote") else "")
            out.append((slug, j["title"], loc, j["jobUrl"]))
    return ats, slug, d_ok(out), out

def d_ok(out): return bool(out)

ap = argparse.ArgumentParser()
ap.add_argument("companies")
ap.add_argument("--title", default=r"software|backend|sde|developer|full.?stack|engineer")
ap.add_argument("--loc", default=r"india|bangalore|bengaluru|hyderabad|pune|mumbai|delhi|gurgaon|gurugram|noida|chennai|remote")
ap.add_argument("--exclude", default=r"senior|sr\.?|staff|principal|lead|manager|director|head|architect|intern|qa|test|sales|support|data analyst|designer|iii|\b3\b|\biv\b")
a = ap.parse_args()
entries = [l.strip() for l in open(a.companies) if l.strip() and not l.startswith("#")]
t, l, x = re.compile(a.title, re.I), re.compile(a.loc, re.I), re.compile(a.exclude, re.I)
dead = []
with ThreadPoolExecutor(12) as ex:
    for ats, slug, ok, jobs in ex.map(fetch, entries):
        if not ok: dead.append(f"{ats}:{slug}"); continue
        for c, title, loc, url in jobs:
            if t.search(title) and l.search(loc) and not x.search(title):
                print(f"{ats}\t{c}\t{title}\t{loc}\t{url}")
if dead: print("# no feed:", " ".join(dead), file=sys.stderr)
