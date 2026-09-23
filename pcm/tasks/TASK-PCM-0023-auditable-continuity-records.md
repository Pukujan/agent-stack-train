# TASK-PCM-0023 — Auditable Continuity Records

<!-- continuity:task {"acceptance":["Canonical policy and normative SPEC guidance define the human-first/evidence-backed structure, PCM ownership boundary, proportionality, and what is explicitly out of scope","Issue and PR templates give new sessions useful problem/outcome/scope/evidence prompts, source citations, task/issue/CI links, and conditional reproduction details without creating a long default report","Fresh PCM adopters receive a concise versioned rule in generated AGENTS/HANDOFF guidance; optional GitHub templates install only by explicit opt-in and never silently overwrite existing project files","Deterministic tests verify policy propagation, template content/synchronization, opt-in generation, idempotent reruns, and conflict safety; full lint/type/test/package/continuity gates pass","PCM issue #32 and the resulting PR present a skimmable human outcome with linked, reproducible evidence; no unrelated project-content changes"],"depends_on":[],"goal":"Define and propagate PCM\u2019s human-first, evidence-backed writing contract for continuity issues, updates, pull requests, and PCM-owned human-readable continuity documents, without taking ownership of unrelated product or marketing documentation.","id":"PCM-0023","next_action":"No further action after PCM-0023 closeout PR #44 merges; PR #43 merged successfully at 867e5ae with all required checks passed.","owner":"Codex PCM task session; GitHub issue #32","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"Future sessions and projects need records that are understandable to people and auditable by machines: clear problem framing, visible outcome, accurate status, citations for external claims, revision provenance, and reproducible evidence when relevant."} -->

- Status: completed
- Owner: Codex PCM task session; GitHub issue #32
- Priority: P1
- Depends on: none

## Goal

Define and propagate PCM’s human-first, evidence-backed writing contract for continuity issues, updates, pull requests, and PCM-owned human-readable continuity documents, without taking ownership of README voice or overwhelming routine PRs.

## Why

Future sessions and projects need records that are understandable to people and auditable by machines: clear problem framing, visible outcome, accurate status, citations for external claims, revision provenance, and reproducible evidence when relevant.

## Allowed files

- \`SPEC.md\`
- \`docs/CONTINUITY_RECORDS_POLICY.md\`
- \`docs/TESTING_POLICY.md\`
- \`docs/TARGET_ADOPTION.md\`
- \`AGENTS.md\`
- \`templates/v1/software/AGENTS.md\`
- \`templates/v1/minimal/HANDOFF.md\`
- \`.github/ISSUE_TEMPLATE/task.md\`
- \`.github/pull_request_template.md\`
- \`src/continuity/cli.py\`
- \`tests/test_cli.py\`
- \`tests/test_continuity_records_policy.py\`
- \`tasks/TASK-PCM-0023-auditable-continuity-records.md\`
- \`checkpoints/CURRENT.md\`
- \`HANDOFF.md\`

## Acceptance criteria

- [x] Canonical policy and normative SPEC guidance define the human-first/evidence-backed structure, PCM ownership boundary, proportionality, and what is explicitly out of scope.
- [x] Issue and PR templates give new sessions useful problem/outcome/scope/evidence prompts, source citations, task/issue/CI links, and conditional reproduction details without creating a long default report.
- [x] Fresh PCM adopters receive a concise versioned rule in generated AGENTS/HANDOFF guidance; optional GitHub templates install only by explicit opt-in and never silently overwrite existing project files.
- [x] Deterministic tests verify policy propagation, template content/synchronization, opt-in generation, idempotent reruns, and conflict safety; full lint/type/test/package/continuity gates pass.
- [x] PCM issue #32 and the resulting PR present a skimmable human outcome with linked, reproducible evidence; no unrelated project-content changes.

## Checkpoint log

### 2026-09-23 — activation

Completed:
- Expanded existing issue #32 instead of opening a duplicate; its scope now defines a layered, human-first and auditable contract for continuity issues, updates, PRs, and PCM-owned continuity documents.
- Activated PCM-0023 after the user selected this as the next PCM priority. PCM-0022/#39 remains open for its independent post-#34 holdout.

Evidence:
- \`git status --short --branch\` -> clean \`main...origin/main\` before task activation; task branch created in the canonical checkout.
- GitHub issue #32 -> updated title and acceptance plan; existing tracking task is the right owner for this work.
- \`SPEC.md\`, generated templates, \`.github\` templates, \`init_repo\`, and current testing policy inspected to identify propagation points and avoid unrelated project-document changes.

Decisions:
- Make PR narratives skimmable and put detailed reproduction/provenance in linked or expandable sections; detail should improve auditability, not create a default paperwork burden.
- Propagate guidance through versioned generated instructions and optional opt-in templates. Installing templates must not claim automatic GitHub synchronization and must refuse conflicting existing files without partial writes.
- Keep scope to continuity records and PCM-owned continuation documents; do not change unrelated product content.

Changed:
- \`tasks/TASK-PCM-0023-auditable-continuity-records.md\`
- \`checkpoints/CURRENT.md\`
- \`HANDOFF.md\`
- GitHub issue #32

Blocked/uncertain:
- None known. Semantic accuracy still requires human review; deterministic checks will validate structure, links/IDs where local, and template propagation—not truth of prose.

Next:
- Implement the canonical policy, generated guidance, opt-in GitHub templates, and deterministic tests within the allowed files.

### 2026-09-23 — implementation and local verification

Completed:
- Added the versioned continuity-record policy and normative specification guidance for human-readable outcomes, scope, provenance, reproducibility when needed, and proportionate enforcement.
- Added version markers and concise record-writing rules to PCM's own instructions and both generated adoption profiles.
- Added opt-in GitHub issue/PR prompts with clear scope, evidence, conditional reproduction detail, and an explicit statement that templates do not synchronize tracker records.
- Added regression coverage for installed-template parity, opt-in/idempotent initialization, conflict-safe refusal, policy-version propagation, and new-project/task guidance.

Evidence:
- `PYTHONPATH=src python -m unittest discover -s tests -q` -> 31 tests passed.
- `ruff check .` -> passed; `mypy src` -> no issues; `python -m compileall -q src tests` -> passed.
- `python -m build` -> source distribution and wheel built successfully.
- `PYTHONPATH=src python -m continuity validate --root .` -> `VALID`.
- `git diff --check` -> passed.

Decisions:
- GitHub writing prompts are explicitly opt-in and do not enable or claim an issue/checkpoint synchronization adapter.
- Machine-readable policy version is `continuity-records/1.0.0`; testing checks that PCM and generated guidance share the same marker.
- The README image source is not present in this checkout or its tracked image history; no image was invented or added to issue #32.

Changed:
- Canonical policy, SPEC, testing/adoption guidance, PCM and generated agent/handoff instructions.
- Optional GitHub issue/PR templates and `continuity init --github-templates`.
- Deterministic CLI and policy-propagation tests.
- PCM-0023 task, CURRENT checkpoint, and HANDOFF.

Blocked/uncertain:
- Remote CI and automatic merge remain pending.
- The referenced “old images” for the current README could not be identified from this repository or the referenced chat preview; the README remains unchanged pending the user's image/source clarification.

Next:
- Commit and publish the tested changes, open the PR linked to issue #32, and verify required CI and automatic merge before closing the issue.

### 2026-09-23 — merged delivery and closeout

Completed:
- PR #43 merged to `main` as `867e5ae`; its policy, CLI, tests, and documentation are now part of the canonical repository.
- GitHub Actions passed `quality`, `test (3.11)`, `test (3.12)`, `package`, and `auto-merge`.
- PCM-0023 acceptance checks are complete. This closeout aligns the task/current/handoff state and closes issue #32.

Evidence:
- PR #43: https://github.com/Pukujan/project-continuity-modules/pull/43
- CI run: https://github.com/Pukujan/project-continuity-modules/actions/runs/35900978807 — all required jobs passed.
- Merge commit: `867e5aeae351591a232866b32082ccbe05bad7cd`.
- The PR's `Closes #32` text did not close the issue on GitHub; issue closure is performed explicitly after this final checkpoint is merged.

Decisions:
- Do not mark issue #32 closed until the task status and canonical active-task pointer are updated by this auto-merged closeout.
- Keep the separate README-image request open for clarification: no matching image assets or source references exist in this PCM checkout or the referenced conversation preview. No images were added to issue logs.

Changed:
- `tasks/TASK-PCM-0023-auditable-continuity-records.md`
- `checkpoints/CURRENT.md`
- `HANDOFF.md`
- GitHub issue #32 closeout

Blocked/uncertain:
- The source and intended placement of the user's “old images” remain unidentified. The README is unchanged.

Next:
- Merge closeout PR #44 through required CI, close issue #32, then leave PCM with no active task until the user selects the next priority.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
