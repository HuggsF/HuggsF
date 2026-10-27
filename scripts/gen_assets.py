"""Generates the SVG cards used by the profile README from public GitHub data.

Original design: dark card, emerald accent, window dots, system fonts only.
Needs the GitHub CLI (`gh`) authenticated, or GH_TOKEN set. Run from the repo root:

    python scripts/gen_assets.py HuggsF
"""
import base64
import json
import os
import subprocess
import sys
import urllib.request
from html import escape
from pathlib import Path

USER = sys.argv[1] if len(sys.argv) > 1 else "HuggsF"
DISPLAY_NAME = "Hugo Melo"  # public name; the GitHub profile name may differ
OUT = Path(__file__).resolve().parent.parent / "assets"
FEATURED = ["rag-dojo", "second-brain-open", "edtech-cloud-deploy",
            "leaderboard-cache-shield", "resilient-pdf-worker"]
STACK = ["TypeScript", "Node.js", "Python", "Java", "RabbitMQ", "Redis", "MySQL", "GraphQL",
         "Neo4j", "ChromaDB", "Docker", "Terraform", "AWS ECS", "Prometheus"]

BG, BORDER, TEXT, MUTED = "#0b0f14", "#1f2a33", "#e6edf3", "#8b98a5"
ACC, ACC2 = "#34d399", "#22d3ee"
LANG_COLORS = {"TypeScript": "#3178c6", "Python": "#3776ab", "Java": "#e76f00", "JavaScript": "#f1e05a",
               "HCL": "#844fba", "CSS": "#8b5cf6", "Dockerfile": "#384d54", "Shell": "#89e051"}
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "Segoe UI, Inter, Helvetica, Arial, sans-serif"


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True,
                          env=os.environ.copy()).stdout


def api(path):
    return json.loads(gh("api", path))


def card(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}">'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{BG}" stroke="{BORDER}"/>'
            f'{body}</svg>')


def dots(y=18):
    return "".join(f'<circle cx="{22+i*16}" cy="{y}" r="4.5" fill="{c}"/>'
                   for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))


def text(x, y, s, size=13, fill=TEXT, weight=400, font=SANS, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{escape(str(s))}</text>')


def chip(x, y, label, color=ACC):
    w = 14 + int(len(label) * 7.2)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="12" fill="{color}" fill-opacity="0.12" '
            f'stroke="{color}" stroke-opacity="0.5"/>' + text(x + w / 2, y + 16, label, 12, TEXT, 500, MONO, "middle")), w


def dot_art(x0, y0, cols, rows):
    """Decorative dot-matrix, denser towards the centre. Deterministic, no data in it."""
    out = []
    for r in range(rows):
        for c in range(cols):
            d = ((c - cols / 2) / (cols / 2)) ** 2 + ((r - rows / 2) / (rows / 2)) ** 2
            if d < 1:
                op = round(0.9 * (1 - d) * (0.35 + 0.65 * ((c * 7 + r * 13) % 5) / 4), 2)
                out.append(f'<circle cx="{x0+c*9}" cy="{y0+r*9}" r="2" fill="{ACC}" fill-opacity="{op}"/>')
    return "".join(out)


def header(u, repos, stars, contribs):
    avatar = base64.b64encode(urllib.request.urlopen(u["avatar_url"].split("?")[0] + "?s=240").read()).decode()
    stats = [("Repositories", repos), ("Stars", stars), ("Contributions", contribs), ("Followers", u["followers"])]
    b = [dots(), text(88, 22, f"{u['login'].lower()}@github ~ $ ./profile", 12, MUTED, 400, MONO)]
    b.append(f'<defs><clipPath id="av"><circle cx="82" cy="112" r="46"/></clipPath></defs>'
             f'<circle cx="82" cy="112" r="50" fill="none" stroke="{ACC}" stroke-width="2"/>'
             f'<image href="data:image/png;base64,{avatar}" x="36" y="66" width="92" height="92" clip-path="url(#av)"/>')
    b.append(text(158, 96, DISPLAY_NAME, 28, TEXT, 700))
    b.append(text(158, 120, "Back-end engineer · distributed systems & AI platforms", 14, MUTED))
    x = 158
    for lang in ["TypeScript", "Python", "Java"]:
        c, w = chip(x, 134, lang)
        b.append(c)
        x += w + 8
    for i, (k, v) in enumerate(stats):
        sx = 40 + i * 150
        b.append(text(sx, 206, v, 22, ACC, 700, MONO))
        b.append(text(sx, 224, k, 12, MUTED))
    b.append(dot_art(660, 52, 22, 18))
    return card(860, 244, "".join(b), f"{DISPLAY_NAME} GitHub profile")


def stack(langs):
    total = sum(langs.values()) or 1
    b = [dots(), text(88, 22, "toolbox --list", 12, MUTED, 400, MONO), text(30, 62, "Tech Stack", 16, TEXT, 700)]
    x, y = 30, 78
    for s in STACK:
        c, w = chip(x, y, s)
        if x + w > 830:
            x, y = 30, y + 34
            c, w = chip(x, y, s)
        b.append(c)
        x += w + 8
    y += 52
    b.append(text(30, y, "Languages (public repositories, by bytes)", 12, MUTED))
    y += 14
    x = 30
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    for name, n in top:
        w = 800 * n / total
        b.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w-2,2):.1f}" height="10" rx="3" fill="{LANG_COLORS.get(name, MUTED)}"/>')
        x += w
    y += 32
    x = 30
    for name, n in top:
        b.append(f'<circle cx="{x+5}" cy="{y-4}" r="5" fill="{LANG_COLORS.get(name, MUTED)}"/>')
        b.append(text(x + 16, y, f"{name} {100*n/total:.0f}%", 12, TEXT))
        x += 28 + int(len(name) * 7) + 44
    return card(860, y + 24, "".join(b), "Tech stack"), y + 24


def projects(rows):
    b = [dots(), text(88, 22, "ls featured/", 12, MUTED, 400, MONO), text(30, 62, "Featured Projects", 16, TEXT, 700)]
    y = 92
    for r in rows:
        b.append(f'<rect x="30" y="{y-14}" width="14" height="14" rx="3" fill="none" stroke="{ACC}" stroke-width="1.5"/>')
        b.append(text(54, y - 2, r["name"], 14, TEXT, 600, MONO))
        desc = (r["description"] or "")[:78] + ("…" if len(r["description"] or "") > 78 else "")
        b.append(text(54, y + 15, desc, 12, MUTED))
        lang = r["language"] or "-"
        b.append(f'<circle cx="700" cy="{y-6}" r="5" fill="{LANG_COLORS.get(lang, MUTED)}"/>')
        b.append(text(712, y - 2, lang, 12, TEXT))
        b.append(text(830, y - 2, f"★ {r['stargazers_count']}", 12, ACC, 600, MONO, "end"))
        y += 46
    return card(860, y + 4, "".join(b), "Featured projects")


def activity(cal):
    weeks = cal["weeks"]
    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    mx = max(counts) or 1
    shades = ["#161b22", "#0e4a35", "#117a55", "#22b07a", ACC]

    def level(n):
        if n == 0:
            return 0
        ratio = n / mx
        return 1 if ratio <= 0.25 else 2 if ratio <= 0.5 else 3 if ratio <= 0.75 else 4

    b = [dots(), text(88, 22, "git log --since=1y", 12, MUTED, 400, MONO),
         text(30, 62, "Contribution Activity", 16, TEXT, 700),
         text(830, 62, f"{cal['totalContributions']} contributions in the last year", 12, MUTED, 400, SANS, "end")]
    for i, w in enumerate(weeks):
        for d in w["contributionDays"]:
            n = d["contributionCount"]
            b.append(f'<rect x="{30+i*14.9:.1f}" y="{84+d["weekday"]*14}" width="11" height="11" rx="2" fill="{shades[level(n)]}"/>')
    return card(860, 204, "".join(b), "Contribution activity")


def main():
    u = api(f"users/{USER}")
    repos = [r for r in api(f"users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in repos)
    langs = {}
    for r in repos:
        for k, v in api(f"repos/{USER}/{r['name']}/languages").items():
            langs[k] = langs.get(k, 0) + v
    cal = json.loads(gh("api", "graphql", "-f", "query=query{user(login:\"%s\"){contributionsCollection{contributionCalendar"
                        "{totalContributions weeks{contributionDays{contributionCount weekday}}}}}}" % USER)
                     )["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    featured = [r for n in FEATURED for r in repos if r["name"] == n]
    OUT.mkdir(exist_ok=True)
    stack_svg, _ = stack(langs)
    for name, svg in [("header", header(u, len(repos), stars, cal["totalContributions"])), ("stack", stack_svg),
                      ("projects", projects(featured)), ("activity", activity(cal))]:
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print("wrote", OUT / f"{name}.svg", len(svg), "bytes")


if __name__ == "__main__":
    main()
