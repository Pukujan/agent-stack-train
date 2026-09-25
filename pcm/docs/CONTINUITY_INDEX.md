# Continuity Document Index

<!-- continuity:documents-index {"catalog_sha256":"b2cf1bfacc4bce816ed5fc40cca16c3ae5992a50b37bf9e0b324b8a1e03d5d0b","schema":"project-continuity.documents-index.v1"} -->

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

## Astra owner and Grok staff operating model (`astra-grok-staff`)

- File: [`docs/ASTRA_GROK_STAFF.md`](../docs/ASTRA_GROK_STAFF.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `1eeac1d94790df132e38e8c990fdd97adfcf284c`
- Reviewed SHA-256: `e6a55f797d2e7b457ae4edc4f2cac7c29eba5f5ecf5c2c6aed96761c15ec51d8`
- Current SHA-256: `be911bb409ef3be361422c9cd91fb9b99f424e7ecc220220e91e3446fb5e1a05`
- Summary: Astra owns planning and verification. A failure is repaired and Astra is restored. Staff execute assigned tasks and do not choose the next slice.
- Search terms: `Astra`, `Grok staff`, `background helper`, `failure recovery`
- Neighboring records: `agent-lifecycle`
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
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `b88ef1eba097d0927c55e9ef14ba3c76bbb2f5b2`
- Reviewed SHA-256: `c212e2e143c318f47ab578d51d087a1f866f4db713afbb0bdde75e6112f6fbc2`
- Current SHA-256: `f6dd332d5155ab219adf289b766fa80e9ec8b196fb85926311e454252c9e14a9`
- Summary: Human-readable and machine-verifiable issue, task, checkpoint and handoff records.
- Search terms: `GitHub authority`, `issue logs`, `lineage`, `provenance`, `receipts`, `records`
- Neighboring records: `pcm-0015-research`
- Task associations: `PCM-0018`, `PCM-0025`, `PCM-0026`

## GitHub authority and finite progression (`github-progression-spec`)

- File: [`SPEC.md`](../SPEC.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `b88ef1eba097d0927c55e9ef14ba3c76bbb2f5b2`
- Reviewed SHA-256: `b2e589024208e4fe88e84adee7baa7d84a885b11d526f01eae2517dc2b62b527`
- Current SHA-256: `506d0aae9a674f11891597c5508a0e505b9a20ea7aca8b82a87b9c9dc2298e19`
- Summary: Normative field authority, lineage correction, synchronized docs and finite push/CI/merge receipts.
- Search terms: `GitHub authority`, `lineage`, `receipts`
- Neighboring records: `continuity-records-policy`, `testing-policy`
- Task associations: `PCM-0025`, `PCM-0026`

## Issue log format (`issue-log-format`)

- File: [`docs/ISSUE_LOG_FORMAT.md`](../docs/ISSUE_LOG_FORMAT.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `7f3a0315a2bcfdd04ecac004bae277ce3b2a39efc1778d441666d2eadbd52f5b`
- Current SHA-256: `7f3a0315a2bcfdd04ecac004bae277ce3b2a39efc1778d441666d2eadbd52f5b`
- Summary: One plain-language shape for issue logs, updates and PRs that adopters can apply mechanically.
- Search terms: `PR`, `format`, `issue`, `log`, `readability`
- Neighboring records: `continuity-records-policy`
- Task associations: none

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
- Last reviewed at commit: `b88ef1eba097d0927c55e9ef14ba3c76bbb2f5b2`
- Reviewed SHA-256: `403f918b19f35de27139d3fb820d78ae001a15feef6209bbfceaac7af559147c`
- Current SHA-256: `3b4c47fe27ca23b36e1207e8430c892fd8252cf329239d0d39a9fc5e258410b6`
- Summary: Parent GitHub-authority task; current correction removes the second-account requirement and links policy and receipt children.
- Search terms: `GitHub authority`, `automatic merge`, `fresh session`, `issue lifecycle`, `large repository`
- Neighboring records: `continuity-records-policy`, `testing-policy`
- Task associations: `PCM-0018`, `PCM-0024`, `PCM-0025`

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

## PCM-0028 versioned modules design (`pcm-0028-versioned-modules-design`)

- File: [`docs/plans/PCM-0028-versioned-modules-design.md`](../docs/plans/PCM-0028-versioned-modules-design.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `8c600a5b9054b947e86698cfe128e668812feb44b4c2b991f88388bf3bd231e3`
- Current SHA-256: `8c600a5b9054b947e86698cfe128e668812feb44b4c2b991f88388bf3bd231e3`
- Summary: Proposal for independently versioned PCM guidance modules: inventory, stamps, registry, pins, upgrade command and phased rollout. Not implemented.
- Search terms: `issue-log-format`, `modules`, `registry`, `upgrade`, `versioning`
- Neighboring records: `continuity-records-policy`
- Task associations: none

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
