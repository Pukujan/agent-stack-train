# PCM-0024 large-repository stress profile

This reproducible synthetic profile measures the cost of document lookup,
checkpoint append, and task context-pack generation when a repository has a
large indexed history. It complements deterministic correctness tests; it does
not prove behavior on every repository or machine.

## Reproduce

From the repository root, install the project in editable mode or make `src`
importable, then run:

```powershell
$env:PYTHONPATH = 'src'
python tests/pcm0024_stress_profile.py
```

The defaults create 5,000 indexed Markdown documents, mark 50 relevant to one
task, seed 2,000 checkpoint records, perform 40 lookups, and append 40 measured
checkpoints. The script uses a temporary repository and removes it when the
run ends. Override the fixture with `--documents`, `--task-documents`,
`--checkpoints`, and `--lookup-repetitions`; document and checkpoint counts
must each be at least 1,000. The repetition count is also the number of measured
checkpoint appends.

## Human-usable guardrails

These are provisional single-machine targets for a local developer workflow,
not claims that every repository stays below them:

| Measurement | Target |
| --- | ---: |
| Document lookup p95 | ≤ 250 ms |
| Checkpoint append p95 with 2,000 existing records | ≤ 1,000 ms |
| Context-pack generation | ≤ 10 s |
| Context-pack size | ≤ 5 MiB |
| Python traced peak memory | ≤ 512 MiB |
| Fixture file storage, excluding `.git` and environments | ≤ 20 MiB |

Exceeding a target should prompt profiling and a documented decision; the
numbers are not enforced as timing-sensitive CI assertions.

## Recorded run

Command: `python tests/pcm0024_stress_profile.py` with the defaults above.

Environment: Windows 11 (10.0.26200), Python 3.12.10, AMD64 Family 25 Model
116 Stepping 1 (AuthenticAMD). One local run on 2026-09-24.

| Measurement | Result | Target |
| --- | ---: | ---: |
| Lookup p50 / p95 | 66.537 / 77.637 ms | p95 ≤ 250 ms |
| Checkpoint append p50 / p95 | 435.299 / 461.396 ms | p95 ≤ 1,000 ms |
| Context-pack generation | 6,916.171 ms | ≤ 10 s |
| Context-pack size | 1,905,540 bytes | ≤ 5 MiB |
| Task file after appends | 1,864,408 bytes | informational |
| Fixture file storage, excluding `.git` | 9,532,017 bytes | ≤ 20 MiB |
| Python `tracemalloc` peak | 31,686,050 bytes | ≤ 512 MiB |

The 40 lookup and append measurements are one run; p95 is the nearest-rank
sample percentile. The document bodies and checkpoint histories are generated
synthetically. The memory number covers Python-traced allocations, not Git
child-process memory, filesystem cache, or total machine usage. File storage
excludes Git internals, filesystem metadata, and dependency environments.
Context-pack generation measured 11.5 seconds before batching committed source
reads and avoiding full-tree validation work for unrelated documents; this
profile now records the 6.9-second candidate path.

This establishes a local baseline and guardrail check, not repeatability or
production-scale behavior. Before turning these provisional targets into a
release guarantee, repeat the profile on multiple supported operating systems
and representative repositories, and retain each run's raw JSON output.
