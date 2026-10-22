import html

LANES = ["You", "Session (skills)", "Gates — automatic", "Outside the repo"]
COL = 156
NW, NH = 112, 56
LANE_H = 118
LEFT = 118
TOP = 28

def node(nid, lane, col, lines, kind="skill"):
    return {"id": nid, "lane": lane, "col": col, "lines": lines, "kind": kind}

def edge(a, b, label="", loop=False):
    return {"a": a, "b": b, "label": label, "loop": loop}

def pos(n):
    x = LEFT + n["col"] * COL + (COL - NW) / 2
    y = TOP + n["lane"] * LANE_H + (LANE_H - NH) / 2
    return x, y

def render(fig_id, title, nodes, edges, cols):
    W = LEFT + cols * COL + 12
    H = TOP + len(LANES) * LANE_H + 10
    byid = {n["id"]: n for n in nodes}
    out = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape(title)}" xmlns="http://www.w3.org/2000/svg">',
           '<defs><marker id="%s-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>' % fig_id]
    # lanes
    for i, name in enumerate(LANES):
        y = TOP + i * LANE_H
        fill = "var(--lane-gate)" if i == 2 else ("var(--lane-alt)" if i % 2 else "none")
        out.append(f'<rect x="0" y="{y}" width="{W}" height="{LANE_H}" fill="{fill}" stroke="none"/>')
        out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="currentColor" stroke-opacity="0.18" stroke-width="1"/>')
        out.append(f'<text x="12" y="{y + 20}" font-size="11" font-weight="600" fill="currentColor" letter-spacing="0.4">{html.escape(name).upper()}</text>')
    # edges first (under nodes)
    for e in edges:
        a, b = byid[e["a"]], byid[e["b"]]
        ax, ay = pos(a); bx, by = pos(b)
        mk = f'marker-end="url(#{fig_id}-arrow)"'
        if e["loop"]:
            # backward: arc above the source lane
            y0 = ay + NH / 2
            top = min(ay, by) - 22
            d = f"M{ax + NW} {y0} C{ax + NW + 60} {top} {bx - 60} {top} {bx + NW/2} {by}"
            out.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="1.3" stroke-dasharray="5 4" {mk}/>')
            lx, ly = (ax + NW + bx + NW/2) / 2, top + 2
            out.append(f'<text x="{lx}" y="{ly}" font-size="10.5" text-anchor="middle" fill="currentColor"><tspan style="fill:var(--bg)" stroke="var(--bg)" stroke-width="4" paint-order="stroke">{html.escape(e["label"])}</tspan><tspan x="{lx}">{html.escape(e["label"])}</tspan></text>')
            continue
        if a["lane"] == b["lane"]:
            x1, y1, x2, y2 = ax + NW, ay + NH / 2, bx, by + NH / 2
            out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" stroke-width="1.3" {mk}/>')
            lx, ly = (x1 + x2) / 2, y1 - 6
            if len(e["label"]) > 9:
                e = dict(e, label="")
        else:
            down = b["lane"] > a["lane"]
            x1 = ax + NW / 2; y1 = ay + NH if down else ay
            x2 = bx + NW / 2; y2 = by if down else by + NH
            if abs(x1 - x2) < 1:
                out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" stroke-width="1.3" {mk}/>')
                lx, ly = x1 + 6, (y1 + 13) if down else (y1 - 6)
                out.append(f'<text x="{lx}" y="{ly}" font-size="10.5" fill="currentColor" stroke="var(--bg)" stroke-width="4" paint-order="stroke">{html.escape(e["label"])}</text>')
                continue
            ym = (y1 + y2) / 2
            d = f"M{x1} {y1} L{x1} {ym} L{x2} {ym} L{x2} {y2}"
            out.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="1.3" {mk}/>')
            lx, ly = (x1 + x2) / 2, ym - 5
        if e["label"]:
            out.append(f'<text x="{lx}" y="{ly}" font-size="10.5" text-anchor="middle" fill="currentColor" stroke="var(--bg)" stroke-width="4" paint-order="stroke">{html.escape(e["label"])}</text>')
    # nodes
    for n in nodes:
        x, y = pos(n)
        k = n["kind"]
        if k == "human":
            style = 'fill="var(--panel)" stroke="currentColor" stroke-width="1.4" rx="14"'
        elif k == "gate":
            style = 'fill="var(--gate)" stroke="var(--accent)" stroke-width="1.8" rx="4"'
        elif k == "outside":
            style = 'fill="var(--panel)" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3" rx="4"'
        else:
            style = 'fill="var(--panel)" stroke="currentColor" stroke-width="1.2" rx="4"'
        out.append(f'<rect x="{x}" y="{y}" width="{NW}" height="{NH}" {style}/>')
        lines = n["lines"]
        lh = 13
        y0 = y + NH / 2 - (len(lines) - 1) * lh / 2 + 4
        for i, ln in enumerate(lines):
            w = "600" if i == 0 else "400"
            out.append(f'<text x="{x + NW/2}" y="{y0 + i*lh}" font-size="11" font-weight="{w}" text-anchor="middle" fill="currentColor">{html.escape(ln)}</text>')
    out.append("</svg>")
    return "\n".join(out)

# ---------------------------------------------------------------- Scenario A
A_nodes = [
    node("start", 0, 0, ["Start the repo", "new-client-theme.sh"], "human"),
    node("ssh", 2, 0, ["SessionStart hook", "doctor · drift · open", "incidents · 3 rules"], "gate"),
    node("recon", 1, 1, ["/recon-theme", "--live-url", "/store-recon"]),
    node("live", 3, 1, ["Live store", "theme pull, apps,", "popups, markets"], "outside"),
    node("map", 1, 2, ["Reference map", "state of the theme", "gap table"]),
    node("ref", 0, 3, ["Name the reference", "Figma · live · both", "per band"], "human"),
    node("order", 1, 3, ["Playbook order", "1 foundations", "2 commerce path"]),
    node("build", 1, 4, ["/build-page-from-figma", "or /build-section-", "from-live"]),
    node("src", 3, 4, ["Figma frame", "or live page", "(behaviour, copy)"], "outside"),
    node("write", 1, 5, ["Write section,", "template, locale", "/scaffold-section"]),
    node("post", 2, 5, ["PostToolUse", "contract · conventions", "· JSON, per file"], "gate"),
    node("verify", 1, 6, ["/verify-against-", "reference", "+ commerce-check"]),
    node("stop", 2, 6, ["Stop gate", "gate · Theme Check ·", "verify/commerce/GitBot"], "gate"),
    node("dev", 3, 6, ["Dev theme", "preview URL", "(never live)"], "outside"),
    node("commit", 1, 7, ["Commit"]),
    node("pre", 2, 7, ["pre-commit", "8 checks + both", "mirrors + self-tests"], "gate"),
    node("push", 1, 8, ["Push"]),
    node("nudge", 2, 8, ["Push nudge", "→ /gitbot-preflight"], "gate"),
    node("gitbot", 3, 8, ["GitBot review", "posts to Slack", "in 1–2 min"], "outside"),
    node("preflight", 1, 9, ["/gitbot-preflight", "fix, or flag with", "your reason"]),
    node("ci", 2, 9, ["CI on the PR", "same checks", "+ tooling drift"], "gate"),
    node("pr", 0, 10, ["Review, say", "merge"], "human"),
    node("hand", 1, 10, ["Notion handoff", "QA checklist incl.", "purchase path"]),
    node("notion", 3, 10, ["Notion card", "QI picks it up"], "outside"),
    node("inc", 1, 11, ["/record-incident", "the moment a rule", "should have caught"]),
    node("base", 3, 11, ["Base", "/harvest opens", "the PR"], "outside"),
]
A_edges = [
    edge("start", "ssh", "opens a session"),
    edge("ssh", "recon", "context injected"),
    edge("recon", "live", "reads only"),
    edge("recon", "map", "writes"),
    edge("map", "ref", "asks"),
    edge("ref", "order", "per band"),
    edge("order", "build", "stage by stage"),
    edge("build", "src", "look · behaviour · copy"),
    edge("build", "write", ""),
    edge("write", "post", "each file"),
    edge("write", "verify", ""),
    edge("verify", "dev", "renders"),
    edge("verify", "stop", "turn ends"),
    edge("verify", "commit", ""),
    edge("commit", "pre", "new file blocks"),
    edge("commit", "push", ""),
    edge("push", "gitbot", "every push"),
    edge("push", "nudge", ""),
    edge("push", "preflight", ""),
    edge("preflight", "gitbot", "read · fix · flag"),
    edge("preflight", "ci", "PR"),
    edge("ci", "pr", "green"),
    edge("pr", "hand", "merge"),
    edge("hand", "notion", "comment"),
    edge("hand", "inc", "as you go"),
    edge("inc", "base", "generic"),
    edge("preflight", "write", "findings → fix → push again", loop=True),
]

# ---------------------------------------------------------------- Scenario B
B_nodes = [
    node("arrive", 0, 0, ["Arrive on a repo", "someone else", "started"], "human"),
    node("link", 1, 1, ["base-link.sh", "pull-base-tooling.py", "three-way overlay"]),
    node("basew", 3, 1, ["Base", "development", "(remote + worktree)"], "outside"),
    node("ssh", 2, 1, ["SessionStart", "drift from Base ·", "compliance · incidents"], "gate"),
    node("recon", 1, 2, ["/recon-theme", "--live-url", "/store-recon"]),
    node("live", 3, 2, ["Live store", "+ the previous", "team's rule edits"], "outside"),
    node("verdict", 1, 3, ["Carry verdict", "as-is · with fixes ·", "rebuild · missing"]),
    node("decide", 0, 4, ["Argue in the state", "doc, not in code;", "pick the 3 decisions"], "human"),
    node("order", 1, 4, ["Missing list, sorted", "by stage: commerce", "before content"]),
    node("xlog", 1, 5, ["Cross-batch log", "if another session", "runs in parallel"]),
    node("build", 1, 6, ["Per build: the", "same loop as a", "fresh rebuild"]),
    node("post", 2, 6, ["PostToolUse +", "Stop gate", "(legacy reported, not gated)"], "gate"),
    node("regress", 1, 7, ["live-parity regress", "consumers outside", "the batch at 0.0%"]),
    node("commerce", 1, 8, ["commerce-check", "green at the close", "of every stage"]),
    node("dev", 3, 8, ["Dev theme", "QA theme read-only", "live never"], "outside"),
    node("merge", 1, 9, ["Merge the project", "branch early;", "push, PR, preflight"]),
    node("gitbot", 3, 9, ["GitBot", "+ CI drift report"], "outside"),
    node("harvest", 1, 10, ["/record-incident", "→ /harvest"]),
    node("base2", 3, 10, ["Base", "rules + checks", "improve for all"], "outside"),
    node("done", 0, 10, ["Merge on", "your word"], "human"),
]
B_edges = [
    edge("arrive", "link", "three commands"),
    edge("link", "basew", "reads at the stamp"),
    edge("link", "ssh", "ADD · UPDATE · KEEP · RETIRE"),
    edge("ssh", "recon", ""),
    edge("recon", "live", "inventory"),
    edge("recon", "verdict", "state doc"),
    edge("verdict", "decide", ""),
    edge("decide", "order", ""),
    edge("order", "xlog", ""),
    edge("xlog", "build", ""),
    edge("build", "post", "each write"),
    edge("build", "regress", "shared section touched"),
    edge("regress", "commerce", ""),
    edge("commerce", "dev", "purchase path"),
    edge("commerce", "merge", "green"),
    edge("merge", "gitbot", "every push"),
    edge("merge", "harvest", ""),
    edge("merge", "done", "previews first"),
    edge("harvest", "base2", "generic"),
    edge("regress", "build", "not 0.0% → not additive → fix", loop=True),
]

# ---------------------------------------------------------------- Scenario C
C_nodes = [
    node("qi", 3, 0, ["Notion", "QI logs issues", "on the card"], "outside"),
    node("ask", 0, 0, ["Ask for the", "QA round"], "human"),
    node("close", 1, 1, ["/close-qa-loop", "picks each issue up"]),
    node("ssh", 2, 1, ["SessionStart", "open incidents,", "compliance number"], "gate"),
    node("ref", 1, 2, ["Which reference?", "reference-map.md", "names it per band"]),
    node("fix", 1, 3, ["Fix against the", "standards, not", "around them"]),
    node("post", 2, 3, ["PostToolUse", "the file you just", "wrote"], "gate"),
    node("stop", 2, 4, ["Stop: 3 advisories", "verify newer? commerce", "report? GitBot read?"], "gate"),
    node("verify", 1, 4, ["/verify-against-", "reference on the", "changed band"]),
    node("src", 3, 4, ["Figma frame", "or live section"], "outside"),
    node("commerce", 1, 5, ["commerce-check", "if the purchase", "path moved"]),
    node("regress", 1, 6, ["regress: the other", "pages still 0.0%", "at defaults"]),
    node("dev", 3, 6, ["Dev theme", "vs QA theme"], "outside"),
    node("push", 1, 7, ["Push"]),
    node("pre", 2, 7, ["pre-commit +", "push nudge"], "gate"),
    node("gitbot", 3, 7, ["GitBot", "follow-up review:", "fixed or still open"], "outside"),
    node("preflight", 1, 8, ["/gitbot-preflight", "fixed, or flagged", "in your words"]),
    node("ci", 2, 8, ["CI on the PR"], "gate"),
    node("merge", 0, 9, ["Say merge"], "human"),
    node("closen", 1, 9, ["Close the issue", "in Notion with", "the evidence"]),
    node("notion2", 3, 9, ["Notion", "comment, status"], "outside"),
    node("inc", 1, 10, ["/record-incident", "→ /harvest to Base"]),
    node("base", 3, 10, ["Base", "the gate learns"], "outside"),
]
C_edges = [
    edge("ask", "close", ""),
    edge("qi", "close", "reads the list"),
    edge("close", "ssh", ""),
    edge("close", "ref", ""),
    edge("ref", "fix", ""),
    edge("fix", "post", "each write"),
    edge("fix", "verify", ""),
    edge("verify", "src", "diff + boxes"),
    edge("verify", "stop", "turn ends"),
    edge("verify", "commerce", ""),
    edge("commerce", "regress", ""),
    edge("regress", "dev", "consumers"),
    edge("regress", "push", "0.0%"),
    edge("push", "pre", ""),
    edge("push", "gitbot", ""),
    edge("push", "preflight", ""),
    edge("preflight", "gitbot", "read · flag"),
    edge("preflight", "ci", "PR"),
    edge("ci", "merge", "green"),
    edge("merge", "closen", ""),
    edge("closen", "notion2", "evidence"),
    edge("closen", "inc", "rule gap?"),
    edge("inc", "base", ""),
    edge("preflight", "fix", "still open → fix again", loop=True),
]

figA = render("a", "Fresh rebuild: from a new repo to a merged, handed-off page, with the automatic gates at each step", A_nodes, A_edges, 12)
figB = render("b", "Joining a rebuild midway: tooling pulled three-way, a carry verdict, the missing list built in stage order", B_nodes, B_edges, 11)
figC = render("c", "Rebuild done, correcting: a QA issue fixed against the standards, proved, and closed with evidence", C_nodes, C_edges, 11)

page = f"""<title>Base Workflow v3</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: one column of reading text at 68ch, each figure breaking out to the full width with its own horizontal scroll. */
:root {{
  --bg: #f6f7f5; --fg: #1d2327; --muted: #5a6670; --panel: #ffffff; --line: #d3d9d6;
  --lane-alt: rgba(29,35,39,0.035); --lane-gate: rgba(201,120,10,0.07);
  --accent: #b9650a; --gate: #fff4e3;
  --font-body: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "IBM Plex Mono", "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #15191c; --fg: #e6e9e7; --muted: #9aa5ad; --panel: #1e2428; --line: #333c42;
  --lane-alt: rgba(230,233,231,0.04); --lane-gate: rgba(240,160,60,0.09);
  --accent: #f0a23c; --gate: #2b2419; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #15191c; --fg: #e6e9e7; --muted: #9aa5ad; --panel: #1e2428; --line: #333c42;
  --lane-alt: rgba(230,233,231,0.04); --lane-gate: rgba(240,160,60,0.09);
  --accent: #f0a23c; --gate: #2b2419; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font-family: var(--font-body); font-size: 16px; line-height: 1.55;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 32px 64px; }}
.wrap {{ max-width: 1180px; margin-inline: auto; }}
.prose {{ max-width: 68ch; }}
h1 {{ font-size: 2rem; line-height: 1.15; margin: 0 0 8px; text-wrap: balance; font-weight: 600; }}
h2 {{ font-size: 1.35rem; margin: 48px 0 8px; text-wrap: balance; font-weight: 600; }}
p {{ margin: 0 0 14px; }}
.eyebrow {{ font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 10px 22px; margin: 18px 0 6px; font-size: 13px; color: var(--muted); }}
.legend span {{ display: inline-flex; align-items: center; gap: 8px; }}
.sw {{ width: 26px; height: 16px; border-radius: 3px; background: var(--panel); border: 1.3px solid var(--fg); display: inline-block; }}
.sw.human {{ border-radius: 8px; }}
.sw.gate {{ background: var(--gate); border: 1.8px solid var(--accent); }}
.sw.outside {{ border-style: dashed; }}
.sw.loop {{ border: none; border-top: 1.5px dashed var(--fg); height: 0; border-radius: 0; }}
figure {{ margin: 18px 0 8px; }}
.scroll {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 6px; background: var(--bg); }}
.scroll svg {{ display: block; font-family: var(--font-body); }}
figcaption {{ font-size: 14px; color: var(--muted); margin-top: 10px; max-width: 80ch; }}
code {{ font-family: var(--font-mono); font-size: 0.86em; background: var(--lane-alt); padding: 1px 5px; border-radius: 3px; }}
table {{ border-collapse: collapse; width: 100%; max-width: 920px; font-size: 14px; margin: 10px 0 18px; }}
th, td {{ text-align: left; vertical-align: top; padding: 8px 10px; border-bottom: 1px solid var(--line); }}
th {{ font-weight: 600; color: var(--muted); font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; }}
.tbl {{ overflow-x: auto; }}
ul {{ padding-left: 20px; margin: 0 0 14px; }} li {{ margin-bottom: 6px; }}
@media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto; }} }}
</style>
<div class="wrap">
<div class="prose">
<div class="eyebrow">Base theme · AI workflow v3 · 22 Oct 2026</div>
<h1>What happens behind the scenes</h1>
<p>Three situations a developer lands in, drawn as what actually runs: the person's four or five decisions in the top lane, the skills the session invokes below them, the gates that fire whether anyone remembers them in the orange lane, and the systems outside the repo at the bottom. The orange lane is the point of v3. Everything in it fired on its own during the Pique rebuild's successor, or will.</p>
<p>Read each figure left to right. A solid arrow is the next step; a label on it is what crosses. A dashed arc is the loop that runs until a gate or GitBot is clean.</p>
<div class="legend">
<span><i class="sw human"></i> you decide</span>
<span><i class="sw"></i> a skill the session runs</span>
<span><i class="sw gate"></i> a gate that fires on its own</span>
<span><i class="sw outside"></i> outside the repo</span>
<span><i class="sw loop"></i> loop until clean</span>
</div>
</div>

<h2>A. A fresh rebuild</h2>
<div class="prose"><p>From a new client repo to a merged page. The two things that changed since v2 sit in columns three and seven: the reference is named per band before anything is fetched, and the purchase path is built and checked second, not last.</p></div>
<figure><div class="scroll">{figA}</div>
<figcaption>Scenario A. Every file written is checked as it is written; every turn is checked as it ends; every commit, push and pull request is checked again by something that does not need to be remembered. The developer's decisions are the reference per band, the review, and the word "merge".</figcaption></figure>

<h2>B. Joining a rebuild midway</h2>
<div class="prose"><p>Someone else started the store. The first act is measurement, and the tooling arrives by a three-way overlay that keeps the previous team's edits and retires what Base has renamed.</p></div>
<figure><div class="scroll">{figB}</div>
<figcaption>Scenario B. Three commands on arrival; a carry verdict that is argued in the state document, never in code; the missing list sorted by the stage table so commerce comes before content; and from then on the same loop as a fresh rebuild, with one addition: every shared section the batch touches is proved unchanged for the pages built before it.</figcaption></figure>

<h2>C. The rebuild is done; QA found things</h2>
<div class="prose"><p>Quality inspection logs issues on the Notion card. A correction is a smaller build with the same proof: the fix is verified against the band's reference, the purchase path is re-walked when it moved, the other pages are shown unchanged, and GitBot's follow-up review says whether the finding is closed.</p></div>
<figure><div class="scroll">{figC}</div>
<figcaption>Scenario C. The Stop gate carries three advisories for exactly this case: a changed band with no verify report newer than the change, a purchase-path change with no commerce report, and a client branch whose GitBot findings nobody has read. An issue closes in Notion with the evidence quoted, and a fix that a rule should have prevented becomes an incident, then a Base pull request.</figcaption></figure>

<h2>What fires without anyone remembering</h2>
<div class="prose"><p>The orange boxes, as a list, with what each one reads. These are the same in Base and in every client fork that has pulled the tooling.</p></div>
<div class="tbl"><table>
<tr><th>When</th><th>What runs</th><th>What it does</th></tr>
<tr><td>A session starts</td><td>SessionStart hook</td><td>Injects doctor status, tooling drift from Base, the compliance number, open incidents and the three most-missed rules.</td></tr>
<tr><td>A theme file is written</td><td>PostToolUse hook</td><td>Settings contract, the grep-level conventions (now including what GitBot reports and the raw cart requests), JSON validity and the locale key cap, on that one file, handed back at once.</td></tr>
<tr><td>A push happens</td><td>PostToolUse on Bash</td><td>Says that GitBot is reviewing it and points at the preflight.</td></tr>
<tr><td>A turn ends</td><td>Stop hook</td><td>The same gate over everything changed, plus Theme Check; a new file that fails blocks the turn. Three advisories: verify report, commerce report, GitBot findings read.</td></tr>
<tr><td>A commit</td><td>pre-commit</td><td>Section contract, both mirrors regenerated and staged, Theme Check on staged files, rule links, AI config caps, docs interpolation, conventions, and the checks' own 74 self-tests.</td></tr>
<tr><td>A pull request</td><td>CI</td><td>The same checks, plus the tooling drift report either way.</td></tr>
<tr><td>Every push, every branch</td><td>GitBot</td><td>Reviews against Base's rules and posts to the client's Slack. The session reads it back with the preflight.</td></tr>
</table></div>

<h2>Where each step lives</h2>
<div class="tbl"><table>
<tr><th>Step</th><th>File</th></tr>
<tr><td>The order of attack, commerce second</td><td><code>.claude/workflows/rebuild-playbook.md</code></td></tr>
<tr><td>Arriving, measuring, the live inventory</td><td><code>recon-theme</code>, <code>recon-theme.py --live-url</code>, <code>store-recon</code></td></tr>
<tr><td>The reference per band</td><td><code>docs/ai-workflow/reference-map.md</code></td></tr>
<tr><td>Building from a frame or from live</td><td><code>build-page-from-figma</code>, <code>build-section-from-live</code></td></tr>
<tr><td>Proving the look</td><td><code>verify-against-reference</code>, <code>live-parity.py</code>, <code>compare.py</code></td></tr>
<tr><td>Proving the purchase path</td><td><code>commerce-check.py</code></td></tr>
<tr><td>Reading GitBot from the session</td><td><code>gitbot-preflight</code>, <code>preflight-status.py</code></td></tr>
<tr><td>A card of landing pages</td><td><code>landing-batch.md</code>, <code>assemble-templates.py</code>, <code>push-dev-theme.sh</code></td></tr>
<tr><td>The gates</td><td><code>check-conventions.py</code>, <code>check-section-contract.py</code>, <code>check-json.py</code>, <code>test-checks.py</code></td></tr>
<tr><td>Lessons flowing up</td><td><code>record-incident</code>, <code>harvest</code>; the Pique harvest index in <code>docs/ai-workflow/incidents/README.md</code></td></tr>
</table></div>
</div>
"""
open(__import__("os").path.join(__import__("os").path.dirname(__file__), "workflow-v3-map.html"), "w", encoding="utf-8").write(page)
print("written", len(page), "bytes")
