# Continuity Document Index

<!-- continuity:documents-index {"catalog_sha256":"ec01c6f8c48e387ecaea10c23c5ecfb998002f92b75b486e3ab8e0c777ed9e30","schema":"project-continuity.documents-index.v1"} -->

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
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `ae83b9b6ba84dcc02963c6a467adbc52e3448dc08860cdae1f82c8c3ce1a96e3`
- Current SHA-256: `4e3d490452169a87e5c7200834e09d88cf450e4c1f45c6bb96aa2a3f6377063c`
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
- Current SHA-256: `85e4a9ae275753cfeb28bbde8dcedb87fa6d6b1d9f114ee55b7b1a004451362d`
- Summary: Normative field authority, lineage correction, synchronized docs and finite push/CI/merge receipts.
- Search terms: `GitHub authority`, `lineage`, `receipts`
- Neighboring records: `continuity-records-policy`, `testing-policy`
- Task associations: `PCM-0025`, `PCM-0026`

## Issue log format (`issue-log-format`)

- File: [`docs/ISSUE_LOG_FORMAT.md`](../docs/ISSUE_LOG_FORMAT.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `7f3a0315a2bcfdd04ecac004bae277ce3b2a39efc1778d441666d2eadbd52f5b`
- Current SHA-256: `a9cd7d61a96772125e99b6718729678b1d9c01dbc29710de1e20fae25d8a1c56`
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
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `381b052e0b0cf4ac835391a923b8d248a936a4a753d68a4e6cabedac9ccca113`
- Current SHA-256: `270f3fa3499d176d90f8fff77c86526767d36c83571f6e05057fd693fa394c6a`
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
- Current SHA-256: `44a0d5ed5587eeaf028fd0b33d5de72487dcc5b161dfbd8bd532808b70d28a79`
- Summary: Decision-slice projection for PCM-0050.
- Search terms: `PCM-0050`, `decision`, `projection`
- Neighboring records: none
- Task associations: `PCM-0050`

## PCM-0051 sanitizer forms task projection (`pcm-0051-task`)

- File: [`tasks/TASK-PCM-0051-sanitizer-forms.md`](../tasks/TASK-PCM-0051-sanitizer-forms.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `9877b229ca916c0926aa4ffaff3357f9423225133a46dabd96e148f324356b6c`
- Current SHA-256: `e2e0dc78cdbb90e49fba4db9e39830cfc129ba8ddab1d1d2d5f342b618348272`
- Summary: Active task: widen checkpoint sanitizer to colon and cross-repo closing forms.
- Search terms: `PCM-0051`, `closing-keyword`, `sanitizer`
- Neighboring records: none
- Task associations: `PCM-0051`

## PCM-0052 stale installed CLI bypassed the checkpoint sanitizer (incident record) (`pcm-0052-incident`)

- File: [`tasks/TASK-PCM-0052-stale-cli-incident.md`](../tasks/TASK-PCM-0052-stale-cli-incident.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `6171aed26136ab97a7d4ccaefa689ded092a606e6f3cdeaacadc83bb0608fe0a`
- Current SHA-256: `ede105e53c865c54d98b087cf8f9ad7e124b53741675b030485c3dffb074487b`
- Summary: Incident: PR #161 checkpoint composed by uv-tool CLI 0.4.0 (pre-sanitizer) carried a raw closing keyword; squash merge auto-closed active issue #139; reopened with correction; version-drift gate decision open on #162.
- Search terms: `closing-keyword`, `incident`, `sanitizer-bypass`, `stale-cli`, `version-drift`
- Neighboring records: none
- Task associations: `PCM-0052`

## PCM-0053 stale-base guard: checkpoint refuses overlapping upstream edits (`pcm-0053-guard-plan`)

- File: [`tasks/TASK-PCM-0053-stale-base-guard.md`](../tasks/TASK-PCM-0053-stale-base-guard.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `00b2e8bc91952312d8d9d8e5f009f9ae54273f2a09e35b29f5dd57276209e3bb`
- Current SHA-256: `57f46635d3c597a6ad40dc76db12f596c41b42fa98e32934668d5937ac9772b3`
- Summary: Design decision + red-first evidence for the publish-path guard against silently reverting accepted history from a stale local base; incident provenance on #166/#162.
- Search terms: `authoritative-remote`, `checkpoint-guard`, `publish-path`, `stale-base`
- Neighboring records: none
- Task associations: `PCM-0053`

## PCM-0054 durable-publication enforcement matrix + receipt-gap audit proposal (`pcm-0054-durability-receipt-audit`)

- File: [`tasks/TASK-PCM-0054-durability-receipt-audit.md`](../tasks/TASK-PCM-0054-durability-receipt-audit.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `0fb5aca9d0e2f363a45244095313ba01d7510a74`
- Reviewed SHA-256: `1cdd94b473b812508c76de2a43d218e36aa48dc62d30f3a61dcb18cddc4dff22`
- Current SHA-256: `e70d46080278e2f6995e9d2b5e16a3b7d5745e6d233f6f9e2e67ec9bffa416ee`
- Summary: What publish_checkpoint enforces vs convention at 690b7f8; three backfilled merge receipts; detector proposal (Refs #169).
- Search terms: none
- Neighboring records: none
- Task associations: `PCM-0054`

## PCM-0055 receipt JSON wire-format fix (`pcm-0055-receipt-json`)

- File: [`tasks/TASK-PCM-0055-receipt-json-encoding.md`](../tasks/TASK-PCM-0055-receipt-json-encoding.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `b9969f3754738546f287b988cb8f4f7a666dae74858dee344f52f2e723eb8646`
- Current SHA-256: `68fa8f658cb13cbc5e7382905fad7b8a86ab517ef6e2ed24cd0314599b4945e2`
- Summary: gh api --input - needs JSON request parameters; red-first fix + shim test; checkpoint dogfoods the opt-in flags (Refs #171).
- Search terms: none
- Neighboring records: `pcm-0054-durability-receipt-audit`
- Task associations: `PCM-0055`

## PCM-0056 merge-window guidance fold (`pcm-0056-merge-window`)

- File: [`tasks/TASK-PCM-0056-merge-window-guidance.md`](../tasks/TASK-PCM-0056-merge-window-guidance.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `f2261f6600bfda57ebba2b477887977ca567b895bf4e5f66a7c6acfd11d9c635`
- Current SHA-256: `adef641e5766451b2223099d3bd2cd5253c459ada119413240202a4335919b48`
- Summary: Arm auto-merge only after the final push: one sentence in all 9 guidance copies + policy-test pin; parent decision #166 5842002451 (Refs #175).
- Search terms: `auto-merge`, `guidance`, `merge-window`
- Neighboring records: `pcm-0053-guard-plan`
- Task associations: `PCM-0056`

## PCM-0057 version-drift NOTE + 0.6.0 bump (`pcm-0057-version-note`)

- File: [`tasks/TASK-PCM-0057-version-drift-note.md`](../tasks/TASK-PCM-0057-version-drift-note.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `0e9f11baff9f3ee77d2c6a869212b76a40cfa5597a2ab919339d61ef7e0224ed`
- Current SHA-256: `a66afca3757efff6d4d85f5024ad4d0a331b898681fa0c6bb6f2820705bf815b`
- Summary: Checkpoint publishing prints installed-vs-checkout version mismatch (owner decision B, #162 5842002582); 0.5.0->0.6.0 so the PCM-0055 wire change is distinguishable (Refs #177).
- Search terms: `checkpoint`, `observability`, `version-drift`
- Neighboring records: `pcm-0052-incident`
- Task associations: `PCM-0057`

## PCM-0058 readability rules for tool-composed records (`pcm-0058-readability`)

- File: [`tasks/TASK-PCM-0058-readability-rules.md`](../tasks/TASK-PCM-0058-readability-rules.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `f95ffb23ad984d439b5d3dc339b6ea657ff799474b7b1fa18efeabd4d3a910f1`
- Current SHA-256: `8fc447f2fa3f9af5930764c4e17fa9744344603112b847d5d5a853a63be4d3b4`
- Summary: issue-log-format 1.2.0: plain-word meaning before identifiers, claim-first evidence, no bare acronyms; generator+copies+doc+red pins (Refs #180).
- Search terms: `issue-log-format`, `readability`, `records`
- Neighboring records: `pcm-0057-version-note`
- Task associations: `PCM-0058`

## PCM-0059 decision projection (`pcm-0059-decision`)

- File: [`tasks/TASK-PCM-0059-distributed-runtime-promotion.md`](../tasks/TASK-PCM-0059-distributed-runtime-promotion.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `0ae22e2400ec984045ea2ffd224444ba1ba60bd2eeedc174dd2466b6a939d2c6`
- Current SHA-256: `9fae10473dcd88037c818c852b5eae6eec3d4b47f3d2e430962f205af3dd93a8`
- Summary: Decision-record task projection linked to its leaf issue; owner scope gate pending (Refs #181, #182, #185).
- Search terms: `59`, `decision`
- Neighboring records: none
- Task associations: `PCM-0059`

## PCM-0060 decision projection (`pcm-0060-decision`)

- File: [`tasks/TASK-PCM-0060-host-capability-honesty.md`](../tasks/TASK-PCM-0060-host-capability-honesty.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `4b3b7777b71a284744ea5fcd3c2c19241aedf7ad92e6d060e52611a105038eb6`
- Current SHA-256: `2691ff90ac4624e1edfe50d24c801571e17c47b430ea4d37d1d175900709f816`
- Summary: Decision-record task projection linked to its leaf issue; owner scope gate pending (Refs #181, #182, #185).
- Search terms: `60`, `decision`
- Neighboring records: none
- Task associations: `PCM-0060`

## PCM-0061 status refresh and lifecycle hygiene (`pcm-0061-status-refresh`)

- File: [`tasks/TASK-PCM-0061-status-refresh.md`](../tasks/TASK-PCM-0061-status-refresh.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `7ee1d641b07afeae34b34be783b32feb17923191ee50d5c8dce6d3352940619c`
- Current SHA-256: `5dc8e5a553d8e428182cbfe00dd19748d9b80f1a9ba3d3019bedf520ae82aefe`
- Summary: README evidence table re-pinned to d46e0b7, normative 1.2.0 refs, close-outs for #175/#177/#180 + superseded PRs #93/#111 (Refs #184).
- Search terms: `lifecycle`, `readme`, `status`
- Neighboring records: `pcm-0058-readability`
- Task associations: `PCM-0061`

## PCM-0062 decision projection (`pcm-0062-decision`)

- File: [`tasks/TASK-PCM-0062-agent-labeling-convention.md`](../tasks/TASK-PCM-0062-agent-labeling-convention.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `uncommitted`
- Reviewed SHA-256: `dcc2d7a26d153e5cf213b697469f7263ff7e6c7cd283c3339c0f6153bd272d66`
- Current SHA-256: `6a6842a4abc9491485a37504226b5cef045e57254355d3eb02288e7e510eab49`
- Summary: Decision-record task projection linked to its leaf issue; owner scope gate pending (Refs #181, #182, #185).
- Search terms: `62`, `decision`
- Neighboring records: none
- Task associations: `PCM-0062`

## PCM-0063 — T2 staleness read-rule decision (leaf #189) (`pcm-0063-decision`)

- File: [`tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md`](../tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md)
- Local content status: **NEEDS_REVIEW**
- Last reviewed at commit: `82f1e90413c2d45238cc9fb7b6b8a9cc17611e10`
- Reviewed SHA-256: `0b30810ddf5856b2af6dd3d8aae899ff5dd8318f98ec94acb6dac2e04ece9aba`
- Current SHA-256: `69cd22fd4484fd5b166d28d480253a1960e3c1daf0b0be9d9ffea81b277cdb61`
- Summary: Decision task for the read-time staleness-reconciliation rule: PCM-0046 measured T2 at 0/5 (agents follow the stale projection over the closed live issue); owner picks A/B/C on #189 before any guidance slice.
- Search terms: `63`, `decision`, `staleness`
- Neighboring records: `pcm-0046-arm-plan`
- Task associations: `PCM-0063`

## PCM-0064 — Closing-keyword warning rephrase experiment (leaf #190) (`pcm-0064-decision`)

- File: [`tasks/TASK-PCM-0064-keyword-warning-rephrase-experiment.md`](../tasks/TASK-PCM-0064-keyword-warning-rephrase-experiment.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `82f1e90413c2d45238cc9fb7b6b8a9cc17611e10`
- Reviewed SHA-256: `ca7dadc381511260056b914faf7442d895a4b01235bf8f893ac3199dfbd54029`
- Current SHA-256: `ca7dadc381511260056b914faf7442d895a4b01235bf8f893ac3199dfbd54029`
- Summary: Decision task: the candidate keyword-warning sentence showed no measured benefit (T3 3/4 smuggled vs T3b 0/3); owner selects variants to pre-register on #190 before a re-measure ships any text.
- Search terms: `64`, `decision`, `keyword`
- Neighboring records: none
- Task associations: `PCM-0064`

## PCM-0065 — Hidden-arm holdout isolation gates (leaf #191) (`pcm-0065-decision`)

- File: [`tasks/TASK-PCM-0065-holdout-isolation-gates.md`](../tasks/TASK-PCM-0065-holdout-isolation-gates.md)
- Local content status: **CURRENT**
- Last reviewed at commit: `82f1e90413c2d45238cc9fb7b6b8a9cc17611e10`
- Reviewed SHA-256: `49431b88781c6d600d3728eb2de1a50d0889041dfc5db65eab1e0d8722c3e152`
- Current SHA-256: `49431b88781c6d600d3728eb2de1a50d0889041dfc5db65eab1e0d8722c3e152`
- Summary: Decision task: PCM-0046's own harness let arms reach the grader's repository and enumerate sibling bundles; owner picks gate set A/B/C on #191 for future holdouts.
- Search terms: `65`, `decision`, `isolation`
- Neighboring records: none
- Task associations: `PCM-0065`

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
