# Astra owner and Grok staff operating model

This document records how Astra and Kilo staff divide work on this repository. It is an operating record for a fresh session. It is not a protocol change, not implementation proof, and not a substitute for the GitHub issue that owns a task.

Recorded on 2026-09-24 for child issue #69 of parent issue #53. The facts below are owner-authorized operating facts from that session. A fact that was not re-measured here stays labeled as recorded direction, not as a new experiment.

## Command split

Astra, on the InferHub route `cb/gpt-6-astra`, is the planner, researcher, owner, and verifier.

Kilo and in-session subagents are execution staff. Staff do not choose the next slice.

Astra does not spawn Codex or Luna subagents for this project.

## Session hygiene

Helpers must be in-session subagents, not new Agent Manager sessions.

A helper that the parent does not need before continuing must be started with `background: true`. A foreground `task` makes the parent wait until the child finishes, which stops the main project. That is what blocked the 2026-09-24 staff-doc turn. Kilo's documented split is: foreground when the next step depends on the child; background when the parent should keep moving and receive the result later. Do not poll a background child. Do not edit the same files it is editing.

Agent Manager sessions are a separate layer. They do not block this chat, but they open extra tabs and do not auto-close. They are not Astra's staff.

[`docs/AGENT_LIFECYCLE.md`](AGENT_LIFECYCLE.md) requires the parent to capture the result and close the worker immediately. A completed worker left open still consumes a slot. That policy is local operating guidance. It is not a live GitHub registry of open agents. GitHub Issues own task scope and lifecycle. The checkpoint, pushed branch, CI result, and merge own the durable record. The policy file has no `policy_version` of its own. The catalog id is `agent-lifecycle`, reviewed at `85f1346`, with no task id on that catalog row. The task that created the policy is PCM-0014, issue #24, completed in PR #26. Its checkpoint timestamp is 2026-09-23T13:34:48Z and its protocol version is `0.1.0-draft`.

Only the Astra Codex process stays alive until its goal finishes. Astra itself runs as a background process, not as a chat turn that holds this session.

Extra Agent Manager sessions opened on 2026-09-24 for citation research and this document were a lifecycle miss and were stopped.

## Worktrees

`docs/AGENT_LIFECYCLE.md` does not mention worktrees. A `task` subagent does not create a git worktree. Worktree removal is a separate rule: after required checks pass, the PR is merged, the task is complete, and the tree is clean, run `continuity worktree remove <TASK-ID>`. Do not leave a task worktree open after that point. The staff-doc worktree used to publish this file was removed after the branch was pushed and the tree was clean. Do not create one worktree per agent.

## Full privilege

The first Astra launch used `workspace-write`. `continuity issue verify` then failed with HTTP 401 because that sandbox could not read the owner `gh` keyring.

The owner authorized a relaunch with these settings:

- `codex exec --sandbox danger-full-access`
- `approval_policy=never`
- `shell_environment_policy.inherit=all`
- `GH_TOKEN` and `GITHUB_TOKEN` loaded from `gh auth token`, without printing the token

`gh` was already logged in as `Pukujan`. This document records the key name and the load command. It does not record token values or API key values.

## Launch contract

These paths are private local launch files. They are not shared project authority, and they are not a place to copy secrets into GitHub or this repository.

| Piece | Value |
| --- | --- |
| Launcher | `D:\claude\_workspace\pcm-astra-owner\launch-astra.ps1` |
| Prompt | `D:\claude\_workspace\pcm-astra-owner\astra-prompt.md` |
| Inbox | `D:\claude\_workspace\pcm-astra-owner\inbox` |
| Model | `cb/gpt-6-astra` |
| Provider | `inferhub` |
| Base URL | `https://api.inferhub.dev/v1` |
| Env key name | `INFERHUB_API_KEY` |
| Wire API | `responses` |
| Output | JSON |
| Working directory | the canonical checkout of this repository (`D:\claude\projects\project-continuity-modules`) |

The env key name is the launch contract. The key value is not recorded here.

## Research contract

Use an external primary source when one exists. A citation is the title, URL, access date, and the claim that source supports. Unknown stays unknown.

Durable notes go in `docs/research/`, named for the task and issue, and they state the problem solved. Evidence is not implementation proof.

## Execution contract

Astra writes the execution contract for each task. The contract is spec-driven, property-driven, and test-driven. It uses metamorphic and differential oracles where a relation exists.

Worker files name the spec section, properties, tests, allowed files, and stop boundary. Staff write failing tests before production code, then close.

## Assignment loop

Astra writes `astra-plan.md` and `TASK` files in the inbox. The parent Kilo session spawns one background in-session subagent per task (`background: true`), records the result when it arrives, and closes that subagent. It does not wait on the child before Astra's own planning continues.

Do not repeat receipts that are already on GitHub. [Issue #66 comment 5818370226](https://github.com/Pukujan/project-continuity-modules/issues/66#issuecomment-5818370226) and [issue #53 comment 5818370504](https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5818370504) already record merge `9328f363a56d46290904b786eb43cff87e23c2b4`.

## Boundaries

Staff still do not choose the next slice. This record does not implement PCM-0026 and does not close issues #53, #66, or #67. Catalog registration for this file was not required for `continuity validate` to accept an unregistered document, so that registration is a follow-up rather than part of this change.
