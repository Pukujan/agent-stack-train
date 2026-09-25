# TASK-PCM-0047 — Checkpoint hygiene

<!-- continuity:task {"acceptance": ["Deterministic tests fail before and pass after: checkpoint commit message carries no effective closing keyword without opt-in, with an operator-visible note", "After a checkpoint touching a cataloged task file, docs render --check is SYNCHRONIZED at the pushed head without a manual second render", "Dogfooded on this repository: one checkpoint lands keyword-free with a current index in a single pass", "Existing suite green locally and the six required hosted contexts pass on the exact candidate; receipts link #122 and #123"], "depends_on": [], "goal": "Fix the checkpoint publish path: sanitize closing keywords in generated commit messages and refresh the generated index when a cataloged file changes", "id": "PCM-0047", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/140", "next_action": "Implement red-to-green on the branch, then open the PR (Refs #140) linking #122 and #123.", "owner": "owner/Astra planning; subagent execution", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "Two observed self-inflicted failures this week: accidental issue auto-closures via checkpoint commit text (#53, #129) and stale generated index pushing hosted validate red (third occurrence at PR #117)"} -->

- Status: active
- Owner: owner/Astra planning; subagent execution
- Priority: P2
- Depends on: none

## Checkpoint log

### 2026-09-25 — Checkpoint hygiene implemented (subagent)

- Completed: red->green on branch `task/PCM-0047-checkpoint-hygiene`. (1) Closing-keyword sanitizer: `publish_checkpoint` now rewrites `close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved` + whitespace-or-hyphen + `#N` or `.../issues/N` to the non-closing `Refs` form in the generated commit message and prints an operator note; opt-in `--allow-closing-keywords` preserves the text verbatim. (2) Index freshness: when `.continuity/documents.json` catalogs the checkpointed path, `publish_checkpoint` re-renders `docs/CONTINUITY_INDEX.md` and stages it in the same commit, so `docs render --check` is SYNCHRONIZED at the pushed head.
- Evidence: `tests/test_checkpoint_hygiene.py` (10 tests: sanitizer, opt-in flag, index refresh incl. fresh-clone `docs render --check`, preserved request-id idempotency / changed-payload refusal / no-catalog repos). Red run showed 6 failures on the unfixed path; green run: 10/10 OK. ruff 0.16.9 and mypy 1.18.1 clean; compileall clean.
- Decisions: sanitizer covers hyphen separators (`close-#53`, the observed #53/#129 trigger) as well as whitespace; rewrite target is `Refs<sep><ref>`. Index refresh runs after staging the checkpoint and reads working-tree bytes, so the rendered index matches the committed task file.
- Blocked/uncertain: dogfood acceptance (one real checkpoint on this repository) not executed here — publishing one would rewrite `checkpoints/CURRENT.md`/the generated index outside this slice's allowed-file list, and the parent directive forbids `continuity checkpoint` in the worktree. Hosted CI + receipts linking #122/#123 remain with the PR owner. Local `continuity validate` reports one environmental error caused by an unrelated foreign worktree (`/private/tmp/pcm-pinned`) registered in the shared checkout; the branch itself validates VALID in an isolated clone. The six known macOS-environmental local test failures (tmpdir `/var` vs `/private/var` symlink + registered-worktree leakage into `test_cli`/`test_worktrees`) reproduce identically at baseline `a7d07ca`.
- Next: open the PR under required CI; post receipts linking #122 and #123; dogfood one checkpoint on the main checkout.

## Handoff

Read PROJECT -> CURRENT -> this task -> #140. Implemented on `task/PCM-0047-checkpoint-hygiene`: sanitizer regex `(?i)\b(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)([-\s]+)(#[0-9]+|https?://[^ ]*issues/[0-9]+)` -> `Refs\2\3` in `publish_checkpoint` message composition (src/continuity/cli.py), opt-out flag `--allow-closing-keywords`; index refresh hook `refresh_index_for_cataloged_change` runs in `publish_checkpoint` after `git add` of the checkpoint and stages the regenerated `docs/CONTINUITY_INDEX.md` in the same commit. Receipts must link #122 and #123.
