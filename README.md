# Agent Stack

> **One repository for the agent stack.** Continuity, narrative, the install surface, and the issue log ship together, so they live together and move as one version.

The stack is four components that have always had to move together. Each used to live in its own repository and pin the other three, and most pull requests only moved those pins. The components now sit side by side in this repository, with their history. The plan of record is [#21](https://github.com/Pukujan/agent-stack-train/issues/21).

## What is here

| Folder | Component | Owns |
| --- | --- | --- |
| [`pcm/`](pcm/) | Project Continuity Modules | Execution continuity: tasks, checkpoints, push receipts, required PR gates, and the `continuity` CLI. |
| [`cgm/`](cgm/) | Content Generation Modules | Narrative and style: writing routing, human-sounding writing, output naming, visual direction, image generation. |
| [`acs/`](acs/) | Agent Custom Setup | The install surface: the hot-loader that wires PCM, CGM and OIO into a project, plus the coordination runtime. |
| [`oio/`](oio/) | Observational Issue Ops | The issue log: the issue form, the filer stamp, triage, and the close workflows adopters call. |
| root | Release train | [`stack-releases.json`](stack-releases.json), the certified version record adopters read today, and the checks in [`scripts/`](scripts/). |

Each folder keeps its own README, AGENTS.md, tasks and tests. Read the folder's own files before you change it.

## Where the move stands

1. **Freeze.** Done. The open pull requests in the four old repositories were merged or closed, and the mesh and train refresh workflows were turned off.
2. **Combine.** This repository now holds all four components with their history. One `gates` check runs every component's tests.
3. **Switch install.** Done. ACS's installer takes one checkout of this repository and installs PCM, CGM and OIO from its folders, all at that checkout's commit. OIO's reusable close workflows live in this repository's root [`.github/workflows/`](.github/workflows/), and the callers OIO installs name `Pukujan/agent-stack-train`.
4. **Release.** Not done. The first stack version will be 1.0.0. Tagging it adds an `agent-stack-train` entry to the train, which manifests from the new install pin. The old repositories are archived after it ships, never deleted.
5. **Move adopters.** Not done. Old pins keep working until each adopter moves.

Until step 4 records the `agent-stack-train` entry, a manifest written by the new installer fails `check-adopter`, so no adopter moves before then.

## Run the checks

[`ci.yml`](.github/workflows/ci.yml) runs these on every pull request and push to `main`. Each component's checks run from inside its folder.

```bash
(cd pcm && pip install -e ".[dev]" && PYTHONPATH=src python -m unittest discover -s tests)
(cd cgm && python scripts/validate_content_system.py --root . && python -m unittest discover -s tests)
(cd acs && python -m pytest modules/coordination/multi-agent-hotload/v0.1.0/tests -q)
(cd oio && pip install -r requirements.txt && python -m unittest discover -s tests)
python scripts/check_manifest.py --self
```

## The release train

Adopters still pin the stack through the train, as before the move.

| Document | Lives in | Owns |
| --- | --- | --- |
| [`stack-releases.json`](stack-releases.json) | **this repository** | The certified versions: one entry per component, with version, commit, and role. |
| `stack-manifest.json` | **each adopter** | That adopter's pins: which train it follows, and either `agent-stack-train` alone (installed from one checkout of this repository) or one pin per component (installed before the move). |

The adopter manifest shape is [`stack-manifest.schema.json`](stack-manifest.schema.json). Versions are not copied into this README; [`stack-releases.json`](stack-releases.json) is the one answer. The train was last refreshed from the old repositories' default branches when they were frozen, and its refresh workflow is now off.

To check an adopter's pins in CI:

```bash
python scripts/check_manifest.py --manifest stack-manifest.json \
  --train-url https://raw.githubusercontent.com/Pukujan/agent-stack-train/main/stack-releases.json
```

The check fails closed: a missing component, a version or commit that disagrees with the train, a manifest that pins a component the train does not certify, or an `agent-stack-train` pin next to component pins all exit non-zero.

**A stack document may not restate a current component version or commit.** It points at `stack-releases.json` instead. `scripts/check_prose_pins.py` fails this README, `AGENTS.md` or `PROJECT.md` when one states a pin the certified set does not name.

## License

Everything in this repository is licensed under the Functional Source License, Version 1.1, ALv2 Future License (FSL-1.1-ALv2). Each version becomes available under the Apache License, Version 2.0 two years after it is published. FSL is source-available, not OSI open source. Commits published under the Apache License, Version 2.0 before the move stay available under it. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
