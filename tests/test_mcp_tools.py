"""Smoke tests for the TPS Report MCP tools.

These tests exercise the pure functions exposed by ``mcp/server.py``
(``validate_body``, ``suggest_schema``, ``build_report``) so they run
without requiring the ``mcp`` package to be installed.

Run:
    python tests/test_mcp_tools.py

Each test prints PASS/FAIL and the script exits non-zero on any failure.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mcp"))

import server  # noqa: E402  (after sys.path mutation)


FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}{(' — ' + detail) if detail and not condition else ''}")
    if not condition:
        FAILURES.append(label)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_BODY = (
    '<div class="sec xsec" data-open="false">\n'
    '  <div class="stitle xhdr" onclick="toggleXSec(this)">'
    '<span class="xtrig">&#x25BC;</span> ELI5 &#x2014; tl;dr</div>\n'
    '  <div class="xbody">\n'
    '    <div class="cal ci"><div class="ct">Plain English</div>'
    'This report covers the migration of the auth subsystem and the '
    'expected downstream effects on existing users and integrations. '
    'It enumerates rollout steps and rollback hooks.</div>\n'
    '  </div>\n'
    '</div>\n'
    '<div class="sec xsec" data-open="false">\n'
    '  <div class="stitle xhdr" onclick="toggleXSec(this)">'
    '<span class="xtrig">&#x25BC;</span> Proposed design</div>\n'
    '  <div class="xbody">A concrete design paragraph with enough text '
    'to clear the thinness heuristic and describe the approach in detail.'
    '</div>\n'
    '</div>'
)

VALID_CONTENT = {
    "title": "Auth Refactor",
    "branch": "feature/auth-v2",
    "pills": ["Active", "2026-05-27", "Chris"],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_get_requirements_shape() -> None:
    print("\n[1] get_tps_requirements returns all hard invariants and presets")
    # Equivalent of the registered tool body
    out = {
        "hard_invariants": server.HARD_INVARIANTS,
        "forbidden_strings": server.FORBIDDEN,
        "schema_presets": server.SCHEMA_PRESETS,
        "ticket_schema": server.TICKET_SCHEMA,
        "component_examples": server.COMPONENT_EXAMPLES,
    }
    check("9 hard invariants", len(out["hard_invariants"]) == 9)
    expected_presets = {
        "feature_build", "research_digest", "progress_report",
        "database_migration", "styling_ui_polish",
        "incident_or_bug_analysis", "chaos_mode",
    }
    check("all 7 schema presets present",
          set(out["schema_presets"]) == expected_presets)
    check("ticket schema has 9 fields", len(out["ticket_schema"]) == 9)
    check("forbidden strings non-empty", len(out["forbidden_strings"]) > 10)


def test_suggest_feature_build() -> None:
    print("\n[2] suggest_tps_schema → feature_build for checkout-flow prompt")
    out = server.suggest_schema("Add a new checkout flow with UI states")
    check("preset == feature_build",
          out["recommended_preset"] == "feature_build",
          f"got {out['recommended_preset']!r}")


def test_suggest_database_migration() -> None:
    print("\n[3] suggest_tps_schema → database_migration for migration prompt")
    out = server.suggest_schema("Add column, backfill rows, rollback plan")
    check("preset == database_migration",
          out["recommended_preset"] == "database_migration",
          f"got {out['recommended_preset']!r}")


def test_validate_missing_eli5() -> None:
    print("\n[4] validate_tps_body rejects missing ELI5")
    body = (
        '<div class="sec xsec" data-open="false">'
        '<div class="stitle">Other</div></div>'
    )
    out = server.validate_body(body)
    check("ok == False", out["ok"] is False)
    check("ELI5 error present",
          any("ELI5" in e for e in out["errors"]),
          f"errors={out['errors']}")


def test_validate_rejects_open_section() -> None:
    print("\n[5] validate_tps_body rejects data-open=\"true\"")
    body = (
        '<div class="sec xsec" data-open="true">'
        '<div class="stitle">ELI5</div></div>'
    )
    out = server.validate_body(body)
    check("ok == False", out["ok"] is False)
    check("data-open error present",
          any("data-open" in e for e in out["errors"]),
          f"errors={out['errors']}")



def test_validate_missing_sections_is_warning() -> None:
    print("\n[6] validate_tps_body warns (not errors) on missing suggested sections")
    out = server.validate_body(VALID_BODY, schema_preset="feature_build")
    check("ok == True", out["ok"] is True, f"errors={out['errors']}")
    check("at least one suggested-section warning",
          any("suggested section missing" in w for w in out["warnings"]),
          f"warnings={out['warnings']}")


def test_chaos_mode_explicit() -> None:
    print("\n[6b] chaos_mode explicit suppresses section coaching warnings")
    out = server.validate_body(VALID_BODY, schema_preset="chaos_mode")
    check("ok == True", out["ok"] is True, f"errors={out['errors']}")
    check("no 'suggested section missing' warnings",
          not any("suggested section missing" in w for w in out["warnings"]),
          f"warnings={out['warnings']}")


def test_chaos_mode_omitted_warns() -> None:
    print("\n[6c] omitted schema_preset warns to pass chaos_mode explicitly")
    out = server.validate_body(VALID_BODY, schema_preset=None)
    check("ok == True", out["ok"] is True)
    check("explicit chaos_mode warning present",
          any("chaos_mode" in w for w in out["warnings"]),
          f"warnings={out['warnings']}")


def test_formatted_field_present() -> None:
    print("\n[6d] validate_body and build_report include 'formatted' field")
    out = server.validate_body(VALID_BODY, schema_preset="chaos_mode")
    check("formatted field present", "formatted" in out)
    check("formatted is a non-empty string",
          isinstance(out["formatted"], str) and len(out["formatted"]) > 0)
    with tempfile.TemporaryDirectory() as tmp:
        result = server.build_report(VALID_CONTENT, VALID_BODY,
                                     str(Path(tmp) / "r.html"))
        check("build formatted field present", "formatted" in result)


def test_build_writes_html() -> None:
    print("\n[7] build_tps_report writes a valid HTML file")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "report.html"
        out = server.build_report(VALID_CONTENT, VALID_BODY, str(out_path))
        check("ok == True", out["ok"] is True, f"errors={out['errors']}")
        check("file exists", out_path.exists())
        check("file non-empty", out_path.stat().st_size > 0)
        check("bytes match", out["bytes"] == out_path.stat().st_size)
        text = out_path.read_text(encoding="utf-8")
        check("title injected", "Auth Refactor" in text)
        check("branch injected", "feature/auth-v2" in text)
        check("no leftover {{TITLE}}", "{{TITLE}}" not in text)
        check("report_key derived", out["report_key"] == "auth-refactor")


def test_build_from_files() -> None:
    print("\n[8] build_tps_report_from_files reads adjacent files")
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "tps-content.json").write_text(json.dumps(VALID_CONTENT), encoding="utf-8")
        (d / "tps-body.html").write_text(VALID_BODY, encoding="utf-8")
        out_path = d / "report.html"
        content = json.loads((d / "tps-content.json").read_text(encoding="utf-8"))
        body = (d / "tps-body.html").read_text(encoding="utf-8")
        out = server.build_report(content, body, str(out_path))
        check("ok == True", out["ok"] is True, f"errors={out['errors']}")
        check("file exists", out_path.exists())


def test_build_rejects_forbidden() -> None:
    print("\n[9] build_tps_report rejects forbidden placeholder strings")
    bad_body = VALID_BODY + "\nReplace with the actual content."
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "report.html"
        out = server.build_report(VALID_CONTENT, bad_body, str(out_path))
        check("ok == False", out["ok"] is False)
        check("placeholder error present",
              any("Replace with" in e for e in out["errors"]),
              f"errors={out['errors']}")
        check("no file written", not out_path.exists())


def test_security_no_overwrite_without_force() -> None:
    print("\n[9b] build refuses to overwrite existing file without force=True")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "report.html"
        # First write succeeds
        r1 = server.build_report(VALID_CONTENT, VALID_BODY, str(out_path))
        check("first write ok", r1["ok"] is True, f"errors={r1['errors']}")
        # Second write without force must fail
        r2 = server.build_report(VALID_CONTENT, VALID_BODY, str(out_path))
        check("second write blocked", r2["ok"] is False)
        check("overwrite error message",
              any("already exists" in e for e in r2["errors"]),
              f"errors={r2['errors']}")
        # With force=True it succeeds
        r3 = server.build_report(VALID_CONTENT, VALID_BODY, str(out_path), force=True)
        check("force=True succeeds", r3["ok"] is True, f"errors={r3['errors']}")


def test_security_non_html_extension_rejected() -> None:
    print("\n[9c] build rejects output_path that doesn't end in .html")
    with tempfile.TemporaryDirectory() as tmp:
        out = server.build_report(VALID_CONTENT, VALID_BODY, str(Path(tmp) / "report.txt"))
        check("ok == False", out["ok"] is False)
        check(".html extension error",
              any(".html" in e for e in out["errors"]),
              f"errors={out['errors']}")


def test_security_tmp_warning() -> None:
    print("\n[9d] build warns (not blocks) on /tmp output path")
    out = server.build_report(
        VALID_CONTENT, VALID_BODY, "/tmp/tps-smoke-test-delete-me.html"
    )
    check("ok == True (not blocked)", out["ok"] is True, f"errors={out['errors']}")
    check("/tmp warning present",
          any("/tmp" in w or "tmp" in w.lower() for w in out["warnings"]),
          f"warnings={out['warnings']}")
    # Clean up
    p = Path("/tmp/tps-smoke-test-delete-me.html")
    if p.exists():
        p.unlink()


def test_sidecars_written() -> None:
    print("\n[9e] build_tps_report writes tps-content.json and tps-body.html sidecars")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "report.html"
        out = server.build_report(VALID_CONTENT, VALID_BODY, str(out_path),
                                  write_sidecars=True)
        check("ok == True", out["ok"] is True, f"errors={out['errors']}")
        check("sidecars list non-empty", len(out.get("sidecars", [])) == 2)
        check("tps-content.json exists", (Path(tmp) / "tps-content.json").exists())
        check("tps-body.html exists", (Path(tmp) / "tps-body.html").exists())
        # Confirm content.json is valid JSON with the right title
        c = json.loads((Path(tmp) / "tps-content.json").read_text())
        check("sidecar title matches", c["title"] == VALID_CONTENT["title"])


def test_sidecars_off() -> None:
    print("\n[9f] write_sidecars=False skips sidecar files")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "report.html"
        out = server.build_report(VALID_CONTENT, VALID_BODY, str(out_path),
                                  write_sidecars=False)
        check("ok == True", out["ok"] is True, f"errors={out['errors']}")
        check("sidecars list empty", out.get("sidecars") == [])
        check("no tps-content.json", not (Path(tmp) / "tps-content.json").exists())


def test_repo_artifacts_build() -> None:
    print("\n[10] live repo content.json + body.html builds cleanly")
    content_path = ROOT / "content.json"
    body_path = ROOT / "body.html"
    if not content_path.exists() or not body_path.exists():
        print("  [SKIP] no repo artifacts to validate")
        return
    content = json.loads(content_path.read_text(encoding="utf-8"))
    body = body_path.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "report.html"
        out = server.build_report(content, body, str(out_path))
        check("ok == True", out["ok"] is True, f"errors={out['errors']}")
        check("output exists", out_path.exists())
        check("output > 50 KB", out_path.stat().st_size > 50_000)


def main() -> int:
    print("TPS Report MCP smoke tests")
    print("=" * 60)
    test_get_requirements_shape()
    test_suggest_feature_build()
    test_suggest_database_migration()
    test_validate_missing_eli5()
    test_validate_rejects_open_section()
    test_validate_missing_sections_is_warning()
    test_chaos_mode_explicit()
    test_chaos_mode_omitted_warns()
    test_formatted_field_present()
    test_build_writes_html()
    test_build_from_files()
    test_build_rejects_forbidden()
    test_security_no_overwrite_without_force()
    test_security_non_html_extension_rejected()
    test_security_tmp_warning()
    test_sidecars_written()
    test_sidecars_off()
    test_repo_artifacts_build()
    print("\n" + "=" * 60)
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): {FAILURES}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
