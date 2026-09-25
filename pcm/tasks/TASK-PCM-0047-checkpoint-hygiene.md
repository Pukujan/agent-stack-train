# TASK-PCM-0047 — Checkpoint hygiene

<!-- continuity:task {"acceptance": ["Deterministic tests fail before and pass after: checkpoint commit message carries no effective closing keyword without opt-in, with an operator-visible note", "After a checkpoint touching a cataloged task file, docs render --check is SYNCHRONIZED at the pushed head without a manual second render", "Dogfooded on this repository: one checkpoint lands keyword-free with a current index in a single pass", "Existing suite green locally and the six required hosted contexts pass on the exact candidate; receipts link #122 and #123"], "depends_on": [], "goal": "Fix the checkpoint publish path: sanitize closing keywords in generated commit messages and refresh the generated index when a cataloged file changes", "id": "PCM-0047", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/140", "next_action": "Implement red-to-green on the branch, then open the PR (Refs #140) linking #122 and #123.", "owner": "owner/Astra planning; subagent execution", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "Two observed self-inflicted failures this week: accidental issue auto-closures via checkpoint commit text (#53, #129) and stale generated index pushing hosted validate red (third occurrence at PR #117)"} -->

- Status: active
- Owner: owner/Astra planning; subagent execution
- Priority: P2
- Depends on: none

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → #140. Scope: publish_checkpoint message composition + index refresh in src/continuity/cli.py, deterministic tests. Receipts must link #122 and #123.
