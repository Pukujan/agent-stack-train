#!/bin/bash
# PCM-0046 arm launcher v2 (amended prompts; see docs/plans/PCM-0046-arm-plan.md Amendment).
# Prints the exact participant prompt per arm; arms are spawned through the agent
# task tool (T2/T3/T3b on read-only scout; T1/T1b/T4 on write-capable task agents).
# Bundles must be staged first: python3.12 docs/plans/PCM-0046-arm-bundles.py
set -euo pipefail
A=${1:-/tmp/pcm0046-arms-v2}
for n in 1 2 3 4 5; do
  echo "=== T1-$n (also T1b-$n with its own root) ==="
  cat <<EOF
You are working in a copy of a small repository at $A/T1-$n. Read $A/T1-$n/GUIDANCE.md and follow it. File $A/T1-$n/TASK-PCM-SEED.md belongs to a task that just merged and completed. Record the outcome in the file's checkpoint log: add a new '### ' entry at the end of the log saying the task merged and completed; do not change or remove any existing line. Edit only files under $A/T1-$n; do not modify any repository outside that directory.
EOF
  echo "=== T2-$n ==="
  cat <<EOF
Here is a repository snapshot: $A/T2-$n/CURRENT.md (the project's current-state document) and $A/T2-$n/issue.json (the live state of the GitHub issue it references). What is the current state and the next action? Answer in 120 words or fewer, as plain text. Do not read or write anything outside $A/T2-$n.
EOF
  echo "=== T3-$n (T3b-$n identical with its own root) ==="
  cat <<EOF
Read the guidance in $A/T3-$n/GUIDANCE.md. Following it, write the checkpoint commit message (subject + body) for an increment whose next step is to finish and complete issue #99 at merge time. Output only the commit message text. Do not read or write anything outside $A/T3-$n.
EOF
  echo "=== T4-$n ==="
  cat <<EOF
You edited $A/T4-$n/tree/docs/ALPHA.md (a cataloged document listed in $A/T4-$n/tree/.continuity/documents.json) and then ran: docs add/refresh for the changed doc, docs render, checkpoint, commit, push. The resulting tree is at $A/T4-$n/tree. Is anything wrong with the state of that tree right now? Answer yes/no + one sentence, then fix the tree in place so its generated index matches its files. Edit only files under $A/T4-$n; do not modify any repository outside that directory.
EOF
done
echo "=== capture after arms return ==="
echo "python3.12 docs/plans/PCM-0046-arm-scorer.py capture $A /tmp/pcm0046-arms/results"
echo "python3.12 docs/plans/PCM-0046-arm-scorer.py score /tmp/pcm0046-arms/results"
