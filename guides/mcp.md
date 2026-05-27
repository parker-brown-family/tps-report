# TPS Report — MCP Server Setup

Expose `tps-report` as an MCP (Model Context Protocol) tool so any  
MCP-compatible client can call it — Claude Desktop, Cursor, Zed, Windsurf, etc.

---

## What MCP gives you

MCP is a standard protocol (by Anthropic, now widely adopted) that lets a  
local server expose **tools**, **resources**, and **prompts** to any compatible  
AI client. Once the server is running, the client discovers it automatically —  
no copy-pasting, no per-project setup.

The `tps-report` MCP server exposes:

- one **prompt** — `tps-report` (interview-driven generation, kept for compatibility)
- five **tools** for validation and building (see below)

When the prompt is called, the full skill (interview steps + HTML template) is
injected into the conversation and the AI begins the interview. The tools let
an agent skip the interview and drive the build directly from source material.

See `guides/mcp-build-plan.md` for the design rationale.

---

## Tools

### `get_tps_requirements`

No inputs. Returns the canonical structure:

- `hard_invariants` — 9 must-pass rules (ELI5 present, sections collapsible, etc.)
- `forbidden_strings` — Zero-Placeholder Policy list
- `schema_presets` — 7 preset section lists (`feature_build`, `research_digest`,
  `progress_report`, `database_migration`, `styling_ui_polish`,
  `incident_or_bug_analysis`, `chaos_mode`)
- `ticket_schema` — recommended ticket fields
- `component_examples` — minimal HTML for ELI5, collapsible sections, ticket rows

Call this first when an agent needs to know what to produce.

### `suggest_tps_schema(source_summary, operator_intent?)`

Heuristic preset recommender. Returns:

- `recommended_preset` — one of the seven preset names
- `suggested_sections` — the section list for that preset
- `rationale` — which keywords matched
- `allowed_deviations` — restatement of the rename/merge/drop freedom
- `preset_scores` — keyword-match scores per preset (debug aid)

Example:

```json
{"source_summary": "Add a new checkout flow with UI states"}
// → recommended_preset: "feature_build"

{"source_summary": "Add column, backfill rows, rollback plan"}
// → recommended_preset: "database_migration"
```

### `validate_tps_body(body_html, schema_preset?)`

Returns `{ok, errors, warnings}`.

Errors (hard invariants, block the build):

- missing ELI5
- no top-level `.sec` sections
- top-level section missing `xsec` class
- top-level section not `data-open="false"`
- forbidden placeholder string present

Warnings (coach, do not block):

- `schema_preset` omitted
- suggested section missing for chosen preset
- tickets present but no Gherkin
- tickets present but no `gotcha` field
- report body looks thin
- section title looks generic

### `build_tps_report(content, body_html, output_path, schema_preset?)`

Validates content + body, assembles against `skill/template.html`, writes the
final `.html`, verifies the file exists and is non-empty.

`content` shape:

```json
{
  "title": "Auth Refactor",
  "branch": "feature/auth-v2",
  "pills": ["Active", "2026-05-27", "Chris"],
  "key": "auth-refactor-v1"
}
```

`key` is optional and slug-derived from `title` when omitted.

Returns `{ok, output_path, bytes, report_key, errors, warnings}`. `ok=False`
means nothing was written; check `errors`.

### `build_tps_report_from_files(content_path, body_path, output_path, schema_preset?)`

Same as `build_tps_report` but reads `tps-content.json` and `tps-body.html`
from disk. Useful for the adjacent-file workflow described in
`guides/agent-workflow.md`.

---

## Smoke tests

```bash
python tests/test_mcp_tools.py
```

Covers acceptance criteria across all five tools using `tempfile` so it never
writes outside the test sandbox. The script also exercises the live
`content.json` + `body.html` in the repo root.

---

## Server

The server lives at `mcp/server.py`.

**Install the MCP SDK (one time):**
```bash
pip install mcp
```

**Run:**
```bash
python mcp/server.py
```

The server speaks the MCP stdio transport by default — clients launch it as  
a subprocess automatically from their config.

---

## Client configuration

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`  
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "tps-report": {
      "command": "python",
      "args": ["/absolute/path/to/tps-report/mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop. The `tps-report` prompt will appear in the  
**Prompts** panel. Click it or type `/tps-report` to start.

---

### Cursor

In Cursor settings → **MCP** → **Add server**:

```json
{
  "tps-report": {
    "command": "python",
    "args": ["/absolute/path/to/tps-report/mcp/server.py"]
  }
}
```

Or edit `~/.cursor/mcp.json` directly with the same JSON.

---

### Zed

In `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "tps-report": {
      "command": {
        "path": "python",
        "args": ["/absolute/path/to/tps-report/mcp/server.py"]
      }
    }
  }
}
```

---

### Windsurf / Codeium

In Windsurf settings → **Cascade** → **MCP Servers** → **Add**:

```json
{
  "tps-report": {
    "command": "python",
    "args": ["/absolute/path/to/tps-report/mcp/server.py"]
  }
}
```

---

### Any MCP client (generic)

All MCP clients use the same shape:

```json
{
  "command": "python",
  "args": ["/absolute/path/to/tps-report/mcp/server.py"]
}
```

The transport is stdio. No ports, no auth, no network.

---

## Using a virtualenv (recommended)

```bash
cd tps-report
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install mcp
```

Then point clients at the venv Python:

```json
{
  "command": "/absolute/path/to/tps-report/.venv/bin/python",
  "args": ["/absolute/path/to/tps-report/mcp/server.py"]
}
```

---

## How the server works

`mcp/server.py` registers one prompt and five tools.

- The `tps-report` prompt reads `skill/SKILL.md` at call time and returns it
  as the prompt body. The AI client receives the full interview + HTML
  template and runs the interview exactly as if you had pasted the skill
  manually. Updating `skill/SKILL.md` requires no restart — the file is
  read fresh on each call.
- The tools use `skill/template.html` directly. The template is the canonical
  source; do not copy it into Python.

To extend validation rules or add presets, edit the constants at the top of
`mcp/server.py` (`FORBIDDEN`, `HARD_INVARIANTS`, `SCHEMA_PRESETS`,
`TICKET_SCHEMA`) and re-run `python tests/test_mcp_tools.py`.
