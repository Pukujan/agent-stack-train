# Lifecycle model

The stack promises that finished work never lives only on one machine and that a merged pull request that finishes an issue closes it. This folder checks those promises against a formal model instead of hand-picked test cases (#73, acceptance criterion 1).

**TLA+** is a language for describing a system as states and the steps that move between them. **TLC** is its model checker: it explores every reachable state, within the bounds a configuration sets, and either proves a property holds there or prints a counterexample, the exact sequence of steps that breaks it.

## What it models

One issue #N, one agent session, one task branch, at most two edits (`MaxEdits = 2`). [`Lifecycle.tla`](Lifecycle.tla) names the code each step stands for.

| Actor | Steps | Grounded in |
|---|---|---|
| Agent (no fairness: may do anything allowed, or nothing) | edit, commit, PCM checkpoint, push, open a pull request saying `Closes #N` or only `Refs #N`, arm auto-merge itself, switch branch, try to stop | `pre_tool` and `check_git` in `claude_guard.py`; `pcm/AGENTS.md` checkpoint rule (`continuity checkpoint` commits and pushes) |
| Stop hook | blocks a stop when the checked-out task branch has uncommitted work, unpushed commits, a push without a checkpoint, or no open pull request with auto-merge armed; on the default branch or a detached HEAD, only uncommitted work counts (`GuardSeesAllBranches = FALSE`); lets the stop through when `stop_hook_active` is set (`RetryBypass = "all"`); does not block on the pull request when `gh` fails | `stop`, `checkout_problems`, `pull_request_problem` (PR #72) |
| CI | the `gates` check passes or fails, nondeterministically | `ci.yml` |
| Auto-merge | the workflow arms with the personal token, or (variant) a bot token | `auto-merge.yml` |
| GitHub merge | squash-merges an armed pull request once `gates` passes | GitHub |
| Close-on-merge | runs only for a merge attributed to a user; may succeed or fail; never touches a closed issue | `close-on-merge-caller.yml`, `close-on-merge.yml`, `_settle` in `oio_close_refs.py` |
| Daily sweep | when apply is on, closes an open issue that a merged pull request named with a closing verb | `close-sweep-caller.yml`, `close-sweep.yml`, `_sweep_merged` |

The three promises:

- **(a) `NoLocalWorkAtEnd`**: the session never ends while work is only local (uncommitted, or committed and not pushed).
- **(b) `ClosesEventuallyClosed`**: a merged pull request that says `Closes #N` eventually leaves #N closed. This is a liveness property: it holds only because CI, auto-merge, merge, close-on-merge and the sweep are *weakly fair* (a step that stays possible eventually happens).
- **(c) `NeverReopened`**: no step of the process moves a closed issue back to open.

## Results

`check.sh` runs every configuration and fails unless each gives its expected result. CI runs it as the `lifecycle-model` job, part of `gates`.

| Configuration | What it sets | Expected and found | Distinct states |
|---|---|---|---|
| `Lifecycle.cfg` | the real design, bot-token variant included | (b) and (c) hold | 8,582 |
| `StopReal.cfg` | the real Stop hook | **(a) broken: findings 1 and 2** | 32 |
| `StopRetryOnly.cfg` | only the `stop_hook_active` bypass left open | (a) broken by finding 1 alone | 40 |
| `BranchSwitchOnly.cfg` | only the checked-out-branch gap left open | (a) broken by finding 2 alone | 45 |
| `StopFixed.cfg` | the proposed guard (below) | (a), (b) and (c) hold | 7,511 |
| `GuardOff.cfg` | `ACS_GUARD=off` | (a) broken: negative control | 12 |
| `SweepOff.cfg` | sweep apply off | (b) broken: negative control | 6,834 |

Each run takes about a second. The two negative controls show the model can fail: with the guard off the agent edits and stops at once; with the sweep off a pull request saying `Closes #N`, armed with the bot token, merges, nothing closes #N, and nothing ever will.

## Findings: the real Stop hook does not keep (a)

Hypothesis H1 in #73 (exhaustive checking finds a gap the unit tests miss) is **confirmed**. TLC found two separate ways the session ends with work only local while the guard is on.

1. **The hook blocks only once.** `stop()` returns at once when Claude Code sets `stop_hook_active`, which it does when the agent is already continuing because a Stop hook blocked it. Counterexample (4 states): edit → try to stop (blocked) → try to stop again (allowed) → the session ends with uncommitted work.
2. **The hook checks only the checked-out branch.** `checkout_problems()` counts unpushed commits only on the current branch, and nothing blocks `git switch`. Counterexample (5 states): edit → commit → switch to the default branch or a detached HEAD → stop (allowed) → the commit exists only locally. In the `<project>/worktrees/<TASK-ID>` layout `git switch main` fails because main is checked out elsewhere, but `git switch --detach` works.

Closing (b) and (c) hold in the real design. The sweep is what closes an issue after a bot-token merge; this repository has `OIO_CLOSE_SWEEP_APPLY` set to `true` (seen in the repository's variables on 2026-10-31).

Noted while modelling, not checked by a property: after a squash merge the branch's own commits are still not ancestors of main, so the Stop hook keeps reporting a pushed branch with no open pull request until the agent leaves the branch. Today finding 1 lets the agent stop anyway; the proposed guard keeps that once-only bypass for the pull-request checks, so the agent can still finish.

## Proposal *(proposal)*

The guard described here does not exist; only its model does. `StopFixed.cfg` models a guard that (1) still blocks a retried stop (`stop_hook_active` set) while work is only local, keeping the once-only bypass for the checkpoint and pull-request checks an agent may not be able to fix, and (2) counts unpushed commits on every local branch (for example `git log --branches --not --remotes`), not only the checked-out one. TLC finds (a), (b) and (c) all hold for it. Changing `claude_guard.py` is follow-up work, not part of this change.

## What it assumes about GitHub and Claude Code

- **Assumed:** a merge armed with the workflow's own token closes nothing natively and starts no close-on-merge run (the comment in `auto-merge.yml`), and a merge armed with a personal token is attributed to a user, so GitHub's closing keyword closes #N (`NativeClose = TRUE`) and close-on-merge runs.
- **Assumed:** auto-merge stays armed when new commits are pushed, and a push to an open pull request reruns CI.
- **Assumed:** Claude Code's `stop_hook_active` stays set for the rest of the agent's continuation, until the next user prompt (which the model does not include).
- **Assumed:** the sweep sees every merged pull request. The real sweep reads the last 100 (`SWEEP_PR_LIMIT`), which the model's one pull request never exceeds.
- `CheckpointFile = TRUE`: the checkout has `checkpoints/CURRENT.md`, so the hook asks for a PCM checkpoint. This repository has no such file, so here that check is skipped; the model takes the stricter case.

## What it does not cover

- The Python code itself; the model covers the process. Property-based tests of the guard are acceptance criterion 2 of #73.
- More than one issue, branch, session or agent; issues in other repositories; forks and draft pull requests.
- People: a human reopening an issue, the `keep-open` label, the sweep skipping an issue reopened after its merge, an agent running `gh issue reopen` (the guard does not block it), or the user ending the session from the terminal. (c) covers the automation only.
- Files the session wrote through a shell command instead of the Edit or Write tools (the hook does not see them), the hook's limits on transcript size (last 4 MB) and checkouts (15), and `gh` failing anywhere other than the Stop hook's pull-request check.
- Merge conflicts, GitHub disabling auto-merge, branch protection, the sweep's roll-up of parent issues, and CI that never passes (there is no fairness on the agent, so a pull request may never merge; (b) only speaks about merged ones).

## Run it

TLC needs Java 11 or newer and `tla2tools.jar` (v1.7.4, the version CI pins with a checksum):

```bash
TLA2TOOLS=/path/to/tla2tools.jar verification/lifecycle/check.sh
```

To read a counterexample, run one configuration directly: `java -cp "$TLA2TOOLS" tlc2.TLC -config StopReal.cfg Lifecycle.tla` from this folder.
