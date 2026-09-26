# TASK-PCM-0058 — Readability Rules

<!-- continuity:task {"acceptance": ["Red-first: test_readability_rules_ship_in_the_block plus 1.2.0 version pins fail before the guidance edit and pass after; rules + 1.2.0 marker present in generator constant, all 7 checked-in copies, module doc with changelog entry.", "Full discover at known baseline (six known names only); ruff clean on changed files; docs render --check SYNCHRONIZED; adopter propagation proven by the generated-artifact and init-profile tests.", "PR merged under six required hosted contexts + auto-merge with merge receipt on #180."], "depends_on": [], "goal": "Ship issue-log-format 1.2.0 readability rules: plain-word meaning before identifiers carry load, claim-first evidence, no bare acronyms/ids on first use — in the generator, all checked-in copies, the module doc, and pinned by tests (Refs #180).", "id": "PCM-0058", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/180", "next_action": "None; task closed. issue-log-format 1.2.0 merged at d46e0b7 (#183, six contexts); #180 CLOSED COMPLETED (merge receipt 5842744084 + append-only citation correction 5842754216). Sync residue (stale active marker) fixed in the PCM-0046 lifecycle increment, disclosed.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "completed", "why": "Tonight's own PR bodies (#176/#178) compressed evidence into unreadable identifier arithmetic while issue logs got praised; the gap is the tool-composed records, and adopters inherit it via continuity init."} -->

- Status: completed
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Ship issue-log-format 1.2.0 readability rules: plain-word meaning before identifiers carry load, claim-first evidence, no bare acronyms/ids on first use — in the generator, all checked-in copies, the module doc, and pinned by tests (Refs #180).

## Why

Tonight's own PR bodies (#176/#178) compressed evidence into unreadable identifier arithmetic while issue logs got praised; the gap is the tool-composed records, and adopters inherit it via continuity init.

## Allowed files

- `src/continuity/cli.py` (ISSUE_LOG_FORMAT_POLICY_VERSION/MARKER/GUIDANCE), the 7 checked-in copies carrying the block (AGENTS.md, HANDOFF.md, templates/v1/minimal/HANDOFF.md, templates/v1/software/{AGENTS,README}.md, .github/{pull_request_template,ISSUE_TEMPLATE/task}.md), `docs/ISSUE_LOG_FORMAT.md`, `tests/test_issue_log_format.py`, this task file, `checkpoints/CURRENT.md`, `.continuity/documents.json`, `docs/CONTINUITY_INDEX.md` (generated).

## Human outcome

A newcomer opening any PCM PR, checkpoint, or CURRENT projection follows the first sentence without prior context: identifiers arrive with plain-word meanings, evidence reads as a claim before it reads as arithmetic, and the same standard ships to every adopter through `continuity init`. Tonight's #178 body is the recorded before/after example.

## Scope and boundaries

- In scope: the Readability-rules paragraph in the issue-log-format guidance block (1.2.0), module-doc section + changelog, copy propagation, test pin (red-first).
- Out of scope: retroactive rewriting of published records (append-only; the #178 exemplar is an added comment, not an edit); enforcement beyond the REQUIRED-phrase pins; PCM-0028 module registry (not released, direction 5830322199).
- Dependencies/uncertainty: depends on #180 (the filed problem record); the 1.2.0 marker bump means stale adopter copies warn under `continuity validate` exactly as with 1.1.0 diagram rules — documented update path reused.

## Acceptance criteria

- [x] Red-first: `test_readability_rules_ship_in_the_block` + 1.2.0 pins fail before the guidance edit, pass after; all 7 checked-in copies + module doc carry the rules and the 1.2.0 marker; guidance/policy suites green (see checkpoint entry for counts).
- [x] Full discover 264 tests (263 + 1) = six known macOS-environmental failures, zero new; ruff@0.6.9 = two pre-existing ISC003; docs render --check SYNCHRONIZED; validate = device-local pcm-pinned only.
- [ ] PR merged under six contexts + auto-merge; merge receipt on #180.

## Evidence and sources

Link repository state at a revision and cite external factual claims directly. Record commands and results for claims that need verification.

## Reproduction details (only when needed)

Base e726ea4 (#179). RED observed: 16 failures (version pins + readability phrases) before the cli.py/doc/copies edits; GREEN: test_issue_log_format + test_github_progression_policy OK; discover 264 as above. Adopter propagation proven by test_every_generated_artifact_carries_the_block + the init-profile tests, not by hand.

## Related records

- Leaf #180 (PCM-0058); parent: none; depends: none; related #99 (format module origin), #126 (diagram-rules precedent for the mechanism), #169/#162 (adjacent record-quality work this session).
- Primary writer: owner/Astra (omp session); branch task/PCM-0058-readability-rules from origin/main e726ea4; source issue revision: #180 body at filing; as-of 2026-09-26T02:45Z.
- Push receipt: continuity checkpoint request pcm-0058-readability-20260926 (--receipt-issue 180).

## Checkpoint log

No checkpoints yet.

### 2026-09-26 03:01:37 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None for this slice; #181/#182 await owner scope answers."],"changed":["src/continuity/cli.py, AGENTS.md, HANDOFF.md, templates/v1/minimal/HANDOFF.md, templates/v1/software/AGENTS.md, templates/v1/software/README.md, .github/pull_request_template.md, .github/ISSUE_TEMPLATE/task.md, docs/ISSUE_LOG_FORMAT.md, tests/test_issue_log_format.py, tasks/TASK-PCM-0058-readability-rules.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Readability rules shipped into the issue-log-format module 1.1.0 -> 1.2.0: plain-word meaning before identifiers carry load; claim-first evidence with numbers as support; no unexplained acronym/bare id on first use; PR openings and checkpoint Completed/Next lead with one problem sentence; applies to CURRENT/checkpoint exactly as issue logs. Updated the GITHUB guidance generator constant, all 7 checked-in copies, docs/ISSUE_LOG_FORMAT.md (section + changelog), tests (red-first readability + version pins), task projection #180, CURRENT, catalog/index."],"decisions":["1.2.0 marker bump reuses the 1.1.0 diagram-rules propagation mechanism; no retroactive rewriting of published records."],"evidence":["RED observed 16 failures before implementation (version pins + readability phrases); GREEN: issue-log-format + progression + records suites OK; discover 264 = six known macOS-environmental names, zero new; ruff = two pre-existing ISC003; docs render --check SYNCHRONIZED; validate = device-local pcm-pinned only. Before/after exemplar: PR #178 comment 5842450065 (append-only, body not rewritten)."],"next_action":"Open PR for task/PCM-0058-readability-rules, arm auto-merge after this final push, merge receipt on #180.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0058","timestamp":"2026-09-26T03:01:37Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"efb56b6a80c9fe12b686ccb6fc7244455320018b916d5d54ee86755b90020025","request_id":"pcm-0058-readability-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0058"} -->

Completed:
- Readability rules shipped into the issue-log-format module 1.1.0 -> 1.2.0: plain-word meaning before identifiers carry load; claim-first evidence with numbers as support; no unexplained acronym/bare id on first use; PR openings and checkpoint Completed/Next lead with one problem sentence; applies to CURRENT/checkpoint exactly as issue logs. Updated the GITHUB guidance generator constant, all 7 checked-in copies, docs/ISSUE_LOG_FORMAT.md (section + changelog), tests (red-first readability + version pins), task projection #180, CURRENT, catalog/index.

Evidence:
- RED observed 16 failures before implementation (version pins + readability phrases); GREEN: issue-log-format + progression + records suites OK; discover 264 = six known macOS-environmental names, zero new; ruff = two pre-existing ISC003; docs render --check SYNCHRONIZED; validate = device-local pcm-pinned only. Before/after exemplar: PR #178 comment 5842450065 (append-only, body not rewritten).

Decisions:
- 1.2.0 marker bump reuses the 1.1.0 diagram-rules propagation mechanism; no retroactive rewriting of published records.

Changed:
- src/continuity/cli.py, AGENTS.md, HANDOFF.md, templates/v1/minimal/HANDOFF.md, templates/v1/software/AGENTS.md, templates/v1/software/README.md, .github/pull_request_template.md, .github/ISSUE_TEMPLATE/task.md, docs/ISSUE_LOG_FORMAT.md, tests/test_issue_log_format.py, tasks/TASK-PCM-0058-readability-rules.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- None for this slice; #181/#182 await owner scope answers.

Next:
- Open PR for task/PCM-0058-readability-rules, arm auto-merge after this final push, merge receipt on #180.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
