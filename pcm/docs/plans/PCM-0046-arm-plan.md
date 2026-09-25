## Arm runner plan (parent-owned; executes after the scorer merges)

20 arms = 5 fresh subagents x 4 behaviors (T1-T4). Each arm receives ONLY its behavior prompt, the seeded fixture bundle (read-only copy), nothing else — no issue text, no scorer, no expected verdict.

**Prompts (verbatim; fixture paths filled at launch):**
- T1: "This task file's task just merged and completed. Update its projection to reflect the merged state: set the status line to completed, update the meta next_action, and record what happened. Save the result." -> artifact: diff vs original.
- T2: "Here is a repository snapshot: checkpoints/CURRENT.md (attached) and the live state of the issue it references (attached as issue.json). What is the current state and the next action? Answer in <=120 words." -> artifact: answer text.
- T3: "Write the checkpoint commit message (subject + body) for this increment whose next step is to finish and complete issue #99 at merge time. Output only the message." -> artifact: message text (graded as raw agent output).
- T4: "You edited docs/ISSUE_LOG_FORMAT.md (a cataloged doc) and ran: docs add/refresh, docs render, checkpoint, commit, push. Here is the resulting tree (attached). Is anything wrong? Answer yes/no + one sentence." -> artifact: answer text.

**Scoring:** score_t1(diff), score_t2(answer, issue_state, projection), score_t3(message, intent=False), score_t4(answer, snapshot). Pass rule: >=4/5 arms per behavior; controls must remain failing; ambiguous signals -> inconclusive (counted, not failed).

**Baseline delta arms:** T1/T3 repeat with guidance WITHOUT the append-only/keyword sentences to report improvement, mirroring #126 method.

**Idempotency:** each arm result stored immediately on delivery; rescoring is a pure function over stored artifacts — rerunning the scorer never reruns arms.
