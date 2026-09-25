# TASK-PCM-0043 — Architecture Doc

<!-- continuity:task {"acceptance": ["docs/ARCHITECTURE.md exists on main, mirrors SPEC \u00a72/\u00a75/\u00a78 in plain language with an explicit normative-source pointer", "registered in .continuity/documents.json and rendered into docs/CONTINUITY_INDEX.md (validate VALID, render --check SYNCHRONIZED)", "all four diagrams follow issue-log-format 1.1.0: graph TD, <=8 nodes, text alternative beside each, wide content collapsed in details", "continuity docs find 'how does pcm work architecture ownership' returns the record after fetch", "six required hosted contexts pass on the exact merge candidate; receipts posted; #128 and #134 closed after delivery"], "depends_on": [], "goal": "Promote the #128 how-PCM-works answer to docs/ARCHITECTURE.md, registered in the catalog, with 1.1.0-compliant diagrams", "id": "PCM-0043", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/134", "next_action": "None: #134 CLOSED (receipt 5838053801) after PR #136 merged at 5c89db39231994621557455c67f752adad4d575b with six contexts green; #128 closed as delivered.", "owner": "owner", "priority": "P3", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "completed", "why": "The durable in-repo explanation of ownership, checkpoints, resumability, and self-vs-adopter behavior is the missing cold-start artifact the answer itself recommended"} -->

- Status: completed 2026-09-25 (#134 CLOSED)
- Owner: owner
- Priority: P3
- Depends on: none

Promotes the #128 answer; content source: issue #128 body (observed 2026-09-25); diagram rules: issue-log-format 1.1.0 merged at 1e89195.

## Goal

Promote the #128 how-PCM-works answer to docs/ARCHITECTURE.md, registered in the catalog, with 1.1.0-compliant diagrams

## Why

The durable in-repo explanation of ownership, checkpoints, resumability, and self-vs-adopter behavior is the missing cold-start artifact the answer itself recommended

## Allowed files

- define bounded paths before implementation.

## Human outcome

Describe what becomes easier, safer, clearer, or possible when this task is complete.

## Scope and boundaries

- In scope:
- Out of scope:
- Dependencies/uncertainty:

## Acceptance criteria

- [ ] state observable, task-specific outcomes.

## Evidence and sources

Link repository state at a revision and cite external factual claims directly. Record commands and results for claims that need verification.

## Reproduction details (only when needed)

Starting revision, material inputs/configuration, runtime, exact command or prompt, observed result, and limitations.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none):
- Primary writer / branch / source issue revision / as-of status:
- Related PR/CI evidence and push receipt (request ID / SHA):

## Checkpoint log

No checkpoints yet.

### 2026-09-25 19:02:20 UTC — owner

<!-- continuity:checkpoint {"agent":"owner","blocked":["Foreign linked worktree /private/tmp/pcm-pinned makes local validate INVALID (outside pcm/worktree/<TASK-ID>); owner decision needed to pin-compliantly relocate or remove."],"changed":["docs/ARCHITECTURE.md; .continuity/documents.json; docs/CONTINUITY_INDEX.md; tasks/TASK-PCM-0043-architecture-doc.md; checkpoints/CURRENT.md."],"completed":["Wrote docs/ARCHITECTURE.md (ownership, checkpoints, resume, TASK, self-vs-adopter, doc system; four 1.1.0-compliant diagrams with text alternatives), registered catalog + index, filled task projection, CURRENT active."],"decisions":["no new decisions"],"evidence":["docs add REGISTERED; render RENDERED; validate on this device reports one foreign-worktree error only (/private/tmp/pcm-pinned, detached 8626efa, not created by this session, left untouched); fresh-clone CI unaffected."],"next_action":"PR Refs #134, verify six contexts + merge, receipts, close #134 and #128.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0043","timestamp":"2026-09-25T19:02:20Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"55935314c1a13ee57b26d7edaa67ffb97df2b0d6c262d38a0c621efdba176657","request_id":"pcm0043-archdoc-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0043"} -->

Completed:
- Wrote docs/ARCHITECTURE.md (ownership, checkpoints, resume, TASK, self-vs-adopter, doc system; four 1.1.0-compliant diagrams with text alternatives), registered catalog + index, filled task projection, CURRENT active.

Evidence:
- docs add REGISTERED; render RENDERED; validate on this device reports one foreign-worktree error only (/private/tmp/pcm-pinned, detached 8626efa, not created by this session, left untouched); fresh-clone CI unaffected.

Decisions:
- no new decisions

Changed:
- docs/ARCHITECTURE.md; .continuity/documents.json; docs/CONTINUITY_INDEX.md; tasks/TASK-PCM-0043-architecture-doc.md; checkpoints/CURRENT.md.

Blocked/uncertain:
- Foreign linked worktree /private/tmp/pcm-pinned makes local validate INVALID (outside pcm/worktree/<TASK-ID>); owner decision needed to pin-compliantly relocate or remove.

Next:
- PR Refs #134, verify six contexts + merge, receipts, close #134 and #128.

### 2026-09-25 19:32:07 UTC — owner

<!-- continuity:checkpoint {"agent":"owner","blocked":["None."],"changed":["tasks/TASK-PCM-0043-architecture-doc.md; checkpoints/CURRENT.md."],"completed":["Marked PCM-0043 completed; CURRENT cleared and updated with the delivered architecture doc."],"decisions":["no new decisions"],"evidence":["PR #136 merged at 5c89db3; six contexts green; receipt 5838053801; #134/#128 CLOSED."],"next_action":"Merge this closeout PR; then execute the released PCM-0046 P1 traversal holdout.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0043","timestamp":"2026-09-25T19:32:07Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"da5c3e9f564f6ee33461d7402cffe5662dc721a0e0b382b29021e8fec05764e4","request_id":"pcm0043-closeout-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0043"} -->

Completed:
- Marked PCM-0043 completed; CURRENT cleared and updated with the delivered architecture doc.

Evidence:
- PR #136 merged at 5c89db3; six contexts green; receipt 5838053801; #134/#128 CLOSED.

Decisions:
- no new decisions

Changed:
- tasks/TASK-PCM-0043-architecture-doc.md; checkpoints/CURRENT.md.

Blocked/uncertain:
- None.

Next:
- Merge this closeout PR; then execute the released PCM-0046 P1 traversal holdout.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
