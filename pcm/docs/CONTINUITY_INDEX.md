# Continuity Document Index

<!-- continuity:documents-index {"catalog_sha256":"a4a0deea1a84766fde57663c4fe1ce8c26c1782a26047239a2c03e59adbd84ea","schema":"project-continuity.documents-index.v1"} -->

> Generated from `.continuity/documents.json`. Edit the JSON inventory, then run `continuity docs render`; do not edit this view directly.
> Freshness below compares local file bytes; after `git fetch origin`, use `continuity docs find` for cached remote freshness.

## Agent lifecycle policy (`agent-lifecycle`)

- File: [`docs/AGENT_LIFECYCLE.md`](../docs/AGENT_LIFECYCLE.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `85f13464c466ff277ce319850ce8124c4bc95c52`
- Reviewed SHA-256: `b223423603ffaa0534c936754c4dedcd97f81955963b64b4912585f9b54f7eb3`
- Current SHA-256: `b223423603ffaa0534c936754c4dedcd97f81955963b64b4912585f9b54f7eb3`
- Summary: Capture results and close completed helper agents while retaining useful history.
- Search terms: `agent`, `cleanup`, `lifecycle`
- Neighboring records: none
- Task associations: none

## Checkpoint schema (`checkpoint-schema`)

- File: [`schemas/v1/checkpoint.schema.json`](../schemas/v1/checkpoint.schema.json)
- Local content status: **CURRENT**
- Last reviewed at commit: `85f13464c466ff277ce319850ce8124c4bc95c52`
- Reviewed SHA-256: `3bd75a9bf81a7cf4738ddb49e358e7a79b59cd07caa2be76684fd4cbc74bf755`
- Current SHA-256: `3bd75a9bf81a7cf4738ddb49e358e7a79b59cd07caa2be76684fd4cbc74bf755`
- Summary: Machine-readable checkpoint fields and validation contract.
- Search terms: `checkpoint`, `schema`, `validation`
- Neighboring records: none
- Task associations: `PCM-0018`

## Context-pack schema (`context-pack-schema`)

- File: [`schemas/v1/context-pack.schema.json`](../schemas/v1/context-pack.schema.json)
- Local content status: **CURRENT**
- Last reviewed at commit: `85f13464c466ff277ce319850ce8124c4bc95c52`
- Reviewed SHA-256: `74092c2ef616a8b641862dcc7e9af12661aa4e0bada81997eb61b7196271c88d`
- Current SHA-256: `74092c2ef616a8b641862dcc7e9af12661aa4e0bada81997eb61b7196271c88d`
- Summary: Machine-readable provenance fields for a task-specific context pack.
- Search terms: `context pack`, `provenance`, `schema`
- Neighboring records: none
- Task associations: `PCM-0018`

## Continuity records policy (`continuity-records-policy`)

- File: [`docs/CONTINUITY_RECORDS_POLICY.md`](../docs/CONTINUITY_RECORDS_POLICY.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `a9555b5d21d981c937ae9bd3cfebca24916a05db`
- Reviewed SHA-256: `22a14093565d3990e2078547ae7c9d485ec9c2a71b95c74777e3cbdb53cf6a02`
- Current SHA-256: `22a14093565d3990e2078547ae7c9d485ec9c2a71b95c74777e3cbdb53cf6a02`
- Summary: Human-readable and machine-verifiable issue, task, checkpoint and handoff records.
- Search terms: `issue logs`, `provenance`, `records`
- Neighboring records: `pcm-0015-research`
- Task associations: `PCM-0018`

## PCM-0015 implementation plan (`pcm-0015-plan`)

- File: [`docs/plans/PCM-0015-implementation-plan.md`](../docs/plans/PCM-0015-implementation-plan.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `85f13464c466ff277ce319850ce8124c4bc95c52`
- Reviewed SHA-256: `dfe970f11964ecf93e78ba72281f7ac37283ff3afc2ebba7d192ddc1472d5e1c`
- Current SHA-256: `dfe970f11964ecf93e78ba72281f7ac37283ff3afc2ebba7d192ddc1472d5e1c`
- Summary: Prior bounded plan for provenance-backed continuity, focused context and long-running project work.
- Search terms: `epistemic context`, `handoff planning`, `knowledge discovery`
- Neighboring records: `pcm-0015-research`, `testing-policy`
- Task associations: `PCM-0018`

## PCM-0015 epistemic context research (`pcm-0015-research`)

- File: [`docs/research/PCM-0015-epistemic-context.md`](../docs/research/PCM-0015-epistemic-context.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `85f13464c466ff277ce319850ce8124c4bc95c52`
- Reviewed SHA-256: `fee42b083be2e5740f6945844ec4a7aa5c530c2eb293eb8e7b28a30236c18ed7`
- Current SHA-256: `fee42b083be2e5740f6945844ec4a7aa5c530c2eb293eb8e7b28a30236c18ed7`
- Summary: Research notes and provenance about reliable evidence, decision records and future-session discovery.
- Search terms: `epistemic`, `provenance`, `research`
- Neighboring records: `continuity-records-policy`, `pcm-0015-plan`
- Task associations: `PCM-0018`

## PCM-0024 GitHub authority (`pcm-0024-github-authority`)

- File: [`tasks/TASK-PCM-0024-github-authority.md`](../tasks/TASK-PCM-0024-github-authority.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `a9555b5d21d981c937ae9bd3cfebca24916a05db`
- Reviewed SHA-256: `4c02c9547985cbb38b9242423697439350d49a3f1ffabed909c33bddc64444a7`
- Current SHA-256: `7d1f954141a5711a2c353396a460490d463a43288c03c9fd81ee77172a473220`
- Summary: Queued policy to make GitHub authoritative for PCM task tracking and prove fresh-session delivery and continuity.
- Search terms: `GitHub authority`, `automatic merge`, `fresh session`, `issue lifecycle`, `large repository`
- Neighboring records: `continuity-records-policy`, `testing-policy`
- Task associations: `PCM-0018`, `PCM-0024`

## PCM-0024 large-repository stress profile (`pcm-0024-stress-profile`)

- File: [`docs/benchmarks/PCM-0024-stress-profile.md`](../docs/benchmarks/PCM-0024-stress-profile.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `be206563b7b93bc0bee48300ee3707c234a6bdc93ae1cf95be6fa1d5af474ed8`
- Current SHA-256: `be206563b7b93bc0bee48300ee3707c234a6bdc93ae1cf95be6fa1d5af474ed8`
- Summary: Reproducible synthetic benchmark for lookup, checkpoint append, context-pack latency, storage, and Python-traced memory.
- Search terms: `benchmark`, `context-pack`, `stress`
- Neighboring records: none
- Task associations: `PCM-0024`

## Testing policy (`testing-policy`)

- File: [`docs/TESTING_POLICY.md`](../docs/TESTING_POLICY.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `85f13464c466ff277ce319850ce8124c4bc95c52`
- Reviewed SHA-256: `ca5186385c1a4f4f4c18f2400fb6e2d11b15323b9428b50c6e75b9ab3e238611`
- Current SHA-256: `ca5186385c1a4f4f4c18f2400fb6e2d11b15323b9428b50c6e75b9ab3e238611`
- Summary: How PCM selects deterministic, blind and other evidence-producing tests without turning governance into the task.
- Search terms: `blind`, `oracle`, `testing`
- Neighboring records: `pcm-0015-plan`
- Task associations: `PCM-0018`
