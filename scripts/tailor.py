"""Build a tailored resume from master.json + a small edit spec, check it for
invented facts, and render it to PDF. The spec is tiny, so tailoring costs a
few hundred tokens instead of rewriting the whole resume.

usage: python tailor.py MASTER.json SPEC.json OUT.pdf

SPEC (all keys optional):
{
  "summary": "new summary text",
  "section_order": ["experience","projects","skills","achievements","education"],
  "bullets": {"0": [2, 0, "r:Reworded bullet using JD terms", 1]},   # per experience index: keep/reorder by index, "r:" = rewritten text
  "skills": {"Languages": ["Java","Python"], "Backend & Web": ["Spring Boot"]},  # group order + items (subset of master)
  "projects": [1, 0],                     # order/subset of projects by index
  "achievements": [0, 2],                 # order/subset by index
  "add_reserve_projects": [0]             # pull from master.reserve.projects
}
"""
import json
import re
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).parent


def text_of(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    master = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    spec = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    out_pdf = Path(sys.argv[3])
    r = deepcopy(master)
    r.pop("reserve", None)

    if "summary" in spec:
        r["summary"] = spec["summary"]
    if "section_order" in spec:
        r["section_order"] = spec["section_order"]
    for i, order in spec.get("bullets", {}).items():
        src = master["experience"][int(i)]["bullets"]
        r["experience"][int(i)]["bullets"] = [
            o[2:] if isinstance(o, str) and o.startswith("r:") else src[o] for o in order]
    if "skills" in spec:
        r["skills"] = [{"group": g, "items": items} for g, items in spec["skills"].items()]
    if "projects" in spec:
        r["projects"] = [master["projects"][i] for i in spec["projects"]]
    for i in spec.get("add_reserve_projects", []):
        r["projects"].append(master.get("reserve", {}).get("projects", [])[i])
    if "achievements" in spec:
        r["achievements"] = [master["achievements"][i] for i in spec["achievements"]]

    # --- honesty checks: tailored text may not introduce facts absent from master ---
    base = text_of(master)
    problems = []
    for num in set(re.findall(r"\d[\d,.]*\+?%?", text_of(r))):
        n = num.rstrip(".,")
        if not re.search(r"(?<![\d.,])" + re.escape(n) + r"(?![\d])", base):
            problems.append(f"number not in master: {num}")
    known = {s.lower() for g in master.get("skills", []) for s in g["items"]}
    for g in r.get("skills", []):
        for s in g["items"]:
            if s.lower() not in known:
                problems.append(f"skill not in master: {s}")
    if problems:
        print("REJECTED - fix the spec:\n  " + "\n  ".join(sorted(problems)))
        sys.exit(2)

    out_json = out_pdf.with_suffix(".json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    res = subprocess.run([sys.executable, str(HERE / "render_resume.py"), str(out_json), str(out_pdf)],
                         capture_output=True, text=True)
    print(res.stdout.strip() or res.stderr.strip())
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
