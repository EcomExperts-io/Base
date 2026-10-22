import html, json, sys, os
import importlib.util as _u
_s = _u.spec_from_file_location("gen", os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflow-v3-map.py"))
gen = _u.module_from_spec(_s)
_s.loader.exec_module(gen)  # reuses the map's node and edge data and grid, so the two never drift

def render(fig_id, nodes, edges, cols):
    W = gen.LEFT + cols * gen.COL + 12
    H = gen.TOP + len(gen.LANES) * gen.LANE_H + 10
    byid = {n["id"]: n for n in nodes}
    out = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Scenario {fig_id.upper()} board" xmlns="http://www.w3.org/2000/svg" data-fig="{fig_id}">',
           f'<defs><marker id="{fig_id}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>']
    for i, name in enumerate(gen.LANES):
        y = gen.TOP + i * gen.LANE_H
        fill = "var(--lane-gate)" if i == 2 else ("var(--lane-alt)" if i % 2 else "none")
        out.append(f'<rect x="0" y="{y}" width="{W}" height="{gen.LANE_H}" fill="{fill}"/>')
        out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="currentColor" stroke-opacity="0.18"/>')
        out.append(f'<text x="12" y="{y + 20}" font-size="11" font-weight="600" fill="currentColor" letter-spacing="0.4">{html.escape(name).upper()}</text>')
    for k, e in enumerate(edges):
        a, b = byid[e["a"]], byid[e["b"]]
        ax, ay = gen.pos(a); bx, by = gen.pos(b)
        NW, NH = gen.NW, gen.NH
        mk = f'marker-end="url(#{fig_id}-arrow)"'
        eid = f'{fig_id}-e-{e["a"]}-{e["b"]}'
        g = [f'<g class="edge" id="{eid}">']
        if e["loop"]:
            y0 = ay + NH / 2; top = min(ay, by) - 22
            d = f"M{ax + NW} {y0} C{ax + NW + 60} {top} {bx - 60} {top} {bx + NW/2} {by}"
            g.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="1.3" stroke-dasharray="5 4" {mk}/>')
            lx, ly = (ax + NW + bx + NW/2) / 2, top + 2
            g.append(f'<text x="{lx}" y="{ly}" font-size="10.5" text-anchor="middle" fill="currentColor" stroke="var(--bg)" stroke-width="4" paint-order="stroke">{html.escape(e["label"])}</text>')
        elif a["lane"] == b["lane"]:
            x1, y1, x2, y2 = ax + NW, ay + NH / 2, bx, by + NH / 2
            g.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" stroke-width="1.3" {mk}/>')
            if e["label"] and len(e["label"]) <= 9:
                g.append(f'<text x="{(x1 + x2) / 2}" y="{y1 - 6}" font-size="10.5" text-anchor="middle" fill="currentColor" stroke="var(--bg)" stroke-width="4" paint-order="stroke">{html.escape(e["label"])}</text>')
        else:
            down = b["lane"] > a["lane"]
            x1 = ax + NW / 2; y1 = ay + NH if down else ay
            x2 = bx + NW / 2; y2 = by if down else by + NH
            if abs(x1 - x2) < 1:
                g.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" stroke-width="1.3" {mk}/>')
                if e["label"]:
                    g.append(f'<text x="{x1 + 6}" y="{(y1 + 13) if down else (y1 - 6)}" font-size="10.5" fill="currentColor" stroke="var(--bg)" stroke-width="4" paint-order="stroke">{html.escape(e["label"])}</text>')
            else:
                ym = (y1 + y2) / 2
                g.append(f'<path d="M{x1} {y1} L{x1} {ym} L{x2} {ym} L{x2} {y2}" fill="none" stroke="currentColor" stroke-width="1.3" {mk}/>')
                if e["label"]:
                    g.append(f'<text x="{(x1 + x2) / 2}" y="{ym - 5}" font-size="10.5" text-anchor="middle" fill="currentColor" stroke="var(--bg)" stroke-width="4" paint-order="stroke">{html.escape(e["label"])}</text>')
        g.append("</g>")
        out.append("".join(g))
    for n in nodes:
        x, y = gen.pos(n)
        k = n["kind"]
        style = {"human": 'fill="var(--panel)" stroke="currentColor" stroke-width="1.4" rx="14"',
                 "gate": 'fill="var(--gate)" stroke="var(--accent)" stroke-width="1.8" rx="4"',
                 "outside": 'fill="var(--panel)" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3" rx="4"'}.get(k, 'fill="var(--panel)" stroke="currentColor" stroke-width="1.2" rx="4"')
        out.append(f'<g class="node" id="{fig_id}-n-{n["id"]}"><rect x="{x}" y="{y}" width="{gen.NW}" height="{gen.NH}" {style}/>')
        lines = n["lines"]; lh = 13
        y0 = y + gen.NH / 2 - (len(lines) - 1) * lh / 2 + 4
        for i, ln in enumerate(lines):
            out.append(f'<text x="{x + gen.NW/2}" y="{y0 + i*lh}" font-size="11" font-weight="{"600" if i == 0 else "400"}" text-anchor="middle" fill="currentColor">{html.escape(ln)}</text>')
        out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)

STEPS = {
"a": [
 (["start"], "You start the repo from Base with one script. It clones the development branch and stamps which Base version the tooling came from."),
 (["ssh"], "The moment a session opens, a hook injects the state: doctor status, drift from Base, the compliance number, open incidents and the three most-missed rules. Nobody runs it."),
 (["recon", "live"], "You run recon with the live URL. It measures the theme and lists what the live store loads: apps, popups, markets, a page builder. It reads; it never writes."),
 (["map"], "Recon writes the state of the theme and the reference map, one row per band."),
 (["ref"], "You name the reference per band: Figma for the look, live for what the band does and says today, or both. Pique never got asked; that is where its fix commits came from."),
 (["order"], "The playbook sets the order: foundations, then the commerce path, then chrome, shared parts, templates, content, the long tail. Commerce comes second because it shipped last on Pique and the client found the bug."),
 (["build", "src"], "Each band is built from its reference: the Figma frame, or the live page through the live-build skill, which pulls the live theme from the store and cleans its code to the rules."),
 (["write", "post"], "Every file written is checked as it is written: the settings contract, the conventions, JSON validity, the locale key cap. The findings come back in the same turn."),
 (["verify", "dev", "stop"], "Verification renders the band and diffs it against its reference; a change to the purchase path gets the commerce check. When the turn ends, the Stop gate runs everything again plus Theme Check, and names what has no report."),
 (["commit", "pre"], "A commit runs eight checks, regenerates both mirrors, and runs the checks' own self-tests. A new file that fails blocks the commit; legacy is reported, never gated."),
 (["push", "nudge", "gitbot"], "A push is reviewed by GitBot within two minutes and posted to the client's Slack. The session is told so at once."),
 (["preflight"], "The preflight reads GitBot's findings from inside the session and settles each one: fixed, or flagged with your reason in your words. Then push again, until nothing is open."),
 (["ci", "pr"], "CI runs the same checks on the pull request plus the drift report. You review and say merge."),
 (["hand", "notion"], "The handoff goes to Notion: what was built, the decisions, and a QA checklist in plain English with the purchase-path rows."),
 (["inc", "base"], "Anything a rule should have caught is recorded the moment it happens. The generic ones go up to Base and reach every fork on the next pull."),
],
"b": [
 (["arrive"], "You arrive on a repo someone else started. Measurement comes before code."),
 (["link", "basew"], "Two scripts link Base as a remote and overlay the tooling three-way against the stamp: files the fork never had are added, Base's changes land where the fork never touched them, and the fork's own edits are kept and listed."),
 (["ssh"], "The overlay sorts every file: ADD, UPDATE, KEEP, RETIRE. A renamed skill is retired, not duplicated. The next session start prints the drift and the compliance number."),
 (["recon", "live"], "Recon measures the theme and the live store, and reads what the previous team wrote into the rule copies: their breakpoints, their container, their decisions."),
 (["verdict"], "It ends with a carry verdict: carry as-is, carry with fixes, rebuild, or missing."),
 (["decide"], "You argue with the verdict in the state document, never in code, and take the three decisions: the breakpoint, the container, and which conventions to keep."),
 (["order"], "The missing list becomes the build order, sorted by the stage table. If the homepage exists and the cart does not, the cart comes next, whatever the tracker says."),
 (["xlog"], "If another session runs in parallel, a shared log records every planned edit to a shared file before it is made, so the two reuse each other's settings instead of adding twins."),
 (["build", "post"], "From here it is the same loop as a fresh rebuild: every file checked as it is written, every turn checked as it ends. Legacy is reported, never gated."),
 (["regress"], "Every shared section the batch touches is proved unchanged for the pages built before it: a consumer page outside the batch, on the QA theme against the dev theme, at 0.0%."),
 (["commerce", "dev"], "The commerce check runs green at the close of every stage. Nothing after stage two may break the cart."),
 (["merge", "gitbot"], "The project branch is merged in early, not only at the end; then push, pull request, and the GitBot preflight."),
 (["harvest", "base2", "done"], "Incidents recorded along the way are harvested to Base. You merge on your word, with the preview links in hand first."),
],
"c": [
 (["qi", "ask"], "Quality inspection logs issues on the Notion card and you ask for the round."),
 (["close", "ssh"], "The QA loop skill picks each issue up. The session start already printed the open incidents and the compliance number."),
 (["ref"], "The reference map says which reference each band has, so the fix is checked against the right thing."),
 (["fix", "post"], "The fix is made against the standards, not around them. Each write is gated as it lands."),
 (["verify", "src"], "The changed band is verified against its reference: a diff and a box table against the frame, or the live section at the same widths."),
 (["stop"], "The Stop gate carries three advisories for exactly this case: a changed band with no newer verify report, a purchase-path change with no commerce report, and GitBot findings nobody has read since the last commit."),
 (["commerce"], "If the purchase path moved, the commerce check walks add, change, discount, remove and the market switch again."),
 (["regress", "dev"], "The other pages that share the section are shown unchanged at defaults: 0.0% on the QA theme against the dev theme."),
 (["push", "pre", "gitbot"], "Push. The pre-commit and the push nudge ran; GitBot's follow-up review says whether each earlier finding is fixed or still open."),
 (["preflight", "ci"], "The preflight settles what is still open, fixed or flagged in your words, and CI runs on the pull request."),
 (["merge", "closen", "notion2"], "You say merge. The issue closes in Notion with the evidence quoted: the numbers, not an assertion."),
 (["inc", "base"], "A fix that a rule should have prevented becomes an incident, then a Base pull request, so the gate learns."),
],
}

def fig(fid, nodes, edges, cols):
    return render(fid, nodes, edges, cols)

figs = {"a": fig("a", gen.A_nodes, gen.A_edges, 12), "b": fig("b", gen.B_nodes, gen.B_edges, 11), "c": fig("c", gen.C_nodes, gen.C_edges, 11)}
edges_json = {k: [[e["a"], e["b"]] for e in v] for k, v in (("a", gen.A_edges), ("b", gen.B_edges), ("c", gen.C_edges))}
steps_json = {k: [{"ids": s[0], "text": s[1]} for s in v] for k, v in STEPS.items()}

page = f"""<title>Base Workflow v3 Walkthrough</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a control bar, one caption line, and the board; one scenario at a time, one step at a time. */
:root {{
  --bg: #f6f7f5; --fg: #1d2327; --muted: #5a6670; --panel: #ffffff; --line: #d3d9d6;
  --lane-alt: rgba(29,35,39,0.035); --lane-gate: rgba(201,120,10,0.07);
  --accent: #b9650a; --gate: #fff4e3; --hi: #b9650a;
  --font-body: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "IBM Plex Mono", "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #15191c; --fg: #e6e9e7; --muted: #9aa5ad; --panel: #1e2428; --line: #333c42;
  --lane-alt: rgba(230,233,231,0.04); --lane-gate: rgba(240,160,60,0.09);
  --accent: #f0a23c; --gate: #2b2419; --hi: #f0a23c; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #15191c; --fg: #e6e9e7; --muted: #9aa5ad; --panel: #1e2428; --line: #333c42;
  --lane-alt: rgba(230,233,231,0.04); --lane-gate: rgba(240,160,60,0.09);
  --accent: #f0a23c; --gate: #2b2419; --hi: #f0a23c; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font-family: var(--font-body); font-size: 16px; line-height: 1.5;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px 48px; }}
.wrap {{ max-width: 1180px; margin-inline: auto; }}
h1 {{ font-size: 1.7rem; margin: 0 0 4px; font-weight: 600; text-wrap: balance; }}
.eyebrow {{ font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }}
.intro {{ max-width: 68ch; color: var(--muted); margin: 0 0 16px; }}
.bar {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin: 12px 0; }}
.tabs {{ display: flex; gap: 6px; flex-wrap: wrap; }}
button {{ font: inherit; color: var(--fg); background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 8px 14px; cursor: pointer; }}
button:focus-visible {{ outline: 2px solid var(--hi); outline-offset: 2px; }}
button[aria-pressed="true"] {{ border-color: var(--hi); box-shadow: inset 0 0 0 1px var(--hi); }}
button.primary {{ background: var(--hi); color: #15191c; border-color: var(--hi); font-weight: 600; }}
.ctl {{ display: flex; gap: 6px; margin-left: auto; }}
.caption {{ min-height: 4.5em; padding: 14px 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); display: grid; grid-template-columns: auto 1fr; gap: 14px; align-items: start; }}
.step-no {{ font-family: var(--font-mono); font-size: 12px; color: var(--hi); padding-top: 4px; white-space: nowrap; }}
.caption p {{ margin: 0; max-width: 72ch; }}
.scroll {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; background: var(--bg); margin-top: 12px; }}
.scroll svg {{ display: block; font-family: var(--font-body); }}
.scroll svg[hidden] {{ display: none; }}
.node, .edge {{ opacity: 0.18; transition: opacity 0.35s ease; }}
@media (prefers-reduced-motion: reduce) {{ .node, .edge {{ transition: none; }} }}
.node.seen, .edge.seen {{ opacity: 1; }}
.node.now rect {{ stroke: var(--hi); stroke-width: 3; }}
.node.now text {{ font-weight: 600; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 10px 22px; margin: 12px 0 0; font-size: 13px; color: var(--muted); }}
.legend span {{ display: inline-flex; align-items: center; gap: 8px; }}
.sw {{ width: 26px; height: 16px; border-radius: 3px; background: var(--panel); border: 1.3px solid var(--fg); display: inline-block; }}
.sw.human {{ border-radius: 8px; }} .sw.gate {{ background: var(--gate); border: 1.8px solid var(--accent); }} .sw.outside {{ border-style: dashed; }}
.hint {{ font-size: 13px; color: var(--muted); margin-top: 10px; }}
</style>
<div class="wrap">
<div class="eyebrow">Base theme · AI workflow v3 · walkthrough</div>
<h1>What runs behind the scenes, one step at a time</h1>
<p class="intro">Pick a situation, then press Play or step with Next. Each step lights one part of the board and says what happens there in one sentence. The orange lane is what fires on its own; the rest is what you or the session does.</p>
<div class="bar">
  <div class="tabs" role="tablist" aria-label="Scenario">
    <button type="button" id="tab-a" role="tab" aria-pressed="true" data-fig="a">A · A fresh rebuild</button>
    <button type="button" id="tab-b" role="tab" aria-pressed="false" data-fig="b">B · Joining midway</button>
    <button type="button" id="tab-c" role="tab" aria-pressed="false" data-fig="c">C · After QA</button>
  </div>
  <div class="ctl">
    <button type="button" id="btn-prev" aria-label="Previous step">Back</button>
    <button type="button" id="btn-play" class="primary" aria-label="Play through the steps">Play</button>
    <button type="button" id="btn-next" aria-label="Next step">Next</button>
    <button type="button" id="btn-all" aria-label="Show the whole board">Show all</button>
    <button type="button" id="btn-voice" aria-pressed="false" aria-label="Read each step aloud">Voice off</button>
  </div>
</div>
<div class="caption" aria-live="polite"><div class="step-no" id="step-no">step 0 of 0</div><p id="step-text">Press Play.</p></div>
<div class="scroll" id="board">
{figs["a"]}
{figs["b"]}
{figs["c"]}
</div>
<div class="legend">
<span><i class="sw human"></i> you decide</span>
<span><i class="sw"></i> a skill the session runs</span>
<span><i class="sw gate"></i> a gate that fires on its own</span>
<span><i class="sw outside"></i> outside the repo</span>
</div>
<p class="hint">Voice reads each step aloud with the voice built into your browser; with it on, Play waits for the sentence to finish before the next step. Keys: Space plays and pauses, the arrow keys step, 1 2 3 switch scenario, V toggles the voice. The board scrolls sideways on a narrow screen; the lit box is scrolled into view at each step.</p>
</div>
<script>
(function () {{
  var STEPS = {json.dumps(steps_json)};
  var EDGES = {json.dumps(edges_json)};
  var fig = 'a', i = -1, timer = null, voice = false, speaking = null;
  var voiceBtn = document.getElementById('btn-voice');
  var canSpeak = !!(window.speechSynthesis && window.SpeechSynthesisUtterance);
  if (!canSpeak) {{ voiceBtn.disabled = true; voiceBtn.textContent = 'No voice here'; }}
  try {{ if (canSpeak && localStorage.getItem('wf3-voice') === '1') voice = true; }} catch (e) {{}}
  function pickVoice() {{
    var vs = window.speechSynthesis.getVoices();
    var en = vs.filter(function (v) {{ return /^en/i.test(v.lang); }});
    var pref = en.filter(function (v) {{ return /Samantha|Daniel|Google UK English|Google US English|Microsoft (Aria|Guy|Ryan)/.test(v.name); }});
    return pref[0] || en[0] || vs[0] || null;
  }}
  function say(txt, done) {{
    if (!voice || !canSpeak) {{ if (done) done(false); return; }}
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(txt);
    var v = pickVoice(); if (v) u.voice = v;
    u.rate = 0.98; u.pitch = 1;
    var finished = false;
    u.onend = u.onerror = function () {{ if (finished) return; finished = true; speaking = null; if (done) done(true); }};
    speaking = u;
    window.speechSynthesis.speak(u);
  }}
  function paintVoice() {{ voiceBtn.setAttribute('aria-pressed', String(voice)); voiceBtn.textContent = voice ? 'Voice on' : 'Voice off'; }}
  var svgs = {{}};
  document.querySelectorAll('#board svg').forEach(function (s) {{ svgs[s.dataset.fig] = s; }});
  var no = document.getElementById('step-no'), text = document.getElementById('step-text'), play = document.getElementById('btn-play');
  try {{ var saved = localStorage.getItem('wf3-fig'); if (saved && STEPS[saved]) fig = saved; }} catch (e) {{}}
  function paint() {{
    var s = svgs[fig], steps = STEPS[fig];
    Object.keys(svgs).forEach(function (k) {{ if (k !== fig) svgs[k].setAttribute('hidden', ''); else svgs[k].removeAttribute('hidden'); }});
    document.querySelectorAll('[role=tab]').forEach(function (b) {{ b.setAttribute('aria-pressed', String(b.dataset.fig === fig)); }});
    var seen = {{}}, now = {{}};
    for (var k = 0; k <= i && k < steps.length; k++) steps[k].ids.forEach(function (id) {{ seen[id] = true; if (k === i) now[id] = true; }});
    s.querySelectorAll('.node').forEach(function (n) {{
      var id = n.id.split('-n-')[1];
      n.classList.toggle('seen', !!seen[id] || i >= steps.length);
      n.classList.toggle('now', !!now[id]);
    }});
    EDGES[fig].forEach(function (e) {{
      var el = s.getElementById(fig + '-e-' + e[0] + '-' + e[1]);
      if (el) el.classList.toggle('seen', (!!seen[e[0]] && !!seen[e[1]]) || i >= steps.length);
    }});
    if (i < 0) {{ no.textContent = 'step 0 of ' + steps.length; text.textContent = 'Press Play, or Next.'; }}
    else if (i >= steps.length) {{ no.textContent = 'all ' + steps.length + ' steps'; text.textContent = 'The whole board. Pick another situation, or press Back to walk it again.'; if (canSpeak) window.speechSynthesis.cancel(); }}
    else {{
      no.textContent = 'step ' + (i + 1) + ' of ' + steps.length; text.textContent = steps[i].text;
      say(steps[i].text, function (spoke) {{ if (spoke && timer === 'voice') {{ var n = STEPS[fig].length; if (i < n) setTimeout(function () {{ if (timer === 'voice') step(1); }}, 700); }} }});
      var first = s.getElementById(fig + '-n-' + steps[i].ids[0]);
      if (first && first.scrollIntoView) first.scrollIntoView({{ block: 'nearest', inline: 'center', behavior: 'smooth' }});
    }}
  }}
  function step(d) {{ var n = STEPS[fig].length; i = Math.max(-1, Math.min(n, i + d)); paint(); if (i >= n) stop(); }}
  function stop() {{ if (timer && timer !== 'voice') clearInterval(timer); timer = null; play.textContent = 'Play'; if (canSpeak) window.speechSynthesis.cancel(); }}
  function start() {{
    if (i >= STEPS[fig].length) i = -1;
    play.textContent = 'Pause';
    if (voice && canSpeak) {{ timer = 'voice'; step(1); }}
    else {{ timer = setInterval(function () {{ step(1); }}, 5200); step(1); }}
  }}
  function setFig(f) {{ stop(); fig = f; i = -1; try {{ localStorage.setItem('wf3-fig', f); }} catch (e) {{}} paint(); }}
  voiceBtn.addEventListener('click', function () {{
    voice = !voice; paintVoice(); try {{ localStorage.setItem('wf3-voice', voice ? '1' : '0'); }} catch (e) {{}}
    if (!voice && canSpeak) window.speechSynthesis.cancel();
    if (voice && i >= 0 && i < STEPS[fig].length) say(STEPS[fig][i].text);
    if (timer) {{ var wasOn = true; stop(); if (wasOn) start(); }}
  }});
  if (canSpeak && window.speechSynthesis.onvoiceschanged !== undefined) window.speechSynthesis.onvoiceschanged = function () {{}};
  paintVoice();
  document.querySelectorAll('[role=tab]').forEach(function (b) {{ b.addEventListener('click', function () {{ setFig(b.dataset.fig); }}); }});
  document.getElementById('btn-next').addEventListener('click', function () {{ stop(); step(1); }});
  document.getElementById('btn-prev').addEventListener('click', function () {{ stop(); step(-1); }});
  document.getElementById('btn-all').addEventListener('click', function () {{ stop(); i = STEPS[fig].length; paint(); }});
  play.addEventListener('click', function () {{ timer ? stop() : start(); }});
  document.addEventListener('keydown', function (ev) {{
    if (ev.target.tagName === 'INPUT' || ev.target.tagName === 'TEXTAREA') return;
    if (ev.key === ' ') {{ ev.preventDefault(); timer ? stop() : start(); }}
    else if (ev.key === 'ArrowRight') {{ stop(); step(1); }}
    else if (ev.key === 'ArrowLeft') {{ stop(); step(-1); }}
    else if (ev.key === '1' || ev.key === '2' || ev.key === '3') setFig('abc'[Number(ev.key) - 1]);
    else if (ev.key === 'v' || ev.key === 'V') voiceBtn.click();
  }});
  paint();
}})();
</script>
"""
open(os.path.join(os.path.dirname(__file__), "workflow-v3-walkthrough.html"), "w", encoding="utf-8").write(page)
print("written", len(page))
