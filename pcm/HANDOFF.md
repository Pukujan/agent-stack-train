# Current Handoff

This repository is ready for a fresh PCM development session without prior chat history.

## Active work

- PCM-0015 is complete as a planning-only task. Its plan merged in PR #29 at `b379ba3`; issue #28 is closed. Read `tasks/TASK-PCM-0015-versioned-project-memory.md` and `docs/plans/PCM-0015-implementation-plan.md` only when working on those follow-ups. The plan does not mean the proposed capabilities have been implemented.
- PCM-0014 is complete and merged automatically in PR #26 at `b9e0f7c`.
- GitHub issue #24 is closed by PR #26.
- Open reports are tracked separately: #30-35. Issue #17's baseline failure, fix, and blind rerun are already recorded and merged; this closeout corrects its stale status. Issue #15 remains open because it includes an unperformed target-repository remediation outside current scope.
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

Prioritize issue #34, starting from its focused research and the existing conflict with strict-checkout issue #20. Implement only under a separately activated bounded task with mandatory green CI, push/merge, and safe cleanup acceptance. Keep issue #15's target remediation unperformed; do not modify Eval Lab, hades-v2, harness-on-steroids, inference-recommendation-engine, or any unrelated target repository.

## Authority

PCM owns only its protocol/tooling development state. When PCM is used as a helper for another repository, that target repository owns its PROJECT/CURRENT/TASK/checkpoint state. A target is not integrated until `continuity validate --root <target>` succeeds. The authoritative identity is the repository/task lineage and Git history; alternate worktrees/hosts are execution infrastructure. Normal checkpoints commit and push the task branch; CI and pull-request automation deliver the pushed state. Use and later reconcile a recovery receipt when canonical continuity state is temporarily unavailable.
