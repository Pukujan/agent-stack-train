# TASK-PCM-0060 — Host Capability Honesty

<!-- continuity:task {"acceptance": ["Owner picks scope on #182 (probe-only / probe+SPEC adapter-seam / defer); decision comment cited in the task record.", "Chosen slice lands red-first: capability classification of origin host in preflight (or doctor) with a printed matrix, template honesty sentence in all guidance copies + init output, SPEC interface note if approved; full suite at baseline; six contexts + receipt on #182."], "depends_on": [], "goal": "Decide and implement non-GitHub host honesty: capability probe (preflight/doctor), template text that states which duties degrade without GitHub, documented 4-operation adapter seam in SPEC, and an install/onboarding page (#182).", "id": "PCM-0060", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/182", "next_action": "None for PCM-0060. The install and onboarding page continues as PCM-0070 (#262).", "owner": "owner/Claude (agent-stack-train session)", "priority": "P3", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "completed", "why": "Today a GitLab adopter silently loses the issue-authority half while generated guidance promises it (cli.py:2256 github-only parse; nine gh call sites)."} -->

- Status: completed
- Owner: owner/Claude (agent-stack-train session)
- Priority: P3
- Depends on: none

## Goal

Decide and implement non-GitHub host honesty: capability probe (preflight/doctor), template text that states which duties degrade without GitHub, documented 4-operation adapter seam in SPEC, and an install/onboarding page (#182).

## Why

Today a GitLab adopter silently loses the issue-authority half while generated guidance promises it (cli.py:2256 github-only parse; nine gh call sites).

## Allowed files

Owner decision on #182 (2026-10-31, https://github.com/Pukujan/project-continuity-modules/issues/182#issuecomment-6550470762): probe plus SPEC adapter seam. Files: `pcm/src/continuity/cli.py`, `pcm/tests/test_host_capabilities.py`, `pcm/SPEC.md` (section 8.3), `pcm/docs/TARGET_ADOPTION.md`, `pcm/docs/CONTINUITY_INDEX.md` (re-render), and every checked-in copy of the github-progression block (pcm, acs and oio AGENTS/HANDOFF/PROJECT, the pcm templates and the `.github` templates), which gains one Git-only durability sentence.

## Human outcome

Adopters on non-GitHub hosts learn, before being surprised, exactly which continuity guarantees (issue authority, receipts, merge-window checks) their host can and cannot provide, so silent loss of the issue-authority half becomes a stated limitation instead of a surprise.

## Scope and boundaries

- In scope: the decision record + any slice the owner approves on the leaf issue.
- Out of scope: everything the leaf issue's boundaries section excludes.
- Dependencies/uncertainty: none; the owner picked the scope on 2026-10-31. The install/onboarding page from the proposal moved to PCM-0070 (#262) by owner direction on 2026-10-31; #182 is closed.

## Acceptance criteria

- [x] Owner picks scope on #182 (probe-only / probe+SPEC adapter-seam / defer); decision comment cited in the task record.
- [x] Chosen slice lands red-first: capability classification of origin host in preflight (or doctor) with a printed matrix, template honesty sentence in all guidance copies + init output, SPEC interface note if approved; full suite at baseline; six contexts + receipt on #182.

## Evidence and sources

Leaf issue #182 records the current silent-degradation behavior; no host-capability probe exists in the CLI at 0.6.0 (observed: continuity preflight classifies nothing about the origin host).

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #182 (PCM-0060); parent: none; depends: none; related #15, #33/#109, #162, #181.
- Primary writer / branch / source issue revision / as-of status: owner/Astra (omp session); branch task/PCM-0063-projections (projection increment only, no code); source: live issue bodies; as-of 2026-09-26T11:35Z.
- Related PR/CI evidence and push receipt (request ID / SHA): none yet (decision gate); arms evidence rides PCM-0046 (PRs #188/#192/#193).

## Checkpoint log

No checkpoints yet.

### 2026-10-31 00:00:00 UTC — claude-opus-5.5

<!-- continuity:checkpoint {"agent":"claude-opus-5.5","blocked":[],"changed":["pcm/src/continuity/cli.py","pcm/tests/test_host_capabilities.py","pcm/SPEC.md","pcm/docs/TARGET_ADOPTION.md","github-progression copies in pcm, acs and oio"],"completed":["Adopters on hosts other than GitHub were told nothing about which duties stop running; preflight now prints HOST and one CAPABILITY line per duty, warns when config claims GitHub issue authority the host lacks, init prints a NOTE on a non-GitHub origin, every github-progression copy states the Git-only durability fallback, and SPEC 8.3 documents the four-operation host adapter seam (no adapter built)."],"decisions":["Owner picked probe plus SPEC adapter seam on #182 (2026-10-31); install/onboarding page left out of this slice."],"evidence":["Nothing this change could break failed: PCM 340 tests with the same six local-machine worktree/drive failures as the 327-test baseline, plus 13 new host tests passing; ACS 358 passed; OIO suite OK; continuity validate VALID for pcm, acs and oio (product commit d3377f6)."],"next_action":"Open the reader-first PR on Pukujan/agent-stack-train, arm auto-merge, and post the receipt on #182.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0060","timestamp":"2026-10-31T00:00:00Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"a714518f56ca15b194c3686bc15e6260b1d256eb11bd732ee6ce353e31802aa3","request_id":"pcm0060-probe-seam-1","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0060"} -->

Completed:
- Adopters on hosts other than GitHub were told nothing about which duties stop running; preflight now prints HOST and one CAPABILITY line per duty, warns when config claims GitHub issue authority the host lacks, init prints a NOTE on a non-GitHub origin, every github-progression copy states the Git-only durability fallback, and SPEC 8.3 documents the four-operation host adapter seam (no adapter built).

Evidence:
- Nothing this change could break failed: PCM 340 tests with the same six local-machine worktree/drive failures as the 327-test baseline, plus 13 new host tests passing; ACS 358 passed; OIO suite OK; continuity validate VALID for pcm, acs and oio (product commit d3377f6).

Decisions:
- Owner picked probe plus SPEC adapter seam on #182 (2026-10-31); install/onboarding page left out of this slice.

Changed:
- pcm/src/continuity/cli.py
- pcm/tests/test_host_capabilities.py
- pcm/SPEC.md
- pcm/docs/TARGET_ADOPTION.md
- github-progression copies in pcm, acs and oio

Blocked/uncertain:
- none

Next:
- Open the reader-first PR on Pukujan/agent-stack-train, arm auto-merge, and post the receipt on #182.

### 2026-10-31 23:26:51 UTC — claude-opus-5.5

<!-- continuity:checkpoint {"agent":"claude-opus-5.5","blocked":[],"changed":["pcm/tests/test_host_capabilities.py",".github/pull_request_template.md"],"completed":["CI's ruff check failed on an unused json import in the new host tests; removed it. Merged current main (#50 added a root pull request template carrying the GitHub progression block) and gave that copy the Git-only durability sentence."],"decisions":["no new decisions"],"evidence":["ruff passes; PCM 350 tests with the same six local-machine failures as baseline; continuity validate VALID; the PR body passes continuity pr-check."],"next_action":"Wait for CI on Pukujan/agent-stack-train#51 and auto-merge, then post the merge receipt on #182.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0060","timestamp":"2026-10-31T23:26:51Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"2d5f975f6dde325b8ea7a44916d31bdcdb9d0f47869e64905ac1c3307c97c856","request_id":"pcm0060-probe-seam-2","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0060"} -->

Completed:
- CI's ruff check failed on an unused json import in the new host tests; removed it. Merged current main (#50 added a root pull request template carrying the GitHub progression block) and gave that copy the Git-only durability sentence.

Evidence:
- ruff passes; PCM 350 tests with the same six local-machine failures as baseline; continuity validate VALID; the PR body passes continuity pr-check.

Decisions:
- no new decisions

Changed:
- pcm/tests/test_host_capabilities.py
- .github/pull_request_template.md

Blocked/uncertain:
- none

Next:
- Wait for CI on Pukujan/agent-stack-train#51 and auto-merge, then post the merge receipt on #182.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
