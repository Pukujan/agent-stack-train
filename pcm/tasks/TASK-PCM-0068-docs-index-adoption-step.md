# TASK-PCM-0068 — Docs Inventory Render Step for Overlays

<!-- continuity:task {"acceptance": ["TARGET_ADOPTION.md overlay gains a step after validation: build the optional documents inventory with `continuity docs init`, register target documents with `continuity docs add`, then `continuity docs render`; wording states the inventory is optional-but-recommended and that `docs find` and `docs render` fail with a distinct actionable error while it is absent, because render reads the catalog and cannot create it.", "`continuity validate` prints a WARNING (not an error, not inside validate_repo's error list) when .continuity/config.json exists with trackers.github true and no .continuity/documents.json exists, naming `continuity docs init` as the remedy; preflight stays error-only and the tests asserting validate_repo(root) == [] are unaffected.", "Red-first test for the warning; the full PCM suite, ruff, mypy, compileall, continuity validate and the docs index check stay green."], "depends_on": [], "goal": "Close the mature-target overlay gap where continuity validate prints VALID but continuity docs find errors: document the docs-inventory build step in TARGET_ADOPTION.md and make validate warn when a GitHub-authoritative repository has no documents index (Refs #210).", "id": "PCM-0068", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/210", "next_action": "Worker on branch task/PCM-0068-docs-index-adoption-step writes the red-first warning test through a separate findings helper surfaced in the validate CLI output branch, adds the docs init/add/render overlay step, and keeps validate_repo error-only.", "owner": "omp worker (delegated)", "priority": "P1", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "An adopter that follows the overlay guide verbatim ends up VALID yet unable to run the deterministic document lookup that PCM's own agent guidance requires of every fresh session, so adoption looks complete while half of the continuity contract is silently unavailable (observed: docs find exit 2, missing file)."} -->

- Status: active
- Owner: omp worker (delegated)
- Priority: P1
- Depends on: none

## Goal

Close the mature-target overlay gap where `continuity validate` prints VALID but `continuity docs find` errors: document the docs-inventory build step in TARGET_ADOPTION.md and make `validate` warn when a GitHub-authoritative repository has no documents index (Refs #210).

## Why

Observed while PCM was dogfooded as a helper on a mature target adopted via the TARGET_ADOPTION overlay, 2026-09-26 ~22:25Z: `continuity validate` exit 0, then `continuity docs find "claim ledger" --root .` exit 2 `ERROR: missing file: .continuity/documents.json`. The overlay procedure steps 3-5 materialize schemas, config.json and markers but never render or build the inventory, while PCM's own agent guidance tells every fresh session to consult it — so adoption looks complete while the docs-search half of the contract is silently unavailable.

## Allowed files

docs/TARGET_ADOPTION.md (overlay step + optional-but-recommended wording), src/continuity/cli.py (a new findings helper mirroring issue_log_format_findings, printed as WARNING in the validate CLI output branch; validate_repo's return list and preflight_repo stay error-only), and a red-first test in the tests/ conventions. Out of scope: forced indexing during init/validate, behavior change for targets without the GitHub tracker, and the active-task origin cross-check (PCM-0067).

## Human outcome

A mature target that follows the overlay guide ends with working deterministic document search or an explicit warning telling it what to run, and a cold-start agent on any GitHub-authoritative repository learns about the missing inventory from `continuity validate` instead of discovering it when a lookup fails.

## Scope and boundaries

- In scope: overlay guide step, validate WARNING, red-first test.
- Out of scope: `docs render` creating a missing catalog (it reads the catalog and must not be presented as the fix step), index-in-errors semantics, PCM-0067's validator change.
- Dependencies/uncertainty: shares src/continuity/cli.py with PCM-0067; publication is serialized and the second branch rebases onto the merged first before its final checkpoint push.

## Acceptance criteria

- [ ] TARGET_ADOPTION.md overlay gains a step after validation: build the optional documents inventory with `continuity docs init`, register target documents with `continuity docs add`, then `continuity docs render`; wording states the inventory is optional-but-recommended and that `docs find`/`docs render` fail with a distinct actionable error while it is absent.
- [ ] `continuity validate` prints a WARNING (not an error, not in validate_repo's error list) when .continuity/config.json exists with trackers.github true and no .continuity/documents.json, naming the docs init path; preflight and tests asserting validate_repo(root) == [] are unaffected.
- [ ] Red-first test for the warning; the full PCM suite, ruff, mypy, compileall, continuity validate and the docs index check stay green.

## Evidence and sources

Observed (continuity 0.6.0, target checkout, 2026-09-26): validate VALID exit 0; docs find exit 2 missing-file; docs/TARGET_ADOPTION.md steps 3-5 list schemas, config, markers, no inventory step; PCM's own repository has .continuity/documents.json checked in. Full reproduction record: issue #210 body.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #210 (PCM-0068); parent: none; dependencies: none (sibling shared-file note above).
- Primary writer / branch / source issue revision / as-of status: omp delegated worker, sole writer on task/PCM-0068-docs-index-adoption-step; source: live #210 body as of 2026-09-26T23:43Z; projection created 2026-09-29.
- Related PR/CI evidence and push receipt (request ID / SHA): none yet; identity recorded on #210 at comment 5896436590.

## Checkpoint log

No checkpoints yet.

### 2026-09-29 20:01:44 UTC — omp-worker-pcm0068

<!-- continuity:checkpoint {"agent":"omp-worker-pcm0068","blocked":[],"changed":["docs/TARGET_ADOPTION.md, src/continuity/cli.py, tests/test_cli.py"],"completed":["Overlay guide gains the optional document-inventory step (docs init -> docs add per document -> docs render); validate prints a WARNING naming continuity docs init when config.json exists, trackers.github is true and documents.json is missing; validate_repo and preflight stay error-only"],"decisions":["Warning is printed only by the validate CLI branch via document_inventory_findings mirroring issue_log_format_findings; docs render is documented as not the fix step because it loads the catalog it renders"],"evidence":["Red-first: AssertionError 'False is not true : VALID' before implementation, both new tests green after; suite 284 tests with only the six pre-existing environmental failures (zero delta); smoke target init --profile minimal --github-authority: WARNING + VALID exit 0, remedy sequence clears warning and docs find works; docs render --check SYNCHRONIZED; mypy clean; ruff at baseline"],"next_action":"Open the PR for task/PCM-0068-docs-index-adoption-step against main with Refs #210 and arm squash auto-merge once gates pass","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0068","timestamp":"2026-09-29T20:01:44Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"a21f82512fece1d336864ca2ac97648244ef41ec5b579e4b4206095aea1c755c","request_id":"413752801525490c94e537888a66c022","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0068"} -->

Completed:
- Overlay guide gains the optional document-inventory step (docs init -> docs add per document -> docs render); validate prints a WARNING naming continuity docs init when config.json exists, trackers.github is true and documents.json is missing; validate_repo and preflight stay error-only

Evidence:
- Red-first: AssertionError 'False is not true : VALID' before implementation, both new tests green after; suite 284 tests with only the six pre-existing environmental failures (zero delta); smoke target init --profile minimal --github-authority: WARNING + VALID exit 0, remedy sequence clears warning and docs find works; docs render --check SYNCHRONIZED; mypy clean; ruff at baseline

Decisions:
- Warning is printed only by the validate CLI branch via document_inventory_findings mirroring issue_log_format_findings; docs render is documented as not the fix step because it loads the catalog it renders

Changed:
- docs/TARGET_ADOPTION.md, src/continuity/cli.py, tests/test_cli.py

Blocked/uncertain:
- none

Next:
- Open the PR for task/PCM-0068-docs-index-adoption-step against main with Refs #210 and arm squash auto-merge once gates pass

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
