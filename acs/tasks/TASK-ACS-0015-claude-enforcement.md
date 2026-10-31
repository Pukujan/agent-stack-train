# TASK-ACS-0015 — Load and enforce the stack's rules in Claude Code

<!-- continuity:task {"acceptance": ["acs_install.py writes CLAUDE.md with the bridge region and .claude/hooks/acs_guard.py with SessionStart, PreToolUse and Stop hooks merged into .claude/settings.json", "hotload_check and check-adopter fail an adopter missing the bridge or the guard", "the guard blocks commits on the default branch, work with no owning issue, pushes to the default branch, worktrees outside <project>/worktrees, off-shape gh issue create, and stopping with unpushed or uncheckpointed work", "CI fails a pull request that names no existing owning issue", "ACS, OIO and PCM tests pass and gates is green on the PR", "PCM delivery: PR Refs #34 and #37"], "depends_on": [], "goal": "Make Claude Code load the stack's rules and enforce them with harness hooks and a required pull-request check, instead of relying on text.", "id": "ACS-0015", "next_action": "Arm auto-merge on PR #36, then certify the next train version so adopters get the guard.", "owner": "owner/Pukujan (Claude Code session)", "priority": "P1", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "Claude Code agents in three adopters skipped the stack's rules because the rules were only text and nothing blocked a skip."} -->

- Status: active
- Owner / primary writer: owner/Pukujan (Claude Code session)
- Priority: P1
- Depends on: none
- Leaf owning issue (not in the metadata: ACS's tracker still names the frozen `Pukujan/agent-custom-setup`, see agent-stack-train#38): [agent-stack-train#37](https://github.com/Pukujan/agent-stack-train/issues/37); also refs [#34](https://github.com/Pukujan/agent-stack-train/issues/34)
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

### 2026-10-31 22:39:25 UTC — claude-code (claude-opus-5-5)

<!-- continuity:checkpoint {"agent":"claude-code (claude-opus-5-5)","blocked":[],"changed":["acs hotload pack scripts and tests, oio close-refs script, ci.yml, check-adopter.yml, upgrade_adopters.py, root .claude/"],"completed":["Claude Code now loads and enforces the stack's rules: the installer writes a CLAUDE.md bridge and the acs_guard hooks, hotload_check and check-adopter fail without them, and CI fails a pull request with no owning issue."],"decisions":["no new decisions"],"evidence":["All PR #36 checks passed (gates, acs, oio, oio/windows, pcm, cgm, train, and the new 'pull request names its owning issue'); ACS 354 tests and OIO 99 tests pass locally."],"next_action":"Arm auto-merge on PR #36, then certify the next train version so the upgrade bot installs the guard in the three adopters.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"ACS-0015","timestamp":"2026-10-31T22:39:25Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"0b87da43aaaed2d135d8f97b47c6fafe76d28d0cda519b2cc217103719cd75a3","request_id":"1e83a37a9c544b86aa40800b08305c22","schema":"project-continuity.checkpoint-operation.v1","task_id":"ACS-0015"} -->

Completed:
- Claude Code now loads and enforces the stack's rules: the installer writes a CLAUDE.md bridge and the acs_guard hooks, hotload_check and check-adopter fail without them, and CI fails a pull request with no owning issue.

Evidence:
- All PR #36 checks passed (gates, acs, oio, oio/windows, pcm, cgm, train, and the new 'pull request names its owning issue'); ACS 354 tests and OIO 99 tests pass locally.

Decisions:
- no new decisions

Changed:
- acs hotload pack scripts and tests, oio close-refs script, ci.yml, check-adopter.yml, upgrade_adopters.py, root .claude/

Blocked/uncertain:
- none

Next:
- Arm auto-merge on PR #36, then certify the next train version so the upgrade bot installs the guard in the three adopters.
