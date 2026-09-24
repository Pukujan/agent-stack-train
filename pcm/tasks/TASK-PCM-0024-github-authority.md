# TASK-PCM-0024 — Make GitHub authoritative and prove reliable continuation

<!-- continuity:task {"acceptance":["Amend the normative specification and adopter guidance so GitHub issues are required and authoritative for PCM-governed task scope and lifecycle; keep merged repository history authoritative for accepted code","Deterministic tests verify the authority rule reaches generated guidance and conflict-safe adoption","A disposable GitHub adoption proves pushed checkpoints, required CI, automatic merge, issue closeout, and safe cleanup, including failure behavior","Fresh sessions without parent-chat history reliably find the authoritative issue, repository handoff, actual status, and next action; record observable baseline/candidate evidence and uncertainty","Add a reproducible larger-repository stress profile while keeping differential tests limited to a named trusted reference and tests proportional to the claim","Required local and hosted quality gates pass, changes merge automatically, and final task/checkpoint/handoff state is reconciled before issue #53 closes"],"depends_on":["PCM-0018"],"goal":"Make GitHub the required authority for PCM project tracking and prove that a fresh session can continue the GitHub-owned task through tested, merged delivery and safe cleanup.","id":"PCM-0024","next_action":"After PCM-0018 / issue #33 records its pinned baseline and candidate fresh-session results and its closeout is merged, activate this task from issue #53 and implement the authority contract in bounded slices.","owner":"Codex PCM session; GitHub issue #53","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"queued","why":"The current SPEC treats external trackers as optional mirrors, while the owner requires GitHub authority. A fresh agent must be able to recover task scope/status and complete the push, CI, merge, closeout, and cleanup path without chat history or contradictory local state."} -->

- Status: queued behind PCM-0018 / issue #33
- Owner: Codex PCM session; GitHub issue #53
- Priority: P1
- Depends on: PCM-0018

## Human outcome

A new session should be able to identify the authorized work from GitHub, resume from the repository’s compact checkpoint, and carry the task through required checks, automatic merge, closeout, and safe cleanup without depending on this chat.

## Scope and boundaries

- Issue [#53](https://github.com/Pukujan/project-continuity-modules/issues/53) owns the full scope and acceptance criteria.
- GitHub authority is requested but **not implemented yet**. Do not describe this queued task as a shipped policy.
- Keep PCM-0018 / issue #33 active until its pinned baseline/candidate reports and closeout are recorded; those runs remain distinct evidence.
- Retain the existing human-first issue policy (#32), fresh-session fairness policy (#39), and bounded worktree lifecycle. Do not create an issue per test type or modify unrelated target repositories.

## Acceptance criteria

- [ ] Implement and test the GitHub authority and delivery contract in the normative spec and generated adopter guidance.
- [ ] Verify the policy and end-to-end issue → checkpoint/push → required CI → automatic merge → issue closeout → safe cleanup path in a disposable adoption.
- [ ] Record independent no-history fresh-session results and a reproducible large-repository stress measurement; label what a single run cannot establish.
- [ ] Run local and hosted quality gates, merge automatically, then reconcile task/current/handoff state and clean task-owned resources before closing #53.

## Related records

- Authoritative task issue: [#53](https://github.com/Pukujan/project-continuity-modules/issues/53)
- Pending fresh-session discovery proof: [#33](https://github.com/Pukujan/project-continuity-modules/issues/33)
- Human-first record policy: [#32](https://github.com/Pukujan/project-continuity-modules/issues/32)
- Fresh-session holdout method: [#39](https://github.com/Pukujan/project-continuity-modules/issues/39)

## Checkpoint log

No PCM-0024 checkpoints yet; task is queued.

## Handoff

When activated, read issue #53, PROJECT, CURRENT, this task, and only the relevant policy/test records. First confirm issue #33’s closeout and the current GitHub state; do not rely on a prior chat or treat this task as already implemented.
