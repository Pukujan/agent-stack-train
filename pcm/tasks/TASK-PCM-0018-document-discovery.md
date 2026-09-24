# TASK-PCM-0018 — Idempotent checkpoints and fresh-session document discovery

<!-- continuity:task {"acceptance":["Repeating a checkpoint with the same caller-supplied request ID and identical task/payload appends no duplicate and creates no additional commit when already delivered; reusing the ID with different content fails before mutation","Checkpoint publication safely retries after local append, local commit, remote push success, and a lost push response while preserving one event and the original event timestamp","A single machine-readable document inventory is the declared source of truth for a generated human-readable index; initialization/add/update and view rendering are deterministic and validate in CI","Deterministic document lookup finds a registered document from an earlier session and its explicitly related neighboring records; unrelated repository changes do not affect the result","Task-specific context packs include only the standard project/current/task records plus documents explicitly associated with that task, state the exact next action, and bind each source to the commit/content actually read","A changed indexed document is visibly marked needs_review for consumers that depend on it; a changed unrelated file does not mark it stale, and old evidence remains available","Ordinary contract, failure-injection, idempotence/metamorphic, source-view synchronization, and context-pack tests pass; full Ruff, MyPy, compile, Python 3.11/3.12 suites, package build/parity, continuity validation, and required GitHub CI pass","An isolated fresh-session blind baseline and post-fix candidate use the visible issue/repository contract without the hidden diagnosis; the candidate finds the seeded document and neighboring records without duplicating them","Checkpoint/document-catalog overhead is measured on a reproducible fixture and reported; implementation remains a bounded Git/JSON/Markdown tool with no graph database or broad crawler","Implementation and canonical closeout merge through required CI/automatic merge, then issue #33 closes only after current task/checkpoint/handoff state proves acceptance; no unrelated target repository is changed"],"depends_on":["PCM-0015"],"goal":"Let retries safely record one durable checkpoint and let a fresh session reliably find the right prior project documents, notice only relevant staleness, and receive a focused handoff without depending on chat history.","id":"PCM-0018","next_action":"Have the task owner remove or explicitly reconcile the remaining disposable trial-copy residue; Windows denied ordinary removal and automatic review blocked the follow-up operation. Then prepare a separate closeout PR with final task/current/handoff state; keep issue #33 open until it merges through required CI and automatic merge.","owner":"Codex PCM development session; GitHub issue #33","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"A retry can currently append duplicate checkpoint history, and a fresh session has no deterministic way to locate earlier decisions or related files. When later work changes a file, an old handoff may also look current even though its evidence is stale. These gaps waste time and can cause sessions to work from the wrong project state."} -->

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

**Original status before 2026-09-24 runs:** Neither a baseline report nor a
candidate report was durably recorded. An earlier checkpoint sentence claimed
a scored baseline but provided no prompt/output, score, elapsed time, starting
revision, or cleanup evidence; treat that claim as unverified, not as a
completed trial. The independent pinned runs are now recorded below; cleanup
remains incomplete.

**Latest run status:** Independent baseline and candidate cold-start reports
have now been captured and are recorded in the 2026-09-24 checkpoint below.
The candidate surfaced the seeded PCM-0015 plan/research and declared related
records via the catalog. Both pinned checkouts started clean and remained
unmodified. Worker tasks were archived. Disposable-clone cleanup is incomplete:
the baseline checkout's source files are gone but its hidden `.git` marker
remains; the candidate checkout remains. Windows denied ordinary removal, and
the environment's automatic review blocked a follow-up cleanup attempt. Do not
mark the blind-trial acceptance complete until cleanup is resolved or the issue
owner explicitly reconciles that criterion.

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

### 2026-09-24 — Codex fresh-session baseline and candidate reports

Completed:
- Ran the same visible prompt in two independent Codex tasks with no prior
  task history in their context. Each used a disposable clone pinned to the
  requested commit; both verified exact detached HEAD and clean status before
  reading the repository and issue #33.
- Archived the baseline participant, candidate participant, and baseline
  wrapper tasks after collecting their reports. No repository files were
  changed by either participant.

Evidence:
- Prompt: the visible prompt in this task's “Fresh-session blind trial”
  section, preceded only by the operational requirement to clone this
  repository, verify the exact pinned clean commit, read normal project/task
  guidance and visible issue #33, and stop if the requested snapshot or issue
  was unavailable. The same prompt and operational constraints were used for
  both runs; neither received prior-run output or the hidden diagnosis.
- Baseline: start commit `85f13464c466ff277ce319850ce8124c4bc95c52`, verified
  clean detached HEAD; participant task `01a0d133-ce3a-7952-b708-35affdffacac`;
  elapsed 151.893 seconds. It identified the normal read paths and issue #33,
  correctly noticed the baseline had no active task or PCM-0018 task file, and
  reported that issue comments supplied the updated next action. It stated the
  exact prompt/rubric was not available from its permitted inputs, which was
  appropriate uncertainty. No edits or duplicate records were made.
- Candidate: start commit `98747fce4d5c805670dc3b00bb572e5c02706237`, verified
  clean detached HEAD; participant task `01a0d133-9ad6-7352-a317-6af02624419b`;
  elapsed 152.034 seconds. It used `continuity docs find` and surfaced
  `docs/research/PCM-0015-epistemic-context.md`,
  `docs/plans/PCM-0015-implementation-plan.md`,
  `docs/CONTINUITY_RECORDS_POLICY.md`, `docs/TESTING_POLICY.md`, and the
  context-pack schema, including catalog-declared related records. It
  identified the active task, issue #33, and unresolved inconsistency between
  task next-action text and merged PR #51. It made no edits or duplicate
  records.
- Objective assessment: baseline demonstrated that the earlier document
  discovery contract was missing (no task-scoped catalog or PCM-0018 file) and
  reported the resulting uncertainty; candidate found the seeded earlier
  documents and related records without editing or duplicating canonical
  files. The reports support the intended baseline-to-candidate discovery
  improvement. Exact model/runtime identifiers were not available from the
  task metadata and are unknown.
- Cleanup at time of the trial report: all three Codex tasks were archived.
  Ordinary recursive removal of both disposable clone folders returned
  Windows “access denied” / “directory not empty”; no force or alternate
  deletion method was attempted at that point. Their absolute local paths are
  omitted from this shared record for privacy.

Decisions:
- Count the pinned reports and discovery comparison as captured evidence, but
  leave the blind-trial acceptance unchecked because disposable-clone cleanup
  remains incomplete.
- Keep issue #33 active and PCM-0024 / issue #53 queued; do not claim task
  completion until cleanup and a separate merged canonical closeout are done.

Changed:
- `tasks/TASK-PCM-0018-document-discovery.md`; `checkpoints/CURRENT.md`;
  `HANDOFF.md`

Blocked/uncertain:
- Trial cleanup follow-up is recorded below. Exact model/runtime identifiers
  were unavailable.

Next:
- Complete or reconcile the blocked cleanup of the task-owned trial copies.
  Then prepare a separate closeout PR with final task/current/handoff state;
  keep #33 open until it merges through required CI and automatic merge.

### 2026-09-24 — Codex disposable trial cleanup follow-up

Completed:
- Rechecked the two task-owned trial folders and confirmed they were the
  disposable baseline and candidate snapshots. Removed the baseline snapshot's
  source contents; only its hidden Git marker remains. The candidate snapshot
  remains intact.
- Inspected the remaining candidate and baseline filesystem entries. Git pack
  files are read-only and the residual baseline `.git` directory is hidden.

Evidence:
- Ordinary removal of the hidden baseline `.git` marker was denied by
  Windows. A follow-up operation to clear attributes and remove only verified
  task-owned residue was rejected by the environment's automatic review with
  “blocked by policy.” No force deletion, permission change, or further cleanup
  attempt was made after that rejection.
- Worker tasks remain archived; the trial checkouts are outside the canonical
  PCM repository and are not registered Git worktrees. Their absolute local
  paths are omitted from this shared record for privacy.

Decisions:
- Keep #33 open and leave the trial-cleanup acceptance incomplete. Do not
  activate queued PCM-0024 until the task owner resolves or explicitly
  reconciles this cleanup requirement.

Changed:
- `tasks/TASK-PCM-0018-document-discovery.md`; `checkpoints/CURRENT.md`;
  `HANDOFF.md`

Blocked/uncertain:
- The candidate trial clone remains; the baseline trial directory retains a
  hidden `.git` marker. Windows denied normal removal and automatic review
  blocked the follow-up cleanup operation.

Next:
- Have the task owner remove the two named disposable trial folders locally,
  or explicitly reconcile this residual cleanup against issue #33 acceptance.
  Then prepare the separate canonical closeout PR; keep PCM-0024 queued until
  #33 closeout merges through required CI/automatic merge.

### 2026-09-24 02:29:50 UTC — Codex PCM-0018 trial closeout

<!-- continuity:checkpoint {"agent":"Codex PCM-0018 trial closeout","blocked":["Two task-owned disposable clone folders remain after Windows denied ordinary recursive cleanup; exact model/runtime identifiers unavailable."],"changed":["tasks/TASK-PCM-0018-document-discovery.md; checkpoints/CURRENT.md; HANDOFF.md"],"completed":["Recorded independent pinned baseline/candidate reports and updated CURRENT/HANDOFF; issue #33 remains open."],"decisions":["Do not complete blind-trial acceptance or activate queued PCM-0024 while task-owned disposable clone cleanup is unresolved."],"evidence":["Baseline 85f13464c466ff277ce319850ce8124c4bc95c52 and candidate 98747fce4d5c805670dc3b00bb572e5c02706237 were verified clean; elapsed 151.893s and 152.034s; candidate surfaced PCM-0015 research/plan and related catalog records.","continuity validate -> VALID; continuity docs render --check -> SYNCHRONIZED; git diff --check passed."],"next_action":"Resolve cleanup of only the two task-owned disposable clones using an ordinary safe operation, then open the separate canonical closeout PR and keep #33 open until required CI and automatic merge complete.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0018","timestamp":"2026-09-24T02:29:50Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"7617b00962be72748ecada27fa78b7eaa742ebce32a9889ebd19e2196d9cfc78","request_id":"14379aa0a4a2499eb546fae8afdb7b7d","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0018"} -->

Completed:
- Recorded independent pinned baseline/candidate reports and updated CURRENT/HANDOFF; issue #33 remains open.

Evidence:
- Baseline 85f13464c466ff277ce319850ce8124c4bc95c52 and candidate 98747fce4d5c805670dc3b00bb572e5c02706237 were verified clean; elapsed 151.893s and 152.034s; candidate surfaced PCM-0015 research/plan and related catalog records.
- continuity validate -> VALID; continuity docs render --check -> SYNCHRONIZED; git diff --check passed.

Decisions:
- Do not complete blind-trial acceptance or activate queued PCM-0024 while task-owned disposable clone cleanup is unresolved.

Changed:
- tasks/TASK-PCM-0018-document-discovery.md; checkpoints/CURRENT.md; HANDOFF.md

Blocked/uncertain:
- Two task-owned disposable clone folders remain after Windows denied ordinary recursive cleanup; exact model/runtime identifiers unavailable.

Next:
- Resolve cleanup of only the two task-owned disposable clones using an ordinary safe operation, then open the separate canonical closeout PR and keep #33 open until required CI and automatic merge complete.

### 2026-09-24 02:35:00 UTC — Codex PCM-0018 cleanup follow-up

<!-- continuity:checkpoint {"agent":"Codex PCM-0018 cleanup follow-up","blocked":["Candidate trial clone remains; baseline directory retains hidden .git marker. Automatic review blocked cleanup; exact model/runtime identifiers unavailable."],"changed":["tasks/TASK-PCM-0018-document-discovery.md; checkpoints/CURRENT.md; HANDOFF.md"],"completed":["Updated task/current/handoff to record partial disposable-snapshot cleanup, automatic-review rejection, and the remaining #33 blocker."],"decisions":["Stop cleanup attempts after automatic-review rejection; keep issue #33 open and PCM-0024 queued pending owner cleanup or explicit acceptance reconciliation."],"evidence":["Read-only inspection found baseline trial directory retains only a hidden .git marker; candidate disposable checkout remains. Task source paths were omitted from shared continuity records.","Ordinary removal of hidden .git marker was denied by Windows; automatic review rejected follow-up cleanup with 'blocked by policy'. No force deletion or permissions changes were used.","continuity validate -> VALID; continuity docs render --check -> SYNCHRONIZED; git diff --check passed."],"next_action":"Have the task owner remove or explicitly reconcile the remaining disposable trial-copy residue, then prepare separate canonical closeout PR; keep #33 open until required CI and automatic merge complete.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0018","timestamp":"2026-09-24T02:35:00Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"1fa8a27929cc528efec54cff7e8b2c5f065d20d4e9070615facceca7724aaa54","request_id":"178b33542a254284ac68b3d0419518ea","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0018"} -->

Completed:
- Updated task/current/handoff to record partial disposable-snapshot cleanup, automatic-review rejection, and the remaining #33 blocker.

Evidence:
- Read-only inspection found baseline trial directory retains only a hidden .git marker; candidate disposable checkout remains. Task source paths were omitted from shared continuity records.
- Ordinary removal of hidden .git marker was denied by Windows; automatic review rejected follow-up cleanup with 'blocked by policy'. No force deletion or permissions changes were used.
- continuity validate -> VALID; continuity docs render --check -> SYNCHRONIZED; git diff --check passed.

Decisions:
- Stop cleanup attempts after automatic-review rejection; keep issue #33 open and PCM-0024 queued pending owner cleanup or explicit acceptance reconciliation.

Changed:
- tasks/TASK-PCM-0018-document-discovery.md; checkpoints/CURRENT.md; HANDOFF.md

Blocked/uncertain:
- Candidate trial clone remains; baseline directory retains hidden .git marker. Automatic review blocked cleanup; exact model/runtime identifiers unavailable.

Next:
- Have the task owner remove or explicitly reconcile the remaining disposable trial-copy residue, then prepare separate canonical closeout PR; keep #33 open until required CI and automatic merge complete.

## Handoff

Read `PROJECT.md`, `AGENTS.md`, `checkpoints/CURRENT.md`, this task, `SPEC.md`,
`docs/HANDOFF_PROTOCOL.md`, `docs/TESTING_POLICY.md`, and `docs/VERSIONING.md`.
Use only the canonical PCM checkout. Do not modify unrelated target projects.
