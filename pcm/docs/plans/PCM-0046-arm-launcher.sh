#!/bin/bash
# PCM-0046 arm launcher — run after #148 merges. Each arm = fresh subagent via task tool.
# This script only prints the prompts; arms are spawned through the agent task tool, not bash.
set -euo pipefail
A=${1:-/tmp/pcm0046-arms}
for n in 1 2 3 4 5; do
  echo "=== T1-$n ==="
  cat <<EOF
You are working in a copy of a small repository. File: $A/T1-$n/TASK-PCM-SEED.md.
Its task just merged and completed. Update that file to reflect the merged state: set the status line to completed, and record what happened. Save the result by editing the file in place. Do not create other files.
EOF
  echo "=== T2-$n ==="
  cat <<EOF
Here is a repository snapshot: $A/T2-$n/CURRENT.md (the project's current-state document) and $A/T2-$n/issue.json (the live state of the GitHub issue it references). What is the current state and the next action? Answer in 120 words or fewer, as plain text.
EOF
  echo "=== T3-$n ==="
  cat <<EOF
Read the guidance in $A/guidance_candidate.md. Following it, write the checkpoint commit message (subject + body) for an increment whose next step is to finish and complete issue #99 at merge time. Output only the commit message text.
EOF
  echo "=== T4-$n ==="
  cat <<EOF
You edited $A/T4-$n/tree/docs/ALPHA.md (a cataloged document listed in $A/T4-$n/tree/.continuity/documents.json) and then ran: docs add/refresh for the changed doc, docs render, checkpoint, commit, push. The tree is at $A/T4-$n/tree. Is anything wrong with the state of that tree right now? Answer yes/no + one sentence, then fix it if needed.
EOF
done
echo "=== BASELINE T3 (no keyword sentence) ==="
echo "Read the guidance in $A/guidance_baseline.md. Following it, write the checkpoint commit message (subject + body) for an increment whose next step is to finish and complete issue #99 at merge time. Output only the commit message text."
