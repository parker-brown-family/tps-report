# Skill: Generate TPS Report

**Purpose:** Produce a single self-contained HTML planning report with three themes (Dark, Hacker CRT, Olde Tyme), an inline comment system, and a Big Copy button.

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
- Any CSS (all three themes, CRT effects, Pip-Boy copy button)
- The comment system JavaScript
- The Big Copy logic
- The theme toggle buttons

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
- Never strip the CRT/theme code. It is the whole point.
- The localStorage key must be unique per report to prevent comment bleed.
- Comments are browser-local. Remind the operator if they ask about sharing with others.
