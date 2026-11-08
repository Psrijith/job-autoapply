"""Application log for job-autoapply. Stores one JSON object per line in
~/.claude/job-autoapply/applications.jsonl. Later lines for the same URL
override earlier ones (append-only, so the history is preserved)."""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

DATA = Path.home() / ".claude" / "job-autoapply"
LOG = DATA / "applications.jsonl"


def norm(url: str) -> str:
    p = urlsplit(url.strip())
    # drop tracking query/fragment; keep path, which identifies the job on all major sites
    keep_query = p.query if any(k in p.netloc for k in ("indeed.", "naukri.")) else ""
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), keep_query, ""))


def load():
    jobs = {}
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                jobs.setdefault(rec["url"], {}).update(rec)
    return jobs


def append(rec):
    DATA.mkdir(parents=True, exist_ok=True)
    rec["ts"] = datetime.now().isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("seen")
    for a in ("url", "company", "title", "site"):
        s.add_argument(f"--{a}", required=True)
    s.add_argument("--location", default="")
    s.add_argument("--score", type=int, default=0)
    st = sub.add_parser("status")
    st.add_argument("--url", required=True)
    st.add_argument("--status", required=True,
                    choices=["approved", "applied", "skipped", "failed", "needs_input",
                             "viewed", "interviewing", "rejected", "offer"])
    st.add_argument("--note", default="")
    sub.add_parser("bulk", help='stdin: one JSON per line {"url","company","title","site","location"?,"score"?}; prints NEW/DUP per line')
    c = sub.add_parser("check")
    c.add_argument("--url", required=True)
    r = sub.add_parser("report")
    r.add_argument("--since", default="")
    r.add_argument("--status", default="")
    args = ap.parse_args()

    jobs = load()
    if args.cmd == "seen":
        u = norm(args.url)
        if u in jobs:
            print(f"already logged: {jobs[u].get('status')}")
            return
        append({"url": u, "company": args.company, "title": args.title, "site": args.site,
                "location": args.location, "score": args.score, "status": "seen",
                "first_seen": datetime.now().date().isoformat()})
        print("logged")
    elif args.cmd == "bulk":
        for line in sys.stdin:
            if not line.strip():
                continue
            j = json.loads(line)
            u = norm(j["url"])
            if u in jobs:
                print(f"DUP [{jobs[u].get('status')}] {j.get('company')} - {j.get('title')}")
                continue
            rec = {"url": u, "company": j.get("company", ""), "title": j.get("title", ""),
                   "site": j.get("site", ""), "location": j.get("location", ""),
                   "score": j.get("score", 0), "status": "seen",
                   "first_seen": datetime.now().date().isoformat()}
            append(rec)
            jobs[u] = rec
            print(f"NEW {j.get('company')} - {j.get('title')}")
    elif args.cmd == "status":
        u = norm(args.url)
        rec = {"url": u, "status": args.status, "note": args.note}
        if args.status == "applied":
            rec["applied_on"] = datetime.now().date().isoformat()
        append(rec)
        print(f"{u} -> {args.status}")
    elif args.cmd == "check":
        u = norm(args.url)
        if u in jobs:
            print(f"exists: {jobs[u].get('status')} ({jobs[u].get('company')} - {jobs[u].get('title')})")
            sys.exit(0)
        print("new")
        sys.exit(1)
    elif args.cmd == "report":
        rows = [j for j in jobs.values()
                if (not args.since or j.get("ts", "") >= args.since)
                and (not args.status or j.get("status") == args.status)]
        counts = Counter(j.get("status") for j in rows)
        print("Totals:", ", ".join(f"{k}={v}" for k, v in counts.most_common()) or "none")
        for j in sorted(rows, key=lambda j: j.get("ts", ""), reverse=True):
            if j.get("status") in ("seen", "skipped"):
                continue
            print(f"- [{j.get('status')}] {j.get('company')} | {j.get('title')} | {j.get('site')} | "
                  f"{j.get('applied_on', '')} | {j['url']}" + (f" | {j['note']}" if j.get("note") else ""))


if __name__ == "__main__":
    main()
