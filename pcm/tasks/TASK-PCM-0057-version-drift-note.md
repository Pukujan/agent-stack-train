# TASK-PCM-0057 — Version Drift Note

<!-- continuity:task {"acceptance":["version_drift_note returns a NOTE naming both versions on mismatch, None on match / non-Python checkout / malformed version file; publish_checkpoint prints it on every publish (observability only, never refuses).","Red-first tests/test_version_note.py (4 cases) fails before and passes after; checkpoint hygiene/retry/stale-base suites + full discover stay at the known baseline (259 tests, six known macOS-environmental names); ruff 0.6.9 clean on changed files.","Package version raised 0.5.0 -> 0.6.0 (docs/VERSIONING.md MINOR rule: backward-compatible safety capability; PCM-0055 changed wire behavior under the old label); docs/ARCHITECTURE.md current-version line and README dated note updated; version-pin test updated; merge receipt on #162 closes acceptance 2 end-to-end."],"depends_on":[],"goal":"Deliver owner decision B on #162: publish_checkpoint prints a version-drift NOTE comparing installed CLI vs checkout version (observability only, no refusal), and bump the package to 0.6.0 so the two 0.5.0 wire behaviors are distinguishable.","id":"PCM-0057","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/177","next_action":"Commit product, checkpoint with --receipt-issue 162, open PR, arm auto-merge after final push, post merge receipt on #162.","owner":"owner/Astra planning","priority":"P2","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"#162 incident: a stale 0.4.0 install composed the sanitizer-bypassing checkpoint; owner chose option B (5842002582). 0.5.0 now denotes two receipt-posting behaviors (PCM-0055 changed wire format), so continuity --version must distinguish them."} -->

- Status: completed
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Deliver owner decision B on #162: publish_checkpoint prints a version-drift NOTE comparing installed CLI vs checkout version (observability only, no refusal), and bump the package to 0.6.0 so the two 0.5.0 wire behaviors are distinguishable.

## Why

#162 incident: a stale 0.4.0 install composed the sanitizer-bypassing checkpoint; owner chose option B (5842002582). 0.5.0 now denotes two receipt-posting behaviors (PCM-0055 changed wire format), so continuity --version must distinguish them.

## Allowed files

- `src/continuity/cli.py` (`version_drift_note` + one print in `publish_checkpoint`), `src/continuity/__init__.py`, `tests/test_version_note.py` (new), `tests/test_issue_log_format.py` (pin), `docs/VERSIONING.md`, `docs/ARCHITECTURE.md`, `README.md` (dated note), this task file, `checkpoints/CURRENT.md`, `.continuity/documents.json`, `docs/CONTINUITY_INDEX.md` (generated).

## Human outcome

A stale installed CLI can no longer silently compose a checkpoint the way `d854175` did (#162): the publish path itself prints which build is running versus what the checkout declares, so drift is visible at the moment it matters, and `continuity --version` distinguishes the pre-PCM-0055 0.5.0 from 0.6.0.

## Scope and boundaries

- In scope: pure version-drift NOTE function + one call site in `publish_checkpoint`; 0.6.0 version bump with VERSIONING entry and doc claims; red-first tests.
- Out of scope: any refusal gate (owner chose B over A on #162); `--allow-version-drift` flag; recovery-path changes; #169 receipt-audit scope (PCM-0054's next increment).
- Dependencies/uncertainty: depends on #162 decision 5842002582 (recorded); NOTE is cosmetic for users who ignore stdout — accepted tradeoff of option B.

## Acceptance criteria

- [x] `version_drift_note`: NOTE naming both versions on mismatch; None on match, non-Python checkout, or malformed version file; printed by `publish_checkpoint` on every publish (never refuses).
- [x] Red-first `tests/test_version_note.py` 4 cases: 1 error pre-fix (import fails) -> all OK post-fix; hygiene/retry/stale-base/json-encoding suites 53 OK; full discover 263 tests (259 + 4 new) = six known broken names (test_worktrees 3F+1E, test_cli 2F), zero regressions; ruff@0.6.9: pre-existing ISC003 only.
- [x] Version 0.5.0 -> 0.6.0: `docs/VERSIONING.md` entry (MINOR: backward-compatible safety capability; PCM-0055 changed receipt wire behavior under the old label), ARCHITECTURE current-line, README dated note (pinned evidence table left intact — rewriting cells against a stale pin would be false evidence), pin test updated.
- [x] PR #178 MERGED via auto-merge at squash `bcc0bf3`, 2026-09-26T02:13:21Z, six required contexts green on the exact candidate; merge receipts on #177 + #162; #162 closed as delivered.

## Evidence and sources

Link repository state at a revision and cite external factual claims directly. Record commands and results for claims that need verification.

## Reproduction details (only when needed)

Base `ff84e91` (#176). RED: `PYTHONPATH=src python3.12 -m unittest tests.test_version_note` -> ImportError (function absent). GREEN: 4 OK; combined 53 OK; discover 263 = six known names. Non-Python adopter checkouts degrade to silence by design (no version file to compare).

## Related records

- Leaf #177 (PCM-0057 implementation; needed because `require_issue_identity` refuses receipts on issues that do not name the task id); parent: #162 (decision 5842002582); depends: #162 decision 5842002582.
- Primary writer: owner/Astra (omp session); branch task/PCM-0057-version-note from `origin/main` `ff84e91`; as-of 2026-09-26T01:55Z.
- Push receipt: pcm-0057-drift-20260926 -> leaf receipt 5842251679 on #177 (tool-posted via the PCM-0055 path, push `beba5ab`); CURRENT-sync push `ccd882e`; PR #178 merged `bcc0bf3`, merge receipts on #177/#162.

## Checkpoint log

No checkpoints yet.

### 2026-09-26 02:08:58 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None for this slice; PCM-0046 arms window ~04:05Z."],"changed":["src/continuity/cli.py, src/continuity/__init__.py, tests/test_version_note.py (new), tests/test_issue_log_format.py, docs/VERSIONING.md, docs/ARCHITECTURE.md, README.md, tasks/TASK-PCM-0057-version-drift-note.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["version_drift_note() + print in publish_checkpoint (option B per #162 5842002582); package 0.5.0 -> 0.6.0 with VERSIONING entry, ARCHITECTURE line, README dated note (pinned 0b3be9c table left intact by design); red-first tests/test_version_note.py 4 cases; task projection #177 + catalog/index."],"decisions":["0.6.0 MINOR (backward-compatible safety capability per docs/VERSIONING.md) \u2014 PCM-0055 changed receipt wire behavior under the old 0.5.0 label; NOTE never refuses."],"evidence":["RED: ImportError before function (1 error); GREEN: 4 OK; combined 53 OK (hygiene/retries/stale-base/json-encoding/issue-log-format pin); discover 263 = exactly the six known macOS-environmental names, zero new; ruff@0.6.9 = two pre-existing ISC003; docs render --check SYNCHRONIZED."],"next_action":"Arm auto-merge on this PR now that the final push is complete, post merge receipt on #177/#162, close #162 acceptance 2.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0057","timestamp":"2026-09-26T02:08:58Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"73f4ef6f2181caa3382bca94de78f18d0ed271f2aca7054fd2c0e2187fa64a62","request_id":"pcm-0057-drift-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0057"} -->

Completed:
- version_drift_note() + print in publish_checkpoint (option B per #162 5842002582); package 0.5.0 -> 0.6.0 with VERSIONING entry, ARCHITECTURE line, README dated note (pinned 0b3be9c table left intact by design); red-first tests/test_version_note.py 4 cases; task projection #177 + catalog/index.

Evidence:
- RED: ImportError before function (1 error); GREEN: 4 OK; combined 53 OK (hygiene/retries/stale-base/json-encoding/issue-log-format pin); discover 263 = exactly the six known macOS-environmental names, zero new; ruff@0.6.9 = two pre-existing ISC003; docs render --check SYNCHRONIZED.

Decisions:
- 0.6.0 MINOR (backward-compatible safety capability per docs/VERSIONING.md) — PCM-0055 changed receipt wire behavior under the old 0.5.0 label; NOTE never refuses.

Changed:
- src/continuity/cli.py, src/continuity/__init__.py, tests/test_version_note.py (new), tests/test_issue_log_format.py, docs/VERSIONING.md, docs/ARCHITECTURE.md, README.md, tasks/TASK-PCM-0057-version-drift-note.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- None for this slice; PCM-0046 arms window ~04:05Z.

Next:
- Arm auto-merge on this PR now that the final push is complete, post merge receipt on #177/#162, close #162 acceptance 2.

### 2026-09-26 02:22:28 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None; #162 closes on the merge receipt for this PR."],"changed":["tasks/TASK-PCM-0057-version-drift-note.md"],"completed":["Closeout projection: acceptance 3 checked with merge facts (PR #178 merged bcc0bf3 six contexts); receipt id corrected to API-verified 5842251679; status completed. Guard self-observation: the first attempt was REFUSED by the PCM-0053 stale-base guard on the overlapping closeout paths; resolved via cherry-pick onto post-merge main + this dedicated closeout branch (repo precedent: PCM-0051/0052/0043 closeout branches; no force-push)."],"decisions":["Old pushed branch tip f33796f (pre-rebase) left untouched on origin; superseded by this branch's history; #162 closes on this PR's merge receipt."],"evidence":["gh pr view 178 -> MERGED 02:13:21Z bcc0bf30c77d6926e2bbd6fcde686d1a4161c5e8; comments API on #177 -> 5842251679 (pcm:receipt-v2 task=PCM-0057 request=pcm-0057-drift-20260926)."],"next_action":"Open closeout PR, arm auto-merge AFTER this push (PCM-0056 rule), verify six contexts, post merge receipts on #177/#162, close #162.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0057","timestamp":"2026-09-26T02:22:28Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"89c0055f192a2c33ff096b69d62ff5ae9b78116dbae9eee88614ee1f395534a7","request_id":"pcm-0057-closeout-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0057"} -->

Completed:
- Closeout projection: acceptance 3 checked with merge facts (PR #178 merged bcc0bf3 six contexts); receipt id corrected to API-verified 5842251679; status completed. Guard self-observation: the first attempt was REFUSED by the PCM-0053 stale-base guard on the overlapping closeout paths; resolved via cherry-pick onto post-merge main + this dedicated closeout branch (repo precedent: PCM-0051/0052/0043 closeout branches; no force-push).

Evidence:
- gh pr view 178 -> MERGED 02:13:21Z bcc0bf30c77d6926e2bbd6fcde686d1a4161c5e8; comments API on #177 -> 5842251679 (pcm:receipt-v2 task=PCM-0057 request=pcm-0057-drift-20260926).

Decisions:
- Old pushed branch tip f33796f (pre-rebase) left untouched on origin; superseded by this branch's history; #162 closes on this PR's merge receipt.

Changed:
- tasks/TASK-PCM-0057-version-drift-note.md

Blocked/uncertain:
- None; #162 closes on the merge receipt for this PR.

Next:
- Open closeout PR, arm auto-merge AFTER this push (PCM-0056 rule), verify six contexts, post merge receipts on #177/#162, close #162.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
