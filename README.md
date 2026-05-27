# tps-report

> Did you get the memo?

A tool for generating styled, interactive HTML planning reports.

## ELI5

You ask an AI to make a planning document. You get a polished, self-contained `.html` file — four themes, collapsible sections, inline comments, a copy-all button. No server, no build step, no dependencies. Open it in any browser, click around, annotate, share.

**[Live demo →](https://htmlpreview.github.io/?https://github.com/parker-brown-family/tps-report/blob/main/example/tps-report.html)**

| | How | Best for |
|---|---|---|
| **MCP tools** | Register the server, then call `build_tps_report(...)` | Claude Code, Codex, Augment — structured, validated, guided |
| **Builder script** | Write two small files, run `bun skill/build.ts` | Any shell-capable agent or CI pipeline |
| **Prompt only** | Load `skill/SKILL.md` as a system prompt | Custom GPTs, Cursor, Claude Desktop, any LLM |

## What it produces

A single self-contained .html file with:

- **Four themes** — Dark (default), Hacker (CRT phosphor), Olde Tyme (parchment), Chalk Flower
- **Inline comment system** — click any block to annotate; comments persist in localStorage
- **Big Copy button** — dumps the full report + comments as plain text to clipboard
- **No dependencies** — zero npm, zero build step; open in a browser and go

## Themes

| Theme | Vibe |
|---|---|
| dark | Clean dark-mode dashboard |
| hacker | Pip-Boy CRT — phosphor glow, scanlines, barrel distortion, tracking sweep |
| olde | Parchment and ink — medieval serif headers, warm callouts |
| chalk | Handwritten chalk-card planning board |

## Usage

Three paths — pick the one that fits your setup.

### Path A — MCP tools (best: structured, validated, guided)

If you have registered the `tps-report` MCP server (Claude Code, Codex, Augment), the tools are available immediately:

```
get_tps_requirements      → what the build expects
suggest_tps_schema(...)   → recommend a section preset from source material
validate_tps_body(...)    → check body HTML before building
build_tps_report(...)     → assemble and write the final .html file
```

See `guides/mcp.md` for tool reference and registration instructions.

### Path B — Builder script (shell access required)

Write two small files, then run the builder. No MCP needed.

```bash
# 1. Write tps-content.json  (title, branch, pills, key)
# 2. Write tps-body.html     (section <div> blocks only)
bun /path/to/tps-report/skill/build.ts content.json body.html output.html
```

See `guides/agent-workflow.md` for the full contract.

### Path C — Prompt only (no shell, no MCP)

Load `skill/SKILL.md` as a system prompt or skill in any AI assistant.
The skill conducts an interview and generates the full HTML inline.
Works with Custom GPTs, raw system-prompt agents, and any LLM that accepts instructions.

See `guides/slash-command.md` for per-platform setup (Augment, Claude Desktop, Cursor, OpenAI, etc.).

## File layout

    tps-report/
      .claude-plugin/
        plugin.json        -- Claude Code plugin manifest
        marketplace.json   -- marketplace listing
      example/
        tps-report.html    -- demo file (all four themes, placeholder content)
      mcp/
        server.py          -- MCP server: 5 tools + tps-report prompt
      skill/
        SKILL.md           -- agent skill: interview → generate report HTML
        build.ts           -- Bun builder script (Path B)
        template.html      -- canonical HTML template (single source of truth)
      tests/
        test_mcp_tools.py  -- smoke tests for all MCP tool behaviors
      guides/
        agent-workflow.md  -- execution contract for shell-capable agents
        mcp.md             -- MCP tool reference and registration
        mcp-build-plan.md  -- design rationale for the MCP surface
        slash-command.md   -- per-platform slash command setup

