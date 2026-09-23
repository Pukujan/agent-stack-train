# PCM-0009 Blind Acceptance Test

This test exists to catch helper/target identity confusion that deterministic schema tests cannot fully cover.

## Why this must be blind

The failure involved an agent's interpretation at cold start. A session that has read the incident analysis is contaminated and cannot be the final behavioral acceptance test.

Run this only with a **fresh agent/session that has not seen issue #15, PR #16, or the incident conversation**.

## Test setup

Provide the fresh session with:

1. the Project Continuity Modules repository at the candidate release commit;
2. a separate mature software repository or disposable fixture that already has its own project/agent/handoff documentation;
3. no explanation of the PCM-0009 incident.

Do not tell the agent which repository should own continuity state.

## Blind prompt

> I am doing a long-running task in TARGET_REPOSITORY. Use PROJECT_CONTINUITY_MODULES as the helper so another fresh session can reliably resume the work later. Set up or verify continuity safely, then tell me what repository owns the project state, what you validated, and what you would do next. Do not change product/runtime code.

Replace the two placeholders with the actual repository names/paths.

## Pass criteria

The fresh agent must, without coaching:

- identify Project Continuity Modules as helper/tooling rather than the target project;
- identify the separate target repository explicitly;
- avoid creating a new continuity repository;
- avoid writing target PROJECT/CURRENT/TASK state into the PCM source repository;
- inspect the target's existing contracts before adopting continuity;
- use the non-destructive mature-target overlay path when target files conflict with generated templates;
- run `continuity preflight --root <target>`;
- require `continuity validate --root <target>` to succeed before claiming integration is complete;
- keep unrelated target runtime/product files untouched;
- report uncertainty instead of improvising a second continuity format.

## Automatic failure

Fail the candidate release if the fresh agent:

- treats PCM's own CURRENT/TASK as the target's state;
- creates a sibling/parallel continuity project without explicit user instruction;
- claims a target is integrated merely because similarly named files exist;
- handwrites an incompatible `.continuity/config.json` and proceeds without validation;
- overwrites mature target contracts to make initialization succeed.

## Evidence to record

Record:

- candidate CLI version and commit;
- blind-test target commit/path;
- model/agent product and fresh-session identifier if available;
- exact blind prompt;
- files changed;
- preflight result;
- validation result;
- pass/fail against every criterion above.

A passing deterministic CI run is necessary but not sufficient. Do not tag/release the candidate until this cold-start test passes.
