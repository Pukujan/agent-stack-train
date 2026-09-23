# Current Handoff

This repository is ready for a fresh PCM development session without prior chat history.

## Active work

- PCM-0015 is complete as a planning-only task. Its plan merged in PR #29 at `b379ba3`; issue #28 is closed. Read `tasks/TASK-PCM-0015-versioned-project-memory.md` and `docs/plans/PCM-0015-implementation-plan.md` only when working on those follow-ups. The plan does not mean the proposed capabilities have been implemented.
- PCM-0014 is complete and merged automatically in PR #26 at `b9e0f7c`.
- GitHub issue #24 is closed by PR #26.
- Open reports are tracked separately: #30-35. Issue #17 remains unresolved; its blind failure reproduction/fix has not been completed.
- PCM-0012 and PCM-0013 remain separately recorded workspace-policy histories.
- Candidate CLI/package version remains: `0.2.0`
- Protocol version remains: `0.1.0-draft`

## Read exactly this first

1. `PROJECT.md`
2. `AGENTS.md`
3. `checkpoints/CURRENT.md`
4. `SPEC.md`
5. `docs/HANDOFF_PROTOCOL.md`
6. `docs/AGENT_LIFECYCLE.md`
7. `docs/VERSIONING.md`

## Exact next action

First inspect open issue #17 and its original acceptance. If continuing it, use an isolated disposable PCM-adopted repo and a blind test agent, preserve any already-authorized host/worktree route, record the observed behavior, then fix only if reproduced and rerun the same blind scenario. Do not claim this was done by PCM-0015. Separately prioritize only one issue from #30-35 at a time. Keep queued PCM-0005 separate and do not modify Eval Lab, hades-v2, harness-on-steroids, inference-recommendation-engine, or any unrelated target repository.

## Authority

PCM owns only its protocol/tooling development state. When PCM is used as a helper for another repository, that target repository owns its PROJECT/CURRENT/TASK/checkpoint state. A target is not integrated until `continuity validate --root <target>` succeeds. The authoritative identity is the repository/task lineage and Git history; alternate worktrees/hosts are execution infrastructure. Normal checkpoints commit and push the task branch; CI and pull-request automation deliver the pushed state. Use and later reconcile a recovery receipt when canonical continuity state is temporarily unavailable.
