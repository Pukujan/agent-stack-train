# Incident report — checkpoint push with a timed-out parent post (run CI-4417)

Seeded fixture recorded 2026-09-25. Write your report of what happened and how
it was resolved, exactly as the project's issue-log-format guidance requires.
Nothing else is provided alongside this file.

Project payment-ledger-service, actor `ci-runner-7`, operator timezone
UTC-04:00 (EDT). The tool performs a checkpoint push of commit 8f31c2d: it
posts a receipt comment to leaf issue #121 and a matching receipt comment to
parent issue #118, then records both comment ids in the local ledger.

Timeline, in order:

- 2026-09-24 14:02:58Z (10:02:58-04:00): preflight passes, 212 files staged,
  0 local drift.
- 14:03:11Z: the leaf post succeeds, HTTP 201, comment 3312000123 on #121,
  body 4,812 bytes.
- 14:03:41Z: the parent post, attempt 1 of 3, aborts after the 30-second cap
  with `gh` exit code 1 and no response body. Whether the comment reached
  the server is unknown.
- 14:04:52Z: the pre-send lookup for attempt 2 lists all comments on #118 and
  finds no comment carrying the run marker for CI-4417.
- 14:05:07Z: the lookup did surface comment 3312000187 on #118, hidden from
  the web UI, whose body mentions payment-ledger-service but not CI-4417.
  Nobody can tell whether it is the timed-out post arriving late. That is
  the fork of the record: branch A retries automatically and risks a second
  parent receipt; branch B resolves manually against the marker payloads.
  The operator took branch B. One reading says the hidden comment is that
  late duplicate and a retry would ship a second copy. The counter-signal:
  the hidden comment's marker payload carries time 14:03:09.2Z, which is
  31.8 seconds before the attempt-1 request left the runner at 14:03:41Z,
  so that comment predates the timed-out request and belongs to the aborted
  run CI-4402 at 14:02:40Z, not to this push.
- 14:06:33Z: the ledger keeps 3312000123 as the leaf receipt and records
  3312000187 as residue of run CI-4402; the operator posts the parent
  receipt manually at 14:07:12Z, HTTP 201, comment 3312000456.

Numbers on the record: leaf body 4,812 bytes; hidden-comment marker payload
214 bytes; attempt-1 timeout cap 30 seconds; marker time gap 31.8 seconds;
attempts used 1 of 3; duplicate posts 0; run CI-4417 closes as recovered.
