# TASK-PCM-0038 — Five-family lifecycle evidence (#53 follow-on)

<!-- continuity:task {"acceptance": ["All five named check families (lint/type/test/package/continuity) run as strict required contexts in the disposable adoption.", "A real trial PR merges with every required context green on the exact candidate head; merge mechanics attributed exactly as the trial timeline shows.", "TR-0002's projection points at its own trial issue and that issue carries the closeout.", "The durable #53 comment names run IDs, SHAs, protections and honest attribution, and the trial repository is archived after recording."], "depends_on": ["PCM-0024"], "goal": "Extend the #53 disposable-adoption proof to all five named check families (lint/type/test/package/manifest-continuity) with observed hosted evidence and record the result durably", "id": "PCM-0038", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/53", "next_action": "None: evidence recorded. See the #53 five-family supplement comment referenced in the Checkpoint log.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "completed", "why": "#53 item 41 names five check families; the merged trial evidence covered three; the gap closed with observation, not argument."} -->

- Status: completed 2026-09-25
- Owner: owner/Astra planning
- Priority: P2
- Depends on: PCM-0024 (child evidence increment; leaf authority stays [#53](https://github.com/Pukujan/project-continuity-modules/issues/53), parent: none)

## Human outcome

The disposable adoption now exercises exactly the five check families #53's acceptance names — lint, type (mypy), test, package (sdist build), and manifest/continuity (`continuity validate` through the installed CLI) — with branch protection read-back confirming all five as required, and a real merged PR green on all five. A cold-start reader gets the evidence without trusting any claim.

## Scope and boundaries

Trial repository `Pukujan/pcm-dogfood-0024-lifecycle` only (workflows, protection, issue links) plus this projection. No PCM product code changes; defects discovered during the trail were filed separately ([#122] index freshness, [#123] closing keywords). #53 stays closed; this is the last evidence supplement (posted after this projection merges).

## Evidence and sources (observed)

- Protection PUT + read-back: required contexts `["lint","type","test","package","continuity"]`, strict, enforce-admins (trial API response 2026-09-25).
- [Trial PR #9](https://github.com/Pukujan/pcm-dogfood-0024-lifecycle/pull/9) head `7730ce3`: all five contexts pass ([run 36138014952](https://github.com/Pukujan/pcm-dogfood-0024-lifecycle/actions/runs/36138014952)); merged `862842c569ad99a845ed3593bcfad84222b6e93f` 2026-09-25T13:03:53Z. Attribution: PR #9 timeline shows no auto-merge event (owner-merged after green); auto-merge firing stays proven by [PR #4](https://github.com/Pukujan/pcm-dogfood-0024-lifecycle/pull/4) (`auto_squash_enabled`, CONFLICTING refusal, fired at `bd0a9ba`).
- Trial issue #7 (TR-0002 owner) closed with closeout [5832880727](https://github.com/Pukujan/pcm-dogfood-0024-lifecycle/issues/7#issuecomment-5832880727); duplicate #8 closed; negative-path #5/PR #6 intentionally OPEN/unmerged as retained failure evidence ([5831842714](https://github.com/Pukujan/pcm-dogfood-0024-lifecycle/issues/5#issuecomment-5831842714)).
- Trial repository re-archived after these facts; links live.

## Checkpoint log

### 2026-09-25 — five-family evidence closed

Completed: five required contexts configured and read back; PR #9 merged green on all five; TR-0002 issue link corrected via trial PR #9; trial issue #7 closeout + archive.

Evidence: links above; #53 supplement comment recorded after this projection merged.

Decisions: honest attribution (no auto-merge claim beyond PR #4's timeline); archive, not delete, to keep evidence links live.

Changed: this file only.

Blocked/uncertain: none.

Next: none — see meta `next_action`.

### 2026-09-25 13:26:07 UTC — owner/Astra planning

<!-- continuity:checkpoint {"agent":"owner/Astra planning","blocked":["None."],"changed":["checkpoints/CURRENT.md; tasks/TASK-PCM-0038-five-family-lifecycle.md."],"completed":["Recorded the five-family lifecycle supplement on #53 after this projection merges; corrected CURRENT's PR #116 merge-SHA citation to 2b28da45d10f55595c1e4118e03e5fad6b46add0."],"decisions":["Archive, not delete, the trial; honest attribution \u2014 auto-merge firing proof remains PR #4 only."],"evidence":["Trial run 36138014952 all five contexts pass on head 7730ce3; merge 862842c; trial issue #7 closeout 5832880727."],"next_action":"Merge this projection PR, then post the #53 five-family supplement comment referenced in this task.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0038","timestamp":"2026-09-25T13:26:07Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"2505a3060a6b61af10e7081d58494bafdc9c44592506cebe07054c37c084ee40","request_id":"pcm0038-evidence-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0038"} -->

Completed:
- Recorded the five-family lifecycle supplement on #53 after this projection merges; corrected CURRENT's PR #116 merge-SHA citation to 2b28da45d10f55595c1e4118e03e5fad6b46add0.

Evidence:
- Trial run 36138014952 all five contexts pass on head 7730ce3; merge 862842c; trial issue #7 closeout 5832880727.

Decisions:
- Archive, not delete, the trial; honest attribution — auto-merge firing proof remains PR #4 only.

Changed:
- checkpoints/CURRENT.md; tasks/TASK-PCM-0038-five-family-lifecycle.md.

Blocked/uncertain:
- None.

Next:
- Merge this projection PR, then post the #53 five-family supplement comment referenced in this task.

## Handoff

Read PROJECT → CURRENT → this task → #53 closeout + supplements. PCM-0024's acceptance now matches its evidence exactly; continuations live only on [#110] (automation research, no slice released) and [#100] (evaluation adjudication).
