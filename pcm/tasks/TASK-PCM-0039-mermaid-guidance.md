# TASK-PCM-0039 — Mermaid Guidance

<!-- continuity:task {"acceptance": ["S1 Adoption: >=80% of candidate-arm outputs (n=5, fresh subagent sessions, current 1.1.0 guidance) pass all applicable deterministic checks \u2014 diagram present when the scenario names >=4 steps, direction TD (or LR within the <=4-short-node cap), <=8 nodes, text alternative present, wide diagram inside <details>, no viewscreen link; every individual run >=60%", "S2 Improvement: candidate arm passes >=30 percentage points above the baseline arm (n=5, 1.0.0 guidance without diagram rules)", "S3 Determinism: the holdout scorer is a pure function with unit tests (positive control: the guidance's own example passes; 3 negative controls fail as intended)", "S4 Gates: module doc, CLI constants, generated + static propagation, staleness warnings and deterministic tests pass local gates (unittest, Ruff, MyPy, compileall, continuity validate, index sync) and the six required hosted contexts with auto-merge on the exact candidate"], "depends_on": [], "goal": "Ship issue-log-format 1.1.0: tested diagram rules so every adopter's issue logs, updates and PRs carry readable mermaid diagrams with text alternatives", "id": "PCM-0039", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/126", "next_action": "None: #126 CLOSED with receipt 5837663115 after PR #130 merged at 1e89195. Follow-ups live on #100 (registry) and #129 (staff-model retirement); real-incident diagram rerun remains a stated follow-up.", "owner": "owner/Astra planning; subagent execution", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "completed", "why": "Multi-step flows are where text-only records fail hardest; mobile readers get illegible strips from wide diagrams; agents need rules proven against real GitHub rendering"} -->

- Status: completed 2026-09-25 (#126 CLOSED)
- Owner: owner/Astra planning; subagent execution
- Priority: P2
- Depends on: none

## Goal

Ship issue-log-format 1.1.0: tested diagram rules so every adopter's issue logs, updates and PRs carry readable mermaid diagrams with text alternatives

## Why

Multi-step flows are where text-only records fail hardest; mobile readers get illegible strips from wide diagrams; agents need rules proven against real GitHub rendering

## Allowed files

- `docs/ISSUE_LOG_FORMAT.md` (module doc: marker, Diagrams section, changelog)
- Static guidance copies: `AGENTS.md`, `HANDOFF.md`, `templates/v1/software/AGENTS.md`, `templates/v1/minimal/HANDOFF.md`, `templates/v1/software/README.md`, `.github/ISSUE_TEMPLATE/task.md`, `.github/pull_request_template.md`
- `src/continuity/cli.py` (guidance constants only)
- Version bookkeeping: `README.md`, `SPEC.md`, `docs/VERSIONING.md`, `.continuity/documents.json` + `docs/CONTINUITY_INDEX.md` (catalog refresh/render)
- Holdout scorer + fixtures + tests: `tests/diagram_holdout_scorer.py`, `tests/test_diagram_holdout_scorer.py`, `tests/fixtures/pcm0039_diagram_holdout/`

## Human outcome

A reader on a phone sees a readable diagram where a record describes a multi-step flow, and the record still makes sense wherever rendering fails; a fresh agent given the guidance block produces such a diagram without knowing GitHub's renderer internals.

## Scope and boundaries

- In scope: diagram rules in the `issue-log-format` 1.1.0 module doc and generated guidance; propagation to static copies and templates; version bookkeeping; hidden-holdout scorer and fixtures.
- Out of scope: no diagram renderer in the CLI; no GitHub API diagram validation; no diagram requirement for trivial issues; no new validator error severity (marker scan unchanged); no edits to target repositories; the package version stays 0.5.0 (guidance text only, protocol unchanged).
- Dependencies/uncertainty: none blocking. n=5 per arm on one synthetic scenario demonstrates followability on cheap sessions, not universality; a real-incident rerun is a follow-up and one pass is not repeatability (*inferred* limit, stated in the issue).

## Acceptance criteria

Pre-registered on the issue body (copy of #126 "How we will know"; numeric thresholds as stated):

- [x] **S1 Adoption:** ≥80% of candidate-arm outputs (n=5, fresh subagent sessions, current guidance) pass all applicable deterministic checks: diagram present when the scenario names ≥4 steps; direction TD (or LR within cap); ≤8 nodes; text alternative present; wide diagram inside `<details>`; no viewscreen link. Every individual run ≥60%. **Observed: 5/5 (100%) candidate runs pass all seven checks; each run 100%.**
- [x] **S2 Improvement:** candidate arm passes ≥30 percentage points above the baseline arm (n=5, 1.0.0 guidance without diagram rules). **Observed: candidate 100% − baseline 0% = +100 points; all five baseline runs failed exactly `diagram_present` (zero fences), confirming the rule — not general diligence — drives the difference.**
- [x] **S3 Determinism:** the scorer is a pure function with unit tests (positive control: the guidance's own example passes; 3 negative controls fail as intended). **Observed: 14 deterministic tests OK; positive control passes; three negative controls fail exactly their intended check sets. The holdout itself exposed a scorer false-negative (indented fence lines rejected by `first_statement`/`_LINE_FORMS`): fixed at the root (strip in `first_statement` + line-form match) with a permanent regression test `test_indented_fences_with_branch_labels_pass`; all four candidate fences re-scored green after the fix — no participant output was edited to pass.**
- [x] **S4 Gates:** module doc, CLI constants, generated + static propagation, staleness warnings, and deterministic tests all pass local gates (unittest, Ruff, MyPy, compileall, `continuity validate`, index sync) and the six required hosted contexts with auto-merge on the exact candidate. **Observed: local battery clean (196 tests; six known macOS-environmental only; ruff/mypy/compileall; VALID; SYNCHRONIZED); [PR #130](https://github.com/Pukujan/project-continuity-modules/pull/130) merged at `1e89195dd511a50cacd84649955b2e5d99de4549` with all six contexts green on the exact candidate (run 36174453270); merge mechanics stated honestly — direct owner merge after green (arm returned clean status; auto-merge job skipping), queue firing evidenced separately by trial PR #4 and increments #113–#125.**

## Evidence and sources

- Source: issue body of [#126](https://github.com/Pukujan/project-continuity-modules/issues/126), observed 2026-09-25 (this branch's planning read of the live issue).
- Rendering evidence (browser DOM + screenshots, verified 2026-09-25, disposable matrix `Pukujan/pcm-mermaid-matrix`): [issue #1 probes](https://github.com/Pukujan/pcm-mermaid-matrix/issues/1), [PR #2 surfaces](https://github.com/Pukujan/pcm-mermaid-matrix/pull/2), [blob view](https://github.com/Pukujan/pcm-mermaid-matrix/blob/main/MERMAID_MATRIX.md). Key measurements: 7-node `flowchart LR` = 2120px in an 878px container (scales to fit, illegible on 390px); same content as `graph TD` = 441px; renderer = viewscreen iframe, info probe reports v11.17.2; `<details>` renders lazily after expansion; broken syntax shows a visible "Syntax error in text" panel; standalone viewscreen URL is an empty shell.
- This increment's local gates (run on the branch): `continuity validate --root .` and `continuity docs render --check --root .` results recorded in the PR verification section.

### Hidden-holdout results (run 2026-09-25, recorded before PR)

Design as pre-registered: 10 fresh subagent sessions (5 candidate / 5 baseline), identical instructions, arms differing only in the guidance block (candidate = branch `ISSUE_LOG_FORMAT_GUIDANCE` 1.1.0; baseline = same constant at `origin/main` 1.0.0 — extracted programmatically, lengths 2,261 vs 1,631 bytes, `Diagrams` present only in candidate). Participants saw only guidance + `tests/fixtures/pcm0039_diagram_holdout/scenario.md` (361 words; rubric-vocabulary leak test passes); the scorer (`tests/diagram_holdout_scorer.py`) judged every returned log.

| Arm | Runs | pass-all | Failures |
| --- | --- | --- | --- |
| candidate | 5 | 5/5 (100%) | none |
| baseline | 5 | 0/5 (0%) | `diagram_present` ×5 (zero fences; all other six checks passed on each) |

Process notes (honest limits): (1) the first launch delivered unsubstituted `{{ARM_TEXT}}` placeholders; corrected full prompts were re-sent before any participant produced a final log — no arm ran on placeholder text. (2) A duplicate scorer agent briefly raced the assigned one; parent arbitration settled ownership and the conformant files were re-verified green on disk. (3) One baseline participant messaged an idle non-participant agent about format requirements; no reply was given (that agent stood down by design), and the baseline logs contain no rubric vocabulary — contamination assessed nil. (4) n=5 per arm, one synthetic scenario: demonstrates followability on cheap sessions, not universality; a real-incident rerun remains a stated follow-up. Raw logs and the scoring driver are session-local evidence; the deterministic scorer + fixtures + controls are committed so any maintainer can re-score.

## Reproduction details (only when needed)

Hidden-holdout arms per S1/S2: participants receive only the guidance block + seeded evidence, never the rubric; the scorer and fixtures are committed with the PR. Local gate commands: `python3.12 -m unittest`, `ruff check .`, `mypy src`, `python3.12 -m compileall src`, `PYTHONPATH=src python3.12 -m continuity validate --root .`, `PYTHONPATH=src python3.12 -m continuity docs render --check --root .`.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #126 (PCM-0039); parent: none; dependencies: none. Extends the merged `issue-log-format` 1.0.0 module from #99 / PCM-0027 (CLOSED) via its recorded 1.1.0 correction path; #100 / PCM-0028 registers the version bump when the registry lands.
- Primary writer / branch / source issue revision / as-of status: owner/Astra planning with subagent execution; branch `task/PCM-0039-mermaid-guidance`; source: #126 body as observed 2026-09-25; as-of: delivered 2026-09-25T18:37:20Z.
- Related PR/CI evidence and push receipt (request ID / SHA): [PR #130](https://github.com/Pukujan/project-continuity-modules/pull/130) at `1e89195dd511a50cacd84649955b2e5d99de4549`; checkpoint request pcm0039-holdout-20260925 pushed `ede9988f597b01de0d792e335d65e5453f0b33ee`; run 36174453270; receipt [5837663115](https://github.com/Pukujan/project-continuity-modules/issues/126#issuecomment-5837663115).

## Checkpoint log

No checkpoints yet.

### 2026-09-25 18:36:00 UTC — owner/Astra planning; subagent execution

<!-- continuity:checkpoint {"agent":"owner/Astra planning; subagent execution","blocked":["None."],"changed":["tasks/TASK-PCM-0039-mermaid-guidance.md; tests/diagram_holdout_scorer.py; tests/test_diagram_holdout_scorer.py."],"completed":["Ran the pre-registered hidden holdout: 5 candidate + 5 baseline fresh subagent arms on the seeded scenario, scored by the committed deterministic scorer. S1 100% (threshold >=80%), S2 +100pp (threshold >=30pp), S3 14 controls green incl. a real scorer false-negative found BY the holdout (indented fences) and fixed with a permanent regression test. Acceptance boxes S1-S3 checked with observed numbers."],"decisions":["Holdout process notes recorded honestly (placeholder-prompt relaunch before any final log; duplicate-scorer arbitration; nil contamination assessment; n=5 single-scenario limit)."],"evidence":["score summary: candidate pass-all 5/5, baseline 0/5 failing exactly diagram_present; scorer suite tests.test_diagram_holdout_scorer 14 OK; full discover 196 with only the six known macOS-environmental failures; ruff/mypy/compileall clean; validate VALID; index SYNCHRONIZED; arms extracted programmatically (baseline from origin/main constant, 1631B no-Diagrams vs candidate 2261B with-Diagrams)."],"next_action":"Re-render index, open PR Refs #126, verify six required contexts + auto-merge, publish leaf/parent receipts, close #126.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0039","timestamp":"2026-09-25T18:36:00Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"a5d257826beae5486a3fdb727f58ec4ac4b4aa69359ab1cf79014602b71ab5f9","request_id":"pcm0039-holdout-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0039"} -->

Completed:
- Ran the pre-registered hidden holdout: 5 candidate + 5 baseline fresh subagent arms on the seeded scenario, scored by the committed deterministic scorer. S1 100% (threshold >=80%), S2 +100pp (threshold >=30pp), S3 14 controls green incl. a real scorer false-negative found BY the holdout (indented fences) and fixed with a permanent regression test. Acceptance boxes S1-S3 checked with observed numbers.

Evidence:
- score summary: candidate pass-all 5/5, baseline 0/5 failing exactly diagram_present; scorer suite tests.test_diagram_holdout_scorer 14 OK; full discover 196 with only the six known macOS-environmental failures; ruff/mypy/compileall clean; validate VALID; index SYNCHRONIZED; arms extracted programmatically (baseline from origin/main constant, 1631B no-Diagrams vs candidate 2261B with-Diagrams).

Decisions:
- Holdout process notes recorded honestly (placeholder-prompt relaunch before any final log; duplicate-scorer arbitration; nil contamination assessment; n=5 single-scenario limit).

Changed:
- tasks/TASK-PCM-0039-mermaid-guidance.md; tests/diagram_holdout_scorer.py; tests/test_diagram_holdout_scorer.py.

Blocked/uncertain:
- None.

Next:
- Re-render index, open PR Refs #126, verify six required contexts + auto-merge, publish leaf/parent receipts, close #126.

### 2026-09-25 18:40:42 UTC — owner/Astra planning

<!-- continuity:checkpoint {"agent":"owner/Astra planning","blocked":["None."],"changed":["tasks/TASK-PCM-0039-mermaid-guidance.md; checkpoints/CURRENT.md."],"completed":["Marked PCM-0039 completed with S4 observed facts and CURRENT synchronized."],"decisions":["no new decisions"],"evidence":["PR #130 merged at 1e89195; six contexts green run 36174453270; receipt 5837663115; #126 CLOSED."],"next_action":"Merge this closeout PR; then execute the released PCM-0042 staff-model retirement on its own branch.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0039","timestamp":"2026-09-25T18:40:42Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"cf541933c5162f471e3a92180fc90d0f13b27f6f31b54a939ea6f6a735f4756a","request_id":"pcm0039-closeout-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0039"} -->

Completed:
- Marked PCM-0039 completed with S4 observed facts and CURRENT synchronized.

Evidence:
- PR #130 merged at 1e89195; six contexts green run 36174453270; receipt 5837663115; #126 CLOSED.

Decisions:
- no new decisions

Changed:
- tasks/TASK-PCM-0039-mermaid-guidance.md; checkpoints/CURRENT.md.

Blocked/uncertain:
- None.

Next:
- Merge this closeout PR; then execute the released PCM-0042 staff-model retirement on its own branch.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
