#!/usr/bin/env python3
"""TPS Report MCP Server.

Exposes the tps-report skill as an MCP surface:

- prompt  : tps-report (interview-driven generation, kept for compatibility)
- tools   : get_tps_requirements, suggest_tps_schema, validate_tps_body,
            build_tps_report, build_tps_report_from_files

The MCP constrains delivery mechanics (template assembly, hard invariants,
Zero-Placeholder Policy) without dictating section names or layout.

Install:  pip install mcp
Run:      python mcp/server.py
Config:   see guides/mcp.md
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - allow pure-function import without mcp installed
    FastMCP = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = ROOT / "skill" / "SKILL.md"
TEMPLATE_PATH = ROOT / "skill" / "template.html"

# ---------------------------------------------------------------------------
# Constants — kept in sync with skill/build.ts and guides/mcp-build-plan.md
# ---------------------------------------------------------------------------

FORBIDDEN: list[str] = [
    "[Project Name]", "[branch-name]", "[Date]", "[Owner]", "[Title of the epic]",
    "Replace with", "Describe the current state", "Who is affected? What breaks",
    "List adjacent problems", "One paragraph describing",
    "Example code snippet (replace", "What did you not do", "Highest-risk files",
    "Backward-compatibility concerns", "Unit tests? Integration tests?",
    "path/to/file.ext", "? points",
    "Step 1 \u2014 reason", "Step 2 \u2014 reason", "Step 3 \u2014 reason",
    "Context: what makes this hard", "Context: who decides this",
    "1\u20133 sentences. What is this? What changes?",
]

HARD_INVARIANTS: list[str] = [
    "Final deliverable is one self-contained .html file.",
    "The report uses the canonical TPS template.",
    "ELI5 appears near the top.",
    "Top-level sections are collapsible with .sec.xsec.",
    "Top-level sections default to data-open=\"false\".",
    "Zero-Placeholder Policy passes.",
    "Output path is explicit.",
    "Output file exists and is non-empty.",
    "Local storage key is unique per report.",
]

SCHEMA_PRESETS: dict[str, list[str]] = {
    "feature_build": [
        "ELI5 \u2014 tl;dr", "User-visible outcome", "Current behavior / problem",
        "Proposed design", "UX and edge states", "Implementation tickets",
        "Testing and acceptance", "Gotchas / rollback", "Open questions",
    ],
    "research_digest": [
        "ELI5 \u2014 tl;dr", "What changed since last update", "Key findings",
        "Evidence and source notes", "Decisions made", "Risks and unknowns",
        "Next probes", "Open questions",
    ],
    "progress_report": [
        "ELI5 \u2014 tl;dr", "What changed since last update", "Key findings",
        "Evidence and source notes", "Decisions made", "Risks and unknowns",
        "Next probes", "Open questions",
    ],
    "database_migration": [
        "ELI5 \u2014 tl;dr", "Schema change summary", "Data/backfill plan",
        "Compatibility and rollout", "Migration tickets", "Verification queries",
        "Rollback / recovery", "Gotchas", "Open questions",
    ],
    "styling_ui_polish": [
        "ELI5 \u2014 tl;dr", "Visual intent", "Before / after behavior",
        "Component touchpoints", "Accessibility and responsive checks",
        "Implementation tickets", "Review checklist", "Open questions",
    ],
    "incident_or_bug_analysis": [
        "ELI5 \u2014 tl;dr", "What happened", "Impact", "Root cause theory",
        "Evidence", "Fix plan", "Prevention tickets", "Gotchas", "Open questions",
    ],
    "chaos_mode": [
        "ELI5 \u2014 tl;dr",
    ],
}

TICKET_SCHEMA: list[str] = [
    "ID", "title", "priority", "intent", "files or systems touched",
    "Gherkin acceptance criteria", "gotchas", "verification",
    "dependencies / blockers",
]

COMPONENT_EXAMPLES: dict[str, str] = {
    "eli5_section": (
        '<div class="sec xsec" data-open="false">\n'
        '  <div class="stitle xhdr" onclick="toggleXSec(this)">'
        '<span class="xtrig">&#x25BC;</span> ELI5 &#x2014; tl;dr</div>\n'
        '  <div class="xbody">\n'
        '  <div class="cal ci commentable" data-id="eli5" data-title="ELI5">\n'
        '    <div class="ct">&#x1F4A1; Plain English</div>\n'
        '    One to three sentences in plain English.\n'
        '  </div>\n'
        '  </div>\n'
        '</div>'
    ),
    "collapsible_section": (
        '<div class="sec xsec" data-open="false">\n'
        '  <div class="stitle xhdr" onclick="toggleXSec(this)">'
        '<span class="xtrig">&#x25BC;</span> Section Title</div>\n'
        '  <div class="xbody"> ... </div>\n'
        '</div>'
    ),
    "ticket_row": (
        '<div class="trow expandable commentable" data-id="ticket-1" '
        'data-title="Ticket 1" data-open="false">\n'
        '  <div class="trow-hdr">\n'
        '    <button class="texp" onclick="toggleTicket(this,event)">&#x25B6;</button>\n'
        '    <div class="tid">T-001</div>\n'
        '    <div class="ttl">Ticket title</div>\n'
        '    <span class="bdg bh">high</span>\n'
        '  </div>\n'
        '  <div class="trow-body"> ... </div>\n'
        '</div>'
    ),
}

GENERIC_SECTION_TITLES: set[str] = {
    "section title", "section 1", "section 2", "section 3",
    "untitled", "tbd", "todo", "placeholder",
}

# Heuristic keyword map for suggest_schema. Order matters — earlier wins ties
# only when scores match; otherwise the highest scoring preset is returned.
_SCHEMA_KEYWORDS: dict[str, list[str]] = {
    "database_migration": [
        "migration", "migrate", "schema", "backfill", "rollback", "column",
        "alter table", "add column", "drop column", "index", "rls",
    ],
    "incident_or_bug_analysis": [
        "incident", "outage", "postmortem", "post-mortem", "root cause",
        "regression", "bug", "broke", "broken", "failure", "5xx", "crash",
    ],
    "styling_ui_polish": [
        "styling", "polish", "css", "visual", "responsive", "accessibility",
        "a11y", "spacing", "color palette", "typography", "ui polish",
    ],
    "research_digest": [
        "research", "investigation", "findings", "digest", "explored",
        "literature", "evidence", "spike", "discovery",
    ],
    "progress_report": [
        "progress", "weekly update", "status update", "since last", "burndown",
        "weekly", "standup",
    ],
    "feature_build": [
        "feature", "flow", "checkout", "new ui", "implement", "build",
        "epic", "design", "user-visible",
    ],
}


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

_SECTION_OPENER_RE = re.compile(
    r'<div\s+class="[^"]*\bsec\b[^"]*"[^>]*>', re.IGNORECASE
)
_DATA_OPEN_FALSE_RE = re.compile(r'data-open="false"')
_XSEC_RE = re.compile(r'\bxsec\b')
_SECTION_TITLE_RE = re.compile(
    r'<div\s+class="[^"]*\bstitle\b[^"]*"[^>]*>(.*?)</div>',
    re.IGNORECASE | re.DOTALL,
)


def _strip_html(fragment: str) -> str:
    """Crude tag/entity stripper for heuristic title comparisons."""
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = (
        text.replace("&#x25BC;", "")
        .replace("&#x2014;", "—")
        .replace("&amp;", "&")
        .replace("&nbsp;", " ")
    )
    return re.sub(r"\s+", " ", text).strip()


def _format_result(ok: bool, errors: list[str], warnings: list[str]) -> str:
    """Render errors + warnings as a human-readable block for LLM consumption."""
    lines = ["TPS validation: " + ("OK" if ok else "FAIL")]
    if errors:
        lines.append("  errors:")
        lines.extend(f"    - {e}" for e in errors)
    if warnings:
        lines.append("  warnings:")
        lines.extend(f"    - {w}" for w in warnings)
    if ok and not warnings:
        lines.append("  all hard invariants satisfied, no warnings")
    return "\n".join(lines)


def validate_body(body_html: str, schema_preset: str | None = None) -> dict[str, Any]:
    """Validate a TPS body fragment against hard invariants and soft schemas.

    Hard invariant failures become errors. Schema and ticket issues are warnings.
    chaos_mode must be passed explicitly to suppress section coaching.
    Returns ``{ok, errors, warnings, formatted}``.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if "ELI5" not in body_html:
        errors.append('missing "ELI5" section (hard invariant)')

    openers = _SECTION_OPENER_RE.findall(body_html)
    if not openers:
        errors.append("no top-level .sec sections found")

    for opener in openers:
        if not _XSEC_RE.search(opener):
            errors.append(f"top-level section missing xsec class: {opener}")
        if not _DATA_OPEN_FALSE_RE.search(opener):
            errors.append(
                f'top-level section must default to data-open="false": {opener}'
            )

    for needle in FORBIDDEN:
        if needle in body_html:
            errors.append(f"forbidden placeholder string present: {needle!r}")

    # ---- schema coaching (warnings only) ------------------------------------
    if schema_preset is None:
        warnings.append(
            "no schema_preset given — section coaching is off; "
            "pass \"chaos_mode\" to silence this warning and opt out explicitly"
        )
    elif schema_preset == "chaos_mode":
        pass  # explicitly opted out — no section warnings
    elif schema_preset in SCHEMA_PRESETS:
        suggested = SCHEMA_PRESETS[schema_preset]
        body_lower = body_html.lower()
        for section in suggested:
            needle = section.split("\u2014")[0].strip().lower()
            if needle and needle not in body_lower:
                warnings.append(
                    f"suggested section missing for preset '{schema_preset}': {section}"
                )
    else:
        warnings.append(
            f"unknown schema_preset {schema_preset!r}; "
            f"valid presets: {list(SCHEMA_PRESETS)}"
        )

    # ---- generic titles -------------------------------------------------------
    titles = [_strip_html(t) for t in _SECTION_TITLE_RE.findall(body_html)]
    for title in titles:
        normalised = re.sub(r"^[\u25BC\s\-\u2014:]+", "", title).strip().lower()
        if normalised in GENERIC_SECTION_TITLES:
            warnings.append(f"section title looks generic: {title!r}")

    # ---- ticket quality -------------------------------------------------------
    has_tickets = bool(re.search(r"\btrow\b|ticket", body_html, re.IGNORECASE))
    if has_tickets:
        if not re.search(r"\bGiven\b.*\bWhen\b.*\bThen\b", body_html, re.DOTALL):
            warnings.append("tickets present but no Gherkin (Given/When/Then) found")
        if not re.search(r"gotcha", body_html, re.IGNORECASE):
            warnings.append("tickets present but no 'gotcha' field found")

    # ---- body thinness -------------------------------------------------------
    plain_len = len(_strip_html(body_html))
    if plain_len < 400:
        warnings.append(
            f"report body appears thin ({plain_len} chars of text); "
            "consider adding evidence, gotchas, or open questions"
        )

    ok = not errors
    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "formatted": _format_result(ok, errors, warnings),
    }


def suggest_schema(
    source_summary: str, operator_intent: str | None = None
) -> dict[str, Any]:
    """Heuristic schema preset recommender. Keyword-scored, simple by design."""
    text = f"{source_summary}\n{operator_intent or ''}".lower()
    scores: dict[str, int] = {}
    for preset, words in _SCHEMA_KEYWORDS.items():
        scores[preset] = sum(1 for w in words if w in text)

    best = max(scores, key=lambda k: (scores[k], -list(_SCHEMA_KEYWORDS).index(k)))
    if scores[best] == 0:
        best = "feature_build"
        rationale = (
            "No strong signal in the source summary. Defaulting to feature_build; "
            "switch to chaos_mode if the material wants a stranger shape."
        )
    else:
        matched = [w for w in _SCHEMA_KEYWORDS[best] if w in text]
        rationale = (
            f"Matched keywords {matched!r} against the source summary. "
            "Rename or merge sections freely — the preset is a launchpad."
        )

    return {
        "recommended_preset": best,
        "suggested_sections": SCHEMA_PRESETS[best],
        "rationale": rationale,
        "allowed_deviations": (
            "Agents may rename, merge, drop, or add sections as long as the hard "
            "invariants (ELI5, collapsible .sec.xsec, data-open=\"false\", "
            "Zero-Placeholder Policy) still hold. Use chaos_mode to opt out of "
            "section coaching entirely."
        ),
        "preset_scores": scores,
    }


_KEY_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _derive_key(title: str) -> str:
    return _KEY_SLUG_RE.sub("-", title.lower()).strip("-") or "tps-report"


def _validate_content(content: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(content, dict):
        return ["content must be a JSON object"]
    if not content.get("title") or not isinstance(content["title"], str):
        errors.append("content.title is required (string)")
    if not content.get("branch") or not isinstance(content["branch"], str):
        errors.append("content.branch is required (string)")
    pills = content.get("pills")
    if not isinstance(pills, list) or len(pills) != 3 or not all(
        isinstance(p, str) for p in pills
    ):
        errors.append("content.pills must be an array of exactly 3 strings")
    return errors


def _resolve_output(output_path: str, force: bool = False) -> tuple[Path, list[str]]:
    """Resolve, create parent dirs, and apply output path safety checks.

    Returns ``(path, warnings)``.  Raises ``ValueError`` on hard violations.
    """
    if not output_path:
        raise ValueError("output_path is required")

    p = Path(output_path)
    if not p.is_absolute():
        p = Path.cwd() / p

    # B. Must end in .html
    if p.suffix.lower() != ".html":
        raise ValueError(
            f"output_path must end in .html (got {p.suffix!r})"
        )

    # A. Refuse to overwrite unless force=True
    if p.exists() and not force:
        raise ValueError(
            f"{p} already exists — pass force=True to overwrite"
        )

    p.parent.mkdir(parents=True, exist_ok=True)

    path_warnings: list[str] = []
    # C. Warn on /tmp writes
    try:
        tmp = Path("/tmp").resolve()
        if p.resolve().is_relative_to(tmp):
            path_warnings.append(
                f"output is under /tmp ({p}); "
                "prefer the target project directory per skill doctrine"
            )
    except (OSError, AttributeError):
        pass

    return p, path_warnings


def build_report(
    content: dict[str, Any],
    body_html: str,
    output_path: str,
    schema_preset: str | None = None,
    force: bool = False,
    write_sidecars: bool = True,
) -> dict[str, Any]:
    """Assemble, validate, and write the final HTML report.

    Parameters
    ----------
    force:
        Overwrite the output file if it already exists.
    write_sidecars:
        Write ``tps-content.json`` and ``tps-body.html`` next to the output
        as a debug/re-run trail. Existing sidecar files are always overwritten.

    Returns ``{ok, output_path, bytes, report_key, errors, warnings, formatted, sidecars}``.
    """
    def _fail(errors: list[str], warnings: list[str], key: str | None = None) -> dict[str, Any]:
        return {
            "ok": False,
            "output_path": None,
            "bytes": 0,
            "report_key": key,
            "errors": errors,
            "warnings": warnings,
            "formatted": _format_result(False, errors, warnings),
            "sidecars": [],
        }

    content_errors = _validate_content(content)
    body_result = validate_body(body_html, schema_preset)

    errors = content_errors + body_result["errors"]
    warnings = list(body_result["warnings"])

    if errors:
        return _fail(errors, warnings)

    try:
        out, path_warnings = _resolve_output(output_path, force=force)
    except ValueError as exc:
        return _fail([str(exc)], warnings)

    warnings.extend(path_warnings)
    key = content.get("key") or _derive_key(content["title"])

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = (
        template.replace("{{TITLE}}", content["title"])
        .replace("{{BRANCH}}", content["branch"])
        .replace("{{PILL_1}}", content["pills"][0])
        .replace("{{PILL_2}}", content["pills"][1])
        .replace("{{PILL_3}}", content["pills"][2])
        .replace("{{REPORT_KEY}}", key)
        .replace("{{BODY_HTML}}", body_html)
    )

    # Re-check forbidden strings on the assembled body slice (matches build.ts).
    body_start = html.find('<div id="zoom-wrap">')
    body_end = html.find("</div><!-- /zoom-wrap -->")
    body_slice = (
        html[body_start:body_end] if body_start != -1 and body_end != -1 else html
    )
    leaks = [s for s in FORBIDDEN if s in body_slice]
    if leaks:
        return _fail(
            [f"forbidden placeholder after assembly: {s!r}" for s in leaks],
            warnings,
            key,
        )

    out.write_text(html, encoding="utf-8")
    size = out.stat().st_size
    if size == 0:
        return _fail(["output file is empty after write"], warnings, key)

    # Write sidecars
    sidecars: list[str] = []
    if write_sidecars:
        sidecar_dir = out.parent
        content_sidecar = sidecar_dir / "tps-content.json"
        body_sidecar = sidecar_dir / "tps-body.html"
        content_sidecar.write_text(json.dumps(content, indent=2), encoding="utf-8")
        body_sidecar.write_text(body_html, encoding="utf-8")
        sidecars = [str(content_sidecar), str(body_sidecar)]

    return {
        "ok": True,
        "output_path": str(out),
        "bytes": size,
        "report_key": key,
        "errors": [],
        "warnings": warnings,
        "formatted": _format_result(True, [], warnings),
        "sidecars": sidecars,
    }


# ---------------------------------------------------------------------------
# MCP surface
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "tps-report",
    instructions=(
        "Generates self-contained HTML planning reports with four themes "
        "(Dark, Hacker CRT, Olde Tyme, Chalk Flower). "
        "Use the tools to validate and build; call the tps-report prompt "
        "to start an interview-driven session."
    ),
) if FastMCP is not None else None


def _register_mcp() -> None:
    if mcp is None:  # pragma: no cover
        return

    @mcp.prompt(
        name="tps-report",
        description=(
            "Interview-driven generator for a self-contained HTML planning report."
        ),
    )
    def tps_report_prompt() -> str:
        return SKILL_PATH.read_text(encoding="utf-8")

    @mcp.tool(
        name="get_tps_requirements",
        description=(
            "Return the structured TPS requirements: hard invariants, "
            "forbidden placeholder strings, schema presets, ticket schema, "
            "and minimal component examples."
        ),
    )
    def get_tps_requirements() -> dict[str, Any]:
        return {
            "hard_invariants": HARD_INVARIANTS,
            "forbidden_strings": FORBIDDEN,
            "schema_presets": SCHEMA_PRESETS,
            "ticket_schema": TICKET_SCHEMA,
            "component_examples": COMPONENT_EXAMPLES,
        }

    @mcp.tool(
        name="suggest_tps_schema",
        description=(
            "Heuristically recommend a schema preset for the source material. "
            "Inputs: source_summary, optional operator_intent."
        ),
    )
    def suggest_tps_schema(
        source_summary: str, operator_intent: str | None = None
    ) -> dict[str, Any]:
        return suggest_schema(source_summary, operator_intent)


    @mcp.tool(
        name="validate_tps_body",
        description=(
            "Validate a TPS body HTML fragment. Hard invariant failures are "
            "errors; schema, ticket, and thinness issues are warnings."
        ),
    )
    def validate_tps_body(
        body_html: str, schema_preset: str | None = None
    ) -> dict[str, Any]:
        return validate_body(body_html, schema_preset)

    @mcp.tool(
        name="build_tps_report",
        description=(
            "Validate content + body, assemble against the canonical template, "
            "write the .html file (must end in .html), and verify it exists. "
            "Pass force=True to overwrite an existing file. "
            "Writes tps-content.json and tps-body.html sidecars by default. "
            "Returns {ok, output_path, bytes, report_key, errors, warnings, formatted, sidecars}."
        ),
    )
    def build_tps_report(
        content: dict[str, Any],
        body_html: str,
        output_path: str,
        schema_preset: str | None = None,
        force: bool = False,
        write_sidecars: bool = True,
    ) -> dict[str, Any]:
        return build_report(
            content, body_html, output_path, schema_preset,
            force=force, write_sidecars=write_sidecars,
        )

    @mcp.tool(
        name="build_tps_report_from_files",
        description=(
            "Read tps-content.json and tps-body.html from disk, then build the "
            "report. Supports adjacent-file workflows. "
            "Pass force=True to overwrite an existing output file."
        ),
    )
    def build_tps_report_from_files(
        content_path: str,
        body_path: str,
        output_path: str,
        schema_preset: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        _fail_shape: dict[str, Any] = {
            "ok": False, "output_path": None, "bytes": 0,
            "report_key": None, "warnings": [], "sidecars": [],
        }
        try:
            content = json.loads(Path(content_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errs = [f"cannot read content file {content_path!r}: {exc}"]
            return {**_fail_shape, "errors": errs,
                    "formatted": _format_result(False, errs, [])}
        try:
            body_html = Path(body_path).read_text(encoding="utf-8")
        except OSError as exc:
            errs = [f"cannot read body file {body_path!r}: {exc}"]
            return {**_fail_shape, "errors": errs,
                    "formatted": _format_result(False, errs, [])}
        # Sidecars already exist on disk as the input files; don't duplicate.
        return build_report(
            content, body_html, output_path, schema_preset,
            force=force, write_sidecars=False,
        )


_register_mcp()


if __name__ == "__main__":
    if mcp is None:
        raise SystemExit(
            "mcp package not installed. Run: pip install mcp"
        )
    mcp.run()
