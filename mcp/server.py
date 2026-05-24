#!/usr/bin/env python3
"""TPS Report MCP Server.

Exposes the tps-report skill as a reusable MCP prompt.
Any MCP-compatible client (Claude Desktop, Cursor, Zed, Windsurf, etc.)
can call the 'tps-report' prompt to start an interview-driven
HTML report generation session.

Install:  pip install mcp
Run:      python mcp/server.py
Config:   see guides/mcp.md
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

SKILL_PATH = Path(__file__).parent.parent / "skill" / "SKILL.md"

mcp = FastMCP(
    "tps-report",
    instructions=(
        "Generates self-contained HTML planning reports with four themes "
        "(Dark, Hacker CRT, Olde Tyme, Chalk Flower). "
        "Call the tps-report prompt to begin the interview."
    ),
)


@mcp.prompt(
    name="tps-report",
    description=(
        "Interview-driven generator for a self-contained HTML planning report. "
        "Asks structured questions, then produces a single .html file with "
        "four themes, an inline comment system, and a Big Copy button. "
        "Zero dependencies — open in any browser."
    ),
)
def tps_report_prompt() -> str:
    """Return the full skill definition: interview steps + HTML template."""
    return SKILL_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
