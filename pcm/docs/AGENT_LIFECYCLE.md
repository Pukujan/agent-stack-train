# Delegated Agent Lifecycle

Delegated agents are temporary execution workers. They are not project identities,
canonical task state, or durable handoff records.

## Required lifecycle

When delegation is useful, the parent session must:

1. give the worker one bounded task, an owner, and an expected result;
2. capture the worker's result, evidence, changed paths, and uncertainty in the
   parent task/checkpoint;
3. close the worker immediately after its result is captured;
4. stop and close a worker early when its work is no longer needed.

The close step is mandatory even when the worker reports `completed`. A completed
worker can remain open and continue consuming an available agent slot until the
runtime explicitly closes it.

Failure, interruption, cancellation, and timeout follow the same rule: preserve
the observed status in the parent task, then close the worker. If a worker needs a
follow-up, reuse it before closing it; do not leave it open for possible future use.

## Concurrency policy

Use the smallest number of workers that materially shortens the task. Prefer one
worker for a small or sequential task, and use bounded parallel workers only for
independent work. The parent session owns coordination and must never rely on an
unbounded pool of background workers.

Do not treat an open agent thread as evidence, canonical state, or a required part
of the finished task. The repository task, pushed branch, CI result, and merge
state are the durable record.

## End condition

A delegated-worker task is not operationally complete until the parent has both:

- recorded the result durably; and
- closed the delegated worker.

