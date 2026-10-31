# Agent Stack — Project Contract

## Main goal

Governed autonomous coding. AI agents work on a repository on their own, and the stack keeps that work inside rules they cannot skip:

- **PCM** sends every change through a pull request with required checks, and leaves a record the next session can start from.
- **CGM** sets how anything a person reads gets written.
- **OIO** gives problems one issue-log shape, and closes an issue when the pull request that fixes it merges.
- **ACS** installs all of it into a project, and lets several agents share one repository without colliding.

This repository holds the four together and ships them as one version, so a change to one component never again needs a pin bump in three others.

## Why

PCM, CGM, ACS and OIO always had to move together, but each lived in its own repository and pinned the other three. Between 2026-09-30 and 2026-10-30, 73 of the 130 pull requests merged in those repositories only moved versions, and the certified train could still not be installed because ACS pinned older PCM and CGM commits than the train certified (#20). One repository cannot have that mismatch.

The release train came first: versions got their own repository so that no component certified its own siblings. That rule still holds inside one repository. The version record lives at the root, and no component folder restates another's version.

## Scope

- `pcm/`, `cgm/`, `acs/`, `oio/`: the four components, each with its own history, tasks and tests.
- `stack-releases.json`: the certified version record adopters read. It certifies the whole stack as `agent-stack-train`, and still lists each component for adopters installed before the move.
- `stack-manifest.schema.json` and `scripts/check_manifest.py`: the shape of an adopter's pins and the check that proves they agree with the train.
- `.github/workflows/ci.yml`: one required `gates` check over every component.

## Non-goals

- **Does not own any adopter's product code, issues, or releases.**
- **Does not change what each component does.** The move changes where code lives, not how it behaves.
- **Does not delete history.** The old repositories are archived after the first combined release, never deleted; adopters' pinned commits exist only there.

## Definition of success

- One pull request can change any component, and one `gates` check proves the whole stack still works.
- An adopter installs one commit of this repository instead of four.
- A version appears in one place, and every document points at it rather than restating it.
