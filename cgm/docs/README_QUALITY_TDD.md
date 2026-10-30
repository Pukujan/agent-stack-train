# Test design: readable, traceable, repeatable output

Status: acceptance plan for Content Generation Modules `0.4.0`.

## Product acceptance tasks

Give a fresh reader the README without the issue or conversation. Ask them to:

1. Explain who the project helps, what situation brings that person there, and what becomes difficult.
2. State what the project offers and describe the mechanism without repeating internal module names.
3. Distinguish shipped behavior from experimental, planned, and unknown work.
4. Find one piece of evidence for a material claim and explain its limitation.
5. Find the smallest useful next action; developers should also find the reproduce/build path.

Record task success, incorrect or missing answers, source-resolution success, and time where practical. Do not treat word count or a model-generated style score as a substitute for comprehension.

## Deterministic contract tests

- Required story-spine fields are present and specific enough to be reviewed.
- Every material claim has nonempty `claim`, `source`, `status`, `supports`, `limits`, and `source_revision` fields, plus a timezone-aware `recorded_at` timestamp.
- A time-bound claim records its `valid_time` interval separately from when its evidence record was recorded; intervals are ordered and corrections remain append-only in the issue/PR/commit history.
- Repository source revisions include an exact repository, full revision, path, locator, and immutable direct permalink.
- External source revisions include a direct URI and access date; publication date is recorded when available.
- Important public claims have a direct citation near the claim or in an immediately relevant evidence section.
- The source supports the stated status; a plan cannot be presented as shipped, and unknown claims remain explicitly unknown.
- No missing source, vague revision, invalid status, unsupported source type, or self-attestation as sole behavioral proof passes silently.
- `0.3.x` adapters remain valid under their pinned contract; `0.4.x` requires project-brief v2.
- A CGM change PR links an open issue with written acceptance/delivery criteria; CI validates this before it can satisfy branch protection.
- Existing image tests still require the declared narrative raster generation path, exact title/subtitle, prompt record, hash, and review evidence.

Network resolution is an optional verification step. Offline validation checks identity and shape; an online verifier may additionally confirm that a permalink and line locator still resolve.

## Metamorphic tests

Run each transformation on a fixed task packet and compare the generated brief and README against the same semantic rubric:

- **M-01 Source-order invariance:** reorder equivalent source files; reader, story spine, claim status, and visual contract stay materially unchanged.
- **M-02 Irrelevant-context invariance:** add unrelated files or metadata; core claims and story do not change.
- **M-03 Locator relocation:** move a source while preserving its content and identity; supported claim meaning/status stays stable while its citation locator updates.
- **M-04 Evidence removal:** remove the sole source for a claim; the claim is removed, qualified, or marked unknown, never left confidently stated.
- **M-05 Evidence-status change:** change a source from planned to shipped or invalidate it; only dependent claim wording/status changes, with the new citation recorded.
- **M-06 Explanation boundary:** change only what the evidence establishes; `supports` and `limits` change accordingly, and public wording never becomes stronger than the source.
- **M-07 Paraphrase invariance:** paraphrase the user task without changing facts; the story and evidence mapping remain materially equivalent.
- **M-08 Visual independence:** change the target's visual adapter; the visual brief follows the new brand while the evidence-supported story remains stable.
- **M-09 Presentation independence:** remove bold styling or change heading wording; the text still explains the same story and citations remain available.
- **M-10 Temporal correction:** append a correction with a later `recorded_at` and changed `valid_time`; the previous record remains attributable, and current prose follows the active evidence.

Metamorphic equality is semantic, not byte-for-byte. Exact prose is not the oracle.

## Differential evaluation

Compare the pinned `0.3.1` contract and the candidate contract on the same task packet, target evidence, model family where practical, and image role. Keep the visual direction and image requirements constant so the comparison isolates writing and evidence improvements. Blind reviewers to the contract version. Report dimension-level results and disagreement, not only an aggregate score.

## Hidden holdout protocol

The hidden target, expected story/evidence map, failure labels, and scoring key must live outside the candidate agent's readable checkout and prompt. A benchmark designer freezes them before the run. A fresh candidate receives only its permitted target repository/context and the pinned CGM contract; an independent evaluator receives the frozen output and the key afterward. Record CGM commit, model/session identity, prompt, target revision, run ID, output hashes, deterministic results, reader tasks, and human review. Run each fixture at least three clean times before making a repeatability claim.

Reference repositories used to design the contract are training/development evidence, not holdouts. Do not call this acceptance suite a hidden-holdout pass unless a separate sealed target and independent run record exist. If the private fixture is unavailable, report the holdout as `not_run` and use visible contract/metamorphic tests only.

## Release gate

Reject a candidate for any missing or false required citation, unsupported shipped claim, image-generation regression, target-brand substitution, or hidden-test leakage. Require all deterministic tests to pass, reader tasks to improve or remain non-inferior on the preregistered dimensions, and independent review to accept the story and visuals. Human review remains the final decision for tone, honesty, and usefulness.
