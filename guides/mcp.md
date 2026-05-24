# TPS Report — MCP Server Setup

Expose `tps-report` as an MCP (Model Context Protocol) tool so any  
MCP-compatible client can call it — Claude Desktop, Cursor, Zed, Windsurf, etc.

---

## What MCP gives you

MCP is a standard protocol (by Anthropic, now widely adopted) that lets a  
local server expose **tools**, **resources**, and **prompts** to any compatible  
AI client. Once the server is running, the client discovers it automatically —  
no copy-pasting, no per-project setup.

The `tps-report` MCP server exposes one **prompt**: `tps-report`.  
When a client calls it, the full skill (interview steps + HTML template) is  
injected into the conversation and the AI begins the interview.

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

`mcp/server.py` reads `skill/SKILL.md` at call time and returns it as the  
prompt body. The AI client receives the full interview + HTML template and  
runs the interview exactly as if you had pasted the skill manually.

To update the skill — change `skill/SKILL.md`. No server restart needed  
(the file is read fresh on each prompt call).
