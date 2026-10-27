"""Animated SVG cards for the profile README. Pure SVG + CSS keyframes, no JavaScript.

Every animation ends in the final state. With prefers-reduced-motion the animations are
switched off and the cards show that final state.

    python scripts/gen_animated.py HuggsF
"""
import base64
import json
import math
import sys
import urllib.request
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_assets as g  # noqa: E402  (reuses the data helpers and the palette)

OUT = g.OUT
BG, BORDER, TEXT, MUTED, ACC, ACC2 = g.BG, g.BORDER, g.TEXT, g.MUTED, g.ACC, g.ACC2
MONO, SANS = g.MONO, g.SANS

CSS = f"""
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
@keyframes fade {{ from {{ opacity: 0; transform: translateY(8px); }} }}
@keyframes type {{ from {{ width: 0; }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes pulse {{ 0% {{ transform: scale(1); opacity: .7; }} 100% {{ transform: scale(1.35); opacity: 0; }} }}
@keyframes twinkle {{ 0%,100% {{ opacity: var(--o); }} 50% {{ opacity: .08; }} }}
@keyframes grow {{ from {{ transform: scaleX(0); }} }}
@keyframes sweep {{ from {{ transform: translateX(0); }} to {{ transform: translateX(1260px); }} }}
@keyframes ticker {{ to {{ transform: translateX(var(--w)); }} }}
@keyframes draw {{ from {{ transform: scaleY(0); }} }}
@keyframes step {{ 0% {{ opacity: 0; }} 2% {{ opacity: 1; }} 96% {{ opacity: 1; }} 98%,100% {{ opacity: 0; }} }}
@keyframes show {{ from {{ opacity: 0; }} }}
@keyframes role {{ 0% {{ opacity: 0; }} 4%,30% {{ opacity: 1; }} 34%,100% {{ opacity: 0; }} }}
@keyframes cell {{ from {{ opacity: 0; transform: scale(.2); }} }}
.fade {{ animation: fade .6s ease-out both; }}
.cur {{ animation: blink 1s step-end infinite; }}
.gr {{ transform-box: fill-box; transform-origin: 0 50%; animation: grow .9s cubic-bezier(.2,.7,.2,1) both; }}
.dr {{ transform-box: fill-box; transform-origin: 50% 0; animation: draw 1.2s ease-out both; }}
.cl {{ transform-box: fill-box; transform-origin: 50% 50%; animation: cell .45s ease-out both; }}
"""


def d(delay):
    return f'style="animation-delay:{delay:.2f}s"'


def svg(w, h, body, label, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}"><style>{CSS}</style><defs>{extra_defs}</defs>'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{BG}" stroke="{BORDER}"/>{body}</svg>')


def T(x, y, s, size=13, fill=TEXT, weight=400, font=SANS, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{escape(str(s))}</text>')


def typed(cid, x, y, s, size, fill, start, per_char=0.045, weight=400):
    """Typewriter line: a clip rect whose width animates in `len(s)` discrete steps."""
    cw = size * 0.6
    w = len(s) * cw + 4
    dur = max(len(s) * per_char, 0.3)
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y-size-2}" width="{w:.1f}" height="{size+10}" '
            f'style="animation: type {dur:.2f}s steps({len(s)}) {start:.2f}s both"/></clipPath>'
            f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'clip-path="url(#{cid})" xml:space="preserve">{escape(s)}</text>'), start + dur


def window(title):
    return ("".join(f'<circle cx="{22+i*16}" cy="18" r="4.5" fill="{c}"/>' for i, c in
                    enumerate(["#ff5f57", "#febc2e", "#28c840"])) + T(88, 22, title, 12, MUTED, 400, MONO))


def chip(x, y, label, color=ACC):
    w = 14 + int(len(label) * 7.2)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="12" fill="{color}" fill-opacity="0.12" '
            f'stroke="{color}" stroke-opacity="0.5"/>' + T(x + w / 2, y + 16, label, 12, TEXT, 500, MONO, "middle")), w


def counter(x, y, value, start, label):
    """Count-up: stacked numbers shown one after another, then the real one stays."""
    steps = sorted({0, int(value * .2), int(value * .45), int(value * .7), int(value * .9)})
    out = []
    for i, v in enumerate(steps):
        out.append(T(x, y, v, 24, ACC, 700, MONO, extra=f'opacity="0" style="animation: step .14s linear {start+i*.14:.2f}s both"'))
    out.append(T(x, y, value, 24, ACC, 700, MONO,
                 extra=f'style="animation: show .2s ease-out {start+len(steps)*.14:.2f}s backwards"'))
    out.append(T(x, y + 20, label, 12, MUTED, 400, SANS, extra=f'class="fade" {d(start)}'))
    return "".join(out)


def hero(u, repos, stars, contribs):
    avatar = base64.b64encode(urllib.request.urlopen(u["avatar_url"].split("?")[0] + "?s=240").read()).decode()
    b = [window(f"{u['login'].lower()}@github ~ $ ./profile")]
    # decorative dot matrix with twinkle
    dots = []
    for r in range(15):
        for c in range(20):
            dd = ((c - 10) / 10) ** 2 + ((r - 7) / 7.5) ** 2
            if dd < 1:
                o = round(0.85 * (1 - dd) * (0.4 + 0.6 * ((c * 7 + r * 13) % 5) / 4), 2)
                dots.append(f'<circle cx="{660+c*9}" cy="{52+r*9}" r="2" fill="{ACC}" style="--o:{o};animation: twinkle '
                            f'{2.4+((c*3+r*5)%7)*.35:.2f}s ease-in-out {((c*5+r*11)%13)*.17:.2f}s infinite" opacity="{o}"/>')
    b.append("".join(dots))
    # avatar with spinning dashed ring and pulse
    b.append(f'<circle cx="82" cy="140" r="50" fill="none" stroke="{ACC}" stroke-width="2" style="transform-box:fill-box;'
             f'transform-origin:center;animation: pulse 2.6s ease-out infinite"/>')
    b.append(f'<circle cx="82" cy="140" r="53" fill="none" stroke="{ACC2}" stroke-width="1.5" stroke-dasharray="6 9" '
             f'style="transform-box:fill-box;transform-origin:center;animation: spin 14s linear infinite"/>')
    b.append(f'<clipPath id="av"><circle cx="82" cy="140" r="46"/></clipPath><circle cx="82" cy="140" r="48" fill="none" '
             f'stroke="{ACC}" stroke-width="2"/><image href="data:image/png;base64,{avatar}" x="36" y="94" width="92" '
             f'height="92" clip-path="url(#av)"/>')
    # typed lines
    l1, t1 = typed("t1", 170, 96, "$ whoami", 15, ACC, 0.2, weight=700)
    l2, t2 = typed("t2", 170, 128, g.DISPLAY_NAME.lower().replace(" ", "-") + " · senior back-end engineer", 15, TEXT, t1 + .15, weight=700)
    l3, t3 = typed("t3", 170, 156, "> resilient distributed systems + applied AI", 14, MUTED, t2 + .1)
    b += [l1, l2, l3]
    # rotating roles with blinking cursor
    roles = ["Backend", "Platform", "AI Engineering"]
    start = t3 + .3
    b.append(T(170, 188, "$ open_to", 14, ACC, 600, MONO, extra=f'class="fade" {d(start)}'))
    for i, r in enumerate(roles):
        base = 1 if i == 0 else 0
        b.append(f'<text x="268" y="188" font-family="{MONO}" font-size="14" fill="{TEXT}" font-weight="700" opacity="{base}" '
                 f'style="animation: role 9s linear {start+.3+i*3:.2f}s infinite backwards">{escape(r)}'
                 f'<tspan class="cur" fill="{ACC}"> ▌</tspan></text>')
    # chips
    x = 170
    for lang in ["TypeScript", "Python", "Java"]:
        c, w = chip(x, 204, lang)
        b.append(f'<g class="fade" {d(start+.2)}>{c}</g>')
        x += w + 8
    # counters
    for i, (k, v) in enumerate([("Repositories", repos), ("Stars", stars), ("Contributions", contribs), ("Followers", u["followers"])]):
        b.append(counter(40 + i * 150, 262, v, 0.4 + i * .15, k))
    # scanning light
    b.append(f'<g style="animation: sweep 7s linear 1s infinite"><rect x="-300" y="30" width="3" height="230" fill="url(#scan)" opacity=".35"/></g>')
    defs = (f'<linearGradient id="scan" x1="0" x2="1"><stop offset="0" stop-color="{ACC}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{ACC}"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></linearGradient>')
    return svg(860, 304, "".join(b), f"{g.DISPLAY_NAME} animated profile header", defs)


def stack(langs):
    total = sum(langs.values()) or 1
    b = [window("toolbox --list"), T(30, 62, "Tech Stack", 16, TEXT, 700)]
    # ticker: chips scroll left, duplicated for a seamless loop
    row, x = [], 0
    for s in g.STACK:
        c, w = chip(x, 78, s)
        row.append(c)
        x += w + 8
    b.append(f'<clipPath id="tk"><rect x="30" y="70" width="800" height="40"/></clipPath>'
             f'<g clip-path="url(#tk)"><g style="--w:-{x}px;animation: ticker {max(x/40,14):.0f}s linear infinite">'
             + "".join(row) + f'<g transform="translate({x},0)">' + "".join(row) + '</g></g></g>')
    y = 138
    b.append(T(30, y, "Languages (public repositories, by bytes)", 12, MUTED))
    y += 14
    xx, top = 30, sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    for i, (name, n) in enumerate(top):
        w = 800 * n / total
        b.append(f'<rect class="gr" x="{xx:.1f}" y="{y}" width="{max(w-2,2):.1f}" height="10" rx="3" '
                 f'fill="{g.LANG_COLORS.get(name, MUTED)}" {d(.2+i*.15)}/>')
        xx += w
    y += 32
    xx = 30
    for i, (name, n) in enumerate(top):
        b.append(f'<g class="fade" {d(.6+i*.12)}><circle cx="{xx+5}" cy="{y-4}" r="5" fill="{g.LANG_COLORS.get(name, MUTED)}"/>'
                 + T(xx + 16, y, f"{name} {100*n/total:.0f}%", 12, TEXT) + '</g>')
        xx += 28 + int(len(name) * 7) + 44
    return svg(860, y + 24, "".join(b), "Animated tech stack")


def projects(rows):
    b = [window("ls featured/"), T(30, 62, "Featured Projects", 16, TEXT, 700)]
    y = 92
    for i, r in enumerate(rows):
        dl = .1 + i * .15
        desc = (r["description"] or "")[:78] + ("…" if len(r["description"] or "") > 78 else "")
        lang = r["language"] or "-"
        b.append(f'<g class="fade" {d(dl)}><rect x="30" y="{y-14}" width="14" height="14" rx="3" fill="none" stroke="{ACC}" stroke-width="1.5"/>'
                 + T(54, y - 2, r["name"], 14, TEXT, 600, MONO) + T(54, y + 15, desc, 12, MUTED)
                 + f'<circle cx="700" cy="{y-6}" r="5" fill="{g.LANG_COLORS.get(lang, MUTED)}"/>'
                 + T(712, y - 2, lang, 12, TEXT) + T(830, y - 2, f"★ {r['stargazers_count']}", 12, ACC, 600, MONO, "end") + '</g>')
        b.append(f'<rect class="gr" x="30" y="{y+26}" width="800" height="1.5" fill="{ACC}" fill-opacity=".25" {d(dl+.2)}/>')
        y += 46
    return svg(860, y + 4, "".join(b), "Animated featured projects")


def results():
    rows = [("csv-stream-importer", "peak RAM, 500k CSV rows", "590+ MB", "79 MB", 590, 79),
            ("resilient-pdf-worker", "API calls with the dependency down", "400", "46", 400, 46),
            ("leaderboard-cache-shield", "DB queries, 10,000 concurrent requests", "10,000", "1", 10000, 1),
            ("leaderboard-cache-shield", "worst response time", "13.2 s", "65 ms", 13200, 65),
            ("dashboard-bff-graphql", "response size", "9 MB", "2.6 KB", 9216, 2.6)]
    b = [window("diff naive optimized"), T(30, 62, "Measured Results", 16, TEXT, 700),
         T(830, 62, "measured locally · figures reported by the author · bars not to scale below 2%", 11, MUTED, 400, SANS, "end")]
    y = 92
    bw = 420
    for i, (name, what, bt, at, bv, av) in enumerate(rows):
        dl = .1 + i * .25
        b.append(f'<g class="fade" {d(dl)}>' + T(30, y, name, 13, TEXT, 600, MONO) + T(30, y + 16, what, 11, MUTED) + '</g>')
        b.append(f'<rect class="gr" x="330" y="{y-10}" width="{bw}" height="9" rx="3" fill="#8b98a5" fill-opacity=".35" {d(dl+.1)}/>')
        b.append(T(330 + bw + 12, y - 1, bt, 12, MUTED, 400, MONO, extra=f'class="fade" {d(dl+.6)}'))
        aw = max(bw * av / bv, 8)
        b.append(f'<rect class="gr" x="330" y="{y+4}" width="{aw:.1f}" height="9" rx="3" fill="{ACC}" {d(dl+.5)}/>')
        b.append(T(330 + aw + 12, y + 13, at, 13, ACC, 700, MONO, extra=f'class="fade" {d(dl+1.1)}'))
        y += 48
    y += 6
    b.append(f'<line x1="30" y1="{y-18}" x2="830" y2="{y-18}" stroke="{BORDER}"/>')
    b.append(T(30, y, "edtech-cloud-deploy", 13, TEXT, 600, MONO) + T(30, y + 16, "throughput, workers on ECS (local)", 11, MUTED))
    for j, (lab, val) in enumerate([("1 worker", 1.0), ("2 workers", 1.94), ("4 workers", 3.22)]):
        yy = y - 10 + j * 15
        w = 420 * val / 3.22
        b.append(T(322, yy + 8, lab, 10, MUTED, 400, MONO, "end"))
        b.append(f'<rect class="gr" x="330" y="{yy}" width="{w:.1f}" height="9" rx="3" fill="{ACC2 if j<2 else ACC}" {d(1.6+j*.25)}/>')
        b.append(T(330 + w + 10, yy + 8, f"{val:.2f}×", 11, TEXT, 600, MONO, extra=f'class="fade" {d(2.0+j*.25)}'))
    y += 58
    b.append(T(30, y, "rag-dojo: no benchmark published yet.", 11, MUTED, 400, SANS))
    return svg(860, y + 18, "".join(b), "Animated before and after results")


def activity(cal):
    weeks = cal["weeks"]
    counts = [dd["contributionCount"] for w in weeks for dd in w["contributionDays"]]
    mx = max(counts) or 1
    shades = ["#161b22", "#0e4a35", "#117a55", "#22b07a", ACC]

    def level(n):
        if n == 0:
            return 0
        r = n / mx
        return 1 if r <= .25 else 2 if r <= .5 else 3 if r <= .75 else 4

    active = sum(1 for c in counts if c)
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c else 0
        longest = max(longest, cur)
    b = [window("git log --since=1y"), T(30, 62, "Contribution Activity", 16, TEXT, 700),
         T(830, 62, f"{cal['totalContributions']} contributions in the last year", 12, MUTED, 400, SANS, "end")]
    for i, w in enumerate(weeks):
        for dd in w["contributionDays"]:
            n = dd["contributionCount"]
            b.append(f'<rect class="cl" x="{30+i*14.9:.1f}" y="{84+dd["weekday"]*14}" width="11" height="11" rx="2" '
                     f'fill="{shades[level(n)]}" style="animation-delay:{i*.03+dd["weekday"]*.02:.2f}s"/>')
    b.append(f'<g style="animation: sweep 6s linear 2s infinite"><rect x="-300" y="80" width="40" height="100" fill="url(#hs)" opacity=".18"/></g>')
    for i, (k, v) in enumerate([("active days", active), ("longest streak", f"{longest} days"), ("busiest day", f"{mx} contributions")]):
        x = 30 + i * 200
        b.append(f'<g class="fade" {d(2.2+i*.2)}>' + T(x, 204, v, 16, ACC, 700, MONO) + T(x, 221, k, 12, MUTED) + '</g>')
    defs = (f'<linearGradient id="hs" x1="0" x2="1"><stop offset="0" stop-color="{ACC}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{ACC}"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></linearGradient>')
    return svg(860, 240, "".join(b), "Animated contribution activity", defs)


def experience():
    items = g.EXPERIENCE
    b = [window("git log --author=me"), T(30, 62, "Experience", 16, TEXT, 700)]
    y0 = 98
    n = len(items)
    b.append(f'<rect class="dr" x="111" y="{y0-10}" width="2" height="{(n-1)*62+14}" fill="{BORDER}" {d(.2)}/>')
    for i, (when, org, role, what) in enumerate(items):
        y = y0 + i * 62
        dl = .3 + i * .35
        b.append(f'<g class="fade" {d(dl)}>' + T(30, y + 4, when, 12, MUTED, 400, MONO)
                 + f'<circle cx="112" cy="{y}" r="6" fill="{BG}" stroke="{ACC}" stroke-width="2"/>'
                 + T(132, y + 1, org, 14, TEXT, 700) + T(132 + 16 + int(len(org) * 8.4), y + 1, role, 12, ACC, 500, MONO)
                 + T(132, y + 20, what, 12, MUTED) + '</g>')
        if i == 0:
            b.append(f'<circle cx="112" cy="{y}" r="6" fill="none" stroke="{ACC}" style="transform-box:fill-box;'
                     f'transform-origin:center;animation: pulse 2.2s ease-out 1s infinite"/>')
    return svg(860, y0 + (n - 1) * 62 + 40, "".join(b), "Animated experience timeline")


def connect():
    b = [window("./connect.sh"), T(30, 62, "Open to work", 16, TEXT, 700)]
    b.append(f'<circle cx="212" cy="57" r="5" fill="{ACC}"/><circle cx="212" cy="57" r="5" fill="none" stroke="{ACC}" '
             f'style="transform-box:fill-box;transform-origin:center;animation: pulse 1.8s ease-out infinite"/>')
    x = 30
    for i, lab in enumerate(["Backend", "Platform", "AI Engineering"]):
        c, w = chip(x, 76, lab)
        b.append(f'<g class="fade" {d(.2+i*.15)}>{c}</g>')
        x += w + 8
    b.append(T(30, 128, "On-site, hybrid or remote · Recife, Brazil", 13, MUTED, extra=f'class="fade" {d(.7)}'))
    s1, e1 = typed("l1", 30, 156, "linkedin.com/in/huggsfmelo", 13, ACC, 1.0, weight=700)
    s2, _ = typed("l2", 300, 156, "github.com/HuggsF", 13, ACC, e1 + .1, weight=700)
    return svg(860, 176, "".join(b) + s1 + s2, "Open to work and contact")


def main():
    u = g.api(f"users/{g.USER}")
    repos = [r for r in g.api(f"users/{g.USER}/repos?per_page=100&type=owner") if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in repos)
    langs = {}
    for r in repos:
        for k, v in g.api(f"repos/{g.USER}/{r['name']}/languages").items():
            langs[k] = langs.get(k, 0) + v
    cal = json.loads(g.gh("api", "graphql", "-f", "query=query{user(login:\"%s\"){contributionsCollection{contributionCalendar"
                        "{totalContributions weeks{contributionDays{contributionCount weekday}}}}}}" % g.USER)
                     )["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    featured = [r for n in g.FEATURED for r in repos if r["name"] == n]
    OUT.mkdir(exist_ok=True)
    for name, s in [("a-hero", hero(u, len(repos), stars, cal["totalContributions"])), ("a-stack", stack(langs)),
                    ("a-projects", projects(featured)), ("a-results", results()), ("a-activity", activity(cal)),
                    ("a-experience", experience()), ("a-connect", connect())]:
        (OUT / f"{name}.svg").write_text(s, encoding="utf-8")
        print("wrote", name, len(s), "bytes")


if __name__ == "__main__":
    main()
