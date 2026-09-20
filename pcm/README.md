# Project Continuity Modules

A reusable, versioned protocol and bootstrap toolkit for making repositories resumable by fresh AI or human sessions without depending on prior chat history.

## Point a new agent here

Give a fresh session only the repository and point it to `HANDOFF.md`. That file names the bounded active task and exact cold-start read order. Canonical state is repository state; prior chat history is not required.

## v1 bootstrap CLI

Python 3.11+ is the only runtime requirement. From a source checkout:

```bash
python -m pip install -e .
continuity init --profile software --name "My Project" --task-prefix APP
continuity validate
continuity task new --slug first-task --goal "..." --why "..."
continuity checkpoint APP-0001 --agent "..." --completed "..." --evidence "..." --next "..."
continuity pack APP-0001
```

`init` is non-destructive: it writes continuity-managed files only when absent or already byte-identical, and refuses the entire initialization before writing if a planned path contains different user content.

## v1 layout

- `.continuity/config.json` — protocol/profile/task-prefix declaration.
- `schemas/v1/*.schema.json` — JSON Schema draft 2020-12 contracts for config, project, current, task, checkpoint, and context-pack metadata.
- `templates/v1/minimal` — minimal profile templates.
- `templates/v1/software` — software-profile overlay templates.
- `PROJECT.md` — stable project contract.
- `checkpoints/CURRENT.md` — repository-wide current state.
- `tasks/TASK-*.md` — bounded work plus append-only checkpoint history.
- `.continuity/packs/*.md` — generated, disposable context packs.

Canonical Markdown carries a single-line `<!-- continuity:<kind> {...} -->` JSON metadata marker. The Markdown remains human-readable; the marker makes required fields deterministic to validate.

## Development validation

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m continuity validate --root .
```

The validator checks the declared protocol metadata, canonical file presence, active-task references/status, task dependencies, checkpoint structure, and context-pack provenance metadata. GitHub/Beads adapters remain outside the PCM-0001 core.
