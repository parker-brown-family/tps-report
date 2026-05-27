# TPS Report Agent Workflow

This is the workflow for running the TPS skill from a shell-capable coding agent. It is an agent contract for Augment, Claude Code, Cursor, Codex, and similar tools.

## Outcome

Produce one finished, self-contained `.html` TPS report in the operator's requested location.

The deliverable is the report. The skill text is instructions, not content to paste into the source spec.

## Command vs skill

If `/tps-report` appears as both a command and a skill, treat both as the same request: load the TPS instructions and execute them.

Do not recursively tell the operator to "read and follow the skill." Do not append that instruction to a spec unless the operator asks for a handoff note.

## MCP tool workflow (preferred)

If the `tps-report` MCP server is registered with your client, use the tools — skip the Bun builder entirely:

1. Call `get_tps_requirements` to confirm what is expected.
2. Call `suggest_tps_schema(source_summary)` to pick a section preset.
3. Write `body_html` as a string of `.sec.xsec` section blocks.
4. Call `validate_tps_body(body_html, schema_preset)` and fix any errors.
5. Call `build_tps_report(content, body_html, output_path)` to assemble and write the file.
6. The tool returns `{ok, path, sidecars}` — report the path to the operator.

Sidecars (`tps-content.json`, `tps-body.html`) are written automatically beside the output; the operator can edit them and rebuild later.

For tool signatures, see `guides/mcp.md`.

## Source-first workflow (Bun builder)

1. Read the requested source material: spec, issue, PR, README, repo files, or chat prompt.
2. Infer report fields from that material before asking questions.
3. Ask only for fields that cannot be inferred safely.
4. Choose the output directory, usually beside the source spec or in the folder the operator named.
5. Write small adjacent artifacts:
   - `tps-content.json`
   - `tps-body.html`
   - final `*.html`
6. Run the builder:

```bash
bun /absolute/path/to/tps-report/skill/build.ts /target/tps-content.json /target/tps-body.html /target/report.html
```

7. Verify the output file exists and is non-empty.
8. Report the final path.

## External directories

Agents should expect to write reports into sibling or parent projects. That is one of the main uses of this skill: distilling lessons and plans across projects.

If the editor API cannot write outside the current workspace, use a shell command carefully or ask for the missing permission. Keep all generated artifacts in the target folder when possible. Avoid `/tmp` for final or meaningful intermediate files because it hides the working state from the operator.

## Shell discipline

Prefer normal file editing tools for `content.json` and `body.html`. If shell is the only writer available, keep commands small and inspectable.

Avoid:
- giant heredocs containing a full report
- inline Python or JavaScript blobs stuffed into one command
- paths in `/tmp` when the operator named a target directory
- hand-building the final HTML instead of using `skill/build.ts`
- starting another long command while one is still running

## Report shape

`body.html` must preserve a few hard invariants:

- ELI5 appears near the top.
- Top-level sections use `.sec.xsec`.
- Top-level sections default to `data-open="false"`.
- Template placeholders and instructional prompt text are absent.

The builder enforces these invariants and the Zero-Placeholder Policy. It does not enforce one global section list because different report types need different shapes.

Use suggested schemas as starting points:

- Feature build: outcome, current behavior, proposed design, UX states, tickets, tests, gotchas, open questions.
- Research digest or progress report: recent change, findings, evidence, decisions, unknowns, next probes, open questions.
- Database migration: schema summary, backfill, rollout, migration tickets, verification queries, rollback, gotchas.
- Styling or UI polish: visual intent, before/after behavior, component touchpoints, accessibility, responsive checks, review checklist.
- Incident or bug analysis: what happened, impact, root cause theory, evidence, fix plan, prevention tickets, gotchas.

Agents may rename, merge, or add sections when that makes the report more salient. The structure is a launchpad, not a cage.

## Tickets

Tickets should be semi-rigid:

- ID
- title
- priority
- intent
- files or systems touched
- Gherkin acceptance criteria
- gotchas
- verification
- dependencies / blockers

Every ticket should include at least one gotcha. Gherkin is preferred for acceptance criteria because it forces observable behavior:

```text
Given [starting state]
When [user or system action]
Then [observable outcome]
And [important side effect or guardrail]
```

## Recovery behavior

After a misunderstanding or tool failure, reset to the smallest valid path:

1. State the corrected interpretation.
2. Identify the source spec and target output path.
3. Create or repair `tps-content.json` and `tps-body.html`.
4. Run the builder once.
5. Verify and report.

If interrupted, report:

- what was completed
- what was not completed
- where partial files are
- the exact next command to run

Never answer only "OK."
