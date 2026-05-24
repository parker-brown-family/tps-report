# TPS Report — Slash Command Setup

Using `/tps-report` as a slash command in any AI coding assistant.  
All implementations point at the same source of truth: `skill/SKILL.md`.

---

## How it works

`skill/SKILL.md` contains the full skill definition:
- When to trigger
- The interview questions to ask
- The complete HTML template (CSS, JS, all four themes)

Every platform below is just wiring that file into the right slot.

---

## Augment (native — already works)

Augment reads `skill/SKILL.md` automatically from your workspace.  
Type `/tps-report` in any Augment chat and it will trigger the interview.

Nothing to configure.

---

## Claude Desktop — `/tps-report` command

Claude Desktop supports project-scoped slash commands via `.claude/commands/`.

```bash
mkdir -p .claude/commands
cp skill/SKILL.md .claude/commands/tps-report.md
```

Restart Claude Desktop. Type `/tps-report` in the chat — Claude will load the  
file and begin the interview.

> **Note:** The YAML front matter (`name:`, `description:`) is ignored by  
> Claude Desktop but harmless. The Markdown body is what gets injected.

---

## Cursor — project rule

Cursor supports per-project agent rules via `.cursor/rules/`.

```bash
mkdir -p .cursor/rules
cp skill/SKILL.md .cursor/rules/tps-report.mdc
```

In Cursor Agent chat, type `@tps-report` or reference the rule in your prompt.  
Cursor will prepend the rule content to the agent context.

---

## OpenAI Agents SDK

The [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) (`pip install openai-agents`)  
lets you define an agent with explicit instructions.

```python
from pathlib import Path
from agents import Agent, Runner

skill = Path("skill/SKILL.md").read_text()

tps_agent = Agent(
    name="tps-report",
    instructions=skill,
)

result = Runner.run_sync(tps_agent, "Make a TPS report for the Auth Refactor project")
print(result.final_output)
```

Run with `python your_script.py`. The agent will conduct the interview and  
return the finished HTML.

---

## OpenAI Custom GPT

1. Go to [chat.openai.com/gpts/editor](https://chat.openai.com/gpts/editor)
2. Under **Instructions**, paste the full contents of `skill/SKILL.md`
3. Remove or keep the YAML front matter (GPT builder ignores it)
4. Save and publish (private or public)

Users can then open the GPT and say "make me a TPS report" — the GPT will  
run the interview and produce the HTML.

---

## Any LLM (generic)

For any AI that accepts a system prompt:

1. Copy the contents of `skill/SKILL.md`
2. Paste it as the system prompt (or prepend it to your first message)
3. Then say: "Make a TPS report for [project]"

The skill is self-contained — no tools, no API calls, no external assets.

---

## Keeping it in sync

`skill/SKILL.md` is the single source of truth.  
When the HTML template changes (new themes, CSS tweaks), update `SKILL.md` —  
all downstream platforms pick up the change automatically on next use.
