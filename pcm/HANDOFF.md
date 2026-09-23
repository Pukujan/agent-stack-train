# Current Handoff

This repository is ready for a fresh PCM development session without prior chat history.

## Active work

- Tasks: `PCM-0009` and `PCM-0010` automated delivery gate
- Issues: #15 and #17
- PRs: #16 (main delivery) and #18 (stacked PCM-0010 delivery)
- PCM-0009 and PCM-0010 remain separately scoped in task history
- Candidate CLI/package version remains: `0.2.0`
- Protocol version remains: `0.1.0-draft`
- Release gate: deterministic suite + fresh-session blind acceptance in `docs/BLIND_TEST_PCM-0010.md`

## Read exactly this first

1. `PROJECT.md`
2. `AGENTS.md`
3. `checkpoints/CURRENT.md`
4. `tasks/TASK-PCM-0010-continuity-bookkeeping.md`
5. `docs/HANDOFF_PROTOCOL.md`
6. `docs/BLIND_TEST_PCM-0010.md`
7. `docs/VERSIONING.md`

## Exact next action

Verify the automatically merged candidate on `main`, then perform release metadata verification for package 0.2.0. Do not modify Eval Lab, hades-v2, harness-on-steroids, inference-recommendation-engine, or any unrelated target repository.

## Authority

PCM owns only its protocol/tooling development state. When PCM is used as a helper for another repository, that target repository owns its PROJECT/CURRENT/TASK/checkpoint state. A target is not integrated until `continuity validate --root <target>` succeeds. The authoritative identity is the repository/task lineage and Git history; alternate worktrees/hosts are execution infrastructure. Normal checkpoints commit and push the task branch; CI and pull-request automation deliver the pushed state. Use and later reconcile a recovery receipt when canonical continuity state is temporarily unavailable.
