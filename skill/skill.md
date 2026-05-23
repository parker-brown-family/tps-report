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

If the operator says "skip" or leaves something blank, use the placeholder text from `example/tps-report.html`.

---

## Step 2 — Generate the HTML

Use `example/tps-report.html` as the structural and CSS template.

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
