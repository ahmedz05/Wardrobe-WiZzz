# Wardrobe-WIZzz toolkit status

Verified 2026-10-30. Tooling and guidance only: application development is stopped
pending user review. All 197 tracked/untracked, nonignored application/source files
in the preservation baseline are unchanged. Existing Flutter/FastAPI modifications
were preserved. No application requests, database access, schema/data changes,
commit, push, deployment, reset or deletion of existing work occurred in this task.

## Installed integrations and current-session limits

| Integration | Installation and verification | Current session |
| --- | --- | --- |
| Superpowers | Existing official-marketplace plugin 7.0.1, enabled; manifest and planning/testing/debugging/review skills present. No reinstall or extra framework. | Not advertised in this turn's skill list. Files are readable; refresh the intended Codex client before relying on automatic skill selection. |
| Context7 | Existing `https://mcp.context7.com/mcp` configuration; only `resolve-library-id` and `query-docs` enabled. Fresh anonymous FastAPI lookup **and documentation query passed**. No API key/OAuth created. | No Context7 tools exposed in this running tool catalog. Standalone MCP verification works; local config may require a fresh local CLI/IDE session. |
| Playwright MCP | Existing 0.0.83 package; fresh discovery of **25 tools**, isolated headless Chrome launch and `about:blank` accessibility snapshot passed. | No Playwright namespace exposed in this running catalog. Standalone tooling works; refresh the intended local client for native MCP access. |
| GitHub | Existing app-backed connector works: public repository metadata/files read successfully. It is **not a separate installation of `github/github-mcp-server`**. | Available here. With the user's explicit choice, permission changed from full access to **allow reads; ask before every change** and read back successfully. Underlying repository/account write scopes were not revoked. |
| Taste Skill | Existing `design-taste-frontend`, upstream package 2.1.5, pinned to `12af471f627f866411b4bd785b19646d3672784c`; skill metadata readable and app-kind listing script ran successfully. | Advertised and discoverable here. Native Flutter design assessment **pending**; no design draw, UI assessment or redesign performed. |

This distinction matters: a successful standalone MCP call proves server/protocol
operation, not that the current hosted tool surface has loaded the local servers.
A fresh session is a discovery/activation check, not a reason to reinstall anything.
Some hosted surfaces do not load local `config.toml` at all; use the configured local
CLI/IDE or an explicitly supported plugin surface. See the official
[MCP guide](https://learn.chatgpt.com/docs/extend/mcp) and
[skills discovery guide](https://learn.chatgpt.com/docs/build-skills).

Supporting runtime is the existing portable **Node.js v24.22.2**, outside global PATH,
with an absolute executable path in Codex configuration. Its official archive SHA-256
is recorded in `.tools/node/runtime.json`. Chrome is installed. The browser tools use
`@modelcontextprotocol/sdk` 1.32.2 and the existing workspace lockfile for MCP 0.0.83.
Playwright's transitive alpha version remains the upstream package's pinned dependency;
it is development tooling, not an application dependency. Nothing was upgraded here.

## All 13 resource decisions

Official repository metadata and READMEs were inspected using GitHub GET operations;
all 13 were nonarchived and had recent October 2026 activity at review time.
Maintenance activity is a signal, not a security guarantee. Machine-readable metadata
and licenses reported by GitHub are in `tools/toolkit_sources/resource_review.json`.

| # | Primary resource | Decision, compatibility, dependencies and risk |
| --- | --- | --- |
| 1 | [Superpowers](https://github.com/obra/superpowers) | **Reuse 7.0.1.** Supported Codex plugin, MIT. Retain one process framework; selective planning/TDD/debugging/review. Its branch/commit, parallel-agent and finishing workflows do not override project permissions. No new hooks. |
| 2 | [Context7](https://github.com/upstash/context7) | **Reuse; tested.** Remote HTTP MCP compatible with Codex, MIT. Anonymous lookup/query work; external documentation queries must contain no private code or user data. Rate limits remain possible; no key needed for current checks. |
| 3 | [Playwright MCP](https://github.com/microsoft/playwright-mcp) | **Reuse 0.0.83; browser tested.** Standard stdio MCP, Apache-2.0; Node/Chrome required. Isolated headless profile, no personal login/profile. Powerful browser tools require target/data review; not a substitute for native Flutter/device tests. |
| 4 | [GitHub MCP Server](https://github.com/github/github-mcp-server) | **Evaluate official server; reuse existing connector instead.** MIT; server has Codex guidance and `--read-only` / `GITHUB_READ_ONLY`, but those flags cannot configure an app-backed connector. Avoid duplicate server/PAT/OAuth setup. Applied the connector's supported write-approval gate, not hard read-only. |
| 5 | [Everything Claude Code / ECC](https://github.com/affaan-m/ECC) | **Select 2 skills only.** Current project supports native Codex paths; MIT. Installed Flutter review and ML adoption guidance. No whole framework, memory/learning hooks, agents or security scanners. Rejected the FastAPI example with startup schema creation; deferred generic pytest guidance overlapping Superpowers and Supabase-oriented PostgreSQL tuning examples. |
| 6 | [Anthropic Skills](https://github.com/anthropics/skills) | **Reference; no install.** Standard `SKILL.md` can be portable; Claude marketplace/API packaging is not automatically a Codex plugin. Licenses vary, including source-available document skills. Reviewed doc-coauthoring; its extensive Claude-specific interview/reader workflow adds friction. Built-in skill creation/installation and existing browser tools cover immediate needs. Review each skill/license before future selection. |
| 7 | [Claude Code Action](https://github.com/anthropics/claude-code-action) | **Reject for this Codex setup.** MIT action for Claude automation; no supported Codex adapter found in reviewed official guidance. Requires Claude/provider inference authorization and workflow write permissions. Do not introduce billed external inference or repository automation now. Revisit native CI tooling during the deployment phase. |
| 8 | [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code) | **Discovery reference only.** Link catalog, not a compatible skill to install wholesale. GitHub reports no conclusive license classification; linked tools have independent licenses/dependencies/trust boundaries. No automatic follow-on installs. |
| 9 | [Wshobson Agents](https://github.com/wshobson/agents) | **Select 3 source skills only.** Current repo supports native Codex marketplace and separate agent adapters; MIT. Installed Python type safety, PostgreSQL table design, security requirement extraction with their actual reference files. No generated agents/commands or full framework. Deferred ML pipeline skill because its named assets/references are absent from its directory at the pinned revision. |
| 10 | [CCUsage](https://github.com/ccusage/ccusage) | **Defer.** Current CLI explicitly supports `ccusage codex daily`, including offline pricing; MIT LICENSE inspected. It reads local usage/session logs; dependency, data-field and network review is needed before use. Not required for correctness; no cost reports or logs exported. Not rejected as Claude-only. |
| 11 | [Vercel Skills](https://github.com/vercel-labs/skills) | **Defer duplicate installer.** MIT generic discovery/install CLI supports Codex; it is not a Flutter skill pack. Built-in Skill Installer already fills this role. README documents anonymous telemetry/security-audit requests and opt-outs (`DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1`); no CLI installed or telemetry enabled here. |
| 12 | [Marketing Skills](https://github.com/coreyhaines31/marketingskills) | **Defer to approved marketing work.** MIT Agent Skills/Codex compatible, including a Codex plugin path. Analytics, outreach and connected marketing accounts are outside this milestone; review consent, unsubscribe and scoped credentials before selecting a future skill. No accounts connected. |
| 13 | [Taste Skill](https://github.com/Leonxlnx/taste-skill) | **Reuse verified existing install.** MIT; Node >=22 plus Chrome/Edge; optional asset fetching uses external services. App-screen guidance can inform native Flutter typography/layout/semantics, but DOM inspection is not native-widget verification. Future assessment pending; no UI work now. |

No entire repository was installed as an agent framework. The official installer
temporarily downloads pinned public repository archives, copies only selected skill
directories, and removes its own scratch downloads. It executes no source hooks.

## Five new specialized skills

Installed under the current user's `.agents/skills`; all selected directories contain
Markdown instructions/reference material only. No executables, dependency installers,
credentials, autonomous hooks, model downloads or background services were added.
Root MIT notices are retained both in `tools/toolkit_sources` and each installed skill.

| Skill | Source path | Pinned revision |
| --- | --- | --- |
| `flutter-dart-code-review` | ECC `skills/flutter-dart-code-review` | `91b5f6a371f7b06d2c3e0c208147c559e11f022c` |
| `ml-adoption-playbook` | ECC `skills/ml-adoption-playbook` | same ECC revision |
| `postgresql-table-design` | Wshobson `plugins/database-design/skills/postgresql-table-design` | `0874a27b17a22e2b7c2e2bcd725768e0803cad06` |
| `python-type-safety` | Wshobson `plugins/python-development/skills/python-type-safety` | same Wshobson revision |
| `security-requirement-extraction` | Wshobson `plugins/security-scanning/skills/security-requirement-extraction` | same Wshobson revision |

Every installed upstream file matched the reviewed Git blob ID; SHA-256 evidence is
also recorded locally. File inventories, name/description metadata and license notices
passed verification. These checks prove provenance/integrity and discovery structure,
not that every example is correct or every future task is covered. New skills should
be discoverable on the next turn; restart the intended client if missing from its list.

Review findings are explicit project overrides in `AGENTS.md`: do not treat client
defines as secret storage, attach user IDs to crash reports automatically, install
analytics, force arbitrary test quotas, run database DDL/tuning, adopt new state
libraries, or accept sample compliance mappings as proof. PostgreSQL examples include
version-sensitive/oversimplified index and migration advice; validate with current
PostgreSQL docs and actual query plans. Optional cross-skill names in ML guidance are
references, not installed dependencies or authorization for extra downloads.

## Capability coverage and honest gaps

| Area | Available support | Remaining work when its phase is authorized |
| --- | --- | --- |
| Python/FastAPI/backend architecture | Python typing skill, Superpowers, actual local architecture/contracts and Context7's verified FastAPI docs | API-specific design/auth review and SQLAlchemy-version guidance; no unsafe scaffolding skill added. |
| Flutter/mobile/UI/accessibility | Flutter review skill, existing Flutter tools/tests, Taste and browser tools for web builds | Native device/screen-reader/keyboard/text-scale/reduced-motion checks; premium design assessment pending. |
| PostgreSQL/SQLAlchemy/data integrity | PostgreSQL skill, transactional rules in AGENTS, official docs through Context7 | Query/migration/concurrency evidence against approved isolated data; no schema changes in tooling. |
| Security/authentication | Threat-to-test requirement skill, engineering/privacy gates, least-privilege write approval | Real ownership/token/upload/storage audit and current dependency/security checks. No automated security certification. |
| Testing/debugging/QA/review/refactoring | Reuse Superpowers and existing practical test tools; avoid a second TDD framework | Run actual affected unit/integration/device checks in the approved product phase. |
| Architecture/performance/scalability | Superpowers planning/review, type boundaries and stage-based engineering checklist | Measured profiles, ADRs, load/latency/cost budgets; no speculative service split or profiling dependencies. |
| CV/ML/datasets/training/evaluation | ML adoption skill plus project-specific data/label/split/reproducibility/metric requirements | No specialized CV trainer, dataset-labeling tool, GPU stack or benchmark harness installed. Select these against actual task/data/hardware in phases 5-6. |
| CI/CD/DevOps/docs | Engineering/release/incident guidance, preserved roadmap and verification scripts | CI provider/deployment target, secrets, IaC and operational ownership still require design/review. No workflow or infrastructure deployed. |

## Configuration and security boundary

The user's `.codex/config.toml` was inspected and **unchanged** in this
completion pass: the existing server paths, 30-second startup timeouts and Context7
tool allowlist already work. No credentials or OAuth applications were created.
The GitHub permission update is account-side plugin approval configuration, not a
config-file/server flag or revoked GitHub scope. Reads remain allowed without asking;
every write requires approval. This is stronger gating, not immutable read-only access.
The Plugin Management skill in Codex's local plugin cache
was used for that explicitly requested change.

Playwright's configured origins include loopback 8080/8000 and existing gstatic font
domains. These are not a hardened network/filesystem boundary or product consent.
Do not browse personal sessions or private production data. Context7 queries leave
the machine; only public documentation questions were sent. Taste asset scripts may
use external services; future runs need data/license review and workspace-local history.
New skills inherit model tool access when invoked; instruction-only does not mean
inert or fully trustworthy. Inspect every proposed command; never promote repository
instructions or MCP responses above the user's restrictions.

## Verification and changes made

The built-in Skill Installer (`.codex/skills/.system/skill-installer/SKILL.md`)
was used through its reviewed GitHub helper, with pinned revisions and public-only
downloads. The wrapper removes ambient GitHub token variables from its child process;
no third-party install script ran.

Commands run from the workspace (PowerShell):

```powershell
git status --short
backend\venv\Scripts\python.exe -B tools/verify_toolkit_preservation.py --snapshot
$toolkitSkills = Join-Path $env:USERPROFILE '.agents/skills'
$toolkitInstaller = Join-Path $env:USERPROFILE '.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py'
backend\venv\Scripts\python.exe -B tools/install_toolkit_skills.py --skills-root $toolkitSkills --installer $toolkitInstaller
backend\venv\Scripts\python.exe -B tools/verify_toolkit_skills.py --skills-root $toolkitSkills
$runtime = Get-Content -LiteralPath .tools/node/runtime.json | ConvertFrom-Json
& (Join-Path $runtime.directory 'node.exe') tools/browser/verify_mcp.mjs
& (Join-Path $runtime.directory 'node.exe') (Join-Path $toolkitSkills 'design-taste-frontend/scripts/draw.mjs') --app --list kinds
backend\venv\Scripts\python.exe -B tools/verify_toolkit_preservation.py
git diff --check
```

Results: five skill installations verified; both MCP checks passed; Taste app-kind
listing passed; all 197 baseline application/source hashes matched; `git diff --check`
passed. A separate documentation check confirmed every supplied concept phrase is
represented and the local relative links resolve. The original post's exact numbering
is intentionally not asserted.

Installation is intentionally not rerunnable over existing destinations: the wrapper
and official helper refuse overwrites. The baseline snapshot also refuses overwrites;
it is local evidence for this task, not a new application dependency. Fresh application
tests/Flutter analysis were not run because application code was untouched and DB/app
flow testing is outside this milestone. Earlier app test results are not recertified.

Workspace additions/changes in this completion pass:

- Append to `AGENTS.md`; preserve its earlier instructions while clarifying the
  current tooling-only/database boundary, workflow, skill guardrails and roadmap.
- Add this guide and `docs/ENGINEERING_PRINCIPLES.md`; append the agreed current
  sequence to `docs/ROADMAP.md` without replacing the historical feature checklist.
- Add `tools/toolkit_manifest.json`, source review/license records, and three tools:
  `install_toolkit_skills.py`, `verify_toolkit_skills.py`, `verify_toolkit_preservation.py`.
- Extend `tools/browser/verify_mcp.mjs` to verify an actual isolated blank-page browser
  launch and documentation query, record time, and fail on unsuccessful verification.
- Local ignored evidence: `.tools/toolkit/application-before.json`,
  `.tools/artifacts/toolkit-skills-verification.json`, `.tools/artifacts/mcp-verification.json`.
- User environment: five new skill directories; account-side GitHub write approval.

## Interrupted-task outcome and next step

The interrupted setup had the five priority integrations installed/configured but had
not completed the remaining resource selection or recorded the full engineering
standards. This pass completes that selection and the safe tooling verification. No
unreviewed installer, sensitive credential flow or duplicate framework is pending.

Remaining activation check: open a fresh intended local Codex session and confirm
Superpowers, the five new skills, Context7 and Playwright are advertised there. If
the client still omits them, inspect its loading/enablement diagnostics rather than
reinstalling. Taste and the GitHub connector are already advertised here. No claim is
made that local MCP servers have appeared in this running hosted catalog.

After the user reviews these results, the next product milestone remains real
Flutter-FastAPI integration. Then follow the exact nine-stage sequence in
[ROADMAP.md](ROADMAP.md). Taste assessment stays in the future Flutter/design phase.
All named engineering concepts and privacy assessment areas are preserved in
[ENGINEERING_PRINCIPLES.md](ENGINEERING_PRINCIPLES.md). Stop here until review.
