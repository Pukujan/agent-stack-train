# TASK-PCM-0062 — Agent Labeling Convention

<!-- continuity:task {"acceptance": ["Guidance block gains the tool@device --agent labeling sentence in generator + all checked-in copies, pinned red-first in the policy test (merge-window mechanism); init output proven to carry it.", "docs/HANDOFF_PROTOCOL.md records the identity-layer table (agent label = claim; GitHub actor = permission-checked poster; SHA = artifact; device alias = human-chosen label) and links #144 Q4 as the open deeper-identity question."], "depends_on": [], "goal": "Record the multi-tool/multi-device identity model: what each identity layer proves (agent label vs GitHub actor vs SHA), and ship the tool@device --agent labeling convention pinned in guidance and HANDOFF protocol docs (Refs #185).", "id": "PCM-0062", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/185", "next_action": "Owner scope answer on #185; then ship the labeling sentence + identity-layer table per acceptance.", "owner": "owner/Astra planning", "priority": "P3", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "Same project is worked from oh-my-pi and Claude Code sessions; today the checkpoint names only free text; a cold-start reader cannot tell tool, device, or account (issue #185 records the code survey)."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P3
- Depends on: none

## Goal

Record the multi-tool/multi-device identity model: what each identity layer proves (agent label vs GitHub actor vs SHA), and ship the tool@device --agent labeling convention pinned in guidance and HANDOFF protocol docs (Refs #185).

## Why

Same project is worked from oh-my-pi and Claude Code sessions; today the checkpoint names only free text; a cold-start reader cannot tell tool, device, or account (issue #185 records the code survey).

## Allowed files

See leaf issue: the scope decision names the exact files; until then this task changes no repository content.

## Human outcome

Readers of checkpoints and handoffs can tell what each identity claim actually proves — which tool on which device claimed authorship, which GitHub account posted it, which key signed the artifact — without PCM inventing a global identity system.

## Scope and boundaries

- In scope: the decision record + any slice the owner approves on the leaf issue.
- Out of scope: everything the leaf issue's boundaries section excludes.
- Dependencies/uncertainty: owner scope answer pending.

## Acceptance criteria

- [ ] Guidance block gains the tool@device --agent labeling sentence in generator + all checked-in copies, pinned red-first in the policy test (merge-window mechanism); init output proven to carry it.
- [ ] docs/HANDOFF_PROTOCOL.md records the identity-layer table (agent label = claim; GitHub actor = permission-checked poster; SHA = artifact; device alias = human-chosen label) and links #144 Q4 as the open deeper-identity question.

## Evidence and sources

Leaf issue #185; the two-tools-two-devices ambiguity arose directly in the #184 status-refresh wave (the owner/Astra label is used by more than one runtime).

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #185 (PCM-0062); parent: none; depends: none; related #144 (Q4), #67/#110, #169, #35/#30, #184.
- Primary writer / branch / source issue revision / as-of status: owner/Astra (omp session); branch task/PCM-0063-projections (projection increment only, no code); source: live issue bodies; as-of 2026-09-26T11:35Z.
- Related PR/CI evidence and push receipt (request ID / SHA): none yet (decision gate); arms evidence rides PCM-0046 (PRs #188/#192/#193).

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
