# Harder stale-decision test: Claude checks GitHub when it can, and trusts the files when it can't

As of 2026-11-01. Issue: #64 (parent #52). Follows [the easy baseline](2026-11-01-stale-decision-baseline.md). Data: [`2026-11-01-stale-decision-real/`](2026-11-01-stale-decision-real/) (the `quiet` setup is under `quiet/`). Traces: the stack's Phoenix project (`acs-train-development`), traces `365b8820…` (Haiku) and `74776a29…` (Sonnet) for the live and files setups, and `1d7befc3…` (Haiku) and `f1defffd…` (Sonnet) for the quiet setup.

## Question

The easy baseline gave every agent the closed issue next to the stale status file, and all 20 Claude agents passed. That is not the failure #52 is about. In #52 the stale step came out of a large file, with nothing next to it saying it was out of date. This run asks: **when an agent resumes a real task from a full repository snapshot, taken just before the owner made the decision, does it notice that the recorded next action may no longer hold?**

The case is a real one. PCM-0060 is PCM's task for being honest about what non-GitHub hosts lose. At commit `d41dd55`, the task file's next action reads "Owner scope answer on #182 (probe-only / probe+SPEC adapter-seam / defer); then implement per acceptance", and the 33 KB `CURRENT.md` lists #182 among issues waiting on the owner. Since then the owner chose the probe plus the adapter seam, the work merged (agent-stack-train #51 and #57), #182 closed on 2026-10-31, and the leftover install page moved to PCM-0070.

Each agent got the whole `pcm/` tree at that commit (169 files, with no git history) and was asked for PCM-0060's current state and next action. Three setups, five agents each, per model:

- **live:** the prompt says it has a signed-in, read-only `gh` CLI;
- **files:** the prompt says to work from the files only, with no network or `gh`;
- **quiet:** `gh` works, but the prompt doesn't mention it or the network. This is how a real session starts. It was run after the other two, as a follow-up.

## Result

**With `gh` offered, all 10 agents checked GitHub and found the decision.** Every live answer said #182 is closed, PCM-0060 is done, the snapshot is stale, and the remaining work is PCM-0070.

**Without it, half the agents presented the stale step as settled.** A passing files answer can't know the outcome; it passes by saying the record may be out of date and #182 must be checked before acting. Haiku did that 4 times in 5. Sonnet did it once in 5: its other four answers said the task "is active and waiting on a decision from the owner", with no warning.

| Model | Setup | Passed | Presented the stale step as settled | Found the decision | Warned the record may be stale |
|---|---|---|---|---|---|
| Haiku | live | 5 of 5 | 0 | 5 | 5 |
| Haiku | files | 4 of 5 | 1 | 0 | 4 |
| Sonnet | live | 5 of 5 | 0 | 5 | 5 |
| Sonnet | files | 1 of 5 | 4 | 0 | 1 |

The Haiku answers that passed pointed at the dates: the snapshot's newest entry is from late September, and they said the owner may have answered since. The Sonnet answers that failed gave the same dates as facts ("The status was last updated 2026-09-26") and didn't draw that conclusion.

**In the realistic setup, no agent was misled (10 of 10 passed), but not every agent checked.** With `gh` working and unmentioned, every Haiku agent ran `gh` on its own and found the decision. Three Sonnet agents did. The other two read only the files, gave the stale owner gate as the next step, and said they couldn't tell whether #182 had been answered since. That warning is what made them pass.

| Model | Setup | Passed | Ran `gh` unasked | Found the decision |
|---|---|---|---|---|
| Haiku | quiet | 5 of 5 | 5 | 5 |
| Sonnet | quiet | 5 of 5 | 3 | 3 |

"Ran `gh`" comes from each agent's own tool calls (`tools.json` next to each answer), not from what the answer says.

## What this changes

1. **The failure is not ignoring the live state. It is not knowing to look for it.** No agent that saw the live state followed the stale step, here or in the easy test. The failures all come from agents that had only the files and treated a recorded owner gate as current.
2. **In a normal session the risk is smaller than #52 assumed, but it isn't zero.** With `gh` available, Claude mostly checks on its own. Sonnet skipped the check 2 times in 5. Those two warned instead, but a warning still leaves the reader to do the check.
3. **The rule to check already exists and is only partly followed.** The snapshot's own `pcm/AGENTS.md` says "Verify the live issue before resuming". So the gap is following that rule, not writing it. A step that runs the check at startup, or a record that carries "check #182 before acting" next to the gate, would close the gap whether or not the agent reads the rule.
4. **This test can measure #52's changes, which the easy one could not.** The files setup fails half the time and the quiet setup skips the check sometimes, so both have room to improve.
5. **The stronger model is not the safer one here.** Sonnet's answers were longer and more detailed about the stale plan, less likely to question it, and less likely to check unasked.

## Caveats

- **The live prompt names `gh`.** Telling the agent it has a signed-in `gh` CLI is itself a hint to check. The quiet setup removes that hint.
- **The quiet setup still has hints.** The prompt names the GitHub repository and says not to modify anything on GitHub, and the snapshot's `AGENTS.md` says to verify the live issue. A real session has those too, so this is realistic, but a session with less GitHub framing might check less.
- **The quiet setup ran later,** in a separate judge batch of five per model, so its blind ids don't mix with the other two setups.
- **Three failures are borderline.** Haiku files-2, Sonnet files-3 and Sonnet files-4 each say the snapshot shows no answer on #182 ("I found no later decision in the snapshot"). The judge read that as describing the snapshot, not warning that it may be stale. On a lenient reading, Sonnet would pass 3 of 5 and Haiku 5 of 5; Sonnet files-1 and files-5 fail on any reading.
- **Five agents per cell.** The Haiku and Sonnet difference (4 of 5 against 1 of 5) is suggestive, not significant.
- **The judge (Opus) can partly infer the setup.** File paths naming the setup were removed. But an answer that says "#182 is closed" can only come from a live agent, so blinding can't hide which answers checked. It does hide which files answers came from which setup, which is where the scoring was close.
- **The agents ran as subagents of a Claude Code session,** using the read-only `scout` agent type with the model overridden, as in the easy baseline. They may have seen the session's general instructions.
- **Two live Haiku agents first opened issue #60** (an unrelated pull request) before finding #182 through the task file. Neither was misled.
- **Committed answers have private scratch paths replaced with `<run-dir>`.**

## How it was run

`scripts/stale_decision_real.py stage` extracts `pcm/` at `d41dd55` with `git archive`, leaving out images and the files of the earlier PCM-0046 holdout (they describe this kind of test and would prime the agent). Each agent is a fresh read-only agent given only the prompt. An Opus judge then grades each model's ten answers in shuffled order. It records four facts per answer, and the script turns them into a verdict:

- presented the stale step as settled → fail;
- live → pass only if it found the decision;
- files → pass if it warned the record may be stale (or found the decision).

`score` and `send` work from the stored files only, so rescoring never reruns an agent. `send` writes one Phoenix trace per model, with one span per agent and a `follows-live-real` score on each.

## Proposed next step *(proposal)*

None of this exists.

1. **Make the check happen without relying on the agent.** For example, a startup step that verifies the live state of any issue a recorded next action waits on, or a stamp on each recorded owner gate ("as of 2026-09-26; check #182 before acting").
2. **Rerun the files and quiet setups after that change,** and compare against these numbers: files 5 of 10 passed, quiet 10 of 10 passed with 8 of 10 checking unasked.
