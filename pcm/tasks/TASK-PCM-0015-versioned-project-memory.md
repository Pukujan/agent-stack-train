# TASK-PCM-0015 — Plan versioned, verifiable project memory

<!-- continuity:task {"acceptance":["A durable implementation plan separates minimal core from optional adapters and defines explicit slice boundaries, non-goals, stop/split rules, and acceptance gates","The plan answers how PCM package and protocol versions relate, how Python and Node consumers would install/update, and what the current repository actually manages","The plan defines idempotency and a human-readable plus machine-readable state pattern with one authoritative source and generated/validated views","The plan defines document inventory/discovery, linked claims and evidence, freshness/supersession, and task ownership without assuming a graph database is required","The plan makes ordinary checkpoint cost proportional and specifies which operations happen on every checkpoint versus major handoff/release","The plan includes deterministic tests and a fresh-session blind end-to-end experiment proving an old document is found and not duplicated","The plan labels facts, user requirements, recommendations, inferences, and unresolved decisions; links evidence; and preserves Git as canonical","No implementation beyond this planning task is started"],"depends_on":[],"goal":"Produce a reviewable, evidence-based, sliced plan for testing and incrementally extending PCM with safe versioned adoption, idempotent documentation updates, durable document discovery, and fresh-session handoffs.","id":"PCM-0015","next_action":"GPT-6 Luna reviews the Astra plan, runs repository validation and full tests, then publishes the planning-only result through the normal CI/auto-merge path; implementation requires a separate bounded task.","owner":"GPT-6 Luna parent session (integration, evidence, and delivery)","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Fresh sessions reduce accumulated chat context but have repeatedly failed to discover earlier durable documents, causing duplicate work and incomplete context. PCM needs a small, verifiable, versioned memory and handoff workflow whose actual benefit and overhead are measured before it becomes policy."} -->

- Status: active; planning only
- Owner: GPT-6 Luna parent session (integration, evidence, and delivery); GPT-6 Astra's bounded plan result is captured below
- Priority: P1
- Depends on: none
- GitHub issue: [#28](https://github.com/Pukujan/project-continuity-modules/issues/28)
- Suggested branch: `task/PCM-0015-versioned-project-memory`

## Goal

Plan a small, testable evolution of PCM that helps every new session find existing work, resumes from Git-backed checkpoints, supports versioned updates across project runtimes, and avoids turning ordinary checkpoints into a heavyweight ceremony.

## Planning scope

The plan must inspect the current PCM implementation and distinguish existing behavior from new proposals. It must address:

- separate CLI/package and continuity-protocol versions;
- Python package distribution and possible Node/non-Python consumer support, including what PCM can and cannot enforce without runtime hooks;
- audit, upgrade, migration, compatibility, and local-change preservation;
- idempotent checkpoint, handoff, document inventory, and upgrade operations;
- a concise human view paired with machine-readable canonical state, with a defined generation/validation relationship;
- indexed document discovery, relationships, supersession, evidence-linked claims, stale/unknown state, and single-owner task claims;
- W3C PROV/PROV-O provenance and whether graph serialization should be native, generated, or deferred;
- task-specific context-pack generation and fresh-session takeover;
- checkpoint overhead, optional versus mandatory operations, and when to rotate sessions;
- slices, explicit non-goals, stop/split criteria, deterministic CI, and a blind fresh-session evaluation.

Do not implement the proposed feature set in this planning task. The result is one bounded plan artifact under `docs/plans/PCM-0015-implementation-plan.md` plus evidence in this task. Do not modify other repositories.

## Scope controls

- Keep the existing PCM package usable from Python 3.11+ unless evidence justifies a separately scoped compatibility change.
- Do not make a graph database, hosted service, vector store, or a JavaScript runtime a mandatory dependency without a measured need.
- Preserve Git as canonical project and task history.
- Separate file/schema validation from semantic truth claims; tests must be able to prove concrete behaviors.
- Separate core protocol requirements from Python CLI conveniences and optional adapters.
- Every proposed slice must fit one bounded task with named outputs and acceptance checks. If a slice crosses an unrelated runtime or infrastructure boundary, split it.
- Do not make every checkpoint run every expensive test. CI remains the full merge gate; the plan must state a proportional local checkpoint gate.
- Treat prior assistant designs in the epistemic context as proposals, not adopted requirements.

## Acceptance criteria

- [x] Current package, protocol, templates, CLI, schemas, version policy, and CI are inspected with file/line evidence.
- [x] The plan states a recommended adoption/distribution strategy for Python users and a separately justified approach for Node or other runtimes; unsupported conclusions remain open questions.
- [x] The plan states concretely what PCM can enforce in-repository, what CI can enforce, and what requires a runtime/agent-host adapter.
- [x] Human-readable and machine-readable records have one declared source of truth and a reproducible generation or consistency check.
- [x] Idempotency is specified as repeat-run invariants for relevant commands and migrations.
- [x] A document lookup acceptance scenario starts from a fresh session with no old conversation, finds a document created by an earlier session and related neighbors, and prevents creating a duplicate.
- [x] Claim statuses and provenance distinguish user requirements, direct observations, external sources, model proposals, inferences, and stale/contradictory facts.
- [x] Each slice has scope, files/components, required tests, exit criteria, migration story, and a clear defer/stop condition.
- [x] Checkpoint flow remains concise for routine work and reserves expanded handoff/context-pack generation for meaningful checkpoints or task rotation.
- [x] No implementation is started as part of PCM-0015.

## Evidence record

- Repository starting point: `388df1f057832d99b7c72d8022be5d1dae9a9946` (`origin/main`); working tree was clean.
- GitHub issue: #28.
- Verbatim dialogue and source classifications: `docs/research/PCM-0015-epistemic-context.md`.
- W3C PROV-O provenance graph: `docs/research/PCM-0015-provenance.ttl`.
- Official Codex subagent guidance: <https://learn.chatgpt.com/docs/agent-configuration/subagents>.
- Astra's completed, fresh-context plan review: one plan file only; identified package-version drift, generated-template worker-cleanup gaps, and non-idempotent checkpoint/recovery retries; its validation returned `VALID` and four focused tests passed. Full suite and behavioral acceptance were not run by Astra.
- Parent scope review added a three-part minimum proof path and made later assertions, ownership automation, Node packaging, publication, and host hooks explicitly conditional/separate.
- Parent verified `.github/workflows/ci.yml` triggers the full quality/test/package matrix for both `push` and `pull_request`; the plan records this duplicate-work cost and a narrow CI-trigger regression requirement, without changing workflow code in this planning task.
- Parent checks: `PYTHONPATH=src python -B -m unittest discover -s tests -v` → 21 passed; Ruff → clean; MyPy → clean; compileall → clean; `continuity validate --root .` → `VALID`; rdflib parsed PROV-O Turtle → 135 triples; `git diff --check` → clean.

## Checkpoint log

### 2026-09-23 14:14:42 UTC — GPT-6 Luna parent session

<!-- continuity:checkpoint {"agent":"GPT-6 Luna parent session","blocked":["Actual package and Node distribution strategy remains undecided; no implementation or update behavior has yet been tested."],"changed":["HANDOFF.md; checkpoints/CURRENT.md; docs/research/PCM-0015-epistemic-context.md; docs/research/PCM-0015-provenance.ttl; tasks/TASK-PCM-0015-versioned-project-memory.md"],"completed":["Captured the visible user and assistant discussion verbatim in a Git-backed research record.","Added a W3C PROV-O Turtle graph that labels user requirements, prior proposals, repository observations, external sources, and unresolved questions.","Opened GitHub issue #28 and activated PCM-0015 as a planning-only task."],"decisions":["Prior design proposals remain unadopted until reviewed and tested; Astra owns only a bounded plan artifact."],"evidence":["continuity validate --root . -> VALID.","uv run --with rdflib --no-project python -c ... -> valid Turtle; 89 triples.","GitHub issue #28 -> created."],"next_action":"Delegate the plan-only task to GPT-6 Astra and continue parent review in GPT-6 Luna.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0015","timestamp":"2026-09-23T14:14:42Z"} -->

Completed:
- Captured the visible user and assistant discussion verbatim in a Git-backed research record.
- Added a W3C PROV-O Turtle graph that labels user requirements, prior proposals, repository observations, external sources, and unresolved questions.
- Opened GitHub issue #28 and activated PCM-0015 as a planning-only task.

Evidence:
- continuity validate --root . -> VALID.
- uv run --with rdflib --no-project python -c ... -> valid Turtle; 89 triples.
- GitHub issue #28 -> created.

Decisions:
- Prior design proposals remain unadopted until reviewed and tested; Astra owns only a bounded plan artifact.

Changed:
- HANDOFF.md; checkpoints/CURRENT.md; docs/research/PCM-0015-epistemic-context.md; docs/research/PCM-0015-provenance.ttl; tasks/TASK-PCM-0015-versioned-project-memory.md

Blocked/uncertain:
- Actual package and Node distribution strategy remains undecided; no implementation or update behavior has yet been tested.

Next:
- Delegate the plan-only task to GPT-6 Astra and continue parent review in GPT-6 Luna.

### 2026-09-23 14:19:30 UTC — GPT-6 Luna parent session

<!-- continuity:checkpoint {"agent":"GPT-6 Luna parent session","blocked":["A public release and package update workflow do not yet exist; Python/Node distribution recommendation belongs in the plan."],"changed":["docs/research/PCM-0015-epistemic-context.md; docs/research/PCM-0015-provenance.ttl"],"completed":["Recorded release and package-manager evidence in the epistemic context and PROV-O graph."],"decisions":["Do not claim project-continuity 0.2.0 is externally released; this is only confirmed as the repository version/build output."],"evidence":["gh release list --repo Pukujan/project-continuity-modules --limit 10 -> no GitHub releases listed.","GET https://pypi.org/project/project-continuity/ -> 404 on 2026-09-23.",".github/workflows contains only ci.yml; CI builds the Python package but does not publish it.","PyPA, uv, and npm official docs reviewed; uv supports isolated and persistent CLI tools; npm engines is advisory unless engine-strict is set.","continuity validate --root . -> VALID; rdflib parsed PROV-O Turtle -> 135 triples."],"next_action":"Review the Astra planning artifact when complete, then integrate it into the PCM-0015 checkpoint.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0015","timestamp":"2026-09-23T14:19:30Z"} -->

Completed:
- Recorded release and package-manager evidence in the epistemic context and PROV-O graph.

Evidence:
- gh release list --repo Pukujan/project-continuity-modules --limit 10 -> no GitHub releases listed.
- GET https://pypi.org/project/project-continuity/ -> 404 on 2026-09-23.
- .github/workflows contains only ci.yml; CI builds the Python package but does not publish it.
- PyPA, uv, and npm official docs reviewed; uv supports isolated and persistent CLI tools; npm engines is advisory unless engine-strict is set.
- continuity validate --root . -> VALID; rdflib parsed PROV-O Turtle -> 135 triples.

Decisions:
- Do not claim project-continuity 0.2.0 is externally released; this is only confirmed as the repository version/build output.

Changed:
- docs/research/PCM-0015-epistemic-context.md; docs/research/PCM-0015-provenance.ttl

Blocked/uncertain:
- A public release and package update workflow do not yet exist; Python/Node distribution recommendation belongs in the plan.

Next:
- Review the Astra planning artifact when complete, then integrate it into the PCM-0015 checkpoint.

### 2026-09-23 14:37:19 UTC — GPT-6 Luna parent session

<!-- continuity:checkpoint {"agent":"GPT-6 Luna parent session","blocked":["Proposed features still require separate bounded implementation tasks and deterministic plus fresh-session acceptance."],"changed":["docs/plans/PCM-0015-implementation-plan.md; tasks/TASK-PCM-0015-versioned-project-memory.md; checkpoints/CURRENT.md; HANDOFF.md"],"completed":["Reviewed and narrowed Astra plan into a minimum proof path; recorded current CI duplication and enforcement limits."],"decisions":["Plan is proposal only. No memory/discovery feature, package publication, Node support, or host adapter is claimed to work or authorized for implementation."],"evidence":["PYTHONPATH=src python -B -m unittest discover -s tests -v -> 21 passed.","ruff check . -> passed; mypy src -> no issues; compileall -> passed.","continuity validate --root . -> VALID; PROV-O Turtle -> 135 triples.","git diff --check -> clean."],"next_action":"Create the planning-only PR; verify required CI and automatic merge; then close the plan issue without beginning implementation.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0015","timestamp":"2026-09-23T14:37:19Z"} -->

Completed:
- Reviewed and narrowed Astra plan into a minimum proof path; recorded current CI duplication and enforcement limits.

Evidence:
- PYTHONPATH=src python -B -m unittest discover -s tests -v -> 21 passed.
- ruff check . -> passed; mypy src -> no issues; compileall -> passed.
- continuity validate --root . -> VALID; PROV-O Turtle -> 135 triples.
- git diff --check -> clean.

Decisions:
- Plan is proposal only. No memory/discovery feature, package publication, Node support, or host adapter is claimed to work or authorized for implementation.

Changed:
- docs/plans/PCM-0015-implementation-plan.md; tasks/TASK-PCM-0015-versioned-project-memory.md; checkpoints/CURRENT.md; HANDOFF.md

Blocked/uncertain:
- Proposed features still require separate bounded implementation tasks and deterministic plus fresh-session acceptance.

Next:
- Create the planning-only PR; verify required CI and automatic merge; then close the plan issue without beginning implementation.
