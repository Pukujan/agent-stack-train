# TASK-PCM-0022 — Test agent-facing PCM behavior with fresh-session holdouts

<!-- continuity:task {"acceptance":["Issue plans remain concise: problem, scope/non-goals, human-verifiable outcome, and proportionate verification; no mandatory PDD/SDD/TDD paperwork or test-type sub-issues","Deterministic contract/regression tests are the default; fresh-session holdouts apply to normative agent-facing promises; metamorphic/differential tests are used only when their oracle/comparator fits","A reproducible isolated holdout protocol records prompt, model, starting commit, allowed context, actions/files, commands, and objective outcomes","Each holdout assertion maps to visible issue/spec requirements; ambiguity or conflict is inconclusive, not a hidden failure; implementation choices are not requirements unless stated","Observable checks and independent review are primary; an LLM judgment alone cannot determine pass/fail","Normal lint/type/tests/PCM validation/package/diff checks remain separate gates, and acceptance requires a human-verifiable outcome in addition to passing tests","Recorded #34 baseline demonstrates detection of the worktree-path and task-activation misses; rerun corrected candidate and a fresh variant after #34 is delivered","Stop/close test workers and clean only disposable resources owned by the test; never publish/merge from the holdout harness"],"depends_on":["external:GitHub issue #34 (PCM-0019) corrected-candidate rerun"],"goal":"Define and validate a small, fair, risk-based way to test PCM promises about what a fresh agent can discover and do, without turning each issue into a paperwork or hidden-test burden.","id":"PCM-0022","next_action":"Commit and push the risk-based policy slice, open a PR for required CI/auto-merge, then rerun the corrected-candidate holdout after #34 is delivered before closing #39.","owner":"Codex current PCM session; GitHub issue #39","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Unit tests prove code-level behavior but not that a fresh agent can discover and follow normative repository guidance. Blind evaluation can be unfair when hidden expectations are absent from the visible contract, while applying every test method to every issue creates governance overhead. PCM needs a compact, auditable policy that prioritizes real user outcomes."} -->

- Status: active
- Owner: Codex current PCM session; GitHub issue #39
- Priority: P1
- Depends on: issue #34 for corrected-candidate fresh-session rerun; baseline evidence is already recorded there
- GitHub issue: [#39](https://github.com/Pukujan/project-continuity-modules/issues/39)
- Branch: `task/PCM-0022-agent-facing-holdouts`

## Goal

Establish a fair, repeatable, risk-based testing method for PCM's agent-facing workflow promises. Keep issues focused on user outcomes; tests are evidence for delivery, not the deliverable or a reason to expand governance.

## Scope

- Set a lightweight issue contract: problem, scope/non-goals, observable outcome, and proportionate verification.
- Keep deterministic tests as the default; specify when fresh-session holdouts, metamorphic/property tests, and differential tests are useful.
- Define an oracle/fairness protocol for fresh-session tests and record evidence in a reusable format.
- Add deterministic tests for the durable policy and test the existing #34 baseline against it where possible.
- Do not implement managed worktrees or other #34 behavior in this task. The corrected-candidate rerun depends on #34.

## Out of scope

- Separate PDD, SDD, or TDD documents for every issue.
- Sub-issues for each testing technique.
- Hidden tests for every task or subjective LLM-only scoring.
- Changes to Eval Lab, hades-v2, harness-on-steroids, or inference-recommendation-engine.

## Verification plan

- Focused deterministic policy/contract tests.
- Full test suite, Ruff, MyPy, compile check, package build, continuity validation, and diff check.
- Fresh-session holdout only for agent-facing acceptance cases; use isolated baseline/candidate and a fresh variant, with the candidate run after #34 changes are available.
- Keep the human-verifiable outcome explicit; passing CI alone does not close the work.

## Checkpoint log

### 2026-09-23 — activation

Completed:
- Reviewed PCM's operating contract, project checkpoint, specification, handoff/lifecycle/versioning guidance, package configuration, and CI workflow.
- Recorded the user-approved issue-level testing and ownership clarifications on GitHub issues #32 and #39.

Evidence:
- `git status --short --branch` before activation -> clean `main...origin/main`.
- `.github/workflows/ci.yml` -> separate Ruff, MyPy, compile, Python 3.11/3.12 tests, PCM validation, package-build, and auto-merge jobs.
- GitHub issue #39 -> risk-based testing, oracle safeguards, and governance-overhead limits recorded.
- GitHub issue #32 -> remote Git authority, issue-log ownership, project goal, and temporary local/session work distinguished.

Decisions:
- Start PCM-0022 before previously queued PCM-0019 because the user selected the testing-policy slice; keep #34 implementation separate.
- Use the remote Git repository for canonical code/project history; use GitHub issues as the actionable-work ledger; sessions/local state are temporary.
- Keep issue-level test plans concise. Do not require every testing technique or separate process artifact on each issue.

Changed:
- `tasks/TASK-PCM-0022-agent-facing-holdouts.md`
- `checkpoints/CURRENT.md`
- `HANDOFF.md`

Blocked/uncertain:
- Corrected fresh-session candidate run depends on issue #34; the recorded blind attempt is one baseline observation only.

Next:
- Commit and push this policy slice, open a PR for required CI/auto-merge, then rerun the corrected-candidate holdout after #34 is delivered before closing #39.

### 2026-09-23 — policy and fairness checks

Completed:
- Added a compact testing policy that starts with the human outcome, distinguishes default deterministic tests from risk-triggered holdouts, and explains when metamorphic and differential checks fit.
- Added blind-test oracle safeguards: visible requirements, observable checks, inconclusive handling for ambiguity, isolated snapshots, and no LLM-only scoring.
- Carried the short rule into canonical and generated agent instructions; added deterministic policy tests.
- Inspected `content-generation-modules` on GitHub for human-first writing patterns. Its issue list is empty; its guidance and merged PR descriptions—not hypothetical issue practice—are the relevant reference.
- Astra's research on issue/file freshness is captured in the durable #33 comment and cross-checked against the already-existing PCM-0015 implementation plan.

Evidence:
- `python -c "import sys,unittest; sys.path.insert(0,'src'); s=unittest.defaultTestLoader.discover('tests'); r=unittest.TextTestRunner(verbosity=2).run(s); raise SystemExit(not r.wasSuccessful())` -> 24 tests passed.
- `ruff check .` -> passed.
- `mypy src` -> passed, no issues.
- `python -m compileall -q src tests` -> passed.
- `continuity validate --root .` (invoked through the source CLI) -> VALID.
- `git diff --check` -> passed.
- `python -m build --outdir %TEMP%\\pcm-0022-build` -> sdist and wheel built.
- Independent #34 corrected-candidate fresh-session rerun -> not yet possible; #34 implementation is separate and not done.

Decisions:
- Human-first issue updates follow the content-system pattern: problem/consequence, outcome, evidence/boundary, and next action; no images unless they explain an outcome.
- Keep the broader file-freshness implementation within existing #33 and the issue-tracking lifecycle within #32; do not create duplicate umbrella plans.
- The #34-candidate holdout is a remaining acceptance dependency, so #39 must stay open until that result is captured.

Changed:
- `docs/TESTING_POLICY.md`
- `AGENTS.md`
- `templates/v1/software/AGENTS.md`
- `templates/v1/minimal/HANDOFF.md`
- `tests/test_agent_facing_testing_policy.py`
- `tasks/TASK-PCM-0022-agent-facing-holdouts.md`
- `checkpoints/CURRENT.md`
- `HANDOFF.md`

Blocked/uncertain:
- The corrected-candidate blind rerun depends on issue #34. The package build's small outputs remain in `%TEMP%\\pcm-0022-build`; cleanup was denied by the command safety policy. An empty `src/project_continuity.egg-info` directory remains after its generated files were removed.

Next:
- Commit and push the policy slice, open a PR for required CI/auto-merge, then rerun the corrected-candidate holdout after #34 is delivered before closing #39.

### 2026-09-23 17:16:33 UTC — Codex PCM-0022

<!-- continuity:checkpoint {"agent":"Codex PCM-0022","blocked":[],"changed":["docs/TESTING_POLICY.md; AGENTS.md; templates/v1/software/AGENTS.md; templates/v1/minimal/HANDOFF.md; tests/test_agent_facing_testing_policy.py; tasks/TASK-PCM-0022-agent-facing-holdouts.md; checkpoints/CURRENT.md; HANDOFF.md"],"completed":["Added human-first, risk-based testing policy and deterministic policy tests."],"decisions":["Keep #39 open until corrected-candidate fresh-session rerun after #34."],"evidence":["24 unittest tests passed; Ruff, MyPy, compile, continuity validate, diff check, and package build passed."],"next_action":"Open PR for required CI/auto-merge; after #34, rerun the candidate holdout before closing #39.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0022","timestamp":"2026-09-23T17:16:33Z"} -->

Completed:
- Added human-first, risk-based testing policy and deterministic policy tests.

Evidence:
- 24 unittest tests passed; Ruff, MyPy, compile, continuity validate, diff check, and package build passed.

Decisions:
- Keep #39 open until corrected-candidate fresh-session rerun after #34.

Changed:
- docs/TESTING_POLICY.md; AGENTS.md; templates/v1/software/AGENTS.md; templates/v1/minimal/HANDOFF.md; tests/test_agent_facing_testing_policy.py; tasks/TASK-PCM-0022-agent-facing-holdouts.md; checkpoints/CURRENT.md; HANDOFF.md

Blocked/uncertain:
- none

Next:
- Open PR for required CI/auto-merge; after #34, rerun the candidate holdout before closing #39.
