----------------------------- MODULE Lifecycle -----------------------------
(***************************************************************************)
(* The stack's task lifecycle for one issue #N, one agent session and one *)
(* task branch: edit, commit, PCM checkpoint, push, pull request, CI,      *)
(* auto-merge, merge, close-on-merge and the daily close sweep (#73).      *)
(*                                                                         *)
(* Each action names the code it stands for. Where the model relies on    *)
(* GitHub or Claude Code behaving a certain way, the comment says          *)
(* ASSUMED; README.md lists those assumptions and what is left out.        *)
(***************************************************************************)
EXTENDS Naturals

CONSTANTS
    GuardOn,              \* claude_guard.py main(): FALSE models ACS_GUARD=off
    RetryBypass,          \* what a stop with stop_hook_active set skips: "all" is the real code,
                          \* stop(): `if event.get("stop_hook_active"): return None`; "github" skips
                          \* only the checkpoint and pull-request checks (proposed)
    GuardSeesAllBranches, \* FALSE is the real code: checkout_problems() looks only at the checked-out branch
    CheckpointFile,       \* checkpoints/CURRENT.md exists, so stop() asks for a PCM checkpoint
    SweepApply,           \* close-sweep-caller.yml: vars.OIO_CLOSE_SWEEP_APPLY == 'true'
    ArmTokens,            \* tokens the auto-merge workflow can arm with: subset of {"personal", "bot"}
    NativeClose,          \* ASSUMED: GitHub's own keyword close runs for a merge attributed to a user
    MaxEdits              \* bound: how many edits the agent makes in the session

ASSUME RetryBypass \in {"all", "github"}
ASSUME ArmTokens \subseteq {"personal", "bot"}
ASSUME MaxEdits \in Nat

VARIABLES
    issue,       \* "open" | "closed": issue #N on GitHub
    dirty,       \* uncommitted tracked changes (or files the session wrote that git does not track)
    onTask,      \* the checkout has the task branch checked out (FALSE: default branch or detached HEAD)
    local,       \* commits on the task branch that are not on GitHub
    pushed,      \* the task branch has an upstream with commits beyond main
    unmerged,    \* the pushed branch holds content that main does not have yet
    ckpt,        \* the task branch's last commit is a PCM checkpoint ("PCM " subject)
    pr,          \* "none" | "open": the branch's open pull request
    closes,      \* the open pull request says `Closes #N` (FALSE: only `Refs #N`)
    armed,       \* "no" | "personal" | "bot": who armed auto-merge on the open pull request
    ci,          \* "none" | "pending" | "pass" | "fail": the `gates` check on the open pull request's head
    mergedCloses,\* some merged pull request said `Closes #N`
    comRun,      \* "none" | "pending" | "done" | "failed": the last close-on-merge run
    session,     \* "working" | "ended"
    hookActive,  \* Claude Code's stop_hook_active: the agent is continuing because Stop blocked it
    edits        \* edits made so far (bounded by MaxEdits)

vars == <<issue, dirty, onTask, local, pushed, unmerged, ckpt, pr, closes, armed,
          ci, mergedCloses, comRun, session, hookActive, edits>>

TypeOK ==
    /\ issue \in {"open", "closed"}
    /\ dirty \in BOOLEAN /\ onTask \in BOOLEAN /\ pushed \in BOOLEAN
    /\ unmerged \in BOOLEAN /\ ckpt \in BOOLEAN /\ closes \in BOOLEAN
    /\ local \in 0..MaxEdits + 1
    /\ pr \in {"none", "open"}
    /\ armed \in {"no", "personal", "bot"}
    /\ ci \in {"none", "pending", "pass", "fail"}
    /\ mergedCloses \in BOOLEAN
    /\ comRun \in {"none", "pending", "done", "failed"}
    /\ session \in {"working", "ended"}
    /\ hookActive \in BOOLEAN
    /\ edits \in 0..MaxEdits

Init ==
    /\ issue = "open"          \* the owning issue exists before work starts (pre_tool need_issue)
    /\ dirty = FALSE /\ onTask = TRUE /\ local = 0
    /\ pushed = FALSE /\ unmerged = FALSE /\ ckpt = FALSE
    /\ pr = "none" /\ closes = FALSE /\ armed = "no" /\ ci = "none"
    /\ mergedCloses = FALSE /\ comRun = "none"
    /\ session = "working" /\ hookActive = FALSE /\ edits = 0

\* Work that exists only on this machine: what invariant (a) forbids at the end.
LocalOnly == dirty \/ local > 0

(***************************************************************************)
(* The agent. No fairness: it may do anything allowed, in any order, or   *)
(* stop trying.                                                            *)
(***************************************************************************)
Working == session = "working"

\* Edit / Write tools; pre_tool does not block edits.
Edit ==
    /\ Working /\ edits < MaxEdits
    /\ dirty' = TRUE /\ edits' = edits + 1
    /\ UNCHANGED <<issue, onTask, local, pushed, unmerged, ckpt, pr, closes, armed,
                   ci, mergedCloses, comRun, session, hookActive>>

\* git commit; pre_tool check_git blocks a commit on the default branch or a detached HEAD.
Commit ==
    /\ Working /\ onTask /\ dirty
    /\ dirty' = FALSE /\ local' = local + 1 /\ ckpt' = FALSE
    /\ UNCHANGED <<issue, onTask, pushed, unmerged, pr, closes, armed, ci,
                   mergedCloses, comRun, session, hookActive, edits>>

\* A push to an open pull request's branch starts CI again (`synchronize`).
\* ASSUMED: GitHub keeps auto-merge armed across pushes.
CiAfterPush == ci' = IF pr = "open" THEN "pending" ELSE ci

\* git push of the task branch (pre_tool blocks pushes to main and force pushes).
Push ==
    /\ Working /\ onTask /\ local > 0
    /\ local' = 0 /\ pushed' = TRUE /\ unmerged' = TRUE /\ CiAfterPush
    /\ UNCHANGED <<issue, dirty, onTask, ckpt, pr, closes, armed, mergedCloses,
                   comRun, session, hookActive, edits>>

\* `continuity checkpoint`: commits the checkpoint and pushes the branch (pcm/AGENTS.md).
Checkpoint ==
    /\ Working /\ onTask /\ CheckpointFile /\ ~dirty /\ ~ckpt
    /\ local > 0 \/ pushed
    /\ ckpt' = TRUE /\ local' = 0 /\ pushed' = TRUE /\ unmerged' = TRUE /\ CiAfterPush
    /\ UNCHANGED <<issue, dirty, onTask, pr, closes, mergedCloses, armed,
                   comRun, session, hookActive, edits>>

\* gh pr create, saying `Closes #N` or only `Refs #N`. The opened event also
\* starts CI and the auto-merge workflow.
OpenPR ==
    /\ Working /\ onTask /\ pushed /\ unmerged /\ pr = "none"
    /\ pr' = "open" /\ ci' = "pending" /\ armed' = "no"
    /\ closes' \in BOOLEAN
    /\ UNCHANGED <<issue, dirty, onTask, local, pushed, unmerged, ckpt,
                   mergedCloses, comRun, session, hookActive, edits>>

\* gh pr merge --auto --squash, run by the agent with the owner's login.
AgentArm ==
    /\ Working /\ pr = "open" /\ armed = "no"
    /\ armed' = "personal"
    /\ UNCHANGED <<issue, dirty, onTask, local, pushed, unmerged, ckpt, pr, closes,
                   ci, mergedCloses, comRun, session, hookActive, edits>>

\* git switch main / git switch --detach: nothing in pre_tool blocks it, and
\* uncommitted changes travel with the working tree.
SwitchBranch ==
    /\ Working
    /\ onTask' = ~onTask
    /\ UNCHANGED <<issue, dirty, local, pushed, unmerged, ckpt, pr, closes, armed,
                   ci, mergedCloses, comRun, session, hookActive, edits>>

(***************************************************************************)
(* The Stop hook: stop() and checkout_problems() in claude_guard.py.       *)
(***************************************************************************)
\* Work only on this machine, as the hook sees it.
LocalProblems ==
    IF onTask
    THEN dirty \/ local > 0
    ELSE \/ dirty                                  \* on main or detached: only the working tree
         \/ GuardSeesAllBranches /\ local > 0       \* not in the real code

\* Pushed, but not on its way to merging. ghOk = FALSE models gh failing or
\* being offline: stop() then only notes the pull request and does not block.
\* After a squash merge the branch's commits are still not ancestors of main,
\* so `origin/main..HEAD` stays non-zero and the open-PR check still runs.
GitHubProblems(ghOk) ==
    /\ onTask
    /\ \/ pushed /\ CheckpointFile /\ ~ckpt
       \/ pushed /\ ghOk /\ (pr = "none" \/ armed = "no")

Blocks(ghOk) ==
    /\ GuardOn
    /\ IF hookActive
       THEN RetryBypass = "github" /\ LocalProblems
       ELSE LocalProblems \/ GitHubProblems(ghOk)

\* The agent tries to end its turn. ASSUMED (Claude Code): after one block the
\* agent continues with stop_hook_active true until the next user prompt,
\* which the model does not include.
TryStop ==
    /\ Working
    /\ \E ghOk \in BOOLEAN :
         IF Blocks(ghOk)
         THEN /\ hookActive' = TRUE
              /\ UNCHANGED <<issue, dirty, onTask, local, pushed, unmerged, ckpt, pr,
                             closes, armed, ci, mergedCloses, comRun, session, edits>>
         ELSE /\ session' = "ended"
              /\ UNCHANGED <<issue, dirty, onTask, local, pushed, unmerged, ckpt, pr,
                             closes, armed, ci, mergedCloses, comRun, hookActive, edits>>

(***************************************************************************)
(* GitHub: CI, auto-merge, merge, close-on-merge and the sweep. Weakly    *)
(* fair: a step that stays possible eventually happens.                    *)
(***************************************************************************)
\* The `gates` job passes or fails; nothing is assumed about which.
CIRun ==
    /\ ci = "pending"
    /\ ci' \in {"pass", "fail"}
    /\ UNCHANGED <<issue, dirty, onTask, local, pushed, unmerged, ckpt, pr, closes,
                   armed, mergedCloses, comRun, session, hookActive, edits>>

\* auto-merge.yml arms with STACK_UPGRADE_TOKEN ("personal"); the "bot"
\* variant arms with the workflow token.
ArmWorkflow ==
    /\ pr = "open" /\ armed = "no"
    /\ \E t \in ArmTokens : armed' = t
    /\ UNCHANGED <<issue, dirty, onTask, local, pushed, unmerged, ckpt, pr, closes,
                   ci, mergedCloses, comRun, session, hookActive, edits>>

\* GitHub squash-merges an armed pull request once `gates` passes.
\* ASSUMED (auto-merge.yml's comment): a merge armed with the workflow token
\* closes nothing natively and starts no close-on-merge run.
Merge ==
    /\ pr = "open" /\ armed /= "no" /\ ci = "pass"
    /\ pr' = "none" /\ armed' = "no" /\ ci' = "none" /\ unmerged' = FALSE
    /\ mergedCloses' = (mergedCloses \/ closes)
    /\ LET byUser == armed = "personal"
       IN /\ issue' = IF byUser /\ closes /\ NativeClose THEN "closed" ELSE issue
          /\ comRun' = IF byUser THEN "pending" ELSE comRun
    /\ UNCHANGED <<dirty, onTask, local, pushed, ckpt, closes, session, hookActive, edits>>

\* close-on-merge.yml -> oio_close_refs.py --apply: closes the issues the merged
\* pull request names with a closing verb; _settle() skips an issue already closed.
\* The run may fail (token, outage).
CloseOnMerge ==
    /\ comRun = "pending"
    /\ \/ comRun' = "done" /\ issue' = IF closes THEN "closed" ELSE issue
       \/ comRun' = "failed" /\ UNCHANGED issue
    /\ UNCHANGED <<dirty, onTask, local, pushed, unmerged, ckpt, pr, closes, armed,
                   ci, mergedCloses, session, hookActive, edits>>

\* close-sweep.yml -> oio_close_refs.py --sweep --write, daily: closes open
\* issues named with a closing verb by merged pull requests into main.
Sweep ==
    /\ SweepApply /\ mergedCloses /\ issue = "open"
    /\ issue' = "closed"
    /\ UNCHANGED <<dirty, onTask, local, pushed, unmerged, ckpt, pr, closes, armed,
                   ci, mergedCloses, comRun, session, hookActive, edits>>

\* Nothing is left to do: the model's end state, so TLC does not report a deadlock.
Idle == session = "ended" /\ UNCHANGED vars

Next ==
    \/ Edit \/ Commit \/ Push \/ Checkpoint \/ OpenPR \/ AgentArm \/ SwitchBranch \/ TryStop
    \/ CIRun \/ ArmWorkflow \/ Merge \/ CloseOnMerge \/ Sweep \/ Idle

Spec ==
    /\ Init /\ [][Next]_vars
    /\ WF_vars(CIRun) /\ WF_vars(ArmWorkflow) /\ WF_vars(Merge)
    /\ WF_vars(CloseOnMerge) /\ WF_vars(Sweep)

(***************************************************************************)
(* What the stack promises.                                                *)
(***************************************************************************)
\* (a) The session never ends while work is only on this machine.
NoLocalWorkAtEnd == session = "ended" => ~LocalOnly

\* (b) A merged pull request that says `Closes #N` eventually leaves #N closed.
ClosesEventuallyClosed == mergedCloses ~> (issue = "closed")

\* (c) Nothing in the process reopens a closed issue.
NeverReopened == [][issue = "closed" => issue' = "closed"]_issue
=============================================================================
