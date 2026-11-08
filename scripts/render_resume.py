"""Render a resume JSON (see references/resume-tailoring.md) to a one-page PDF
using headless Chrome/Edge.

usage: python render_resume.py RESUME.json OUT.pdf [--html-only]
Prints the page count; anything other than 1 means trim content and re-render.
"""
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chromium-browser",
]

CSS = """
@page { size: Letter; margin: 0.4in 0.45in; }
* { box-sizing: border-box; }
body { font-family: Charter, 'Bitstream Charter', Cambria, Georgia, serif; font-size: 9.7pt;
       line-height: 1.18; color: #000; margin: 0; }
a { color: #1a0dab; text-decoration: none; }
h1 { text-align: center; font-size: 20pt; margin: 0; }
.contact { text-align: center; margin: 2px 0 8px; }
.contact span + span::before { content: "  |  "; color: #000; white-space: pre; }
h2 { font-size: 12.5pt; margin: 7px 0 3px; border-bottom: 0.8px solid #000; padding-bottom: 1px; }
.row { display: flex; justify-content: space-between; }
.b { font-weight: bold; } .i { font-style: italic; }
.entry { margin-bottom: 3px; }
ul { margin: 1px 0 2px; padding-left: 16px; }
li { margin: 0 0 1px; }
.skills div { margin: 0; }
p { margin: 0 0 2px; }
"""


def md(s: str) -> str:
    """escape, then allow **bold** and [text](url)."""
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    return s


def bullets(items):
    return "<ul>" + "".join(f"<li>{md(b)}</li>" for b in items) + "</ul>" if items else ""


def build(r: dict) -> str:
    out = [f"<h1>{md(r['name'])}</h1>"]
    contact = "".join(
        f'<span><a href="{html.escape(c["url"])}">{md(c["text"])}</a></span>' if c.get("url")
        else f"<span>{md(c['text'])}</span>" for c in r.get("contact", []))
    out.append(f'<div class="contact">{contact}</div>')
    if r.get("summary"):
        out.append(f"<p><b>Professional Summary:</b> {md(r['summary'])}</p>")

    for sec in r.get("section_order", ["experience", "skills", "projects", "achievements", "education"]):
        if sec == "experience" and r.get("experience"):
            out.append("<h2>Experience</h2>")
            for e in r["experience"]:
                company = md(e.get("company", ""))
                if e.get("company_url"):
                    company = f'<a href="{html.escape(e["company_url"])}">{company}</a>'
                out.append(f'<div class="entry"><div class="row"><span class="b">{md(e["title"])}</span>'
                           f'<span>{md(e.get("dates", ""))}</span></div>')
                if company or e.get("location"):
                    out.append(f'<div class="row"><span class="i">{company}</span>'
                               f'<span>{md(e.get("location", ""))}</span></div>')
                out.append(bullets(e.get("bullets", [])) + "</div>")
        elif sec == "skills" and r.get("skills"):
            out.append('<h2>Technical Skills</h2><div class="skills">')
            for g in r["skills"]:
                out.append(f"<div><b>{md(g['group'])}:</b> {md(', '.join(g['items']))}</div>")
            out.append("</div>")
        elif sec == "projects" and r.get("projects"):
            out.append("<h2>Projects</h2>")
            for p in r["projects"]:
                out.append(f'<div class="entry"><div class="row"><span class="b">{md(p["name"])}</span>'
                           f'<span class="i">{md(p.get("stack", ""))}</span></div>{bullets(p.get("bullets", []))}</div>')
            if r.get("projects_footer"):
                out.append(f"<p>{md(r['projects_footer'])}</p>")
        elif sec == "achievements" and r.get("achievements"):
            out.append("<h2>Achievements</h2>" + bullets(r["achievements"]))
        elif sec == "education" and r.get("education"):
            out.append("<h2>Education</h2>")
            for ed in r["education"]:
                out.append(f'<div class="entry"><div class="row"><span class="b">{md(ed["degree"])}</span>'
                           f'<span>{md(ed.get("dates", ""))}</span></div>'
                           f'<div class="row"><span class="i">{md(ed.get("institution", ""))}</span>'
                           f'<span>{md(ed.get("score", ""))}</span></div></div>')
    title = html.escape(r["name"] + " - Resume")
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title>"
            f"<style>{CSS}</style></head><body>{''.join(out)}</body></html>")


def find_browser():
    for b in BROWSERS:
        if Path(b).exists() or shutil.which(b):
            return b
    sys.exit("No Chrome/Edge found for PDF rendering.")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
    page = build(json.loads(src.read_text(encoding="utf-8")))
    dst.parent.mkdir(parents=True, exist_ok=True)
    if "--html-only" in sys.argv:
        dst.with_suffix(".html").write_text(page, encoding="utf-8")
        print(dst.with_suffix(".html"))
        return
    with tempfile.TemporaryDirectory() as td:
        h = Path(td) / "resume.html"
        h.write_text(page, encoding="utf-8")
        subprocess.run([find_browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={Path(td) / 'profile'}",
                        f"--print-to-pdf={dst}", h.as_uri()],
                       check=True, capture_output=True, timeout=120)
    pages = len(re.findall(rb"/Type\s*/Page[^s]", dst.read_bytes()))
    print(f"{dst}  pages={pages}")


if __name__ == "__main__":
    main()
