# Continuity Document Index

<!-- continuity:documents-index {"catalog_sha256":"61a020cdbfea9d286f138f70d9f9b6e1629dcb21eac87f8bc04a4b663691357f","schema":"project-continuity.documents-index.v1"} -->

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

## PCM architecture guide (`architecture-guide`)

- File: [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `ae83b9b6ba84dcc02963c6a467adbc52e3448dc08860cdae1f82c8c3ce1a96e3`
- Current SHA-256: `ae83b9b6ba84dcc02963c6a467adbc52e3448dc08860cdae1f82c8c3ce1a96e3`
- Summary: How PCM works: ownership of issues/history/projections, checkpoints, resume, self vs adopter, doc versioning.
- Search terms: `architecture`, `checkpoint`, `doc-system`, `ownership`, `resume`
- Neighboring records: `continuity-records-policy`, `issue-log-format`
- Task associations: `PCM-0043`

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
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `7f3a0315a2bcfdd04ecac004bae277ce3b2a39efc1778d441666d2eadbd52f5b`
- Current SHA-256: `569625b28335029c844eb0e2a6510bcf09a1e1b0bbb62d23d634af96e95f54c4`
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

## PCM-0046 holdout arm runner plan (`pcm-0046-arm-plan`)

- File: [`docs/plans/PCM-0046-arm-plan.md`](../docs/plans/PCM-0046-arm-plan.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `381b052e0b0cf4ac835391a923b8d248a936a4a753d68a4e6cabedac9ccca113`
- Current SHA-256: `381b052e0b0cf4ac835391a923b8d248a936a4a753d68a4e6cabedac9ccca113`
- Summary: Pre-registered 20-arm hidden holdout protocol: verbatim prompts, scoring, baseline delta, idempotency.
- Search terms: `arms`, `holdout`, `scoring`, `traversal`
- Neighboring records: `pcm-0050-research`
- Task associations: `PCM-0046`

## PCM-0048 task projection (`pcm-0048-task`)

- File: [`tasks/TASK-PCM-0048-deployed-environment.md`](../tasks/TASK-PCM-0048-deployed-environment.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `1d3671d62ad8872b9798415da5b46d9ab7cffbe7`
- Reviewed SHA-256: `cc2baa046a4a1b3408d7843b3a1f37186fab235d69ce4539fbd426adb9508a9e`
- Current SHA-256: `cc2baa046a4a1b3408d7843b3a1f37186fab235d69ce4539fbd426adb9508a9e`
- Summary: Decision-slice projection for PCM-0048.
- Search terms: `PCM-0048`, `decision`, `projection`
- Neighboring records: none
- Task associations: `PCM-0048`

## PCM-0049 task projection (`pcm-0049-task`)

- File: [`tasks/TASK-PCM-0049-adopter-issue-filing.md`](../tasks/TASK-PCM-0049-adopter-issue-filing.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `1d3671d62ad8872b9798415da5b46d9ab7cffbe7`
- Reviewed SHA-256: `19fb393e3d724bfcdd79beb17bcda5e08e5190b0c5a52125e6164aaf13aa3762`
- Current SHA-256: `19fb393e3d724bfcdd79beb17bcda5e08e5190b0c5a52125e6164aaf13aa3762`
- Summary: Decision-slice projection for PCM-0049.
- Search terms: `PCM-0049`, `decision`, `projection`
- Neighboring records: none
- Task associations: `PCM-0049`

## PCM-0050 epistemic bitemporal records research (`pcm-0050-research`)

- File: [`docs/research/PCM-0050-epistemic-bitemporal-records.md`](../docs/research/PCM-0050-epistemic-bitemporal-records.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `4f591713d8ebbfda17111fecef6e533b4207f6410310974787b58a95ba60b91b`
- Current SHA-256: `4f591713d8ebbfda17111fecef6e533b4207f6410310974787b58a95ba60b91b`
- Summary: Bitemporal/PROV prior art, PCM-0015 S9 delta analysis, options O1-O4 for claim provenance, adopter ticket placement, and record aging.
- Search terms: `adopter-feedback`, `bitemporal`, `claim`, `epistemic`, `provenance`, `supersession`
- Neighboring records: `continuity-records-policy`, `issue-log-format`, `pcm-0015-plan`, `pcm-0015-research`
- Task associations: `PCM-0050`

## PCM-0050 task projection (`pcm-0050-task`)

- File: [`tasks/TASK-PCM-0050-epistemic-records.md`](../tasks/TASK-PCM-0050-epistemic-records.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `1d3671d62ad8872b9798415da5b46d9ab7cffbe7`
- Reviewed SHA-256: `dbbd6d7b5fa5a65342093a421eed3fbed7b5d852eed588871c3e15c5dda07599`
- Current SHA-256: `ff58ee74966516c129346aa02cd241157bdae1c113ee7b82a498bac270f3514e`
- Summary: Decision-slice projection for PCM-0050.
- Search terms: `PCM-0050`, `decision`, `projection`
- Neighboring records: none
- Task associations: `PCM-0050`

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
