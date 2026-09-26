# TASK-PCM-0055 — Receipt Json Encoding

<!-- continuity:task {"acceptance":["replace this with observable, task-specific acceptance checks"],"depends_on":[],"goal":"Fix the opt-in checkpoint receipt wire format: the post must send a JSON object {\"body\": ...} to gh api --input - so the shipped receipt path actually posts (Refs #171).","id":"PCM-0055","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/171","next_action":"define scope and observable acceptance checks, then begin bounded work","owner":"owner/Astra planning","priority":"P2","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"First production use of --receipt-repo/--receipt-issue on push 2f8dc7a failed with HTTP 400 Problems parsing JSON; raw markdown stdin rejected, JSON wrapper accepted (proof #166 comment 5841406124)."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Fix the opt-in checkpoint receipt wire format: the post must send a JSON object {"body": ...} to gh api --input - so the shipped receipt path actually posts (Refs #171).

## Why

First production use of --receipt-repo/--receipt-issue on push 2f8dc7a failed with HTTP 400 Problems parsing JSON; raw markdown stdin rejected, JSON wrapper accepted (proof #166 comment 5841406124).

## Allowed files

- `src/continuity/cli.py` (`publish_issue_receipt.post()`), `tests/test_receipt_json_encoding.py` (new), `tests/test_receipt_lookup.py` (contract update), `tasks/TASK-PCM-0055-receipt-json-encoding.md`, `checkpoints/CURRENT.md`, `.continuity/documents.json`, `docs/CONTINUITY_INDEX.md` (generated).

## Human outcome

A writer who passes `--receipt-repo/--receipt-issue` gets a `RECEIPT: post` line and a real comment instead of a post-push 400 with a retry command that would fail identically; the durable issue-log half of the contract finally matches the enforced Git half. The opt-in route frozen in #67 becomes usable for its only designed purpose.

## Scope and boundaries

- In scope: JSON wire format at the single `post()` in `publish_issue_receipt` (covers both leaf and parent `run_post` call sites through the injected runner); red-first tests incl. no-network real-subprocess shim; updating the one existing test that pinned raw-string equality (contract change disclosed below).
- Out of scope: default-on receipts / receipt-gap audit (#169 acceptance 2, owner territory); comment length limits; retry semantics changes; any other AGENTS/SPEC prose.
- Dependencies/uncertainty: depends on none; the 400 repro used the real gh binary; shim test proves stdin format without network; a second production success on this task's own checkpoint is the strongest evidence.

## Acceptance criteria

- [x] Red-first: `tests/test_receipt_json_encoding.py` 2 cases fail pre-fix (raw markdown rejected by `json.loads` / shim-captured stdin), pass post-fix; `test_short_page_without_marker_posts_once` updated to assert `json.loads(payload)["body"] == MARKER`.
- [x] All receipt/checkpoint suites + full discover at known baseline: 259 tests (257 baseline + 2 new), failures = the six known macOS-environmental (worktrees ×4, test_cli ×2); ruff pinned 0.6.9: only the two pre-existing ISC003 findings.
- [ ] This task's own `continuity checkpoint --receipt-repo Pukujan/project-continuity-modules --receipt-issue 171` posts successfully end-to-end (first production use of the fixed path), then PR under six contexts + auto-merge with merge receipt on #171.

## Evidence and sources

- Observed RED pre-fix: `unittest tests.test_receipt_json_encoding` → 2 errors (`JSONDecodeError: Expecting value: line 1 column 1`) at product-rev base `0fb5aca`.
- Observed GREEN post-fix: same 2 OK; `test_receipt_lookup` 3 OK; combined receipt/checkpoint/hook/stale suites OK; full discover as above.
- Production 400 + manual JSON success: #166 comment 5841406124 (raw-stdin failure recorded in PCM-0053 task + PR #170 body); defect filed as #171.
- Contract disclosure: `tests/test_receipt_lookup.py:63` previously asserted exact raw payload equality and now passes with the JSON wrapper — the changed pin is this task's intended behavior change, not a regression.

## Related records

- Leaf #171 (PCM-0055); parent: none; depends: none; related #67 (frozen opt-in route), #169 (policy detector, separate), #166 (push `2f8dc7a` where the defect was caught).
- Primary writer: owner/Astra (omp session); branch task/PCM-0055-receipt-json from `origin/main` `0fb5aca`; source issue revision: #171 body at filing; as-of 2026-09-26T00:25Z.
- Push receipt: continuity checkpoint request pcm-0055-fix-20260926 (opt-in flags exercise the fixed path).

## Checkpoint log

No checkpoints yet.

### 2026-09-26 00:34:14 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None for this slice; PCM-0046 arms still provider-429."],"changed":["src/continuity/cli.py, tests/test_receipt_json_encoding.py (new), tests/test_receipt_lookup.py, tasks/TASK-PCM-0055-receipt-json-encoding.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["JSON wire-format fix in publish_issue_receipt.post() (json.dumps({\"body\": ...}) into gh api --input -), red-first 2-case suite incl. no-network real-subprocess gh shim, disclosed contract update at tests/test_receipt_lookup.py:63, task projection + CURRENT + catalog/index. Dogfood: this very checkpoint command carries the first successful end-to-end production use of --receipt-repo/--receipt-issue."],"decisions":["Single post() encoding site covers leaf+parent paths; default-on-receipts question deliberately untouched (#169 acceptance 2)."],"evidence":["RED pre-fix at 0fb5aca: 2 JSONDecodeError; GREEN: 2 OK + all 12 receipt/checkpoint suites OK; full discover 259 tests = six known macOS-environmental failures (worktrees x4, test_cli x2), no new; ruff@0.6.9 clean on changed files."],"next_action":"Open PR for task/PCM-0055-receipt-json, verify six contexts + auto-merge, post merge receipt on #171.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0055","timestamp":"2026-09-26T00:34:14Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"a782522c65e80184905e9b4084f6ec26ceec0039c5269e3219e618e8bf53b374","request_id":"pcm-0055-fix-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0055"} -->

Completed:
- JSON wire-format fix in publish_issue_receipt.post() (json.dumps({"body": ...}) into gh api --input -), red-first 2-case suite incl. no-network real-subprocess gh shim, disclosed contract update at tests/test_receipt_lookup.py:63, task projection + CURRENT + catalog/index. Dogfood: this very checkpoint command carries the first successful end-to-end production use of --receipt-repo/--receipt-issue.

Evidence:
- RED pre-fix at 0fb5aca: 2 JSONDecodeError; GREEN: 2 OK + all 12 receipt/checkpoint suites OK; full discover 259 tests = six known macOS-environmental failures (worktrees x4, test_cli x2), no new; ruff@0.6.9 clean on changed files.

Decisions:
- Single post() encoding site covers leaf+parent paths; default-on-receipts question deliberately untouched (#169 acceptance 2).

Changed:
- src/continuity/cli.py, tests/test_receipt_json_encoding.py (new), tests/test_receipt_lookup.py, tasks/TASK-PCM-0055-receipt-json-encoding.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- None for this slice; PCM-0046 arms still provider-429.

Next:
- Open PR for task/PCM-0055-receipt-json, verify six contexts + auto-merge, post merge receipt on #171.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
