# TASK-PCM-0018 — Idempotent checkpoints and fresh-session document discovery

<!-- continuity:task {"acceptance":["Repeating a checkpoint with the same caller-supplied request ID and identical task/payload appends no duplicate and creates no additional commit when already delivered; reusing the ID with different content fails before mutation","Checkpoint publication safely retries after local append, local commit, remote push success, and a lost push response while preserving one event and the original event timestamp","A single machine-readable document inventory is the declared source of truth for a generated human-readable index; initialization/add/update and view rendering are deterministic and validate in CI","Deterministic document lookup finds a registered document from an earlier session and its explicitly related neighboring records; unrelated repository changes do not affect the result","Task-specific context packs include only the standard project/current/task records plus documents explicitly associated with that task, state the exact next action, and bind each source to the commit/content actually read","A changed indexed document is visibly marked needs_review for consumers that depend on it; a changed unrelated file does not mark it stale, and old evidence remains available","Ordinary contract, failure-injection, idempotence/metamorphic, source-view synchronization, and context-pack tests pass; full Ruff, MyPy, compile, Python 3.11/3.12 suites, package build/parity, continuity validation, and required GitHub CI pass","An isolated fresh-session blind baseline and post-fix candidate use the visible issue/repository contract without the hidden diagnosis; the candidate finds the seeded document and neighboring records without duplicating them","Checkpoint/document-catalog overhead is measured on a reproducible fixture and reported; implementation remains a bounded Git/JSON/Markdown tool with no graph database or broad crawler","Implementation and canonical closeout merge through required CI/automatic merge, then issue #33 closes only after current task/checkpoint/handoff state proves acceptance; no unrelated target repository is changed"],"depends_on":["PCM-0015"],"goal":"Let retries safely record one durable checkpoint and let a fresh session reliably find the right prior project documents, notice only relevant staleness, and receive a focused handoff without depending on chat history.","id":"PCM-0018","next_action":"Run separate fresh-session baseline and candidate trials using the same visible prompt on pinned snapshots (baseline 85f13464c466ff277ce319850ce8124c4bc95c52 and merged candidate 98747fce4d5c805670dc3b00bb572e5c02706237); record both reports, objective checks, elapsed time, and cleanup. Keep issue #33 open until all remaining acceptance and a separate merged closeout are complete.","owner":"Codex PCM development session; GitHub issue #33","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"A retry can currently append duplicate checkpoint history, and a fresh session has no deterministic way to locate earlier decisions or related files. When later work changes a file, an old handoff may also look current even though its evidence is stale. These gaps waste time and can cause sessions to work from the wrong project state."} -->

## Human outcome

A failed or repeated checkpoint should not create duplicate history, and a new
session should be able to find the earlier document it needs without guessing
or recreating it. If a relevant file changed after the earlier session read it,
PCM should flag that specific evidence for review while leaving unrelated
records alone. The task handoff should point to the exact files and next action
needed to continue.

## Source and baseline evidence

- GitHub issue [#33](https://github.com/Pukujan/project-continuity-modules/issues/33)
  is the authoritative task scope. Its research comment on issue/file drift
  recommends revision-bound evidence, targeted review warnings, and a bounded
  issue-A/issue-B overlap experiment; it explicitly rejects a graph database as
  a first step.
- Activation snapshot: branch `task/PCM-0018-document-discovery`, based on
  merged commit `85f13464c466ff277ce319850ce8124c4bc95c52`; issue #33 is OPEN.
- `src/continuity/cli.py::checkpoint_task` currently appends a new timestamped
  checkpoint on every invocation. `publish_checkpoint` currently requires a
  staged checkpoint change, so retrying after the local commit or a successful
  push cannot complete as a clean no-op.
- `pack_task` currently reads PROJECT, CURRENT, TASK and always adds SPEC/AGENTS
  when present; it has no document inventory, deterministic lookup, task-scoped
  document selection, or per-source content evidence.
- Before task activation, the checkout was clean and was the only registered
  worktree. GitHub confirmed issues #31, #34, and #39 closed; #33 remained open.
  `checkpoints/CURRENT.md` and `HANDOFF.md` incorrectly still said to wait for
  issue #31's closeout PR, so those pointers are corrected in this task start.

## Fresh-session blind trial

**Status:** Neither a baseline report nor a candidate report is durably
recorded here. An earlier checkpoint sentence claimed a scored baseline but
provided no prompt/output, score, elapsed time, starting revision, or cleanup
evidence; treat that claim as unverified, not as a completed trial. Run the
baseline and candidate independently with the visible prompt below, pinned
repository snapshots, and no prior-run results in either prompt.

### Visible prompt and scoring

Each independent session gets only a clean repository snapshot and the visible
GitHub issue #33; the hidden implementation diagnosis and prior chat are
withheld. The same prompt is used for baseline and candidate:

> You are taking over a PCM maintenance task in a new session with no chat
> history. Use only this clean checkout and the visible GitHub issue #33,
> “PCM-0018 — Prove idempotent checkpoints and fresh-session document
> discovery.” Read the repository’s normal project and current/task guidance,
> then report briefly: the relevant existing paths to read, the next actionable
> step you can justify, what context you successfully located, and what remains
> uncertain. Do not edit anything, create duplicate docs, commit, push, open a
> PR, or spawn other workers. Do not rely on other chat sessions.

Score the returned report against issue #33's visible requirements and the
repository's declared task state. Keep the expected paths and prior-run results
out of the prompt; record outcomes, uncertainty, elapsed time, and cleanup after
the candidate has completed so it cannot learn its answer from this test log.

## Existing research and provenance

The issue's linked research result is the design provenance for the overlap
case. It cites primary W3C definitions: [PROV-O](https://www.w3.org/TR/prov-o/)
models provenance relations but does not establish truth;
[SHACL](https://www.w3.org/TR/shacl/) validates a supplied RDF graph against
shapes but cannot discover Git drift by itself; and
[OWL 2 Primer](https://www.w3.org/TR/owl2-primer/) describes ontology
semantics/inference rather than required-field validation. These limits support
keeping runtime state in Git plus JSON/Markdown and using narrow content hashes
for freshness rather than adding an RDF service or reasoner.

## Scope and boundaries

In scope:

- Add retry-safe checkpoint request identity and payload conflict detection,
  including publishing retries across local commit and remote push outcomes.
- Add one optional machine-readable document inventory and a deterministic
  generated human-readable index with one declared source of truth.
- Add deterministic document lookup, explicit neighboring-record discovery,
  task-specific pack selection, exact next-action inclusion, and targeted
  stale-evidence warnings tied to the content/revision read.
- Add reproducible baseline/candidate fresh-session trials and record their
  prompts, rubric provenance, observable results, resource cleanup, and cost.
- Bump the CLI/package minor version if the new public commands require it;
  keep the protocol version unchanged unless implementation proves a required
  canonical-state incompatibility.

Out of scope:

- RDF storage, graph databases, OWL reasoning, vector search, an automatic
  whole-repository semantic crawler, locks on shared files, or broad memory
  platform work.
- PCM-0009's target-repository remediation, README image recovery (#42),
  archiving helper conversations (#30), or main-session rotation (#35).
- Any edits to Eval Lab, hades-v2, harness-on-steroids, or
  inference-recommendation-engine.

## Allowed files

- `src/continuity/cli.py`
- `src/continuity/__init__.py`
- `pyproject.toml`
- `schemas/v1/`
- `docs/VERSIONING.md`
- `docs/HANDOFF_PROTOCOL.md`
- `SPEC.md`
- `AGENTS.md`
- `templates/v1/`
- `.github/workflows/ci.yml`
- `.continuity/` document inventory and generated view files
- `docs/CONTINUITY_INDEX.md`
- `tests/` and `tests/fixtures/`
- `tasks/TASK-PCM-0018-document-discovery.md`
- `checkpoints/CURRENT.md`
- `HANDOFF.md`

## Acceptance criteria

- [ ] An explicit request ID makes checkpoint retries idempotent; identical
  payloads return the existing event, conflicting reuse fails before writing,
  and the event timestamp/history remain unchanged.
- [ ] Publication retries push an existing local commit or safely confirm an
  already-pushed event without making a duplicate commit or checkpoint.
- [ ] The inventory owns stable document IDs, paths, human title/summary,
  search terms, explicit neighbors, task associations, and reviewed content
  identity. The readable index is rendered from it and cannot drift silently.
- [ ] Lookup returns deterministic matches plus declared neighbors and reports
  a changed dependency as `needs_review`; an unrelated-file control stays
  current. Reviewing/refreshing one entry does not rewrite history.
- [ ] A task pack selects only base project/current/task state plus its declared
  relevant documents, includes the exact next action, and records the commit
  and hashes of the content it actually includes. Dirty selected sources must
  not be mislabeled as an immutable HEAD snapshot.
- [ ] The selected checkpoint operation and generated view are idempotent;
  contract tests cover repeat, conflict, lost-push retry, duplicate history,
  search ordering/neighbor relations, stale/unrelated changes, and pack sources.
- [ ] CI verifies the inventory schema and human-view synchronization along
  with the existing quality, test, package, and artifact-parity checks.
- [ ] A blind baseline demonstrates the visible-contract starting behavior;
  a separate fresh-session candidate gets only the visible issue/repository,
  finds the seeded earlier document and neighbors, and does not duplicate
  canonical records. Objective checks, uncertainty, elapsed time, and closure
  of disposable resources are recorded.
- [ ] A reproducible checkpoint/catalog cost measurement is recorded; do not
  add machinery beyond the measured discovery and retry promises.
- [ ] All local/hosted gates pass, PR merges automatically, GitHub issue #33
  closes only after merged task/checkpoint/handoff evidence, and no temporary
  worktree or blind-test worker remains open.

## Checkpoint log

### 2026-09-23 — implementation contract and first measurement

Completed:
- Implemented request-keyed checkpoint entries and retry-safe local commit/push behavior.
- Added an optional document inventory, generated human index, deterministic lookup, content-based freshness checks, and task-scoped context packs.
- Added deterministic tests for lost push responses, content conflicts, remote overlap/deletion, unrelated changes, squash-merge ancestry, Windows line endings, record-order metamorphism, generated-view drift, and package parity.
- Seeded PCM's own catalog with the earlier PCM-0015 plan/research and relevant policy/schema records so later sessions have discoverable examples.

Evidence:
- The full unittest suite passed on Python 3.11.15 and 3.12.10: 64 tests on each runtime. Both package smoke runs passed on both runtimes for wheel and sdist, including PCM-0018 features. `ruff check .`, `mypy src`, and `python -m compileall -q src tests` passed.
- `python tests/measure_pcm0018_overhead.py` on Windows 11 / Python 3.12.10 (100 checkpoint events; 12 indexed documents; 25 lookups) measured checkpoint append p50 17.028 ms / p95 23.272 ms, a 232-byte request-operation marker, and 923 average bytes of task growth per event. The 12-record JSON inventory was 5,718 bytes; its human index was 6,715 bytes. Lookup p50 was 73.482 ms / p95 81.559 ms.
- The first lookup measurement was 699.200 ms p95; batching remote content reads reduced it to 81.559 ms p95 in the same fixture. These are local fixture measurements, not universal performance guarantees.
- `continuity docs render --root . --check` passed. `continuity validate` rejected the disposable baseline checkout while it was detached rather than on the task branch; remove that checkout and rerun validation on the canonical checkout before delivery.
- An earlier note claimed a scored baseline, but supplied no prompt/output, score, starting revision, timing, or cleanup record. No verifiable baseline report is present in this task file or the inspected issue comments; treat baseline and candidate as pending.

Decisions:
- Keep the inventory optional so repositories that do not need explicit
  document discovery keep their existing initialization and pack behavior.
- Compare reviewed file bytes with the fetched remote default-branch tree;
  do not require Git commit ancestry because squash merging can preserve the
  reviewed bytes while changing commit ancestry.
- Treat missing remote information as `REMOTE_UNKNOWN`; compare all selected
  records in one batched Git object read to avoid one Git process per result.
- Keep task retrieval as deterministic metadata search plus explicitly
  declared one-hop neighbors. The human index is generated from the JSON
  inventory and labels its freshness as local-only.

Changed:
- PCM-0018 CLI, package version metadata, schemas, docs/templates, tests,
  measurement script, task log, document catalog/index, CURRENT, and HANDOFF.

Blocked/uncertain:
- Hosted CI has not run because there is no PR yet. Inspect the status and
  ownership of the old detached disposable baseline checkout before any
  cleanup; do not remove unknown content.
- Both fresh-session baseline and candidate reports are pending.
- Remote freshness is based on the fetched local cache of `origin/HEAD`; the
  command does not fetch and must label missing comparison evidence unknown.

Next:
- Commit and push the tested implementation for required CI and automatic
  merge. Then run separate baseline and candidate sessions on pinned snapshots,
  record objective findings and cleanup, and keep #33 open until all acceptance
  and merged closeout requirements are satisfied.

### 2026-09-23 — handoff correction and local verification

Completed:
- Strengthened session-takeover instructions so each new session consults the
  document catalog before choosing its next action, not only before writing
  documentation.
- Reconciled the task log with the actual evidence: the baseline score is not
  present, so neither the baseline nor candidate trial is counted as complete.

Evidence:
- Full unittest suite: 64 tests passed on Python 3.11.15 and 64 on Python
  3.12.10.
- `ruff check .`, `mypy src`, `python -m compileall -q src tests`, and
  `git diff --check` passed.
- `continuity docs find` for PCM-0018 located the earlier plan, research, and
  relevant policies. The first validation of this entry identified two missing
  required headings; they are added below before final validation.
- These handoff and instruction edits are committed on
  `task/PCM-0018-document-discovery` but remain unpushed; hosted CI has
  not run because no PR has been opened. Baseline/candidate blind-trial
  evidence remains absent.

Decisions:
- Do not count an undocumented prior-session claim as holdout evidence; run
  baseline and candidate independently and record their observable evidence.
- Keep GitHub issue #33 open until remaining acceptance is verified and the
  canonical closeout has merged.

Blocked/uncertain:
- Required hosted CI, both fresh-session trials, and final issue closeout are
  still pending. The inherited disposable PCM holdout folders were inventoried
  by name only and were not inspected or removed in this handoff update.

Next:
- Push the committed candidate and open its PR; let required CI auto-merge it,
  then run the
  same visible prompt independently at baseline
  `85f13464c466ff277ce319850ce8124c4bc95c52` and the merged candidate snapshot.
  Record the actual report, model/session, starting revision, objective rubric
  results, elapsed time, and cleanup.

### 2026-09-23 — PR #51 merged and fresh-session handoff

Completed:
- Merged the PCM-0018 implementation automatically through PR #51 at
  `98747fce4d5c805670dc3b00bb572e5c02706237` after required hosted checks.
- Updated the permanent checkout to clean `main` at the merge commit and
  corrected CURRENT/HANDOFF to reflect the merged implementation and exact
  remaining trial work.
- Posted the handoff status and next step to GitHub issue #33.

Evidence:
- PR #51: https://github.com/Pukujan/project-continuity-modules/pull/51
- Required hosted jobs all passed: quality, tests on Python 3.11 and 3.12,
  package build, package parity on Python 3.11 and 3.12, and the auto-merge job.
- Merge commit: `98747fce4d5c805670dc3b00bb572e5c02706237`; local
  `git status --short --branch` reported clean `main` at this revision.
- Issue #33 remains OPEN. Its latest handoff comment is
  https://github.com/Pukujan/project-continuity-modules/issues/33#issuecomment-5804811179.
- Neither the baseline nor candidate trial has a verifiable report. The prior
  claim of a scored baseline lacks a prompt/output, pinned revision, rubric
  result, elapsed time, and cleanup evidence; it is not counted as a pass.

Decisions:
- Keep #33 open; merged implementation is not the full task acceptance.
- Run the same visible prompt independently against baseline `85f13464` and
  candidate `98747fce`, without diagnosis or prior-run results in the prompts.

Changed:
- `tasks/TASK-PCM-0018-document-discovery.md`, `checkpoints/CURRENT.md`, and
  `HANDOFF.md`; added issue #33 handoff comment.

Blocked/uncertain:
- Both fresh-session trials, recording their evidence/cleanup, and a separate
  merged closeout PR remain pending.

Next:
- In fresh sessions, run the task's exact visible prompt once at baseline
  `85f13464c466ff277ce319850ce8124c4bc95c52` and once at candidate
  `98747fce4d5c805670dc3b00bb572e5c02706237`; record actual outcomes, objective
  criteria, timing, and cleanup. Keep #33 open until acceptance and closeout.

### 2026-09-23 — activation

Completed:
- Verified issue #33 is open and selected it as the next active task after
  merged PCM-0017/issue #31.
- Read the PCM project contract, operating instructions, current state,
  handoff/testing contracts, relevant schemas, the PCM-0015 plan, and existing
  checkpoint/context-pack implementation.
- Corrected stale “wait for #31 closeout” instructions while activating this
  task.

Evidence:
- `git status --short --branch` -> clean task branch at merged commit
  `85f13464c466ff277ce319850ce8124c4bc95c52` before task-record changes.
- `git worktree list --porcelain` -> only the permanent checkout is registered.
- `gh issue view 33 --repo Pukujan/project-continuity-modules` -> issue #33
  OPEN with checkpoint retry, discovery, focused pack, and blind-test scope.
- Direct code inspection confirms checkpoint append has no request-key lookup,
  publication rejects no-diff retries, and packs have no document lookup.
- Prior investigation and primary-source citations are linked from issue #33's
  research comments; no new graph platform is needed for this bounded proof.

Decisions:
- Keep GitHub/main as accepted project authority; treat the local task branch
  as execution state. This sequential task uses the permanent checkout, not a
  new worktree.
- Preserve PCM-0009 and other target repositories as separately scoped work.
- Add file-overlap freshness as a narrow acceptance experiment because the
  existing issue research found it is the missing condition for trustworthy
  fresh-session discovery.

Changed:
- `tasks/TASK-PCM-0018-document-discovery.md`
- `checkpoints/CURRENT.md`
- `HANDOFF.md`

Blocked/uncertain:
- The final catalog shape and the exact compatibility boundary for additive
  CLI metadata are to be confirmed by tests before implementation.
- Issue #33, its implementation PR, required CI, and automatic merge remain
  pending.

Next:
- Define the checkpoint request-ID and document-catalog contracts against the
  existing schemas/tests, then implement the smallest compatible CLI changes
  and deterministic regressions.

### 2026-09-23 23:42:58 UTC — Codex PCM handoff preparation

<!-- continuity:checkpoint {"agent":"Codex PCM handoff preparation","blocked":["Fresh-session baseline and candidate trials, hosted CI, and issue #33 closeout remain pending."],"changed":["AGENTS.md; HANDOFF.md; README.md; checkpoints/CURRENT.md; docs/HANDOFF_PROTOCOL.md; src/continuity/cli.py; tasks/TASK-PCM-0018-document-discovery.md; templates/v1/minimal/HANDOFF.md; templates/v1/software/AGENTS.md; tests/test_cli.py"],"completed":["Strengthened fresh-session document discovery instructions; corrected the task log so the undocumented baseline claim is marked unverified and both holdouts remain pending; updated CURRENT and HANDOFF with exact continuation steps."],"decisions":["Do not treat the earlier undocumented baseline-score sentence as evidence; keep issue #33 open until fresh baseline and candidate results and merged closeout are recorded."],"evidence":["Full unittest suite passed 64 tests on Python 3.11.15 and 64 on Python 3.12.10; ruff check ., mypy src, compileall, and git diff --check passed; continuity validate returned VALID; generated document index check returned SYNCHRONIZED; local wheel/sdist smoke parity was previously recorded for Python 3.11 and 3.12. No verifiable baseline/candidate reports or hosted CI results exist yet."],"next_action":"Open an implementation PR for this pushed branch and let required CI auto-merge it; then run the same visible prompt in independent sessions at baseline 85f13464c466ff277ce319850ce8124c4bc95c52 and the merged candidate snapshot, record outcomes and cleanup, and keep #33 open until all acceptance is met.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0018","timestamp":"2026-09-23T23:42:58Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"c1b53991378e0be876b53f9b949559ca388a2aecc9f7dd0d5d83300d4638c6d2","request_id":"33e4c3c45503485082fe3a6023a0229c","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0018"} -->

Completed:
- Strengthened fresh-session document discovery instructions; corrected the task log so the undocumented baseline claim is marked unverified and both holdouts remain pending; updated CURRENT and HANDOFF with exact continuation steps.

Evidence:
- Full unittest suite passed 64 tests on Python 3.11.15 and 64 on Python 3.12.10; ruff check ., mypy src, compileall, and git diff --check passed; continuity validate returned VALID; generated document index check returned SYNCHRONIZED; local wheel/sdist smoke parity was previously recorded for Python 3.11 and 3.12. No verifiable baseline/candidate reports or hosted CI results exist yet.

Decisions:
- Do not treat the earlier undocumented baseline-score sentence as evidence; keep issue #33 open until fresh baseline and candidate results and merged closeout are recorded.

Changed:
- AGENTS.md; HANDOFF.md; README.md; checkpoints/CURRENT.md; docs/HANDOFF_PROTOCOL.md; src/continuity/cli.py; tasks/TASK-PCM-0018-document-discovery.md; templates/v1/minimal/HANDOFF.md; templates/v1/software/AGENTS.md; tests/test_cli.py

Blocked/uncertain:
- Fresh-session baseline and candidate trials, hosted CI, and issue #33 closeout remain pending.

Next:
- Open an implementation PR for this pushed branch and let required CI auto-merge it; then run the same visible prompt in independent sessions at baseline 85f13464c466ff277ce319850ce8124c4bc95c52 and the merged candidate snapshot, record outcomes and cleanup, and keep #33 open until all acceptance is met.

### 2026-09-23 23:50:23 UTC — Codex PCM-0018 post-merge handoff

<!-- continuity:checkpoint {"agent":"Codex PCM-0018 post-merge handoff","blocked":["Fresh-session baseline and candidate reports, plus final canonical closeout, remain outstanding."],"changed":["HANDOFF.md; checkpoints/CURRENT.md; tasks/TASK-PCM-0018-document-discovery.md; GitHub issue #33 status comment"],"completed":["Recorded the automatic merge of implementation PR #51; updated the permanent handoff and current checkpoint to identify the two pending fresh-session trials and keep issue #33 open."],"decisions":["Do not close issue #33 until the two independent pinned-snapshot trials and a separate merged closeout are complete; the old unsupported baseline claim is not a pass."],"evidence":["PR #51 merged at 98747fce4d5c805670dc3b00bb572e5c02706237 after hosted quality, Python 3.11/3.12 tests, package build, package-parity 3.11/3.12, and auto-merge checks passed. Local main is clean at the merge commit. continuity validate returned VALID and docs render --check returned SYNCHRONIZED. No verifiable baseline or candidate session report is recorded."],"next_action":"Run the same visible prompt in two independent fresh sessions: baseline 85f13464c466ff277ce319850ce8124c4bc95c52 and candidate 98747fce4d5c805670dc3b00bb572e5c02706237. Record prompt, model/session, starting commit, objective results, elapsed time, and cleanup; then complete remaining acceptance and use a separate CI/auto-merged closeout PR before closing #33.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0018","timestamp":"2026-09-23T23:50:23Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"35c066428c55c57a6371399f5016b292f0bb61f457c86752fa0e6cd2bae5c16e","request_id":"ab0b938607c54cb8aaec839bbb86d7be","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0018"} -->

Completed:
- Recorded the automatic merge of implementation PR #51; updated the permanent handoff and current checkpoint to identify the two pending fresh-session trials and keep issue #33 open.

Evidence:
- PR #51 merged at 98747fce4d5c805670dc3b00bb572e5c02706237 after hosted quality, Python 3.11/3.12 tests, package build, package-parity 3.11/3.12, and auto-merge checks passed. Local main is clean at the merge commit. continuity validate returned VALID and docs render --check returned SYNCHRONIZED. No verifiable baseline or candidate session report is recorded.

Decisions:
- Do not close issue #33 until the two independent pinned-snapshot trials and a separate merged closeout are complete; the old unsupported baseline claim is not a pass.

Changed:
- HANDOFF.md; checkpoints/CURRENT.md; tasks/TASK-PCM-0018-document-discovery.md; GitHub issue #33 status comment

Blocked/uncertain:
- Fresh-session baseline and candidate reports, plus final canonical closeout, remain outstanding.

Next:
- Run the same visible prompt in two independent fresh sessions: baseline 85f13464c466ff277ce319850ce8124c4bc95c52 and candidate 98747fce4d5c805670dc3b00bb572e5c02706237. Record prompt, model/session, starting commit, objective results, elapsed time, and cleanup; then complete remaining acceptance and use a separate CI/auto-merged closeout PR before closing #33.

### 2026-09-24 00:29:35 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":[],"changed":["tasks/TASK-PCM-0024-github-authority.md; checkpoints/CURRENT.md; HANDOFF.md; .continuity/documents.json; docs/CONTINUITY_INDEX.md"],"completed":["Recorded GitHub issue #53 and registered PCM-0024 as the queued follow-up; preserved PCM-0018 / #33 as the active task."],"decisions":["Do not claim the GitHub-authority policy is implemented; complete the #33 baseline/candidate fresh-session trials and closeout before activating PCM-0024."],"evidence":["Issue #53 is OPEN and links the GitHub-authority policy and missing proof work.","continuity validate -> VALID; docs render --check -> SYNCHRONIZED; document lookup returns PCM-0024 from the active PCM-0018 task.","Python 3.12 unittest suite -> 64 passed; Ruff, MyPy, compileall, and git diff --check passed."],"next_action":"Run separate fresh-session baseline and candidate trials using the same visible prompt at commits 85f13464c466ff277ce319850ce8124c4bc95c52 and 98747fce4d5c8056703329e243d49065e4741806; record the real reports, objective checks, elapsed time, and cleanup before closing #33.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0018","timestamp":"2026-09-24T00:29:35Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"432ef514d2a592050314af27a20eb63177e0b6860ca0843b8c0d524d6e57e91f","request_id":"6cfd942eb36347dda51dab0a4cffece1","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0018"} -->

Completed:
- Recorded GitHub issue #53 and registered PCM-0024 as the queued follow-up; preserved PCM-0018 / #33 as the active task.

Evidence:
- Issue #53 is OPEN and links the GitHub-authority policy and missing proof work.
- continuity validate -> VALID; docs render --check -> SYNCHRONIZED; document lookup returns PCM-0024 from the active PCM-0018 task.
- Python 3.12 unittest suite -> 64 passed; Ruff, MyPy, compileall, and git diff --check passed.

Decisions:
- Do not claim the GitHub-authority policy is implemented; complete the #33 baseline/candidate fresh-session trials and closeout before activating PCM-0024.

Changed:
- tasks/TASK-PCM-0024-github-authority.md; checkpoints/CURRENT.md; HANDOFF.md; .continuity/documents.json; docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- none

Next:
- Run separate fresh-session baseline and candidate trials using the same visible prompt at commits 85f13464c466ff277ce319850ce8124c4bc95c52 and 98747fce4d5c8056703329e243d49065e4741806; record the real reports, objective checks, elapsed time, and cleanup before closing #33.

### 2026-09-24 00:29:57 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":[],"changed":["tasks/TASK-PCM-0018-document-discovery.md"],"completed":["Corrected the fresh-session candidate commit reference in the next action without rewriting the earlier checkpoint."],"decisions":["The previous checkpoint had a mistyped SHA; use the verified PR #51 merge commit for the candidate trial."],"evidence":["PCM-0018 task and merged PR #51 identify the candidate as 98747fce4d5c805670dc3b00bb572e5c02706237."],"next_action":"Run separate fresh-session baseline and candidate trials using the same visible prompt at commits 85f13464c466ff277ce319850ce8124c4bc95c52 and 98747fce4d5c805670dc3b00bb572e5c02706237; record the real reports, objective checks, elapsed time, and cleanup before closing #33.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0018","timestamp":"2026-09-24T00:29:57Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"c76284c6d5d45971d357570f59bca32007b514f43a5e17b4e1905dd9c86d4e43","request_id":"d712d18929d049a69cb3afcf01f7e2b8","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0018"} -->

Completed:
- Corrected the fresh-session candidate commit reference in the next action without rewriting the earlier checkpoint.

Evidence:
- PCM-0018 task and merged PR #51 identify the candidate as 98747fce4d5c805670dc3b00bb572e5c02706237.

Decisions:
- The previous checkpoint had a mistyped SHA; use the verified PR #51 merge commit for the candidate trial.

Changed:
- tasks/TASK-PCM-0018-document-discovery.md

Blocked/uncertain:
- none

Next:
- Run separate fresh-session baseline and candidate trials using the same visible prompt at commits 85f13464c466ff277ce319850ce8124c4bc95c52 and 98747fce4d5c805670dc3b00bb572e5c02706237; record the real reports, objective checks, elapsed time, and cleanup before closing #33.

## Handoff

Read `PROJECT.md`, `AGENTS.md`, `checkpoints/CURRENT.md`, this task, `SPEC.md`,
`docs/HANDOFF_PROTOCOL.md`, `docs/TESTING_POLICY.md`, and `docs/VERSIONING.md`.
Use only the canonical PCM checkout. Do not modify unrelated target projects.
