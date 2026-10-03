# Observational Issue Ops — Project Contract

<!-- continuity:project {"id":"observational-issue-ops","protocol_version":"0.1.0-draft","schema":"project-continuity.project.v1","title":"Observational Issue Ops"} -->

<!-- pcm:github-progression:start -->
## GitHub-owned progression

GitHub Issues are required for PCM-governed project work and own task scope, acceptance, priority, ownership, dependencies, lifecycle and durable project progression. Merged default-branch history owns accepted code and normative/domain documents; PR checks and merge records own delivery facts. Checked-in PROJECT/CURRENT/TASK/checkpoint/handoff documents are mandatory versioned projections for task state, not a parallel authority. Local files, registries, context packs and chat are ephemeral execution aids. Domain-document ownership stays with the target project.

Every issue progress update MUST link the leaf child issue that owns the work, its parent ancestry and dependencies (or explicitly none). A top-level deliverable identifies itself as the leaf and says parent: none. Create one child per independently deliverable scope, never one per comment. Record task ID, primary writer and branch on the issue before creating its repository projection. Re-read live issues and relevant source revisions before resuming; the issue verifier checks identity/status, not semantic agreement.

Authorized owner/user direction can revise intent: record it on the owning GitHub issue with a correction/supersession link before dependent work. It cannot alter observed CI/merge facts or waive required gates. Stale projections yield to their field's authority. If direction, ownership or evidence conflicts remain unresolved, pause affected work and record uncertainty; continue independent safe work. One primary writer owns each task branch/checkpoint stream. Coordinate shared-document edits through linked issues/PRs, re-read the current base and reconcile concurrent changes; never force-push or overwrite another writer. Issue prose is not an atomic lock.

Label observed results, repository/external evidence, agent reports and inference separately. Preserve contradictory evidence with source/revision and mark conclusions disputed or unknown until resolved. Append correction/supersession evidence; never rewrite checkpoint history. An upstream correction MUST identify affected descendants and assumptions on their issues; pause, re-plan and revalidate dependent work before resuming. Follow explicit parent/dependency links within the affected scope; cycles or unknown lineage block affected claims. No graph database, local canonical ledger or autonomous polling agent is required.

Before every push, synchronize relevant docs and task/checkpoint projections, CURRENT/HANDOFF when affected, and reviewed catalog/generated index. Record leaf/parent/dependency links, source issue/comment revision, as-of status, evidence, blockers and next action. Commit product/docs first; `continuity checkpoint` then commits and synchronously pushes the checkpoint with a stable request ID. After every successful push, manually publish a leaf issue receipt keyed by request ID and exact pushed SHA, linking changed docs/checkpoint, PR, tests and pending gates; add a linked parent progression update. Retry a missing receipt without another checkpoint/push; inspect for the same key before posting. --receipt-repo and --receipt-issue are opt-in and still require a proven lookup; omit them and the receipt stays manual. Automatic issue-comment synchronization is not implemented.

Required CI and GitHub auto-merge are mandatory. Arm auto-merge only after the increment's final push: a later push races the merge window and strands outside accepted history. Verify protection, required reviews/checks on the exact current-base or merge-queue candidate, and auto-merge; missing, failed, skipped, stale or unverified gates fail closed: no completion or cleanup. After CI/merge, append the exact check results, PR/merge SHA and live issue status to the leaf and link the parent update; fetch and verify accepted history. Reconcile material doc/status corrections in a new synchronized increment. Receipt-only transitions need no recursive doc commit: docs retain an explicit as-of/pending state and point to the live issue. Never label local-only or merely pushed work delivered. Preserve unsafe resources and keep incomplete issues open.
<!-- pcm:github-progression:end -->

## Main goal

Hold **one repeatable observational and operational issue-log protocol** — a single, portable way to file, stamp, assess, and route an observation or current operational failure. General proposals and incident-management records remain outside this ontology. Every record carries source, account, destination, ontology, impact, risk, and release context.

The system must be **repeatable**: the same protocol drops into any repository, anywhere, and behaves identically there.

## Why

The issue log was duplicated across repositories, leaving no single set of definitions. OIO packages one default observational/operational ontology and a project-scoped extension; provenance records distinguish direct human, human-via-agent, agent-proposed, and agent-initiated origins while keeping authorization evidence separate.

Measured 2026-10-01: one CGM version pin lived in thirteen files across three revisions. OIO removes the copy: the protocol lives in one place and every repository points at it.

## What an issue is here

One canonical form, with a **type** field choosing between two kinds:

| Type | What it records |
| --- | --- |
| **observational** | Something someone saw — a fact, a symptom, a discrepancy — with provenance and citations. |
| **operational** | Something broken or degraded right now: an outage, failed run, or blocked pipeline. It is not an incident-management record. |

## The filer stamp

Every issue carries a **required, machine-checkable filer stamp**. It answers two questions: *who initiated this filing*, and *whose identity is on it*.

**Origin** — exactly one of four classes: `human-direct` (class 1), `human-via-agent` (class 2), `agent-proposed` (class 3, for human consideration), or `agent-initiated` (class 4, lowest). Human class claims require a separate authenticated GitHub account attestation; body text cannot verify itself.

**Identity** — record content author, authenticated GitHub actor/account, directing account when applicable, timestamp, session reference when available, authorization evidence, and exact destination. Shared credentials still cannot prove who typed a prompt.

## Scope

- The **issue form** — one canonical template with the type field, the filer stamp, provenance, citations, operational data, and the project-scoped priority path and impact/release assessment (`.github/ISSUE_TEMPLATE/`).
- The **triage** — automation that reads a filed issue, validates the filer stamp, and applies the type, filer-class, account-tier, project-priority, risk-lane, and release labels (`.github/workflows/issue-triage.yml`).
- The **intake contract** — the written rule for how a filed issue is received, handled, and closed, and the bootstrap steps that install this protocol into any repository.
- **One place to point** — every other repository consumes this source rather than keeping its own copy.

## Non-goals

- **Not a tracker, a workflow engine, or a place to store another project's issues.** Each repository keeps its own issue history.
- **Does not own any adopter's product code, issues, or releases.**
- **Does not own version pins or the release train.** A proposed version manifest lives in its own train repository; OIO neither publishes nor certifies it. OIO is an adopter of the train, not its owner.
- **Does not own narrative or style.** README, issue, PR, and commit prose route through CGM.
- **Does not own execution continuity.** Tasks, checkpoints, push receipts, and PR gates belong to PCM.
- **Does not own the install surface.** How the stack is hot-loaded and wired belongs to ACS.
- **Does not make any issue binding.** Every issue log is non-binding evidence for review, not implementation or release authorization.

## How OIO separates from the rest of the stack

OIO exists separately because the issue log used to live *inside* the installer. When ACS owned both the install surface and the coordination rules, installing ACS installed governance — the installer was grading itself. OIO takes the governance out and gives it its own repository. The same reasoning applies to versions: a product repository must not certify its own siblings.

| Repository | Owns | Does not own |
| --- | --- | --- |
| **OIO** (this repository) | The observational/operational issue-log ontology, form, provenance, triage, installer, and adopter bootstrap. | Product code, adopter issue histories, releases, stack version certification, narrative, execution continuity, the install surface. |
| **PCM** — `project-continuity-modules` | Execution continuity: tasks, checkpoints, immutable push receipts, required PR gates, the `continuity` CLI. | Issue governance, narrative, versions. |
| **CGM** — `content-generation-modules` | Narrative and style authority: writing routing, human-sounding writing, output naming, visual direction, image generation. | Issue governance, execution continuity, versions. |
| **ACS** — `agent-custom-setup` | The install surface: the hot-loader and the runtime safety that wires PCM + CGM + OIO together. | Issue governance, narrative, execution continuity, versions. |
| **The train repository** | The proposed version manifest for stack compatibility; its current record is not a final certification. | Everything else. |

An adopter pins the train once, consumes OIO's form once, and keeps its own issue history.

## Definition of success

- Direct human, human-via-agent, agent-proposed, and agent-initiated records share one schema; authorization claims are distinct from authenticated account evidence.
- Observational and operational records share triage for source authority, project priority, impact evidence, and the risk-versus-product review lane.
- The ontology, form, triage, and installer live in **exactly one repository**; each adopter retains its own extension and issue history.
- The train repository contains the current proposed version set; OIO's own pins point at it and preserve its proposed status.
