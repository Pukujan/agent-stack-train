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

Hold **one repeatable issue-log ticketing system** — a single, portable way to file, stamp, rate, and route a record of something observed or something broken — so that a human working through an agent, or an agent acting on its own initiative, records an **observational issue**, an **operational issue**, or a **proposal** with full provenance, and any repository handles it the same way.

The system must be **repeatable**: the same protocol drops into any repository, anywhere, and behaves identically there.

## Why

The same issue-governance rule was hand-copied into several repositories. Copies drift, so a report filed in one repository no longer matches the trail in another, and nobody can tell which copy is authoritative. Worse, the copies were narrower than the need: they captured only "I observed something", not "something is broken right now" and not "an agent proposes this change" — and they never recorded *who or what filed the issue*, so a human's direct report and an agent's own proposal looked identical on the record.

Measured 2026-10-01: one CGM version pin lived in thirteen files across three revisions. OIO removes the copy: the protocol lives in one place and every repository points at it.

## What an issue is here

One canonical form, with a **type** field choosing between four kinds:

| Type | What it records |
| --- | --- |
| **observational** | Something someone saw — a fact, a symptom, a discrepancy — with provenance and citations. |
| **operational** | Something broken or degraded right now: an incident, an outage, a failed run, a blocked pipeline. |
| **proposal** | A proposed change. Every issue is a non-binding proposal; this type is for one whose main content *is* the change. |
| **incident** | An operational issue with a timeline and an impact, filed for the record while it is handled. |

## The filer stamp

Every issue carries a **required, machine-checkable filer stamp**. It answers two questions: *who initiated this filing*, and *whose identity is on it*.

**Origin** — exactly one:

- `human-direct` — a human filed the issue themselves.
- `human-via-agent` — a human directed an agent to file it; the human owns the intent.
- `agent-initiated` — an agent filed it on its own initiative, without a human asking for this specific issue.

**Identity** — the stamp also carries the filing identity: the human's handle when a human is involved, the agent's identity and session identifier when an agent filed it, and the timestamp. Triage reads the stamp, labels it, and can reject a filing that does not state its origin.

## Scope

- The **issue form** — one canonical template with the type field, the filer stamp, provenance, citations, operational data, and the priority rating (`.github/ISSUE_TEMPLATE/`).
- The **triage** — automation that reads a filed issue, validates the filer stamp, and applies the type, plane, and priority labels (`.github/workflows/issue-triage.yml`).
- The **intake contract** — the written rule for how a filed issue is received, handled, and closed, and the bootstrap steps that install this protocol into any repository.
- **One place to point** — every other repository consumes this source rather than keeping its own copy.

## Non-goals

- **Not a tracker, a workflow engine, or a place to store another project's issues.** Each repository keeps its own issue history.
- **Does not own any adopter's product code, issues, or releases.**
- **Does not own version pins or the release train.** The certified version set of the stack lives in its own dedicated train repository; OIO neither publishes nor certifies it. OIO is an adopter of the train, not its owner.
- **Does not own narrative or style.** README, issue, PR, and commit prose route through CGM.
- **Does not own execution continuity.** Tasks, checkpoints, push receipts, and PR gates belong to PCM.
- **Does not own the install surface.** How the stack is hot-loaded and wired belongs to ACS.
- **Does not make any issue binding.** Every issue filed under this protocol is a proposal.

## How OIO separates from the rest of the stack

OIO exists separately because the issue log used to live *inside* the installer. When ACS owned both the install surface and the coordination rules, installing ACS installed governance — the installer was grading itself. OIO takes the governance out and gives it its own repository. The same reasoning applies to versions: a product repository must not certify its own siblings.

| Repository | Owns | Does not own |
| --- | --- | --- |
| **OIO** (this repository) | The issue-log ticketing system: the form, the filer stamp, the triage, the intake contract, the bootstrap into any repository. | Product code, releases, version pins, narrative, execution continuity, the install surface. |
| **PCM** — `project-continuity-modules` | Execution continuity: tasks, checkpoints, immutable push receipts, required PR gates, the `continuity` CLI. | Issue governance, narrative, versions. |
| **CGM** — `content-generation-modules` | Narrative and style authority: writing routing, human-sounding writing, output naming, visual direction, image generation. | Issue governance, execution continuity, versions. |
| **ACS** — `agent-custom-setup` | The install surface: the hot-loader and the runtime safety that wires PCM + CGM + OIO together. | Issue governance, narrative, execution continuity, versions. |
| **The train repository** | The certified version set of the stack — one place adopters read compatible versions from. | Everything else. |

An adopter pins the train once, consumes OIO's form once, and keeps its own issue history.

## Definition of success

- A human filing directly, a human filing through an agent, and an agent proposing an issue on its own initiative all produce the **same shape of record**, distinguishable by the filer stamp, and all three are traceable from first sighting to a decision.
- An observational issue and an operational issue both route through the same triage, labelled by type, plane, and priority.
- The protocol, the filer stamp, and the triage live in **exactly one repository**, and any other repository can adopt them by pointing at this source — no hand-copied rule.
- The certified version set lives in the train repository, and OIO's own pins point at it.
