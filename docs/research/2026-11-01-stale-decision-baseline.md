# Stale-decision baseline: Claude follows the closed issue, and PCM's scorer can't tell

As of 2026-11-01. Issue: #64 (parent #52). Data: [`2026-11-01-stale-decision-baseline/`](2026-11-01-stale-decision-baseline/). Traces: the stack's Phoenix project (`acs-train-development`), traces `85975f4c…` (Haiku) and `a34c32a4…` (Sonnet).

## Question

In PCM's T2 holdout (September 2026), every one of five agents was given a status file saying issue #53 was open, with a next action, plus the live issue, which was closed. All five reported that the issue was closed and still recommended the stale next action. #52 cites this as the reason the stack needs a decision register. Before changing anything, this run asks: **do the Claude models the stack runs on today make the same mistake, and does PCM's current guidance change the answer?**

## Result

**No Claude agent recommended the stale action: 20 of 20 passed on meaning.** Every answer said the status file was out of date, said #53 was closed, and told the reader to check the live issue before running the acceptance step. That held for both models and both setups (5 arms each).

| Model | Setup | Passed on meaning | Recommended the stale action | Passed PCM's word scorer |
|---|---|---|---|---|
| Haiku | no guidance | 5 of 5 | 0 | 0 of 5 |
| Haiku | PCM guidance | 5 of 5 | 0 | 0 of 5 |
| Sonnet | no guidance | 5 of 5 | 0 | 3 of 5 |
| Sonnet | PCM guidance | 5 of 5 | 0 | 3 of 5 |

**PCM's scorer failed 14 of these 20 correct answers.** Its "follows the live issue" check fails any answer that contains the stale action's text, even when the answer quotes it in order to say not to do it ("CURRENT.md says … 'Execute the hosted two-user acceptance on the parent issue.' … it should not be run from this snapshot"). All 14 failures are that one check. So the scorer can't separate quoting a stale step from recommending it.

**The guidance made no measurable difference, because there was no failure left to fix.** Guided answers cited the rule that GitHub owns status. Unguided answers reached the same conclusion without it.

## What this changes

1. **The September result doesn't carry over to Claude.** Those arms ran on small non-Claude models (`yolo-auto/yolo-small`, per that run's `meta.json`), not on the models the stack's sessions use now.
2. **This test can no longer measure #52's changes.** Every arm already passes, so a decision register or startup step can't show an improvement on it. A useful baseline needs a harder version of the test.
3. **PCM's T2 scorer needs a meaning check before it's reused.** As it stands, it would report a failure for answers that are right.

## Caveats

- **The test is easy.** The contradiction is two short lines, and the prompt hands the agent the live issue. The failure seen in the #52 Octo experiment was different: search returned a stale acceptance line first, from a large file, with no live issue next to it. This run says nothing about that case.
- **Five arms per cell.** 0 of 20 failures is strong for this easy test, but it can't rule out a low failure rate.
- **The arms ran as subagents of a Claude Code session,** using the read-only `scout` agent type with the model overridden. They may have seen the session's general instructions. The originals also ran as read-only subagents, in a different harness.
- **The judge (Opus) was blinded to setup and model.** File paths that named the setup were removed from the answers it saw. But a guided answer that mentions "the guidance" in its own words still reveals its setup; four Sonnet and three Haiku answers do. Every answer passed, so this can't have helped one setup over the other.
- **Committed answers have private scratch paths replaced with `<run-dir>`.** The scores don't depend on paths.

## How it was run

`scripts/stale_decision.py` stages the original T2 bundle from `pcm/tests/fixtures/pcm0046_traversal/`, unchanged. The "PCM guidance" setup adds the GitHub-progression block from `pcm/AGENTS.md` as `GUIDANCE.md`. The prompt is the original T2 prompt; the guided setup adds "Read GUIDANCE.md and follow it." in front, the way the original's T1 arms did. Each arm is a fresh read-only agent. A separate Opus judge grades each model's ten answers in a shuffled order. The script scores both checks from the stored files, then sends one Phoenix trace per model: one span per arm, with the `t2-lexical` and `follows-live` scores attached. Rescoring never reruns an arm.

## Proposed next step *(proposal)*

None of this exists. Build a harder version of the test that matches the failure actually seen. The agent would get a full-size CURRENT.md with the superseded decision buried in it, and would have to find the live state itself, through `gh` or an Octo search, instead of being handed it. Run that before and after #52's decision register, and score it on meaning.
