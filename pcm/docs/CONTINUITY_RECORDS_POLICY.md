# Human-first, auditable continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.0.0","protocol_version":"0.1.0-draft"} -->

PCM records exist so another person or agent can understand what happened and continue accurately without the original conversation. A record must be readable as a human explanation and traceable to the evidence behind its claims.

## What PCM owns

PCM defines and distributes the structure and evidence rules for continuity-specific records:

- issue intake and progress updates used to coordinate continuity work;
- project, current-state, task, checkpoint, handoff, and context-pack records;
- pull-request descriptions that deliver or change continuity behavior;
- compact machine-readable identifiers and provenance needed to connect those records.

PCM defines how those records explain a person's problem and a verifiable outcome. It does not define unrelated product documentation, marketing language, visual design, or every project's domain-specific writing contract. Preserve the target project's existing ownership and conventions.

## A layered record

Give a new reader enough context to understand and verify the work, without putting the entire history in every place.

1. **Human explanation:** the problem and consequence, who or what is affected, the desired observable outcome, and what is still unknown.
2. **Boundaries and status:** scope, non-goals, dependencies, what is shipped versus planned, and one next action.
3. **Evidence and provenance:** direct source links, relevant repository revision, issue/task/PR identifiers, commands and results, and linked CI or artifacts.
4. **Reproduction detail when needed:** the smallest exact setup another person needs to check a research result, failure, migration, or agent-facing claim.

The human explanation can be detailed when the decision is consequential or unfamiliar. Keep the opening skimmable; place lengthy logs, transcripts, diffs, and rubrics in linked or expandable sections. Do not repeat full issue or task contents in every progress update or PR.

## Use by record type

### New issue

Describe the real-world or project consequence first. State the intended result in terms someone can observe, then scope/non-goals and proportionate acceptance checks. Link the canonical task when one is activated. Add sources and reproduction details only when they support a claim or are needed to repeat the reported behavior.

### Issue progress update

Record what changed for the person or project, the evidence that supports the update, what remains open or uncertain, and the next action. Link the PR, commit, CI run, or source; do not paste their full contents or restate the issue.

### Pull request

Keep the visible summary easy to scan: human outcome, change and scope, verification result, and related task/issue. Put detailed reproduction, logs, and provenance behind a short expandable section or direct artifact links. Include the CI result and merge/closeout status when known. Do not claim a PR is merged until the remote confirms it.

### Project-continuity documents

Use ordinary language to explain purpose, current state, task, decisions, evidence, blockers, and next action. Keep structured identifiers in the existing metadata markers or manifests. Prefer one authoritative record; if a human view and machine record are separate, generate one from the other or validate their shared IDs, versions, links, and status. A context pack remains a derived view, not a new authority.

## Evidence, citations, and reproducibility

- Link external factual claims directly to a relevant, authoritative source. Include its version or publication/access date when the source can change. A citation should substantiate the nearby claim, not merely point to a homepage.
- Link repository claims to a stable commit, file revision, issue, PR, or CI run. A file path without a revision may drift.
- For commands and tests, record the command and the observed result; link full logs when they are long.
- For experiments and research, include the starting code/data/source revision, material inputs and configuration, runtime or model when relevant, exact command or prompt, observed result, and limitations.
- For an agent-behavior claim, preserve the prompt/rubric version and allowed context when needed to reproduce the result. Keep a blind evaluator's answer key away from the participant, but preserve it for maintainers.
- Label inference, uncertainty, and agent-reported claims. A well-written record or valid metadata does not prove a claim is true.
- Reproduce only what the claim depends on. Do not require experiment fields for ordinary documentation or routine code changes.

## Machine-readable layer

Use stable task IDs, issue numbers/URLs, PR numbers/URLs, commit IDs, protocol/policy versions, and source revisions. Keep these identifiers compact and consistent across the issue, task/checkpoint, PR, and CI evidence. Do not create a second prose copy of the full project state.

Structural checks can validate required sections, identifiers, versions, and local references. A live tracker check requires a separately implemented integration. Neither a schema nor a link checker can judge whether a human explanation is accurate; review and source evidence remain necessary.

## Proportionality and enforcement

- Make a record as detailed as the reader needs to make a correct decision, not as detailed as the system can possibly collect.
- No mandatory PDD/SDD/TDD bundle, citation quota, issue per test type, or extra approval gate.
- Missing evidence is marked unknown. It blocks only a claim or merge that depends on it, not unrelated safe work.
- Generated PCM instructions and optional GitHub templates carry this contract to future adopters. Template installation must be opt-in where it may conflict with a project's existing conventions and must never overwrite different content silently.
- CI checks the mechanical contract and policy propagation. It does not replace the human-visible outcome or claim semantic truth.
- PCM must not claim automatic chat capture or issue synchronization until that behavior exists and has been tested.

## Short update pattern

Use this when a comment or checkpoint needs a compact progress update:

    Human outcome / change:
    Evidence and provenance:
    Still open or unknown:
    Next action:

Leave a field out when it truly does not apply; do not fill space with “N/A” blocks.
