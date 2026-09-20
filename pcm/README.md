# Project Continuity Modules

A reusable, versioned protocol and bootstrap toolkit for making repositories resumable by fresh AI or human sessions without depending on prior chat history.

## Start here

If you are a new agent/session, read in this order:

1. `PROJECT.md`
2. `AGENTS.md`
3. `checkpoints/CURRENT.md`
4. the active task linked from CURRENT
5. the minimum relevant design/spec document

Do not reconstruct project state from old conversations unless the active task explicitly requires historical evidence.

## Main idea

A continuity-enabled project separates:

- stable project intent — why the project exists;
- current program state — where the project is now;
- bounded task state — what one agent/session should do;
- append-only checkpoints — what actually happened and what evidence exists;
- coordination mirrors — GitHub Issues/Beads/PRs;
- generated context packs — disposable summaries derived from canonical repository state.

The repository is the durable state. Chat sessions are execution environments.

## Target user experience

Eventually, another repository should be able to run something like:

```bash
continuity init --profile software
continuity validate
continuity task new
continuity checkpoint
continuity pack TASK-0001
```

and become continuity-compliant without hand-authoring the protocol.

## Current status

The protocol is in bootstrap/design phase. The active task is `PCM-0001`: define v1 schemas/templates/validator/bootstrap behavior and dogfood the protocol on this repository itself.

See `checkpoints/CURRENT.md`.
