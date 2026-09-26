# TASK-PCM-0056 — Merge Window Guidance

<!-- continuity:task {"acceptance":["The sentence 'Arm auto-merge only after the increment's final push: a later push races the merge window and strands outside accepted history.' appears verbatim in all 9 checked-in copies (generator constant + AGENTS/HANDOFF/templates/.github) and the REQUIRED tuple of tests/test_github_progression_policy.py pins it; policy tests green on 3.11+3.12.","Full discover stays at the six known macOS-environmental failures; ruff clean on changed files; continuity docs render --check SYNCHRONIZED.","PR merged under six required hosted contexts + auto-merge with merge receipt on #175, then #166 closes as delivered (Refs #166, parent decision 5842002451)."],"depends_on":[],"goal":"Fold the merge-window discipline sentence into all 9 guidance copies and pin it in the policy test, per owner decision #166 5842002451 (Refs #175).","id":"PCM-0056","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/175","next_action":"Open PR for task/PCM-0056-merge-window, verify six contexts + auto-merge, post merge receipt on #175, then close #166.","owner":"owner/Astra planning","priority":"P3","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Two incidents tonight (stranded 791abd4 vs #167 window; #164/#165 class) proved the guard narrows but does not close the race; owner accepted the one-rule docs fix and closes #166 with it."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P3
- Depends on: none

## Goal

Fold the merge-window discipline into the shared guidance text per owner decision 5842002451: arm auto-merge only after the increment's final push; propagate to all checked-in copies and pin it in the policy test (Refs #166).

## Why

Two incidents tonight (stranded 791abd4 vs #167 window; #164/#165 class) proved the guard narrows but does not close the race; owner accepted the one-rule docs fix and closes #166 with it.

## Allowed files

- The 9 checked-in guidance copies: `AGENTS.md`, `HANDOFF.md`, `src/continuity/cli.py` (`GITHUB_PROGRESSION_GUIDANCE` string constant only), `templates/v1/minimal/{PROJECT,HANDOFF}.md`, `templates/v1/software/{AGENTS,README}.md`, `.github/{pull_request_template.md,ISSUE_TEMPLATE/task.md}`; `tests/test_github_progression_policy.py` (REQUIRED tuple); this task file; `checkpoints/CURRENT.md`; `.continuity/documents.json`; `docs/CONTINUITY_INDEX.md` (generated).

## Human outcome

Every fresh session — PCM's or any adopter's via `continuity init` — reads one explicit rule where the race used to be relearned by burning a stranded push: finish all pushes of an increment, THEN arm auto-merge. Tonight's `791abd4` strand (recovered only via #168) becomes a documented dead-end instead of a surprise.

## Scope and boundaries

- In scope: one sentence in the shared guidance block (generator + 8 checked-in copies), REQUIRED-phrase pin in the policy test, projection/CURRENT sync, #175 filing, #166 closeout flow.
- Out of scope: any CLI behavior change (PCM-0057/PCM-0054 own those), auto-rebase, GitHub merge-queue racing, PCM-0028 module registry (NOT released, direction 5830322199).
- Dependencies/uncertainty: parent decision #166 5842002451 (accepted); the sentence is normative guidance, enforcement is convention + the policy test against deletion.

## Acceptance criteria

- [x] Sentence present verbatim in all 9 copies + pinned in `tests/test_github_progression_policy.py` REQUIRED; policy tests 5 OK on Python 3.11 and 3.12.
- [x] Full discover 259 tests = the six known macOS-environmental broken names, zero new; ruff 0.6.9 on tree = only the two pre-existing ISC003; `continuity docs render --check` SYNCHRONIZED; adopter-profile init test proves `continuity init` output carries the new rule.
- [ ] PR merged under six required hosted contexts + auto-merge with merge receipt on #175, then #166 closed as delivered per the owner decision.

## Evidence and sources

- Observed: `grep -c` shows exactly 1 verbatim occurrence in each of the 9 files; policy suite OK on both interpreters; discover failure set identical to the `690b7f8` detached-worktree baseline (test_worktrees 3 FAIL + 1 ERROR, test_cli 2 FAIL).
- Parent: #166 decision 5842002451 (2026-09-26T01:32Z, owner session); leaf #175.
- Incidents motivating: `791abd4` stranded vs #167 window (#166 comment 5841072961 self-report); #164/#165 double-sync class.

## Related records

- Leaf #175 (PCM-0056); parent: #166 (decision 5842002451); depends: none.
- Primary writer: owner/Astra (omp session); branch task/PCM-0056-merge-window from `origin/main` `dcb75dc`; source issue revision: #175 body at filing; as-of 2026-09-26T01:35Z.
- Push receipt: continuity checkpoint request pcm-0056-guidance-20260926 (--receipt-issue 175 through the fixed tool path).

## Checkpoint log

No checkpoints yet.

### 2026-09-26 01:42:53 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["PCM-0046 arms still provider-429 (~04:05Z)."],"changed":["src/continuity/cli.py (constant only), AGENTS.md, HANDOFF.md, templates x4, .github x2, tests/test_github_progression_policy.py, tasks/TASK-PCM-0056-merge-window-guidance.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Merge-window sentence inserted verbatim in all 9 checked-in guidance copies (GITHUB_PROGRESSION_GUIDANCE generator + AGENTS/HANDOFF/templates/.github) per owner decision #166 5842002451; pinned in tests/test_github_progression_policy.py REQUIRED so CI catches deletion/drift and continuity init propagates it to adopters; task projection #175 + CURRENT decision-log paragraph + catalog/index."],"decisions":["Docs/guidance-only increment; no CLI behavior change; PCM-0057 (version NOTE) and PCM-0054-impl (receipt audit) proceed on separate branches per decisions 5842002582/5842002712."],"evidence":["grep -c = 1 per file (9); policy tests OK on 3.11+3.12 incl. adopted-profile init assertion; full discover 259 = six known broken names (test_worktrees 3F+1E, test_cli 2F) identical to 690b7f8 baseline; ruff@0.6.9 = two pre-existing ISC003 only; docs render --check SYNCHRONIZED; validate = device-local pcm-pinned only."],"next_action":"Open PR for task/PCM-0056-merge-window (final push already done), arm auto-merge, post merge receipt on #175, close #166 as delivered.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0056","timestamp":"2026-09-26T01:42:53Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"fef683b5a44b797a4b720187765d506d82bb3438df8d51e6fb5c4b656edff71d","request_id":"pcm-0056-guidance-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0056"} -->

Completed:
- Merge-window sentence inserted verbatim in all 9 checked-in guidance copies (GITHUB_PROGRESSION_GUIDANCE generator + AGENTS/HANDOFF/templates/.github) per owner decision #166 5842002451; pinned in tests/test_github_progression_policy.py REQUIRED so CI catches deletion/drift and continuity init propagates it to adopters; task projection #175 + CURRENT decision-log paragraph + catalog/index.

Evidence:
- grep -c = 1 per file (9); policy tests OK on 3.11+3.12 incl. adopted-profile init assertion; full discover 259 = six known broken names (test_worktrees 3F+1E, test_cli 2F) identical to 690b7f8 baseline; ruff@0.6.9 = two pre-existing ISC003 only; docs render --check SYNCHRONIZED; validate = device-local pcm-pinned only.

Decisions:
- Docs/guidance-only increment; no CLI behavior change; PCM-0057 (version NOTE) and PCM-0054-impl (receipt audit) proceed on separate branches per decisions 5842002582/5842002712.

Changed:
- src/continuity/cli.py (constant only), AGENTS.md, HANDOFF.md, templates x4, .github x2, tests/test_github_progression_policy.py, tasks/TASK-PCM-0056-merge-window-guidance.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- PCM-0046 arms still provider-429 (~04:05Z).

Next:
- Open PR for task/PCM-0056-merge-window (final push already done), arm auto-merge, post merge receipt on #175, close #166 as delivered.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
