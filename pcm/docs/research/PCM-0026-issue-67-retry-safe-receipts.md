# PCM-0026 / issue 67 — Research for retry-safe GitHub receipts

This is the durable research record for [leaf #67](https://github.com/Pukujan/project-continuity-modules/issues/67), under [parent #53](https://github.com/Pukujan/project-continuity-modules/issues/53), dependent on [policy #66](https://github.com/Pukujan/project-continuity-modules/issues/66). It addresses the gap between a successful checkpoint push and a missing, duplicated, or partially published GitHub receipt. Author: owner-authorized planning/research/verification lead, operating under the Astra assignment role. Access and observation date: **2026-09-24**.

Like the [PCM-0015 research record](PCM-0015-epistemic-context.md), this records requirements, sources, observations, decisions and uncertainty separately. **Evidence is not implementation proof.** Neither citations nor a successful policy CI run demonstrate that the new publisher works. The implementation contract, properties and executable-test plan are together in [TASK-PCM-0026](../../tasks/TASK-PCM-0026-github-receipts.md); staff must implement that contract, not substitute a design of their own.

## Accepted prerequisite and ownership

**Observed external state:** issues #66, #53 and #67 were OPEN. PR [#68](https://github.com/Pukujan/project-continuity-modules/pull/68) merged candidate `6af791384713c3ead4064273fc801b85e8c7c9bd` as `9328f363a56d46290904b786eb43cff87e23c2b4` at 2026-09-24T16:03:43Z. Pull-request run [36024619438](https://github.com/Pukujan/project-continuity-modules/actions/runs/36024619438) identifies that candidate SHA and succeeded. Its six protected contexts (quality, test on 3.11/3.12, package, package parity on 3.11/3.12) and pull-request auto-merge job succeeded. Squash auto-merge was enabled at 16:03:09Z. Current protection requires those six contexts, strict current-base checks and zero approving reviews; force pushes are disabled and administrators are covered. Current protection is an as-of observation, not a claim that we reconstructed every historical rules change. Earlier skipped auto-merge jobs are different runs, not the accepted pull-request run.

**Observed repository state:** fetched `origin/main` includes the policy merge. Planning base is `af4b8b27eb0298c6d2b6ff5970fbf8df9d0b3836`, which also includes staff's operating-model PR [#70](https://github.com/Pukujan/project-continuity-modules/pull/70). That document is outside this edit scope. The canonical checkout is on `task/PCM-0026-github-receipts`; this session created no clone or worktree.

**Owner decision:** [activation comment 5818847546](https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5818847546) accepts #66's delivered policy scope as PCM-0026's prerequisite, reserves the task/branch/primary writer, and supersedes the queued/unassigned start boundary. This changes permission to begin PCM-0026, not issue #66's lifecycle or any observed CI fact. The existing [leaf receipt](https://github.com/Pukujan/project-continuity-modules/issues/66#issuecomment-5818370226) and [parent receipt](https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5818370504) remain intact; neither was reposted. **#53 remains OPEN.**

Reproduction: `gh issue view 66/53/67 --repo Pukujan/project-continuity-modules --json number,title,state,body,updatedAt,comments` (one issue per invocation); `gh pr view 68 --repo Pukujan/project-continuity-modules --json state,headRefOid,baseRefOid,mergeCommit,mergedAt,autoMergeRequest,statusCheckRollup`; `gh api repos/Pukujan/project-continuity-modules/branches/main/protection`; `gh api repos/Pukujan/project-continuity-modules/actions/runs/36024619438`; `git fetch origin`; `git merge-base --is-ancestor 9328f363a56d46290904b786eb43cff87e23c2b4 origin/main` (exit 0). Installed `gh` is 2.93.0; `gh api user --jq .login` returned `Pukujan`. Tokens were neither printed nor recorded.

## Direct source register

Every URL below was fetched and its relevant text read by this planning session on **2026-09-24**. HTTP fetches returned 200. Staff's earlier citation summaries were discovery leads only, not accepted evidence.

| ID | Title and primary URL | Claim supported; boundary |
| --- | --- | --- |
| S1 | GitHub, [REST API endpoints for issue comments](https://docs.github.com/en/rest/issues/comments#list-issue-comments) | Issue comments are ordered by ascending ID; `per_page` defaults to 30 and permits 100; `page` and `since` are supported. Read raw Markdown `body`, not rendered HTML. A first page cannot establish absence. |
| S2 | GitHub, [Create an issue comment](https://docs.github.com/en/rest/issues/comments#create-an-issue-comment) | `POST /repos/{owner}/{repo}/issues/{issue_number}/comments` takes `body`; 201 returns the comment ID, URL, body and author. Fine-grained permissions include Issues write or Pull requests write. Listed errors include 403, 404, 410, 422. Creation triggers notifications and can be secondarily rate limited. The inspected endpoint contract documents no client idempotency key or conditional create. Absence in these docs is not proof of every server implementation detail. |
| S3 | GitHub, [Using pagination in the REST API](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api) | The Link header identifies additional pages; omission can mean one complete page. Follow pagination to a proven end or stop with an explicit incomplete-lookup result. A bounded cutoff must not become evidence that a marker is absent. |
| S4 | GitHub, [Best practices for using the REST API](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api) | Serialize requests; pause at least one second between large numbers of mutations. Respect Retry-After and rate-reset headers; otherwise wait at least a minute for rate-limit failures and stop after bounded retries. These recommendations do not make a POST idempotent. |
| S5 | GitHub CLI, [gh api manual](https://cli.github.com/manual/gh_api), corroborated by installed `gh api --help` | `--input` accepts a file or stdin; explicit `--method GET` is necessary when using field parameters for a read; `--include` exposes response headers; `--paginate` follows all pages. Use argv and structured JSON through stdin, never shell interpolation of body text. Unlimited CLI pagination is unsuitable for the contract's finite page budget. |
| S6 | IETF, [RFC 9110: HTTP Semantics, section 9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2), June 2022 | A client SHOULD NOT automatically retry a non-idempotent method unless it knows the semantics are idempotent or can determine the original was never applied. A lost response is not proof of non-application. |
| S7 | Malcolm Featonby, AWS Builders' Library, [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | Caller-supplied request identifiers express intent; a reused identifier with different parameters should fail validation. AWS describes atomically recording the token with server-side effects. PCM cannot infer that GitHub supplies this atomicity merely by placing a marker in a body. |
| S8 | T. Y. Chen, S. C. Cheung and S. M. Yiu, [Metamorphic Testing: A New Approach for Generating Next Test Cases](https://arxiv.org/abs/2002.12543), report HKUST-CS98-01, arXiv v1 posted 2020-02-28 | The inspected abstract describes deriving additional cases from successful tests and testing where ordinary oracles are unavailable. This supports testing retry/permutation relations. Only the abstract/record was independently read here; no peer-review status or full-paper result is asserted. |

Fetch provenance, SHA-256 over received HTML bytes (content hashes aid audit; they do not establish truth):

| Resource | SHA-256 |
| --- | --- |
| S1/S2 combined comments page | `8324748dbbcd6107b796292552e0df4f2d583612065162735a02502d75e6d055` |
| S3 | `cce4f4cef17f4f1e045c79f245a321c4c21d9d884d1bac28a1fee6eb526532fc` |
| S4 | `4eddda65572223fe47f676631870e4adc08c976e3940cfd52387bed8eb51f7f1` |
| S5 | `8cc05b0daf5bbe677853c72426001fc0fc84f1d6b2be83b41e43ea12169132bd` |
| S6 | `d431760660ea44e130f6e919dab216df2d0b3a490567a98089267523368fe1e5` |
| S7 | `4b2546f6c45a713098c8052345e26dffa407aa9f543024e5a7ed2372ae0166` |
| S8 | `af765ccb68f12d08e9ad9a666b747db82798725304f7b1721f883605ac6136f7` |

## Existing implementation and discovery

**Observed repository facts at the planning base:** [`publish_checkpoint`](https://github.com/Pukujan/project-continuity-modules/blob/af4b8b27eb0298c6d2b6ff5970fbf8df9d0b3836/src/continuity/cli.py#L2468) commits the checkpoint and invokes Git push, returning the commit SHA. Its existing retry path checks for a matching committed checkpoint. It has no comment transaction. [`checkpoint_payload_sha256`](https://github.com/Pukujan/project-continuity-modules/blob/af4b8b27eb0298c6d2b6ff5970fbf8df9d0b3836/src/continuity/cli.py#L1683) excludes first-write timestamp; receipt identity must not change that historical format. `verify_task_issue` checks identity/status, not ownership or semantic lineage. `local_task_lock` already provides an OS-backed per-repository/task lock; it is not a distributed lock.

Existing [`test_checkpoint_retries.py`](https://github.com/Pukujan/project-continuity-modules/blob/af4b8b27eb0298c6d2b6ff5970fbf8df9d0b3836/tests/test_checkpoint_retries.py) includes accepted-push/lost-response recovery and changed-payload rejection. This inspection is not a new run of those tests. Their Git behavior supplies a compatibility baseline; it is not an oracle for new GitHub behavior.

`continuity docs find 'Publish retry-safe GitHub checkpoint receipts publisher automation' --task PCM-0026` after fetch returned SPEC, PCM-0024, records policy and their research/testing neighbors as CURRENT; those sources were read. The existing optional catalog does not require registering every new research file. This pass leaves the catalog unchanged and assigns explicit registration/render verification to staff. Task links make this note discoverable immediately. No duplicate research note or general process document is needed.

## Decisions derived from the evidence

1. **Accepted design:** use the existing publisher plus a narrow `gh api` adapter, opt-in receipt context, frozen payload and an explicit receipt-only resume command. An existing non-GitHub or recovery-checkpoint call keeps its old behavior; manual receipts remain required wherever automation is not selected or cannot verify its inputs.
2. **Accepted design:** stable identity is repository/task/request ID/exact pushed SHA, plus destination and receipt kind. A canonical payload digest detects changed intent. The marker is an application convention, not a GitHub uniqueness constraint. Historical manual `pcm:receipt` merge markers are not silently upgraded into the new format.
3. **Accepted design:** complete bounded lookup precedes a new comment. A lost response triggers bounded reads only; an exact remote comment recovers success. If the result remains unknown, stop visibly instead of issuing another POST. The distinction between a request known never attempted and one possibly dispatched survives process restart in a private local attempt guard.
4. **Authority boundary:** that guard is a transport safety interlock, never task/progression truth. It can forbid a POST but cannot prove receipt existence or delivery. Missing/corrupt guard during resume defaults to read-only recovery. No background outbox dispatcher, local canonical ledger, scheduler or distributed lock is introduced. Losing the guard may reduce availability; it must not reduce safety.
5. **Accepted design:** one local writer, sequential leaf then nearest parent outward; remote body/actor/identity checks always settle receipt existence. Discovered duplicate or mismatched markers stop with links. Cross-device check-then-create races remain possible without coordinated ownership or server uniqueness; do not claim exactly-once delivery against arbitrary concurrent clients.
6. **Accepted test strategy:** deterministic fault injection and a separately written finite-state reference model, plus metamorphic retries, irrelevant-comment insertion and page-boundary shifts. Compare legacy Git behavior with the pinned accepted base. Hosted production outage, replication consistency, second-account permissions and universal secret detection remain unverified. No stochastic fresh-agent holdout is needed for this bounded API behavior change.

## Unknowns and acceptance limits

- GitHub read-after-write visibility timing after a timed-out POST is **unknown** from the inspected contract. Absence after a bounded lookup is not proof of failed creation.
- Server-side duplicate suppression, GraphQL clientMutationId idempotency, and atomic conditional comment creation are **not established**. The plan uses none of them.
- No credentialed create-comment failure experiment was run. This session posted only the owner-authorized issue-67 activation, not synthetic receipts.
- A live issue's arbitrary prose cannot be semantically verified by a deterministic parser. A human-reviewed authority snapshot plus exact drift checks supplies the boundary; unreviewed drift stops mutation.
- Secret/path rejection can cover the specified syntactic classes and known credentials; it cannot prove arbitrary free text contains no secret. Do not serialize subprocess environments or raw error bodies.
- PCM-0026 is planned, not implemented, pushed or delivered. Staff test results, full local gates and hosted required checks remain pending. The lead retains acceptance decisions.

Next action: Kilo executes released worker TASK-04 against task-contract sections S1–S3 and tests T01–T05, returns red/green evidence, and closes that worker. Later assignments remain held until lead review.
