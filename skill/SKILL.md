---
name: tps-report
description: Generate a self-contained HTML planning report. Use when asked to create a TPS report, planning doc, or HTML design report. Conducts a short interview, then produces a single .html file with 4 themes (Dark, Hacker CRT, Olde Tyme, Chalk Flower), inline comments, expandable sections, and a Big Copy button. Zero dependencies — open in any browser.
license: MIT
---

# Skill: Generate TPS Report

**Purpose:** Produce a single self-contained HTML planning report with four themes (Dark, Hacker CRT, Olde Tyme, Chalk Flower), expandable sections, an inline comment system, and a Big Copy button.

---

## When to use this skill

Run when the operator says:
- "make a TPS report for [project]"
- "generate a planning report"
- "I need an HTML report for [topic]"

---

## Step 1 — Interview (gather inputs)

Ask all of the following in a single message. Do not ask one at a time.

1. **Project name** — what goes in the H1 title? (e.g. "Auth Refactor")
2. **Branch name** — the git branch this report is for
3. **Status pills** — up to 3 short labels for the header pills (e.g. "Active", "2026-05-22", "Chris")
4. **Problem statement** — one paragraph: what is broken or missing?
5. **Proposed design** — one paragraph: what is the solution approach?
6. **Code snippet** (optional) — a YAML or code block to embed in the design section
7. **Tradeoffs** — what did you NOT do, and why?
8. **Downstream risks** — list the highest-risk files
9. **Tickets** — list of tickets: ID + title + priority (high / medium / low)
10. **Open questions** — 1–3 unresolved questions

If the operator says "skip" or leaves something blank, use the placeholder text from the **HTML Template** section below.

---

## Step 2 — Generate the HTML

Use the **HTML Template** section below as the structural and CSS template.

**Replace placeholders:**
- `[Project Name]` → answer 1
- `[branch-name]` → answer 2
- Status pills → answer 3
- Problem Statement section → answer 4
- Proposed Design section → answers 5, 6, 7
- Considerations section → answer 8
- Tickets section → answer 9
- Open Questions section → answer 10

**Do NOT modify:**
- Any CSS (all four themes, CRT effects, Pip-Boy copy button, chalk SVG filter)
- The comment system JavaScript
- The Big Copy logic
- The theme toggle buttons

---

## Expandable sections

Any `.sec` can be made collapsible by adding the `xsec` class, a `data-open` attribute, and wrapping the body content in `.xbody`:

```html
<div class="sec xsec" data-open="true">
  <div class="stitle xhdr" onclick="toggleXSec(this)">
    <span class="xtrig">&#x25BC;</span> Section Title
  </div>
  <div class="xbody">
    <!-- section content here -->
  </div>
</div>
```

- `data-open="true"` — starts expanded (default)
- `data-open="false"` — starts collapsed
- The `&#x25BC;` triangle rotates 90° when collapsed (CSS handles it)
- Big Copy captures content regardless of collapsed state

---

## Expandable rows (inline detail, with comment preserved)

A `.trow.commentable` can have an expand arrow that reveals verbose detail **without** triggering the comment modal. The two interactions coexist because the arrow calls `e.stopPropagation()`, which stops the click from bubbling up to the `.commentable` listener.

```html
<div class="trow expandable commentable" data-id="ticket-1" data-title="Ticket 1" data-open="false">
  <span class="hint-tip">&#x1F4AC; comment</span>
  <div class="trow-hdr">
    <button class="texp" onclick="toggleTicket(this,event)" title="Expand details">&#x25B6;</button>
    <div class="tid">T-001</div>
    <div class="ttl">Ticket title</div>
    <span class="bdg bh">high</span>
  </div>
  <div class="trow-body">
    <!-- verbose detail: description, acceptance criteria, files, estimate, etc. -->
  </div>
</div>
```

**How the two clicks stay separate:**

| Target clicked | Fires |
|---|---|
| `button.texp` | `toggleTicket` → `e.stopPropagation()` — row expands, modal stays closed |
| Anywhere else on `.trow` | `.commentable` listener → comment modal opens, expand state unchanged |

**JS:**
```js
function toggleTicket(btn, e) {
  e.stopPropagation();                          // prevents .commentable from firing
  const row = btn.closest('.trow');
  row.dataset.open = row.dataset.open === 'true' ? 'false' : 'true';
}
```

**Key CSS classes:**
- `.trow.expandable` — switches the row to `flex-direction:column`
- `.trow-hdr` — the always-visible top line (arrow + ID + title + badge)
- `.trow-body` — hidden by default; `display:block` when `[data-open="true"]`
- `.texp` — the arrow button; rotates 90° via CSS when `[data-open="true"]`

**Rule:** Never put a `.commentable` inside another `.commentable`. The expand arrow pattern is the correct solution when you need a nested action — it stays outside the comment system entirely and blocks propagation explicitly.

---

## Chalk Flower theme

The 🌸 button activates the **chalk** theme. Key characteristics:
- **Font**: Caveat (handwritten, from Google Fonts — already imported)
- **Palette**: warm cream background, pastel callout fills (yellow, lavender, mint), rose-pink accent
- **Chalk stroke effect**: inline SVG `<filter id="chalk-rough">` using `feTurbulence` + `feDisplacementMap` — applied via CSS `filter: url(#chalk-rough)` on cards and callouts
- **Copy button**: soft gradient rose-pink, rounded pill, Caveat font

The SVG filter element must be present in the `<body>` (before `.page`) for the chalk filter to work:

```html
<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0"
     style="position:absolute;overflow:hidden" aria-hidden="true">
  <defs>
    <filter id="chalk-rough" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" seed="5" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="1"
        xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>
```

**Storage key:** Change `tps-report-v1` to `<project-slug>-v1` so comments don't bleed across reports.

**Output file:** `<project-slug>.html` in the location the operator specifies.

---

## Step 3 — Deliver

1. Write the file.
2. Tell the operator the path.
3. Suggest: "Open in a browser. Default theme is Hacker. Click any block to comment. Big Copy exports everything."

---

## Rules

- One file, no dependencies, no build step — all CSS and JS inline.
- Never strip the CRT/theme code or the chalk SVG filter. They are the whole point.
- The localStorage key must be unique per report to prevent comment bleed.
- Comments are browser-local. Remind the operator if they ask about sharing with others.
- Expandable sections: Big Copy always captures collapsed content. Do not rely on visual state.

---

## HTML Template

Copy this file verbatim, then replace placeholders as described in Step 2.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>TPS Report</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=VT323&family=Uncial+Antiqua&family=Caveat:wght@400;600;700&display=swap');
:root,[data-theme="dark"]{--bg:#0f1117;--s1:#1a1d27;--s2:#22263a;--bd:#2e3350;--ac:#5b7fff;--acd:#1e2a5e;--gr:#3dd68c;--yw:#f5c542;--rd:#ff6b6b;--mu:#8891b4;--tx:#dde1f0;--td:#9aa0bd;--rev-bg:#2a1f00;--rev-bd:#f5c542;--rev-glow:rgba(245,197,66,.45);--font-body:"Inter","Segoe UI",system-ui,sans-serif;--font-mono:"JetBrains Mono","Fira Code",monospace}
[data-theme="hacker"]{--bg:#08140c;--s1:#0f2216;--s2:#0d1a0d;--bd:#1a4a2a;--ac:#00ff9c;--acd:#0a2a15;--gr:#00ff9c;--yw:#adff2f;--rd:#ff4444;--mu:#2a7a4a;--tx:#00ff9c;--td:#00c070;--rev-bg:#0a2a15;--rev-bd:#00ff9c;--rev-glow:rgba(0,255,156,.5);--font-body:"VT323",monospace;--font-mono:"VT323",monospace}
[data-theme="olde"]{--bg:#f4ead5;--s1:#ede0c4;--s2:#e4d4ae;--bd:#b89a6a;--ac:#8b1a1a;--acd:#f9e8d0;--gr:#4a7a2a;--yw:#c8860a;--rd:#9b1515;--mu:#7a6040;--tx:#2c1a0a;--td:#5a4020;--rev-bg:#faf0d8;--rev-bd:#8b1a1a;--rev-glow:rgba(139,26,26,.25);--font-body:Georgia,"Times New Roman",serif;--font-mono:"Courier New","Courier",monospace}
[data-theme="chalk"]{--bg:#fdf9f2;--s1:#fff5e8;--s2:#fde8d0;--bd:#e0bfa0;--ac:#c85080;--acd:#fce8f0;--gr:#68b878;--yw:#e8b030;--rd:#d84848;--mu:#9a7090;--tx:#362030;--td:#6e4a58;--rev-bg:#fde8f0;--rev-bd:#c85080;--rev-glow:rgba(200,80,128,.3);--font-body:"Caveat",cursive;--font-mono:"Courier New","Courier",monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--tx);font:16px/1.65 var(--font-body);padding:40px 24px 100px}
.page{max-width:940px;margin:0 auto;position:relative}
.header{border-bottom:1px solid var(--bd);padding-bottom:24px;margin-bottom:32px}
.header h1{font-size:25px;font-weight:700;color:#fff;letter-spacing:-.3px}
.branch{display:inline-flex;align-items:center;gap:6px;background:var(--acd);color:var(--ac);font:14px "JetBrains Mono","Fira Code",monospace;padding:3px 10px;border-radius:4px;margin-top:8px}
.meta{display:flex;gap:12px;margin-top:14px;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:6px;background:var(--s2);border:1px solid var(--bd);border-radius:20px;padding:4px 12px;font-size:14px;color:var(--td)}
.dot{width:7px;height:7px;border-radius:50%}.dg{background:var(--gr)}.dy{background:var(--yw)}.dr{background:var(--rd)}
.sec{margin-bottom:36px}
.stitle{font-size:21px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:var(--mu);margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid var(--bd)}
.sgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.sc{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:16px}
.lbl{font-size:13px;color:var(--mu);text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px}
table{width:100%;border-collapse:collapse;font-size:15px}
th{background:var(--s2);color:var(--mu);text-align:left;font-size:13px;font-weight:600;letter-spacing:.6px;text-transform:uppercase;padding:10px 14px;border-bottom:1px solid var(--bd)}
td{padding:11px 14px;border-bottom:1px solid var(--bd);vertical-align:top;color:var(--tx)}
tr:last-child td{border-bottom:none}
.tw{border:1px solid var(--bd);border-radius:8px;overflow:hidden}
.bdg{display:inline-block;padding:2px 8px;border-radius:4px;font-size:13px;font-weight:600}
.bm{background:#1a3a5e;color:#7eb8f7}.br{background:#2a3a2a;color:#6fcc88}.bt{background:#2e2a1a;color:#d4a84b}
.bh{background:#3a1a1a;color:#f78080}.bmd{background:#2e2a12;color:#d4b04b}.bk{background:var(--s2);color:var(--mu)}
pre{background:var(--s2);border:1px solid var(--bd);border-radius:6px;padding:16px;font-family:"JetBrains Mono","Fira Code",monospace;font-size:14px;line-height:1.6;overflow-x:auto;color:#c9d1f5}
code{font-family:"JetBrains Mono","Fira Code",monospace;font-size:14px;background:var(--s2);padding:1px 5px;border-radius:3px;color:#a8b8f0}
.cal{border-left:3px solid;border-radius:0 6px 6px 0;padding:14px 16px;margin-bottom:12px;font-size:15px}
.cw{border-color:var(--yw);background:#1f1c0e}.ci{border-color:var(--ac);background:#101826}.cn{border-color:var(--mu);background:var(--s1)}
.cal .ct{font-weight:700;margin-bottom:4px;font-size:14px}
.cw .ct{color:var(--yw)}.ci .ct{color:var(--ac)}.cn .ct{color:var(--mu)}
.tbox{border:1px solid var(--bd);border-radius:8px;overflow:hidden;background:var(--s1)}
.trow{display:flex;align-items:flex-start;gap:12px;padding:12px 16px;border-bottom:1px solid var(--bd)}
.trow:last-child{border-bottom:none}
.trow.expandable{flex-direction:column;gap:0}
.trow-hdr{display:flex;align-items:flex-start;gap:12px;width:100%}
.texp{background:none;border:none;color:var(--mu);cursor:pointer;font-size:11px;padding:2px 2px;border-radius:3px;transition:transform .2s;flex-shrink:0;margin-top:3px;line-height:1}
.texp:hover{color:var(--ac)}
.trow[data-open="true"] .texp{transform:rotate(90deg)}
.trow-body{display:none;padding:10px 0 2px calc(78px + 12px + 18px);font-size:14px;line-height:1.65;color:var(--td)}
.trow[data-open="true"] .trow-body{display:block}
.trow-body .tbfield{margin-bottom:8px}
.trow-body .tblabel{font-size:12px;color:var(--mu);font-weight:600;letter-spacing:.04em;text-transform:uppercase;margin-bottom:3px}
.trow-body .tbfiles{font-family:"JetBrains Mono","Fira Code",monospace;font-size:12px;color:var(--ac);line-height:1.8}
.tid{font-family:"JetBrains Mono","Fira Code",monospace;font-size:13px;color:var(--mu);white-space:nowrap;padding-top:2px;min-width:78px}
.ttl{font-size:15px;flex:1}
.olist{list-style:none;counter-reset:s}
.olist li{counter-increment:s;display:flex;align-items:flex-start;gap:12px;padding:8px 0;color:var(--td);font-size:15px}
.olist li::before{content:counter(s);min-width:22px;height:22px;border-radius:50%;background:var(--acd);color:var(--ac);font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.qbox{background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:16px;margin-bottom:12px}
.qnum{font-size:13px;color:var(--ac);font-weight:700;margin-bottom:6px}
.qtxt{font-size:15px}.qctx{font-size:14px;color:var(--td);margin-top:6px;line-height:1.5}
.commentable{cursor:pointer;position:relative;transition:outline .1s}
.commentable:hover{outline:1px solid var(--ac);border-radius:4px}
.cmtablerow{cursor:pointer}
.cmtablerow:hover td{background:#1a2040}
.hint-tip{display:none;position:absolute;bottom:-24px;right:0;font-size:12px;color:var(--ac);background:var(--acd);padding:2px 8px;border-radius:4px;white-space:nowrap;z-index:10;pointer-events:none}
.commentable:hover .hint-tip,.cmtablerow:hover .hint-tip{display:block}
dialog#cm{background:var(--s1);border:1px solid var(--bd);border-radius:10px;color:var(--tx);padding:0;max-width:540px;width:90vw;box-shadow:0 20px 60px rgba(0,0,0,.6)}
dialog#cm::backdrop{background:rgba(0,0,0,.72)}
.mh{display:flex;align-items:flex-start;justify-content:space-between;padding:20px 24px 14px;border-bottom:1px solid var(--bd)}
.mh h3{font-size:16px;font-weight:700;color:#fff;flex:1;margin-right:12px;line-height:1.4}
.mclose{background:none;border:none;color:var(--mu);font-size:23px;cursor:pointer;line-height:1;padding:0}
.mclose:hover{color:var(--tx)}
.mclist{padding:16px 24px;max-height:240px;overflow-y:auto}
.nocom{color:var(--td);font-size:15px;font-style:italic}
.citem{background:var(--s2);border-radius:6px;padding:12px;margin-bottom:8px}
.citem:last-child{margin-bottom:0}
.cmeta{display:flex;justify-content:space-between;align-items:center;font-size:13px;color:var(--mu);margin-bottom:6px}
.cdel{background:none;border:none;color:var(--mu);cursor:pointer;font-size:15px;line-height:1}
.cdel:hover{color:var(--rd)}
.ctext{font-size:15px;white-space:pre-wrap}
.minput{padding:14px 24px 20px;border-top:1px solid var(--bd)}
#newcomment{width:100%;background:var(--s2);border:1px solid var(--bd);border-radius:6px;color:var(--tx);font:15px "Inter","Segoe UI",sans-serif;padding:10px 12px;resize:vertical;min-height:80px;outline:none}
#newcomment:focus{border-color:var(--ac)}
.mbtns{display:flex;gap:8px;margin-top:10px;justify-content:flex-end}
.btn{padding:7px 18px;border-radius:6px;font-size:15px;font-weight:600;cursor:pointer;border:none}
.bpri{background:var(--ac);color:#fff}.bpri:hover{opacity:.88}
.bsec{background:var(--s2);color:var(--td);border:1px solid var(--bd)}.bsec:hover{color:var(--tx)}
.copybar{position:fixed;bottom:0;left:0;right:0;background:var(--s1);border-top:1px solid var(--bd);padding:12px 32px;display:flex;align-items:center;justify-content:space-between;z-index:100}
.copybar p{font-size:14px;color:var(--td)}
#copybtn{background:var(--gr);color:#0f1117;padding:9px 24px;border-radius:6px;font-size:15px;font-weight:700;cursor:pointer;border:none}
#copybtn:hover{opacity:.9}
[data-theme="hacker"] .copybar{background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='90'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch' seed='9'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .35 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>"),repeating-linear-gradient(0deg,rgba(0,0,0,.18) 0px,rgba(0,0,0,.18) 1px,transparent 1px,transparent 3px),repeating-linear-gradient(90deg,rgba(0,0,0,.12) 0px,rgba(0,0,0,.12) 1px,transparent 1px,transparent 3px),linear-gradient(175deg,#3e3c2a 0%,#2c2b1d 45%,#1c1b12 100%);border-top:4px solid #0a0a06;box-shadow:inset 0 1px 0 rgba(255,200,80,.07),0 -8px 28px rgba(0,0,0,.98);padding:10px 36px;z-index:9999;animation:none!important;filter:none!important}
[data-theme="hacker"] .copybar p{font-family:"Share Tech Mono","Courier New",monospace!important;font-size:11px!important;font-weight:700!important;color:#120e00!important;text-shadow:none!important;letter-spacing:.16em;text-transform:uppercase;background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='280' height='64'><defs><linearGradient id='d' x1='0' y1='0' x2='280' y2='64' gradientUnits='userSpaceOnUse'><stop offset='0' stop-color='white' stop-opacity='0.15'/><stop offset='1' stop-color='white' stop-opacity='0.5'/></linearGradient><mask id='m'><rect width='100%25' height='100%25' fill='url(%23d)'/></mask><filter id='g'><feTurbulence type='fractalNoise' baseFrequency='0.035' numOctaves='4' seed='12' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1.5 -.2'/></filter></defs><rect width='100%25' height='100%25' filter='url(%23g)' mask='url(%23m)'/></svg>"),url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='32'><filter id='g'><feTurbulence type='fractalNoise' baseFrequency='0.15' numOctaves='2' seed='7' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .5 0'/></filter><rect width='100%25' height='100%25' filter='url(%23g)'/></svg>"),linear-gradient(135deg,#b89018 0%,#8a6c14 40%,#6a520e 65%,#44360a 100%);background-blend-mode:multiply,multiply,normal;background-size:100% 100%,50% 50%,100% 100%;padding:8px 18px 7px;border:2px solid #1e1600;box-shadow:inset 0 1px 0 rgba(240,200,60,.15),inset 0 -2px 0 rgba(0,0,0,.7),inset 2px 0 0 rgba(0,0,0,.4),inset -1px 0 0 rgba(0,0,0,.3),0 2px 6px rgba(0,0,0,.75);transform:rotate(-.5deg);max-width:62%;filter:saturate(.7) contrast(1.08)}
[data-theme="hacker"] #copybtn{position:relative;width:64px;height:64px;border-radius:50%;padding:0;border:none;font-size:0!important;cursor:pointer;filter:none!important;text-shadow:none!important;transform:none!important;animation:pip-pulse 2.4s ease-in-out infinite!important;background:radial-gradient(circle at 38% 32%,#ffe566 0%,#e89a00 38%,#b05800 65%,#4a2000 86%,#180a00 100%);box-shadow:0 0 0 4px #1c1a0c,0 0 0 7px #2e2b18,0 0 0 9px #0b0a06,0 0 22px rgba(240,148,0,.82),0 0 44px rgba(200,100,0,.4),inset 0 3px 7px rgba(255,238,120,.48),inset 0 -3px 6px rgba(0,0,0,.88)}
[data-theme="hacker"] #copybtn::before{content:"COPY";position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:"Share Tech Mono","Courier New",monospace;font-size:12px;font-weight:900;color:#1a0d00;letter-spacing:.12em;text-shadow:none}
[data-theme="hacker"] #copybtn:hover{animation:none!important;box-shadow:0 0 0 4px #1c1a0c,0 0 0 7px #2e2b18,0 0 0 9px #0b0a06,0 0 30px rgba(255,168,0,.98),0 0 60px rgba(220,120,0,.65),inset 0 2px 5px rgba(255,250,140,.55),inset 0 -3px 6px rgba(0,0,0,.75)!important;filter:none!important;transform:scale(1.06)!important}
@keyframes pip-pulse{0%,100%{box-shadow:0 0 0 4px #1c1a0c,0 0 0 7px #2e2b18,0 0 0 9px #0b0a06,0 0 22px rgba(240,148,0,.82),0 0 44px rgba(200,100,0,.4),inset 0 3px 7px rgba(255,238,120,.48),inset 0 -3px 6px rgba(0,0,0,.88)}50%{box-shadow:0 0 0 4px #1c1a0c,0 0 0 7px #2e2b18,0 0 0 9px #0b0a06,0 0 32px rgba(255,165,0,.98),0 0 62px rgba(220,110,0,.58),inset 0 3px 7px rgba(255,238,120,.48),inset 0 -3px 6px rgba(0,0,0,.88)}}
@media(max-width:640px){.sgrid{grid-template-columns:1fr 1fr}}
.commentable.has-comment{outline:2px solid var(--rev-bd)!important;background:var(--rev-bg)!important;border-radius:6px;box-shadow:0 0 12px var(--rev-glow),inset 0 0 18px rgba(0,0,0,.12)}
.cmtablerow.has-comment td{background:var(--rev-bg)!important;box-shadow:inset 3px 0 0 var(--rev-bd)}
.cbadge{position:absolute;top:6px;right:8px;border-radius:10px;font-size:12px;font-weight:700;padding:1px 7px;min-width:20px;text-align:center;pointer-events:none;z-index:5}
.has-comment > .cbadge,.has-comment .cbadge{background:var(--rev-bd);color:var(--bg);box-shadow:0 0 6px var(--rev-glow)}
.cmtablerow .cbadge{position:static;display:inline-block;margin-left:6px;vertical-align:middle;background:var(--rev-bd);color:var(--bg)}
.theme-toggle{position:absolute;top:32px;right:24px;display:flex;gap:6px;align-items:center;z-index:200}
.tthm{background:var(--s2);border:1px solid var(--bd);color:var(--tx);border-radius:6px;font-size:21px;width:38px;height:38px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .15s,border-color .15s;line-height:1}
.tthm:hover{background:var(--bd);border-color:var(--ac)}
.tthm.active{background:var(--acd);border-color:var(--ac);box-shadow:0 0 8px var(--rev-glow)}
[data-theme="olde"] .tthm{background:#6b2d2d;border-color:#4a1a1a;color:#f4ead5}
[data-theme="olde"] .tthm:hover{background:#8b3a3a;border-color:#8b1a1a}
[data-theme="olde"] .tthm.active{background:#8b1a1a;border-color:#5a0a0a;box-shadow:0 0 8px rgba(139,26,26,.5)}
[data-theme="hacker"] body{font-size:18px;letter-spacing:.04em;text-shadow:0 0 2px rgba(0,255,156,.38),0 0 6px rgba(0,255,156,.17);animation:flicker .12s infinite}
[data-theme="hacker"] .header h1{font-size:30px;letter-spacing:.08em;text-shadow:0 0 6px rgba(0,255,156,.50),0 0 18px rgba(0,255,156,.27)}
[data-theme="hacker"] .stitle{letter-spacing:.25em;text-shadow:0 0 5px rgba(0,255,156,.27)}
[data-theme="hacker"] pre,[data-theme="hacker"] code{color:var(--ac);border-color:var(--bd);text-shadow:0 0 4px rgba(0,255,156,.32)}
[data-theme="hacker"] .trow,.hacker .sc,[data-theme="hacker"] .qbox{box-shadow:0 0 4px rgba(0,255,156,.15),inset 0 0 8px rgba(0,255,156,.04)}
[data-theme="hacker"] body{padding-top:60px!important;padding-bottom:200px!important}
[data-theme="hacker"] .page{border-radius:26px;overflow:hidden;transform-origin:top center;transform:perspective(280px) scale(1.032,1.055);filter:contrast(1.08) brightness(1.05) saturate(1.15);animation:crt-jitter 9s ease-in-out infinite}
[data-theme="hacker"] .bm{background:#0a2a15;color:#00ff9c}[data-theme="hacker"] .bh{background:#2a0a0a;color:#ff6666}
[data-theme="hacker"] .br{background:#0a2a15;color:#adff2f}[data-theme="hacker"] .bt,[data-theme="hacker"] .bmd{background:#0a1a0a;color:#adff2f}
[data-theme="hacker"] .bk{background:#0d1a0d;color:#2a7a4a}
#crt-scanlines,#crt-vignette,#crt-tracking{display:none;position:fixed;inset:0;pointer-events:none}
[data-theme="hacker"] #crt-scanlines{display:block;z-index:997;background:repeating-linear-gradient(to bottom,rgba(0,0,0,.55) 0px,rgba(0,0,0,.55) 2px,transparent 2px,transparent 4px);opacity:.12;mix-blend-mode:multiply}
[data-theme="hacker"] #crt-vignette{display:block;z-index:996;background:radial-gradient(ellipse at center,transparent 28%,rgba(0,0,0,.5) 68%,rgba(0,0,0,.92) 100%)}
[data-theme="hacker"] #crt-tracking{display:block;z-index:998;overflow:hidden}
[data-theme="hacker"] #crt-tracking::before{content:"";position:absolute;left:0;width:100%;height:160px;background:linear-gradient(to bottom,transparent,rgba(0,255,156,.06),transparent);animation:tracking 7s linear infinite}
[data-theme="hacker"] #crt-tracking::after{content:"";position:absolute;left:0;width:100%;height:160px;background:repeating-linear-gradient(to bottom,rgba(0,0,0,.55) 0px,rgba(0,0,0,.55) 2px,transparent 2px,transparent 4px);mask-image:linear-gradient(to bottom,transparent 0%,black 25%,black 75%,transparent 100%);-webkit-mask-image:linear-gradient(to bottom,transparent 0%,black 25%,black 75%,transparent 100%);opacity:.3;mix-blend-mode:multiply;animation:tracking 7s linear infinite}
@keyframes flicker{0%{opacity:.96}50%{opacity:1}100%{opacity:.97}}
@keyframes tracking{from{transform:translateY(-220px)}to{transform:translateY(105vh)}}
@keyframes crt-jitter{0%{transform:perspective(280px) scale(1.032,1.055) translateX(0)}96%{transform:perspective(280px) scale(1.032,1.055) translateX(0)}97%{transform:perspective(280px) scale(1.032,1.055) translateX(-1px)}98.5%{transform:perspective(280px) scale(1.032,1.055) translateX(1px)}100%{transform:perspective(280px) scale(1.032,1.055) translateX(0)}}
[data-theme="olde"] .header h1{color:var(--ac);font-family:'Uncial Antiqua',Georgia,serif!important}
[data-theme="olde"] .stitle,[data-theme="olde"] h2,[data-theme="olde"] h3{font-family:'Uncial Antiqua',Georgia,serif!important;color:var(--ac)}
[data-theme="olde"] .mh h3{color:var(--ac)}
[data-theme="olde"] .cw{background:#fef5d8;border-color:#c8860a}[data-theme="olde"] .ci{background:#f0e8d8;border-color:#7a5a2a}
[data-theme="olde"] .cw .ct{color:#8a5a00}[data-theme="olde"] .ci .ct{color:#5a3a10}[data-theme="olde"] .cn .ct{color:#5a4020}
[data-theme="olde"] .bm{background:#d0e4f8;color:#1a3a6e}[data-theme="olde"] .bh{background:#fce0e0;color:#7a1010}
[data-theme="olde"] .br{background:#d8f0d8;color:#2a5a2a}[data-theme="olde"] .bt{background:#fef0d0;color:#7a4a00}
[data-theme="olde"] .bmd{background:#fef8d0;color:#6a4800}[data-theme="olde"] .bk{background:#e8dcc8;color:#5a4020}
[data-theme="olde"] pre{color:var(--tx);background:#e8dcc8;border-color:var(--bd)}
[data-theme="olde"] code{color:#6b2d2d;background:#ede0c4;border-radius:3px}
[data-theme="olde"] .cmtablerow:hover td{background:#f0e8d0}
[data-theme="olde"] dialog#cm{background:var(--s1);border-color:var(--bd)}
[data-theme="olde"] #copybtn{background:var(--ac);color:#fff}
/* ── expandable sections ── */
.xhdr{cursor:pointer;user-select:none;display:flex!important;align-items:center;gap:8px;padding:10px 0;margin-bottom:14px}
.xhdr:hover{color:var(--ac)}
.xtrig{display:inline-block;flex-shrink:0;font-size:14px;color:var(--ac);opacity:.75;transition:transform .25s ease}
.xsec[data-open="false"] .xtrig{transform:rotate(-90deg)}
.xbody{overflow:hidden;transition:max-height .35s ease,opacity .25s ease;max-height:4000px;opacity:1}
.xsec[data-open="false"] .xbody{max-height:0;opacity:0;pointer-events:none}
/* ── chalk flower theme ── */
[data-theme="chalk"] body{font-size:21px;background:radial-gradient(ellipse at 25% 0%,#fff9e0 0%,#fdf6f0 45%,#faf2ee 100%)}
[data-theme="chalk"] .header h1{font-family:'Caveat',cursive!important;font-size:41px;font-weight:700;color:var(--ac);text-shadow:1px 2px 4px rgba(200,80,128,.15)}
[data-theme="chalk"] .stitle{font-family:'Caveat',cursive!important;font-size:26px;font-weight:700;text-transform:none;letter-spacing:.02em;color:var(--ac);border-bottom:3px solid var(--ac);padding-bottom:6px}
[data-theme="chalk"] .lbl{font-family:'Caveat',cursive;font-size:16px;letter-spacing:.03em}
[data-theme="chalk"] .sc{filter:url(#chalk-rough)}
[data-theme="chalk"] .cal{filter:url(#chalk-rough)}
[data-theme="chalk"] .qbox{filter:url(#chalk-rough)}
[data-theme="chalk"] .cw{background:#fffbe0;border-color:#e8c048;border-width:2px}
[data-theme="chalk"] .cw .ct{color:#a87800}
[data-theme="chalk"] .ci{background:#ede8ff;border-color:#9070d0;border-width:2px}
[data-theme="chalk"] .ci .ct{color:#5840a0}
[data-theme="chalk"] .cn{background:#e8f8f0;border-color:#58b870;border-width:2px}
[data-theme="chalk"] .cn .ct{color:#2a7040}
[data-theme="chalk"] .bm{background:#dde8ff;color:#2f50a8}[data-theme="chalk"] .bh{background:#fde0e0;color:#a02020}
[data-theme="chalk"] .br{background:#d8f0e0;color:#2a7040}[data-theme="chalk"] .bt{background:#fef8d0;color:#806000}
[data-theme="chalk"] .bmd{background:#fff0d0;color:#906000}[data-theme="chalk"] .bk{background:#f0e8e0;color:#7a5050}
[data-theme="chalk"] pre{background:#f0e8d8;border-color:#d4b890;color:#3a2030}
[data-theme="chalk"] code{background:#f0e8d8;color:#a03060}
[data-theme="chalk"] .tthm{background:#f0e4dc;border-color:#d4b098;color:#6a3848}
[data-theme="chalk"] .tthm:hover{background:#fce0ec;border-color:var(--ac)}
[data-theme="chalk"] .tthm.active{background:var(--acd);border-color:var(--ac);box-shadow:0 0 8px var(--rev-glow)}
[data-theme="chalk"] .cmtablerow:hover td{background:#fde8f0}
[data-theme="chalk"] dialog#cm{background:var(--s1);border-color:var(--bd)}
[data-theme="chalk"] .mh h3{color:var(--ac)}
[data-theme="chalk"] .copybar{background:#fdf4ec;border-top-color:var(--bd)}
[data-theme="chalk"] #copybtn{background:linear-gradient(135deg,#d85888,#b03868);color:#fff;border-radius:24px;font-family:'Caveat',cursive;font-size:22px;font-weight:700;padding:9px 26px;box-shadow:0 4px 14px rgba(176,56,100,.35)}
[data-theme="chalk"] #copybtn:hover{opacity:.9;transform:scale(1.04)}
[data-theme="chalk"] .branch{font-family:'Caveat',cursive;font-size:17px}
[data-theme="chalk"] .xtrig{color:var(--ac)}
</style>
</head>
<body>
<div id="crt-scanlines"></div>
<div id="crt-vignette"></div>
<div id="crt-tracking"></div>
<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute;overflow:hidden" aria-hidden="true">
  <defs>
    <filter id="chalk-rough" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" seed="5" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="1" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>
<div class="page">

<div class="theme-toggle" id="theme-toggle">
  <button class="tthm active" id="btn-dark"   onclick="setTheme('dark')"   title="Dark">&#x1F319;</button>
  <button class="tthm"        id="btn-hacker" onclick="setTheme('hacker')" title="Hacker" style="font-family:monospace;font-size:15px;font-weight:700;letter-spacing:-1px">/&gt;</button>
  <button class="tthm"        id="btn-olde"   onclick="setTheme('olde')"   title="Olde Tyme">&#x1F4DC;</button>
  <button class="tthm"        id="btn-chalk"  onclick="setTheme('chalk')"  title="Chalk Flower">&#x1F338;</button>
</div>

<div class="header" style="position:relative">
  <h1>TPS Report &#x2014; [Project Name]</h1>
  <div class="branch">&#x2387; [branch-name]</div>
  <div class="meta">
    <div class="pill"><span class="dot dg"></span>Status: Active</div>
    <div class="pill"><span class="dot dy"></span>[Date]</div>
    <div class="pill"><span class="dot dr"></span>[Owner]</div>
  </div>
</div>

<div class="sec xsec" data-open="true">
  <div class="stitle xhdr" onclick="toggleXSec(this)"><span class="xtrig">&#x25BC;</span> Project Summary</div>
  <div class="xbody">
  <div class="sgrid">
    <div class="sc commentable" data-id="summary-stack" data-title="Stack">
      <span class="hint-tip">&#x1F4AC; comment</span>
      <div class="lbl">Stack</div>
      <div>Replace with your tech stack.</div>
    </div>
    <div class="sc commentable" data-id="summary-scope" data-title="Scope">
      <span class="hint-tip">&#x1F4AC; comment</span>
      <div class="lbl">Scope</div>
      <div>One-sentence scope. What does this change affect?</div>
    </div>
    <div class="sc commentable" data-id="summary-risk" data-title="Risk Level">
      <span class="hint-tip">&#x1F4AC; comment</span>
      <div class="lbl">Risk Level</div>
      <div><span class="bdg bmd">Medium</span> &#x2014; Replace with your assessment.</div>
    </div>
  </div>
  </div>
</div>

<div class="sec xsec" data-open="true">
  <div class="stitle xhdr" onclick="toggleXSec(this)"><span class="xtrig">&#x25BC;</span> 1 &#x2014; Problem Statement</div>
  <div class="xbody">
  <div class="cal cw commentable" data-id="problem-core" data-title="Core Problem">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="ct">What is broken / missing</div>
    Describe the current state and why it is insufficient. Name files, functions, or user-visible symptoms.
  </div>
  <div class="cal ci commentable" data-id="problem-impact" data-title="Impact">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="ct">Impact if unaddressed</div>
    Who is affected? What breaks downstream?
  </div>
  <div class="cal cn commentable" data-id="problem-scope" data-title="Out of Scope">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="ct">Explicitly out of scope</div>
    List adjacent problems this report does NOT address.
  </div>
  </div>
</div>

<div class="sec xsec" data-open="true">
  <div class="stitle xhdr" onclick="toggleXSec(this)"><span class="xtrig">&#x25BC;</span> 2 &#x2014; Proposed Design</div>
  <div class="xbody">
  <div class="cal ci commentable" data-id="design-approach" data-title="Approach">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="ct">APPROACH</div>
    One paragraph describing the solution strategy.
  </div>
<pre>
# Example code snippet (replace with your own)
entity_type: municipality
parent_region: null
</pre>
  <div style="margin-top:14px" class="cal cn commentable" data-id="design-tradeoffs" data-title="Tradeoffs">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="ct">Tradeoffs &amp; alternatives considered</div>
    What did you not do, and why?
  </div>
  </div>
</div>

<div class="sec xsec" data-open="true">
  <div class="stitle xhdr" onclick="toggleXSec(this)"><span class="xtrig">&#x25BC;</span> 3 &#x2014; Considerations</div>
  <div class="xbody">
  <div class="cal cw commentable" data-id="cons-downstream" data-title="Downstream risk">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="ct">&#x26A0;&#xFE0F; Downstream files at risk</div>
    Highest-risk files that touch this change.
  </div>
  <div class="cal cw commentable" data-id="cons-migration" data-title="Migration risk">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="ct">&#x26A0;&#xFE0F; Data migration notes</div>
    Backward-compatibility concerns.
  </div>
  <div class="cal cn commentable" data-id="cons-testing" data-title="Testing strategy">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="ct">Testing strategy</div>
    Unit tests? Integration tests? Manual smoke test?
  </div>
  </div>
</div>

<div class="sec xsec" data-open="true">
  <div class="stitle xhdr" onclick="toggleXSec(this)"><span class="xtrig">&#x25BC;</span> 4 &#x2014; Tickets</div>
  <div class="xbody">
  <div class="tbox">
    <div class="trow commentable" data-id="ticket-epic" data-title="EPIC">
      <span class="hint-tip">&#x1F4AC; comment</span>
      <div class="tid">EPIC</div>
      <div class="ttl"><strong>EPIC</strong>: [Title of the epic]</div>
      <span class="bdg bh">high</span>
    </div>
    <div class="trow expandable commentable" data-id="ticket-1" data-title="Ticket 1" data-open="false">
      <span class="hint-tip">&#x1F4AC; comment</span>
      <div class="trow-hdr">
        <button class="texp" onclick="toggleTicket(this,event)" title="Expand details">&#x25B6;</button>
        <div class="tid">T-001</div>
        <div class="ttl">SCHEMA: Add new fields to the data model</div>
        <span class="bdg bh">high</span>
      </div>
      <div class="trow-body">
        <div class="tbfield">
          <div class="tblabel">Description</div>
          Replace with ticket description.
        </div>
        <div class="tbfield">
          <div class="tblabel">Acceptance Criteria</div>
          Replace with acceptance criteria.
        </div>
        <div class="tbfield">
          <div class="tblabel">Files Affected</div>
          <div class="tbfiles">path/to/file.ext</div>
        </div>
        <div class="tbfield" style="display:flex;gap:24px">
          <div><div class="tblabel">Estimate</div>? points</div>
          <div><div class="tblabel">Blocks</div>none</div>
          <div><div class="tblabel">Blocked by</div>none</div>
        </div>
      </div>
    </div>
    <div class="trow commentable" data-id="ticket-2" data-title="Ticket 2">
      <span class="hint-tip">&#x1F4AC; comment</span>
      <div class="tid">T-002</div>
      <div class="ttl">Replace with ticket title</div>
      <span class="bdg bmd">medium</span>
    </div>
    <div class="trow commentable" data-id="ticket-3" data-title="Ticket 3">
      <span class="hint-tip">&#x1F4AC; comment</span>
      <div class="tid">T-003</div>
      <div class="ttl">Replace with ticket title</div>
      <span class="bdg bmd">medium</span>
    </div>
  </div>

  <div style="margin-top:24px">
    <div class="stitle">Recommended Execution Order</div>
    <ol class="olist">
      <li class="commentable" data-id="order-1" data-title="Step 1"><span class="hint-tip">&#x1F4AC; comment</span>Step 1 &#x2014; reason</li>
      <li class="commentable" data-id="order-2" data-title="Step 2"><span class="hint-tip">&#x1F4AC; comment</span>Step 2 &#x2014; reason</li>
      <li class="commentable" data-id="order-3" data-title="Step 3"><span class="hint-tip">&#x1F4AC; comment</span>Step 3 &#x2014; reason</li>
    </ol>
  </div>
  </div>
</div>

<div class="sec xsec" data-open="true">
  <div class="stitle xhdr" onclick="toggleXSec(this)"><span class="xtrig">&#x25BC;</span> Open Questions</div>
  <div class="xbody">
  <div class="qbox commentable" data-id="q-1" data-title="Q1">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="qnum">Q1</div>
    <div class="qtxt">Replace with your first open question.</div>
    <div class="qctx">Context: what makes this hard to decide?</div>
  </div>
  <div class="qbox commentable" data-id="q-2" data-title="Q2">
    <span class="hint-tip">&#x1F4AC; comment</span>
    <div class="qnum">Q2</div>
    <div class="qtxt">Replace with your second open question.</div>
    <div class="qctx">Context: who decides this, and by when?</div>
  </div>
  </div>
</div>

</div>

<div class="copybar">
  <p>Click any item to leave a comment. Comments persist in your browser and are included in the copy.</p>
  <button id="copybtn" onclick="bigCopy()">&#x1F4CB; Big Copy</button>
</div>

<dialog id="cm">
  <div class="mh">
    <h3 id="modal-title"></h3>
    <button class="mclose" onclick="closeModal()">&#x2715;</button>
  </div>
  <div class="mclist" id="modal-comments"></div>
  <div class="minput">
    <textarea id="newcomment" placeholder="Add a comment&#x2026; (Ctrl+Enter to save)"></textarea>
    <div class="mbtns">
      <button class="btn bsec" onclick="closeModal()">Done</button>
      <button class="btn bpri" onclick="addComment()">Add Comment</button>
    </div>
  </div>
</dialog>

<script>
const SK = 'tps-report-v1';
let C = JSON.parse(localStorage.getItem(SK) || '{}');
let aid = null;
function save(){ localStorage.setItem(SK, JSON.stringify(C)); }
function esc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>'); }
function renderBadges(){
  document.querySelectorAll('.commentable, .cmtablerow').forEach(el=>{
    const id = el.dataset.id;
    const n = (C[id]||[]).length;
    el.classList.toggle('has-comment', n > 0);
    let b = el.querySelector(':scope > .cbadge');
    if(n > 0){
      if(!b){ b=document.createElement('span'); b.className='cbadge'; el.appendChild(b); }
      b.textContent = '\u2713 '+n;
    } else if(b) b.remove();
  });
}
function renderModalComments(id){
  const list = C[id]||[];
  const el = document.getElementById('modal-comments');
  if(!list.length){ el.innerHTML='<p class="nocom">No comments yet \u2014 add one below.</p>'; return; }
  el.innerHTML = list.map((c,i)=>`
    <div class="citem">
      <div class="cmeta"><span>${esc(c.ts)}</span><button class="cdel" onclick="delComment(${i})">&#x2715;</button></div>
      <div class="ctext">${esc(c.text)}</div>
    </div>`).join('');
}
function openModal(id, title){
  aid=id;
  document.getElementById('modal-title').textContent=title;
  renderModalComments(id);
  document.getElementById('newcomment').value='';
  document.getElementById('cm').showModal();
  setTimeout(()=>document.getElementById('newcomment').focus(),50);
}
function closeModal(){ document.getElementById('cm').close(); aid=null; }
function addComment(){
  const ta=document.getElementById('newcomment');
  const txt=ta.value.trim(); if(!txt) return;
  if(!C[aid]) C[aid]=[];
  C[aid].push({text:txt, ts:new Date().toLocaleString()});
  ta.value=''; save(); renderModalComments(aid); renderBadges();
}
function delComment(i){
  C[aid].splice(i,1); save(); renderModalComments(aid); renderBadges();
}
document.getElementById('newcomment').addEventListener('keydown',e=>{
  if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){ e.preventDefault(); addComment(); }
  if(e.key==='Escape'){ e.preventDefault(); closeModal(); }
});
document.querySelectorAll('.commentable,.cmtablerow').forEach(el=>{
  el.addEventListener('click',e=>{
    if(e.target.closest('.cdel,.mclose,.btn')) return;
    openModal(el.dataset.id, el.dataset.title||el.dataset.id);
  });
});
function itemText(el){
  const clone=el.cloneNode(true);
  clone.querySelectorAll('.hint-tip,.cbadge').forEach(n=>n.remove());
  return clone.textContent.replace(/\s+/g,' ').trim();
}
function toggleXSec(hdr){
  const sec=hdr.closest('.xsec');
  const isOpen=sec.dataset.open!=='false';
  sec.dataset.open=isOpen?'false':'true';
}
function toggleTicket(btn,e){
  e.stopPropagation();
  const row=btn.closest('.trow');
  const isOpen=row.dataset.open==='true';
  row.dataset.open=isOpen?'false':'true';
}
function bigCopy(){
  const lines=[];
  lines.push('# TPS REPORT');
  lines.push('Generated: '+new Date().toLocaleString());
  lines.push('');
  document.querySelectorAll('.sec').forEach(sec=>{
    const t=sec.querySelector('.stitle');
    if(t){const tc=t.cloneNode(true);tc.querySelectorAll('.xtrig').forEach(n=>n.remove());lines.push('\n## '+tc.textContent.trim()+'\n');}
    sec.querySelectorAll('.commentable,.cmtablerow').forEach(el=>{
      lines.push(itemText(el));
      (C[el.dataset.id]||[]).forEach(c=>lines.push('  > ['+c.ts+'] '+c.text));
      if((C[el.dataset.id]||[]).length) lines.push('');
    });
  });
  navigator.clipboard.writeText(lines.join('\n')).then(()=>{
    const btn=document.getElementById('copybtn');
    const orig=btn.textContent;
    btn.textContent='\u2713 Copied!';
    setTimeout(()=>btn.textContent=orig,2200);
  });
}
const TK = 'tps-report-theme';
function setTheme(t){
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem(TK, t);
  document.querySelectorAll('.tthm').forEach(b=>b.classList.remove('active'));
  const btn = document.getElementById('btn-'+t);
  if(btn) btn.classList.add('active');
}
(function initTheme(){ setTheme(localStorage.getItem(TK)||'hacker'); })();
renderBadges();
</script>
</body></html>
```
