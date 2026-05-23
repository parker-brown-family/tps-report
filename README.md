# tps-report

> Did you get the memo?

A tool for generating styled, interactive HTML planning reports.

## What it produces

A single self-contained .html file with:

- **Three themes** - Dark (default), Hacker (CRT phosphor), Olde Tyme (parchment)
- **Inline comment system** - click any block to annotate; comments persist in localStorage
- **Big Copy button** - dumps the full report + comments as plain text to clipboard
- **No dependencies** - zero npm, zero build step; open in a browser and go

## Themes

| Theme | Vibe |
|---|---|
| dark | Clean dark-mode dashboard |
| hacker | Pip-Boy CRT - phosphor glow, scanlines, barrel distortion, tracking sweep |
| olde | Parchment and ink - medieval serif headers, warm callouts |

## Usage

1. Run the agent skill: skill/skill.md
2. Answer the interview (project name, branch, sections)
3. Open the generated HTML in a browser

Or: copy example/tps-report.html, gut the content sections, fill in your own.

## File layout

    tps-report/
      example/
        tps-report.html   -- working demo with placeholder content
      skill/
        skill.md          -- agent skill: interview -> generate report HTML
      README.md

## Profile

Owned by parker-brown-family. Repo: https://github.com/parker-brown-family/tps-report
