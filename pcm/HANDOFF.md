# Current Handoff

This repository is ready for a fresh PCM development session without prior chat history.

## Active work

- PCM-0015 is active as a planning-only task. Read `tasks/TASK-PCM-0015-versioned-project-memory.md`, `docs/research/PCM-0015-epistemic-context.md`, and `docs/plans/PCM-0015-implementation-plan.md`. The discussion transcript distinguishes user requirements, repository facts, prior proposals, and open questions; the adjacent PROV-O graph records provenance. The plan proposes only a small proof path first; its later slices are conditional, and it authorizes no implementation.
- PCM-0014 is complete and merged automatically in PR #26 at `b9e0f7c`.
- GitHub issue #24 is closed by PR #26.
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

Finish parent review and run repository validation/full tests for the planning-only PCM-0015 changes, then use the normal pushed-branch/required-CI/auto-merge delivery path. Capture Astra's result and close the worker. After merge, decide separately whether to open only the first bounded proof slice. Keep PCM-0005 separate and do not modify Eval Lab, hades-v2, harness-on-steroids, inference-recommendation-engine, or any unrelated target repository.

## Authority

PCM owns only its protocol/tooling development state. When PCM is used as a helper for another repository, that target repository owns its PROJECT/CURRENT/TASK/checkpoint state. A target is not integrated until `continuity validate --root <target>` succeeds. The authoritative identity is the repository/task lineage and Git history; alternate worktrees/hosts are execution infrastructure. Normal checkpoints commit and push the task branch; CI and pull-request automation deliver the pushed state. Use and later reconcile a recovery receipt when canonical continuity state is temporarily unavailable.
