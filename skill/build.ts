#!/usr/bin/env bun
/**
 * TPS Report Builder
 * Usage: bun skill/build.ts content.json body.html [output.html]
 *
 * content.json  — { title, branch, pills: [str,str,str], key? }
 * body.html     — the .sec div blocks only (the actual content)
 * output.html   — defaults to report.html in cwd
 */
import { readFileSync, writeFileSync } from "fs";
import { join } from "path";

const TEMPLATE = join(import.meta.dir, "template.html");

const FORBIDDEN = [
  "[Project Name]", "[branch-name]", "[Date]", "[Owner]", "[Title of the epic]",
  "Replace with", "Describe the current state", "Who is affected? What breaks",
  "List adjacent problems", "One paragraph describing",
  "Example code snippet (replace", "What did you not do", "Highest-risk files",
  "Backward-compatibility concerns", "Unit tests? Integration tests?",
  "path/to/file.ext", "? points",
  "Step 1 — reason", "Step 2 — reason", "Step 3 — reason",
  "Context: what makes this hard", "Context: who decides this",
  "1\u20133 sentences. What is this? What changes?",
];

function die(msg: string): never {
  console.error("❌", msg);
  process.exit(1);
}

function assertReportInvariants(body: string): void {
  const problems: string[] = [];
  const sectionOpeners = body.match(/<div\s+class="[^"]*\bsec\b[^"]*"[^>]*>/g) ?? [];

  if (!body.includes("ELI5")) {
    problems.push('missing "ELI5"');
  }

  if (!sectionOpeners.length) {
    problems.push('missing collapsible sections with class "sec xsec"');
  }

  for (const opener of sectionOpeners) {
    if (!/\bxsec\b/.test(opener)) {
      problems.push(`section is missing xsec class: ${opener}`);
    }
    if (!/data-open="false"/.test(opener)) {
      problems.push(`section must default collapsed with data-open="false": ${opener}`);
    }
  }

  if (problems.length) {
    console.error("❌ TPS report invariant check failed:");
    problems.forEach(p => console.error("   •", p));
    die("Report NOT written.");
  }
}

const [,, metaFile, bodyFile, outFile = "report.html"] = process.argv;
if (!metaFile || !bodyFile) {
  die("Usage: bun skill/build.ts content.json body.html [output.html]");
}

let meta: { title: string; branch: string; pills: string[]; key?: string };
try {
  meta = JSON.parse(readFileSync(metaFile, "utf8"));
} catch (e) {
  die(`Cannot parse ${metaFile}: ${e}`);
}

if (!meta.title) die("content.json missing 'title'");
if (!meta.branch) die("content.json missing 'branch'");
if (!Array.isArray(meta.pills) || meta.pills.length !== 3) die("content.json 'pills' must be array of 3 strings");

const body = readFileSync(bodyFile, "utf8");
const key = meta.key ?? meta.title.toLowerCase().replace(/[^a-z0-9]+/g, "-");

assertReportInvariants(body);

let html = readFileSync(TEMPLATE, "utf8");
html = html
  .replace("{{TITLE}}", meta.title)
  .replace("{{BRANCH}}", meta.branch)
  .replace("{{PILL_1}}", meta.pills[0])
  .replace("{{PILL_2}}", meta.pills[1])
  .replace("{{PILL_3}}", meta.pills[2])
  .replace("{{REPORT_KEY}}", key)
  .replace("{{BODY_HTML}}", body);

// Zero-Placeholder Policy check (body only — skip CSS/JS blocks)
const bodyStart = html.indexOf('<div id="zoom-wrap">');
const bodyEnd = html.indexOf("</div><!-- /zoom-wrap -->");
const bodySlice = bodyStart !== -1 && bodyEnd !== -1 ? html.slice(bodyStart, bodyEnd) : html;

const leaks = FORBIDDEN.filter(s => bodySlice.includes(s));
if (leaks.length) {
  console.error("❌ Zero-Placeholder Policy violation — fix before shipping:");
  leaks.forEach(l => console.error("   •", l));
  die("Report NOT written.");
}

writeFileSync(outFile, html);
console.log("✓", outFile, `(${html.length} bytes, key=${key})`);
