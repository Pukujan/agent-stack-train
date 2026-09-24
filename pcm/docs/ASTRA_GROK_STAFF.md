# Astra owner and Grok staff operating model

This document records how Astra and Kilo staff divide work on this repository. It is an operating record for a fresh session. It is not a protocol change, not implementation proof, and not a substitute for the GitHub issue that owns a task.

Recorded on 2026-09-24 for child issue #69 of parent issue #53. The facts below are owner-authorized operating facts from that session. A fact that was not re-measured here stays labeled as recorded direction, not as a new experiment.

## Command split

Astra, on the InferHub route `cb/gpt-6-astra`, is the planner, researcher, owner, and verifier.

Kilo and in-session subagents are execution staff. Staff do not choose the next slice.

Astra does not spawn Codex or Luna subagents for this project.

## Session hygiene

Helpers must be in-session subagents, not new Agent Manager sessions.

[`docs/AGENT_LIFECYCLE.md`](AGENT_LIFECYCLE.md) requires the parent to capture the result and close the worker immediately. A completed worker left open still consumes a slot.

Only the Astra Codex process stays alive until its goal finishes.

Extra Agent Manager sessions opened on 2026-09-24 for citation research and this document were a lifecycle miss and were stopped.

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

Astra writes `astra-plan.md` and `TASK` files in the inbox. The parent Kilo session spawns one in-session subagent per task, records the result, and closes that subagent.

Do not repeat receipts that are already on GitHub. [Issue #66 comment 5818370226](https://github.com/Pukujan/project-continuity-modules/issues/66#issuecomment-5818370226) and [issue #53 comment 5818370504](https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5818370504) already record merge `9328f363a56d46290904b786eb43cff87e23c2b4`.

## Boundaries

Staff still do not choose the next slice. This record does not implement PCM-0026 and does not close issues #53, #66, or #67. Catalog registration for this file was not required for `continuity validate` to accept an unregistered document, so that registration is a follow-up rather than part of this change.
