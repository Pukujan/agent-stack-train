---
name: content-context
description: Build an evidence-bounded project brief from a repository so generated README, marketing, UX, visual, and HTML content describes what the project actually does.
---

# Content context

Use this module whenever the agent is entering a new repository or the product story has changed.

## Workflow

1. Read the repository's project contract and current checkpoint.
2. Identify the real user, job, problem, solution, mechanism, proof, and limitations.
3. Record exact file paths for evidence.
4. Mark each claim as shipped, experimentally supported, planned, or unknown.
5. For each material claim, record what its evidence supports, what it does not establish, an exact source revision/locator or direct external citation, and timezone-aware `recorded_at` time.
6. For claims that apply only during a known period, add `valid_time` bounds and keep them separate from source event dates and record time.
7. Record technical terms that need plain-language translation.
8. Store the result in `project-brief.json` using the schema version pinned by the target adapter. For helper `0.4.x`, use project-brief v2.

## Output rule

The project brief is a source map, not marketing copy. It should be useful to a fresh agent and easy for a human maintainer to correct. Never let a citation upgrade an inference into an observed fact.
