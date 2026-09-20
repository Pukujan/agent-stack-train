# Minimal v1 dogfood

PCM-0002 exercised the v1 core lifecycle against a freshly initialized minimal repository using the exact PCM-0001 source merged to `main`.

Verified sequence:

```bash
PYTHONPATH=src python -S -m continuity init --root <target> --profile minimal --name "PCM Minimal Dogfood" --task-prefix DOG
PYTHONPATH=src python -S -m continuity validate --root <target>
PYTHONPATH=src python -S -m continuity task new --root <target> --slug first-dogfood-task --goal "Exercise the initialized minimal repository." --why "Verify task creation composes with initialization." --owner dogfood-agent --priority P0
PYTHONPATH=src python -S -m continuity validate --root <target>
PYTHONPATH=src python -S -m continuity checkpoint DOG-0001 --root <target> --agent dogfood-agent --time 2026-09-20T18:35:00Z --completed "Initialized and validated the minimal repository." --evidence "init and validate returned success." --decision "Keep the minimal profile dependency-free." --changed "tasks/TASK-DOG-0001-first-dogfood-task.md" --next "Generate and validate a provenance-bearing context pack."
git -C <target> init -q -b main
git -C <target> add .
git -C <target> commit -m "dogfood: canonical source state"
PYTHONPATH=src python -S -m continuity pack DOG-0001 --root <target>
PYTHONPATH=src python -S -m continuity validate --root <target>
```

Observed results:

- initialization created the expected config, canonical Markdown, and six v1 schemas;
- validation returned `VALID` after init, task creation, checkpoint append, and pack generation;
- task creation allocated `DOG-0001`;
- checkpointing preserved the pre-existing task history and added one checkpoint marker;
- the context pack recorded the target repository, current Git ref, exact commit, protocol version, `DOG-0001`, and its three canonical sources;
- no core CLI/schema/template defect was observed.

The durable regression for this sequence is `ContinuityTests.test_minimal_end_to_end_dogfood_flow`.
