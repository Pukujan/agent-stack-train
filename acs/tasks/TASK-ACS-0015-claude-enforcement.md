# TASK-ACS-0015 — Load and enforce the stack's rules in Claude Code

<!-- continuity:task {"acceptance": ["acs_install.py writes CLAUDE.md with the bridge region and .claude/hooks/acs_guard.py with SessionStart, PreToolUse and Stop hooks merged into .claude/settings.json", "hotload_check and check-adopter fail an adopter missing the bridge or the guard", "the guard blocks commits on the default branch, work with no owning issue, pushes to the default branch, worktrees outside <project>/worktrees, off-shape gh issue create, and stopping with unpushed or uncheckpointed work", "CI fails a pull request that names no existing owning issue", "ACS, OIO and PCM tests pass and gates is green on the PR", "PCM delivery: PR Refs #34 and #37"], "depends_on": [], "goal": "Make Claude Code load the stack's rules and enforce them with harness hooks and a required pull-request check, instead of relying on text.", "id": "ACS-0015", "issue_url": "https://github.com/Pukujan/agent-stack-train/issues/37", "next_action": "Arm auto-merge on PR #36, then certify the next train version so adopters get the guard.", "owner": "owner/Pukujan (Claude Code session)", "priority": "P1", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "Claude Code agents in three adopters skipped the stack's rules because the rules were only text and nothing blocked a skip."} -->

- Status: active
- Owner / primary writer: owner/Pukujan (Claude Code session)
- Priority: P1
- Depends on: none
- Leaf owning issue: [agent-stack-train#37](https://github.com/Pukujan/agent-stack-train/issues/37); also refs [#34](https://github.com/Pukujan/agent-stack-train/issues/34)
- Branch: `fix/claude-loads-the-stack` (PR [#36](https://github.com/Pukujan/agent-stack-train/pull/36))
- Adopter issue logs: Pukujan/voice-agent-research#27, Pukujan-lab/nyc-map-agent#604, Pukujan-lab/octo-database#410

## Goal

Claude Code reads `CLAUDE.md`, not `AGENTS.md`, and weighs written rules against its own defaults. The installer now writes a `CLAUDE.md` bridge that imports `AGENTS.md`, and a guard script (`.claude/hooks/acs_guard.py`) that Claude Code runs before tool calls, at session start and before stopping, so a skipped rule is blocked, not just discouraged. CI fails a pull request with no owning issue.

## Allowed files

- `modules/coordination/multi-agent-hotload/v0.1.0/{HOTLOAD,BEHAVIOR,PROMPT_INJECT}.md`
- `modules/coordination/multi-agent-hotload/v0.1.0/scripts/{claude_bridge,claude_guard,acs_install,hotload_check,dev_root_check}.py` and their tests
- `oio/.github/scripts/oio_close_refs.py`, `oio/tests/test_oio_close.py`
- `.github/workflows/{ci,check-adopter}.yml`, `scripts/upgrade_adopters.py`, root `.claude/`
- `tasks/TASK-ACS-0015-*.md`, `checkpoints/CURRENT.md`

## Non-goals

- Does not change what any rule says, and does not override Claude Code's safety rules or permission prompts.
- Does not edit adopters directly; they get the guard through the train's upgrade pull requests.

## Next atomic action

Arm auto-merge on PR #36, then certify the next train version so adopters get the guard.

## Checkpoint log
