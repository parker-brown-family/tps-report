# TPS Report MCP — Design Rationale

This document captures the design decisions behind the `tps-report` MCP server. The tools described here are **implemented and live** in `mcp/server.py`. For usage and registration, see `guides/mcp.md`.

## Product thesis

The MCP should constrain delivery mechanics, not the interpretive act.

TPS reports are not just structured data. They are meant to be salient, thought-provoking planning artifacts: the agent should read messy source material, find the spine, name risks, surface gotchas, and make the next moves obvious.

The MCP should behave like a kiln, not a mold. It hardens the artifact into a reliable `.html` report without forcing every report into the same section titles or card layout.

## Hard invariants

These should be enforced by MCP tools and the builder:

- Final deliverable is one self-contained `.html` file.
- The report uses the canonical TPS template.
- ELI5 appears near the top.
- Top-level sections are collapsible with `.sec.xsec`.
- Top-level sections default to `data-open="false"`.
- Zero-Placeholder Policy passes.
- Output path is explicit.
- Output file exists and is non-empty.
- Local storage key is unique per report.

## Soft schemas

The MCP should expose suggested schemas for common use cases, not require one global schema.

Suggested presets:

- `feature_build`
- `research_digest`
- `progress_report`
- `database_migration`
- `styling_ui_polish`
- `incident_or_bug_analysis`
- `chaos_mode`

`chaos_mode` means the agent still honors hard invariants, but chooses its own report sections because the source material wants a stranger or more revelatory shape.

## Suggested schema contents

### Feature build

- ELI5 — tl;dr
- User-visible outcome
- Current behavior / problem
- Proposed design
- UX and edge states
- Implementation tickets
- Testing and acceptance
- Gotchas / rollback
- Open questions

### Research digest or progress report

- ELI5 — tl;dr
- What changed since last update
- Key findings
- Evidence and source notes
- Decisions made
- Risks and unknowns
- Next probes
- Open questions

### Database migration

- ELI5 — tl;dr
- Schema change summary
- Data/backfill plan
- Compatibility and rollout
- Migration tickets
- Verification queries
- Rollback / recovery
- Gotchas
- Open questions

### Styling or UI polish

- ELI5 — tl;dr
- Visual intent
- Before / after behavior
- Component touchpoints
- Accessibility and responsive checks
- Implementation tickets
- Review checklist
- Open questions

### Incident or bug analysis

- ELI5 — tl;dr
- What happened
- Impact
- Root cause theory
- Evidence
- Fix plan
- Prevention tickets
- Gotchas
- Open questions

## Tool surface

Start with narrow tools that make the valid next move obvious.

### `get_tps_requirements`

Returns:

- hard invariants
- Zero-Placeholder strings
- suggested schema list
- ticket schema
- small component examples

Use this when an agent needs to know what to produce.

### `suggest_tps_schema`

Input:

- `source_summary`
- optional `operator_intent`

Returns:

- recommended preset
- suggested section list
- why this schema fits
- allowed deviations

Use this to help an agent choose between feature build, research digest, migration, progress report, and chaos mode.

### `validate_tps_body`

Input:

- `body_html`
- optional `schema_preset`

Returns:

- `ok`
- hard invariant failures
- placeholder failures
- schema suggestions, as warnings rather than errors
- ticket quality warnings

This tool should not reject creative section naming unless a hard invariant fails.

### `build_tps_report`

Input:

- `content`
- `body_html`
- `output_path`

Returns:

- output path
- byte count
- report key
- warnings

This tool validates, assembles with the canonical template, writes the final `.html`, and verifies the file exists.

### `build_tps_report_from_files`

Input:

- `content_path`
- `body_path`
- `output_path`

Returns the same shape as `build_tps_report`.

This supports coding agents that already created adjacent files beside a spec.

## Ticket schema

Tickets should be semi-rigid because implementation planning benefits from repeated affordances.

Recommended fields:

- ID
- title
- priority
- intent
- files or systems touched
- Gherkin acceptance criteria
- gotchas
- verification
- dependencies / blockers

Gherkin is strongly preferred:

```text
Given [starting state]
When [user or system action]
Then [observable outcome]
And [important side effect or guardrail]
```

Every ticket should include at least one gotcha. The gotcha field is where the report becomes operationally useful instead of merely tidy.

## Validation philosophy

Errors:

- missing ELI5
- top-level sections not collapsible
- top-level sections default expanded
- forbidden placeholder strings
- malformed content metadata
- output path missing
- builder could not write or verify the file

Warnings:

- schema preset omitted
- suggested section missing for chosen preset
- tickets missing Gherkin
- tickets missing gotchas
- report appears too thin
- section names are generic

Warnings should coach the agent without blocking a vivid, useful report.

## Implementation phases

1. Keep the existing `tps-report` prompt for compatibility.
2. Add read-only requirement/schema tools.
3. Add `validate_tps_body`.
4. Add `build_tps_report_from_files`.
5. Add `build_tps_report`.
6. Update docs and slash-command guidance to prefer tool calls when available.
7. Add lightweight tests for validation and build behavior.

## Open design questions

- Should schema warnings be returned as plain text, structured JSON, or both?
- Should `chaos_mode` be explicit, or should agents simply omit `schema_preset`?
- Should MCP write outside the server repo by default, or require an allowlist/root policy?
- Should the MCP create `tps-content.json` and `tps-body.html` artifacts automatically when called with inline content?
