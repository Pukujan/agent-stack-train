#!/bin/bash
# PCM-0046 arm launcher v3 (amendments 11 supersedes prompt details of 1 and 10).
# Prints the exact participant prompt per arm; arms are spawned through the agent
# task tool. Bundles must be staged first:
#   python3.12 docs/plans/PCM-0046-arm-bundles.py
# Prompts state the SITUATION only; append-vs-rewrite and keyword-vs-Refs are
# decided by each arm's GUIDANCE.md — that is the variable under test.
set -euo pipefail
A=${1:-/tmp/pcm0046-arms-v2}
for n in 1 2 3 4 5; do
  for pfx in T1 T1b; do
    echo "=== $pfx-$n ==="
    cat <<EOF
You are working in a copy of a small repository at $A/$pfx-$n. Read $A/$pfx-$n/GUIDANCE.md and follow it. File $A/$pfx-$n/TASK-PCM-SEED.md belongs to a task that just merged and completed. Record the merge outcome in the file's checkpoint log. Edit only files under $A/$pfx-$n; do not modify any repository outside that directory.
EOF
  done
  echo "=== T2-$n ==="
  cat <<EOF
Here is a repository snapshot: $A/T2-$n/CURRENT.md (the project's current-state document) and $A/T2-$n/issue.json (the live state of the GitHub issue it references). What is the current state and the next action? Answer in 120 words or fewer, as plain text. Do not read or write anything outside $A/T2-$n.
EOF
  for pfx in T3 T3b; do
    echo "=== $pfx-$n ==="
    cat <<EOF
Read the guidance in $A/$pfx-$n/GUIDANCE.md. Following it, write the checkpoint commit message (subject + body) for an increment whose next step is to post the closeout receipt on issue #99. Output only the commit message text. Do not read or write anything outside $A/$pfx-$n.
EOF
  done
  echo "=== T4-$n ==="
  cat <<EOF
You edited $A/T4-$n/tree/docs/ALPHA.md (a cataloged document listed in $A/T4-$n/tree/.continuity/documents.json) and then ran: docs add/refresh for the changed doc, docs render, checkpoint, commit, push. The resulting tree is at $A/T4-$n/tree. Is anything wrong with the state of that tree right now? Answer yes/no + one sentence, then fix the tree in place so its generated index matches its files. Edit only files under $A/T4-$n; do not modify any repository outside that directory.
EOF
done
echo "=== capture after arms return ==="
echo "python3.12 docs/plans/PCM-0046-arm-scorer.py capture $A /tmp/pcm0046-arms/results"
echo "python3.12 docs/plans/PCM-0046-arm-scorer.py score /tmp/pcm0046-arms/results"
