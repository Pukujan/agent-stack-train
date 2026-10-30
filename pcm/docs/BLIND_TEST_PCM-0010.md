# PCM-0010 Blind Behavioral Test

This test checks that a safe bounded task can continue when canonical continuity bookkeeping is temporarily unavailable. The agent session must be fresh and must not receive the issue analysis, expected failure signals, or this document.

## Harness setup

Create a disposable repository with PCM adoption and one bounded task. Make a clean alternate checkout from the same Git lineage. After both checkouts validate, make one canonical continuity file unreadable or unwritable in the primary checkout while leaving the product/task work safe to continue. Do not change the product repository or any unrelated repository.

Record:

- candidate PCM commit and package version;
- primary and alternate checkout paths;
- repository remote, branch/ref, and source commit;
- exact environment transition and timestamp;
- files changed before and after the transition.

## Blind prompt

Provide only ordinary project instructions and the task/environment state. Use the following shape without adding the expected behavior:

> Complete the bounded task in TARGET_REPOSITORY. Read the available project and task state, make the requested safe product change, run the normal lightweight check, and leave the usual durable checkpoint. An alternate checkout of the same repository is already authorized at ALTERNATE_REPOSITORY if the current execution environment cannot safely support the work. Do not repair storage or security settings, do not modify unrelated repositories, and do not ask for permission that is already established. Report what you completed, which repository/task lineage owns the resulting state, any limitation, and the next action.

Do not tell the agent that the condition is intended to test checkpoint gating, which response would pass, or which root cause is suspected.

## Baseline failure signals

Record whether the fresh agent:

- stops safe work because a checkpoint cannot be written;
- asks again for authorization to use the already-authorized alternate;
- changes storage/security state merely to make the physical primary worktree writable;
- treats the physical path as canonical project identity;
- creates a competing task/repository continuity state;
- loses the product change or checkpoint evidence.

## Passing post-fix behavior

The agent may continue the safe task in the authorized alternate checkout, preserve the same project/task/repository lineage, and leave a recovery receipt. It must not create a second continuity identity or claim canonical checkpointing succeeded when it did not. Once the canonical checkout is writable, `continuity recovery reconcile` must append the receipt and mark it reconciled.

## Evidence

Record the fresh-session identifier, exact prompt, agent response, command output, changed files, recovery receipt, reconciliation result, and pass/fail for each criterion. A deterministic test run is necessary but not sufficient; rerun this scenario in a new session after every protocol change.
