# TASK-PCM-0009 — Helper/Target Identity Boundary

<!-- continuity:task {"acceptance":["helper repository and target repository roles are explicit at cold start","continuity preflight classifies helper, valid target, missing adoption, and invalid pseudo-integration without crashing","mature repository adoption has a documented non-destructive overlay path","CLI/package and protocol versions are explicitly separated","automated regression tests and repository validation pass in CI","a fresh-session blind acceptance test passes before release/tag"],"depends_on":[],"goal":"Prevent Project Continuity Modules from being mistaken for the target project when agents use it as a helper for long-running work.","id":"PCM-0009","next_action":"Get PR #16 CI green, then run docs/BLIND_TEST.md in a fresh uncontaminated agent session; do not tag 0.2.0 before it passes.","owner":"ChatGPT/Sol current PCM hardening session; GitHub issue #15","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"A real long-running task conflated the helper repository with the target repository and produced continuity-looking but invalid target state, showing that PCM's bootstrap/adoption boundary was not strong enough."} -->

- Status: completed
- Owner: ChatGPT/Sol current PCM hardening session; GitHub issue #15
- Priority: P0
- Depends on: none
- GitHub issue: #15
- Pull request: #16

## Goal

Prevent Project Continuity Modules from being mistaken for the target project when agents use it as a helper for long-running work.

## Why

A real long-running task conflated the helper repository with the target repository and produced continuity-looking but invalid target state. The failure shows that PCM's cold-start mode boundary, mature-repository adoption path, and fail-closed validation were insufficiently explicit.

## Allowed files

- `AGENTS.md`
- `README.md`
- `docs/TARGET_ADOPTION.md`
- `docs/BLIND_TEST.md`
- `docs/VERSIONING.md`
- `src/continuity/cli.py`
- `tests/**`
- `.github/workflows/**`
- `pyproject.toml`
- this task, `checkpoints/CURRENT.md`, and `HANDOFF.md`

Do not modify unrelated helper modules or any target project's runtime/product repository.

## Acceptance criteria

- [x] helper repository and target repository roles are explicit at cold start.
- [x] `continuity preflight` classifies helper/target/adoption failure states.
- [x] malformed pseudo-integrations fail closed instead of crashing.
- [x] mature repository adoption has a documented non-destructive overlay path.
- [x] CLI/package and protocol versions are explicitly separated.
- [x] automated tests and repository validation pass in CI.
- [x] a fresh-session blind acceptance test passes before release/tag.

## Checkpoint log

### 2026-09-23 01:35:00 UTC — ChatGPT/Sol PCM-0009 hardening

<!-- continuity:checkpoint {"agent":"ChatGPT/Sol PCM-0009 hardening","blocked":["Blind acceptance must be performed by a fresh session that has not seen the incident analysis."],"changed":["AGENTS.md","README.md","docs/TARGET_ADOPTION.md","docs/BLIND_TEST.md","docs/VERSIONING.md","src/continuity/cli.py","tests/test_cli.py",".github/workflows/ci.yml","pyproject.toml","tasks/TASK-PCM-0009-helper-target-boundary.md","checkpoints/CURRENT.md","HANDOFF.md"],"completed":["Created durable GitHub issue #15 for the incident.","Added explicit helper/target identity gate and target preflight command.","Added mature-target adoption guidance and deterministic regression coverage.","CI exposed and the branch fixed an additional fail-open KeyError on malformed config.","Separated CLI/package version 0.2.0 from protocol version 0.1.0-draft.","Defined a cold-start blind acceptance test as a pre-release gate."],"decisions":["Treat the new preflight command as a backward-compatible CLI minor release (0.2.0) while leaving the repository protocol at 0.1.0-draft.","Do not release or tag 0.2.0 until automated CI and a genuinely fresh blind session both pass."],"evidence":["GitHub issue #15 records the incident and acceptance criteria.","PR #16 contains the candidate fix.","First CI run failed because malformed config caused validate_repo to index missing canonical data; regression now asserts clean invalid errors instead of a crash."],"next_action":"Get PR #16 CI green, then run docs/BLIND_TEST.md in a fresh uncontaminated agent session; do not tag 0.2.0 before it passes.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0009","timestamp":"2026-09-23T01:35:00Z"} -->

Completed:
- Created durable GitHub issue #15 for the incident.
- Added explicit helper/target identity gate and target preflight command.
- Added mature-target adoption guidance and deterministic regression coverage.
- CI exposed and the branch fixed an additional fail-open `KeyError` on malformed config.
- Separated CLI/package version 0.2.0 from protocol version 0.1.0-draft.
- Defined a cold-start blind acceptance test as a pre-release gate.

Evidence:
- GitHub issue #15 records the incident and acceptance criteria.
- PR #16 contains the candidate fix.
- First CI run failed because malformed config caused `validate_repo` to index missing canonical data; regression now asserts clean invalid errors instead of a crash.

Decisions:
- Treat the new preflight command as a backward-compatible CLI minor release (0.2.0) while leaving the repository protocol at 0.1.0-draft.
- Do not release or tag 0.2.0 until automated CI and a genuinely fresh blind session both pass.

Changed:
- PCM-0009 bounded files listed above.

Blocked/uncertain:
- Blind acceptance must be performed by a fresh session that has not seen the incident analysis.

Next:
- Get PR #16 CI green, then run `docs/BLIND_TEST.md` in a fresh uncontaminated agent session; do not tag 0.2.0 before it passes.

### 2026-09-23 01:35:00 UTC — GitHub Actions verification

<!-- continuity:checkpoint {"agent":"GitHub Actions verification","blocked":["Fresh-session blind acceptance is still pending and must be run outside this incident-aware session."],"changed":["none"],"completed":["Verified PCM-0009 candidate after fail-closed validator fix."],"decisions":["Keep PR #16 unmerged and do not tag 0.2.0 until the blind acceptance test passes."],"evidence":["PCM CI run 35806854531 completed successfully.","11 unit tests passed.","PYTHONPATH=src python -m continuity validate --root . -> VALID."],"next_action":"Run docs/BLIND_TEST.md in a fresh uncontaminated agent session and record the result before merge/tag.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0009","timestamp":"2026-09-23T01:35:00Z"} -->

Completed:
- Verified PCM-0009 candidate after the fail-closed validator fix.

Evidence:
- PCM CI run 35806854531 completed successfully.
- 11 unit tests passed.
- `PYTHONPATH=src python -m continuity validate --root .` -> `VALID`.

Decisions:
- Keep PR #16 unmerged and do not tag 0.2.0 until the blind acceptance test passes.

Changed:
- none.

Blocked/uncertain:
- Fresh-session blind acceptance is still pending and must be run outside this incident-aware session.

Next:
- Run `docs/BLIND_TEST.md` in a fresh uncontaminated agent session and record the result before merge/tag.

### 2026-09-23 05:10 UTC — Codex automated fresh-session blind acceptance

<!-- continuity:checkpoint {"agent":"Codex automated fresh-session blind acceptance","blocked":[],"changed":["tasks/TASK-PCM-0009-helper-target-boundary.md","checkpoints/CURRENT.md","HANDOFF.md"],"completed":["Ran the PCM-0009 blind acceptance scenario with a fresh independent test agent that received only ordinary helper/target instructions.","Recorded that continuity state was created in the disposable target repository rather than the PCM helper repository.","Confirmed the target product/runtime files remained untouched and the helper repository remained unchanged."],"decisions":["Accept the helper/target boundary as passing because the fresh agent identified the target as the owner, used PCM only as tooling, ran target preflight and validation, and did not create competing helper-owned project state.","Keep PCM-0009 separately scoped from PCM-0010 while allowing the stacked Git delivery to proceed through the protected main branch."],"evidence":["Fresh agent session 01a0cc9e-d9d9-7a80-b950-5ac8f081756d -> target continuity owner identified correctly.","Target preflight -> MODE: TARGET_VALID; target validation -> VALID.","Fresh agent reported helper self-validation -> VALID and 14 tests passed.","Fresh agent reported product src/ unchanged and helper repository unchanged.","Property/metamorphic checks -> PASS: relocation, unrelated-file addition, metadata reordering, malformed-config fail-closed behavior, and helper classification invariance."],"next_action":"Push this completed checkpoint to PR #16, verify protected-main CI, and allow automatic merge." ,"protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0009","timestamp":"2026-09-23T05:10:00Z"} -->

Completed:
- Ran the PCM-0009 blind acceptance scenario with a fresh independent test agent that received only ordinary helper/target instructions.
- Recorded that continuity state was created in the disposable target repository rather than the PCM helper repository.
- Confirmed the target product/runtime files remained untouched and the helper repository remained unchanged.

Evidence:
- Fresh agent session `01a0cc9e-d9d9-7a80-b950-5ac8f081756d` identified the target as the continuity owner.
- Target preflight -> `MODE: TARGET_VALID`; target validation -> `VALID`.
- Fresh agent reported helper self-validation -> `VALID` and 14 tests passed.
- Fresh agent reported product `src/` unchanged and helper repository unchanged.
- Property/metamorphic checks -> `PASS`: relocation, unrelated-file addition, metadata reordering, malformed-config fail-closed behavior, and helper classification invariance.

Decisions:
- Accept the helper/target boundary as passing because the fresh agent identified the target as the owner, used PCM only as tooling, ran target preflight and validation, and did not create competing helper-owned project state.
- Keep PCM-0009 separately scoped from PCM-0010 while allowing the stacked Git delivery to proceed through the protected main branch.

Changed:
- `tasks/TASK-PCM-0009-helper-target-boundary.md`
- `checkpoints/CURRENT.md`
- `HANDOFF.md`

Blocked/uncertain:
- none

Next:
- Push this completed checkpoint to PR #16, verify protected-main CI, and allow automatic merge.

### 2026-09-23 05:02:18 UTC — Codex automated PCM-0009 release gate

<!-- continuity:checkpoint {"agent":"Codex automated PCM-0009 release gate","blocked":[],"changed":["tasks/TASK-PCM-0009-helper-target-boundary.md","checkpoints/CURRENT.md","HANDOFF.md"],"completed":["Recorded the fresh-session blind acceptance pass and marked every PCM-0009 acceptance item complete.","Confirmed protected-main delivery is the next automated gate."],"decisions":["The PCM-0009 candidate is eligible for automatic merge after protected-main CI passes; no manual review is required."],"evidence":["Fresh independent agent 01a0cc9e-d9d9-7a80-b950-5ac8f081756d -> target-owned continuity, TARGET_VALID preflight, VALID target, unchanged product src, unchanged helper repository.","Ruff, MyPy, compileall, 14 unit tests, PCM validation -> all pass.","Property/metamorphic checks -> PASS."],"next_action":"Verify the protected-main pull-request run and allow automatic merge into main.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0009","timestamp":"2026-09-23T05:02:18Z"} -->

Completed:
- Recorded the fresh-session blind acceptance pass and marked every PCM-0009 acceptance item complete.
- Confirmed protected-main delivery is the next automated gate.

Evidence:
- Fresh independent agent 01a0cc9e-d9d9-7a80-b950-5ac8f081756d -> target-owned continuity, TARGET_VALID preflight, VALID target, unchanged product src, unchanged helper repository.
- Ruff, MyPy, compileall, 14 unit tests, PCM validation -> all pass.
- Property/metamorphic checks -> PASS.

Decisions:
- The PCM-0009 candidate is eligible for automatic merge after protected-main CI passes; no manual review is required.

Changed:
- tasks/TASK-PCM-0009-helper-target-boundary.md
- checkpoints/CURRENT.md
- HANDOFF.md

Blocked/uncertain:
- none

Next:
- Verify the protected-main pull-request run and allow automatic merge into main.

## Handoff

Read PROJECT → CURRENT → this task → AGENTS → docs/TARGET_ADOPTION.md → docs/BLIND_TEST.md. Preserve the helper/target boundary and do not use a target project to test by modifying its runtime/product code.
