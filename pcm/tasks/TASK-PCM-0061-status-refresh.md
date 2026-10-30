# TASK-PCM-0061 — Status Refresh

<!-- continuity:task {"acceptance":["README status layer re-pinned to d46e0b7 (intro, checked-at line, four stale rows, line-number citations) with hero images and marketing prose untouched (diff-hunk verified); every changed claim re-verified against live sources before commit.","SPEC.md and docs/ARCHITECTURE.md cite 1.2.0; docs/VERSIONING.md carries the dated 1.2.0 entry; grep shows no stale current-state 0.5.0/1.1.0 claims outside historical narrative.","Delivered issues (#175,#177,#180) and superseded PRs (#93,#111) closed with cited receipts/rationale; #171 left open pending owner confirmation; PR merged under six contexts with merge receipt on #184."],"depends_on":[],"goal":"Refresh the human-facing status layer without touching the marketing half: re-pin the README evidence table to current head, fix stale 1.1.0 refs in SPEC/ARCHITECTURE, VERSIONING 1.2.0 entry, and close superseded issues/PRs with receipts (#184).","id":"PCM-0061","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/184","next_action":"Checkpoint, open PR from task/PCM-0061-status-refresh, arm auto-merge after the final push, then execute close-outs at merge receipt.","owner":"owner/Astra planning","priority":"P2","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The table advertises 0.5.0/1.1.0/138-tests and calls receipt posting experimentally_supported; six deliveries plus four proven production receipts later it under-reads what is real, and open-issue noise hides the actual owner gates."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Refresh the human-facing status layer without touching the marketing half: re-pin the README evidence table to current head, fix stale 1.1.0 refs in SPEC/ARCHITECTURE, VERSIONING 1.2.0 entry, and close superseded issues/PRs with receipts (#184).

## Why

The table advertises 0.5.0/1.1.0/138-tests and calls receipt posting experimentally_supported; six deliveries plus four proven production receipts later it under-reads what is real, and open-issue noise hides the actual owner gates.

## Allowed files

- `README.md` (evidence table + status sentences ONLY; hero images and marketing sections untouched per owner instruction), `SPEC.md` (1.1.0->1.2.0 ref), `docs/ARCHITECTURE.md` (two 1.1.0 refs), `docs/VERSIONING.md` (1.2.0 entry), task projections for PCM-0059..0062 (new), `checkpoints/CURRENT.md`, `.continuity/documents.json`, `docs/CONTINUITY_INDEX.md` (generated).

## Human outcome

A visitor's "what is real today" table tells the truth again — 0.6.0, 1.2.0, 264 tests, receipts proven in production — each row verified at the commit it links; the normative docs agree with the shipped markers; and the open-issue list shows only real work and owner gates, not delivered-but-open noise.

## Scope and boundaries

- In scope: status-layer accuracy + lifecycle hygiene as described on #184; every table claim re-verified against the live API/git before commit.
- Out of scope: README marketing prose, hero images, and the image-generation section (owner: untouched); any CLI/code change; reopening frozen decisions (#67/#110).
- Dependencies/uncertainty: close-outs for #175/#177/#171/#180 need their existing receipts cited (all verified to exist via the comments API before closing); #93/#111 closures must record why superseded (PR refs persist).

## Acceptance criteria

- [x] README re-pinned to `d46e0b7`: intro sentence, checked-at-commit line, and the four stale rows (0.5.0->0.6.0, 1.1.0->1.2.0+readability, receipts experimentally_supported->proven with production comment ids cited, 138-tests row -> 264/CI/six-known-failures); stale line-number citations fixed (L473, L1745-1781); marketing half and hero images byte-identical (`git diff` shows only table/intro hunks).
- [x] SPEC.md:187 and ARCHITECTURE 1.2.0 refs corrected; docs/VERSIONING.md gains the dated 1.2.0 entry; no stale 1.1.0/0.5.0 claims remain outside pinned historical narrative (grep-verified; historical changelog lines intentionally stay).
- [ ] Close-outs executed with receipts cited: issues #175/#177/#180 (and #171 on owner confirmation), PRs #93/#111 as superseded-with-rationale; then PR merged under six contexts + merge receipt on #184.

## Evidence and sources

Link repository state at a revision and cite external factual claims directly. Record commands and results for claims that need verification.

## Reproduction details (only when needed)

Base `d46e0b7` (#183). Verified before editing: `src/continuity/__init__.py` == 0.6.0; discover = 264 tests / six known names; `gh api .../issues/{175,177,180}/comments` listed the receipt ids quoted in the table; PRs #93 (adds tests/test_receipt_acceptance.py, 2026-09-24, superseded by the #67 frozen route + shipped receipt machinery) and #111 (owner wip pack whose docs/tasks content is all in merged history). Line-number helper recomputed for citations (L24/L473/L1745).

## Related records

- Leaf #184 (PCM-0061); parent: none; depends: none; related #180 (exemplar cited), #169 (audit follow-up), #181/#182/#185 (projections minted on this branch).
- Primary writer: owner/Astra (omp session, omp@studio); branch task/PCM-0061-status-refresh from origin/main `d46e0b7`; source issue revision: #184 body at filing; as-of 2026-09-26T03:35Z.
- Push receipt: continuity checkpoint request pcm-0061-refresh-20260926 (--receipt-issue 184).

## Checkpoint log

No checkpoints yet.

### 2026-09-26 03:46:00 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["PCM-0046 arms window ~04:05Z (2/2 probes 429 at 01:3xZ)."],"changed":["README.md, SPEC.md, docs/ARCHITECTURE.md, docs/VERSIONING.md, tasks/TASK-PCM-0054/0055/0056 markers, tasks/TASK-PCM-0059..0062 (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["README evidence table re-pinned 0b3be9c->d46e0b7 (0.6.0; 1.2.0 readability; receipts proven in production with verified comment ids 5841558506/5842251679/5842595705; 264 tests; stale L462/L1632 citations -> L473/L1745-1781) with marketing half + hero images untouched per owner instruction; SPEC.md + ARCHITECTURE.md 1.1.0->1.2.0; dated VERSIONING 1.2.0 entry; PCM-0059/0060/0061/0062 projections minted with real acceptance arrays; placeholder acceptance markers fixed on PCM-0054/0055; #175/#177/#180 closed at receipts, #93/#111 closed as superseded, #171 delivery note awaiting owner confirmation."],"decisions":["README historical rows stay truthful snapshots; only current-state claims re-pinned. 4 stale items closed without data loss (PR heads remain reachable)."],"evidence":["discover 264 = six known macOS-environmental names (worktrees 3F+1E, test_cli 2F); ruff@0.6.9 two pre-existing ISC003; validate device-local pcm-pinned only; close/receipt ids verified via API in-session before posting; #183 checks: 13 pass lines."],"next_action":"PR task/PCM-0061-status-refresh: arm auto-merge after this final push, merge receipt on #184, then resume PCM-0054 audit implementation on task/PCM-0054-receipt-audit.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0061","timestamp":"2026-09-26T03:46:00Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"b56932408e66cbcf88c647ebdc9a930af18aefdc85474e7cf0b4d2426b269ba1","request_id":"pcm-0061-refresh-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0061"} -->

Completed:
- README evidence table re-pinned 0b3be9c->d46e0b7 (0.6.0; 1.2.0 readability; receipts proven in production with verified comment ids 5841558506/5842251679/5842595705; 264 tests; stale L462/L1632 citations -> L473/L1745-1781) with marketing half + hero images untouched per owner instruction; SPEC.md + ARCHITECTURE.md 1.1.0->1.2.0; dated VERSIONING 1.2.0 entry; PCM-0059/0060/0061/0062 projections minted with real acceptance arrays; placeholder acceptance markers fixed on PCM-0054/0055; #175/#177/#180 closed at receipts, #93/#111 closed as superseded, #171 delivery note awaiting owner confirmation.

Evidence:
- discover 264 = six known macOS-environmental names (worktrees 3F+1E, test_cli 2F); ruff@0.6.9 two pre-existing ISC003; validate device-local pcm-pinned only; close/receipt ids verified via API in-session before posting; #183 checks: 13 pass lines.

Decisions:
- README historical rows stay truthful snapshots; only current-state claims re-pinned. 4 stale items closed without data loss (PR heads remain reachable).

Changed:
- README.md, SPEC.md, docs/ARCHITECTURE.md, docs/VERSIONING.md, tasks/TASK-PCM-0054/0055/0056 markers, tasks/TASK-PCM-0059..0062 (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- PCM-0046 arms window ~04:05Z (2/2 probes 429 at 01:3xZ).

Next:
- PR task/PCM-0061-status-refresh: arm auto-merge after this final push, merge receipt on #184, then resume PCM-0054 audit implementation on task/PCM-0054-receipt-audit.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
