# Agent Operating Contract

## Start

Read PROJECT → CURRENT → active TASK → minimum relevant spec before editing.

For GitHub repositories, verify the live linked issue with `continuity issue verify <TASK-ID>` before resuming; the issue owns task scope/lifecycle, merged default-branch history owns accepted code, and PR checks/merge records own delivery. Resolve discrepancies from the issue before editing.

## Stack this repository consumes

Observational Issue Ops is a clean adopter of the shared stack; it vendors none of it. Its pins live in one place — [`stack-manifest.json`](stack-manifest.json) — and the certified versions it points at are published in the dedicated train repository [`Pukujan/agent-stack-train`](https://github.com/Pukujan/agent-stack-train).

| Component | Role here |
| --- | --- |
| **PCM** — `project-continuity-modules` (CLI 0.6.0 @ `4e23854…`) | Continuity files + `continuity` CLI, GitHub-owned progression, PR-only to `main`, required CI gates, leaf receipts. |
| **CGM** — `content-generation-modules` (0.5.7 @ `c069613…`, eight modules) | Narrative and style. README and product entry route through `writing-direction`; issue/PR/commit prose through `human-sounding-writing`; basenames through `human-output-naming`. The adapter is `.content-system/`. |
| **ACS** — `agent-custom-setup`, module `multi-agent-hotload` @ `0.1.0` | The install surface that wires the three together. |

When told to load the agent hot-loader, follow the ACS [HOTLOAD.md](https://github.com/Pukujan/agent-custom-setup/blob/main/modules/coordination/multi-agent-hotload/v0.1.0/HOTLOAD.md) install order. A two-module CGM pin or a continuity-only PCM is an incomplete install. Validate the adapter with:

```bash
python scripts/validate_content_system.py --root "$CGM_ROOT" \
  --adapter .content-system --project-root .
```

## Scope

Work only inside the active bounded task. Split or revise the task before materially expanding scope.

## Issue governance (this repository's product)

OIO owns the repeatable issue-log ticketing system and its triage. The canonical artifacts are `.github/ISSUE_TEMPLATE/observational-issue.yml` and `.github/workflows/issue-triage.yml`; every other repository consumes these rather than keeping its own copy.

- One canonical form with an **issue-type** field: `observational`, `operational`, `proposal`, or `incident`.
- Every issue carries a **required filer stamp**: `filer_origin` (`human-direct`, `human-via-agent`, or `agent-initiated`) plus the filer identity and session. Triage labels the origin and fails closed with `needs-filer-stamp` when it is missing or identity-less.
- Every issue filed under this protocol is a **non-binding proposal**, never an implementation mandate.
- The reporter picks a plane — lead owner (P1–20), approved collaborator (P20–40), or community (P40–100) — and the triage clamps the priority to that plane's range.
- OIO owns the protocol and its triage. It does **not** own any adopter's product code, issues, or releases; each repository keeps its own issue history.

## How OIO separates from the rest of the stack

OIO exists separately because the issue log used to live inside the installer. When ACS owned both the install surface and the coordination rules, installing ACS installed governance — the installer graded itself. OIO takes the governance out. The same reasoning applies to versions: a product repository must not certify its own siblings, so the certified version set lives in the dedicated train repository.

| Repository | Owns | Does not own |
| --- | --- | --- |
| **OIO** (this repository) | The issue-log ticketing system: the form, the filer stamp, the triage, the intake contract, the bootstrap into any repository. | Product code, releases, version pins, narrative, execution continuity, the install surface. |
| **PCM** — `project-continuity-modules` | Execution continuity: tasks, checkpoints, immutable push receipts, required PR gates, the `continuity` CLI. | Issue governance, narrative, versions. |
| **CGM** — `content-generation-modules` | Narrative and style authority: writing routing, human-sounding writing, output naming, visual direction, image generation. | Issue governance, execution continuity, versions. |
| **ACS** — `agent-custom-setup` | The install surface: the hot-loader and the runtime safety that wires PCM + CGM + OIO together. | Issue governance, narrative, execution continuity, versions. |
| **`agent-stack-train`** | The certified version set of the stack — one place adopters read compatible versions from. | Everything else. |

## Canonical checkout

The Git repository, remote, task ID, branch/ref, and commit history identify the work; the physical path does not. Keep one permanent main checkout as the project home base and use it for sequential work. When isolation or parallel work is genuinely useful, create one managed linked worktree per independent active task at `<canonical-root>/.worktrees/<task-id>`. Do not create one per session/agent, sibling clones, or arbitrary worktree paths; resume the same worktree across sessions. Register other existing checkouts with `continuity workspace register --root <checkout>`; PCM checks the private per-device registry and Git's worktree list, reuses one clean unlocked task match, and stops on dirty, locked, conflicting, or ambiguous matches. It never scans drives. Keep absolute paths out of shared handoffs.

After required checks pass, the PR is merged, the task record is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`. It verifies the GitHub PR, required checks, and merged commit and refuses locked/pinned or otherwise unsafe cleanup; never force-remove unfinished or user-modified work.

## Checkpoint

Before stopping after meaningful work, append completed work, exact evidence, decisions, changed paths, blockers, and one next atomic action.

Continuity bookkeeping supports execution but does not gate safe execution. If canonical continuity state is temporarily unavailable, continue safe authorized work only in an already-authorized alternate environment; do not create a clone or a new worktree merely to work around it. When authorized, run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`. Reconcile later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`.

For a normal checkpoint, commit the product change first and then run `continuity checkpoint`; it prints a stable `REQUEST_ID`, commits, and synchronously pushes the checkpoint to the task branch. If interrupted, retry with the same `--request-id`; the same payload is a no-op and a different payload is rejected. Open or update a PR after pushing. CI and auto-merge run asynchronously after required reviews/checks pass; confirm the merge before marking complete or removing a worktree.

## Continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.3.0","protocol_version":"0.1.0-draft"} -->

For continuity issues, progress updates, pull requests, and PCM-owned project-state documents, explain the human problem and outcome first, then scope, status, linked evidence, and one next action. Cite external factual claims and tie repository claims to a revision, issue, PR, or CI result. Record reproduction details only when needed to verify the claim. Keep PR openings skimmable; link or collapse long logs. Preserve the project's existing ownership outside PCM continuity. GitHub's issue-closing keywords in PR descriptions and commit messages remain active under negation; use them only when the issue should complete at merge, and verify issue status afterward.

## Verification

Each task names its human-visible outcome and proportionate checks. Use deterministic regression tests by default. Add a fresh-session holdout only when the task promises that a new agent can discover or follow repository guidance; its checks must come from visible requirements, and ambiguous criteria are inconclusive. Do not create separate PDD/SDD/TDD paperwork or a sub-issue for every test type.

Delegated agents are temporary workers. Give each worker one bounded task, record its result and evidence in the parent task/checkpoint, and explicitly close it immediately after the result is captured. This applies to completed, interrupted, failed, cancelled, and timed-out workers. Stop and close workers that are no longer needed; do not leave completed workers open for possible future use. Use the smallest useful number of workers.

<!-- pcm:github-progression:start -->
## GitHub-owned progression

GitHub Issues are required for PCM-governed project work and own task scope, acceptance, priority, ownership, dependencies, lifecycle and durable project progression. Merged default-branch history owns accepted code and normative/domain documents; PR checks and merge records own delivery facts. Checked-in PROJECT/CURRENT/TASK/checkpoint/handoff documents are mandatory versioned projections for task state, not a parallel authority. Local files, registries, context packs and chat are ephemeral execution aids. Domain-document ownership stays with the target project.

Every issue progress update MUST link the leaf child issue that owns the work, its parent ancestry and dependencies (or explicitly none). A top-level deliverable identifies itself as the leaf and says parent: none. Create one child per independently deliverable scope, never one per comment. Record task ID, primary writer and branch on the issue before creating its repository projection. Re-read live issues and relevant source revisions before resuming; the issue verifier checks identity/status, not semantic agreement.

Authorized owner/user direction can revise intent: record it on the owning GitHub issue with a correction/supersession link before dependent work. It cannot alter observed CI/merge facts or waive required gates. Stale projections yield to their field's authority. If direction, ownership or evidence conflicts remain unresolved, pause affected work and record uncertainty; continue independent safe work. One primary writer owns each task branch/checkpoint stream. Coordinate shared-document edits through linked issues/PRs, re-read the current base and reconcile concurrent changes; never force-push or overwrite another writer. Issue prose is not an atomic lock.

Label observed results, repository/external evidence, agent reports and inference separately. Preserve contradictory evidence with source/revision and mark conclusions disputed or unknown until resolved. Append correction/supersession evidence; never rewrite checkpoint history. An upstream correction MUST identify affected descendants and assumptions on their issues; pause, re-plan and revalidate dependent work before resuming. Follow explicit parent/dependency links within the affected scope; cycles or unknown lineage block affected claims. No graph database, local canonical ledger or autonomous polling agent is required.

Before every push, synchronize relevant docs and task/checkpoint projections, CURRENT/HANDOFF when affected, and reviewed catalog/generated index. Record leaf/parent/dependency links, source issue/comment revision, as-of status, evidence, blockers and next action. Commit product/docs first; `continuity checkpoint` then commits and synchronously pushes the checkpoint with a stable request ID. After every successful push, manually publish a leaf issue receipt keyed by request ID and exact pushed SHA, linking changed docs/checkpoint, PR, tests and pending gates; add a linked parent progression update. Retry a missing receipt without another checkpoint/push; inspect for the same key before posting. --receipt-repo and --receipt-issue are opt-in and still require a proven lookup; omit them and the receipt stays manual. Automatic issue-comment synchronization is not implemented.

Required CI and GitHub auto-merge are mandatory. Arm auto-merge only after the increment's final push: a later push races the merge window and strands outside accepted history. Verify protection, required reviews/checks on the exact current-base or merge-queue candidate, and auto-merge; missing, failed, skipped, stale or unverified gates fail closed: no completion or cleanup. After CI/merge, append the exact check results, PR/merge SHA and live issue status to the leaf and link the parent update; fetch and verify accepted history. Reconcile material doc/status corrections in a new synchronized increment. Receipt-only transitions need no recursive doc commit: docs retain an explicit as-of/pending state and point to the live issue. Never label local-only or merely pushed work delivered. Preserve unsafe resources and keep incomplete issues open.
<!-- pcm:github-progression:end -->

<!-- pcm:issue-log-format:start -->
## Issue log format (issue-log-format 1.2.0)

<!-- pcm:policy {"id":"issue-log-format","policy_version":"1.2.0","protocol_version":"0.1.0-draft"} -->

Write issue logs, progress updates, and pull requests in one plain-language shape a newcomer can follow. Pick the tier by the kind of issue, not by preference. **Core tier (every issue log):** title states the problem and intended direction; a 1-3 paragraph summary naming who/what is affected, the consequence, and what this proposes; identity and lineage (leaf owning issue, parent ancestry or none, task ID, primary writer, branch); observed facts vs interpretation, with inferences labelled *inferred*; acceptance criteria with numeric thresholds marked *(proposed)* when untested; boundaries/non-goals and one next action. **Investigation tier (incidents, failures, research, design issues):** numbered symptoms; hypotheses with Status, confirm/refute, and experiment; evidence with provenance; a **Counter-signal** entry when one exists; honest caveat; problems-vs-gaps; a **Proposal** labelled *(proposal)* stating none of it exists unless named as existing. **Pull requests open reader-first:** problem and consequence, what changes, how to verify, and what stays unchanged; lineage links; evidence and one next action; long logs collapsed or linked; reference issues with "Refs #<number>" and use closing keywords only when closing at merge is intended. **Diagrams (mermaid):** when a record describes a flow with 4+ ordered steps or 2+ branches, add a fenced mermaid diagram *and* keep an adjacent text list or table so the record survives render failure; default to `graph TD` (vertical); cap 8 nodes and 6-word labels; wrap diagrams that may exceed the container width inside `<details>`; preview the rendered diagram before publishing and never cite renderer URLs as standalone sources. **Readability rules:** give every SHA, comment id, flag, file path, or tool name a plain-word meaning in the same sentence before it carries load; write evidence as the claim first, numbers as support; never bare counts; no unexplained acronym or bare identifier on first use in any tier; PR openings and checkpoint Completed/Next lines start with one problem sentence a newcomer can follow; the rule set applies to CURRENT projections and checkpoint entries exactly as to issue logs. No private absolute paths or secrets; link rather than paste long logs. See `docs/ISSUE_LOG_FORMAT.md` in the PCM checkout for the full format, exemplar, and examples.
<!-- pcm:issue-log-format:end -->
