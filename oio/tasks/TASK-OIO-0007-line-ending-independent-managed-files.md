# TASK-OIO-0007 — Line-ending independent managed files

<!-- continuity:task {"acceptance":["Installing OIO writes every managed file with LF line endings and records the digest of those LF bytes, so a Windows (CRLF) install and a Linux (LF) install produce byte-identical files","`--check` passes on a checkout that renders the same content with CRLF, and reports the line-ending difference as a note rather than the 'managed file changed' tamper refusal; a real content edit is still refused","An existing install whose manifest recorded CRLF digests (from an installer that hashed a Windows worktree) migrates to LF through a normal re-install, without deleting the install or hand-editing the manifest","`python -m unittest discover -s tests` passes on Windows and on ubuntu CI, with new regression tests that fail against the pre-fix installer","A `.gitattributes` in the OIO source pins LF checkout so the shipped package bytes are canonical on every platform"],"depends_on":[],"goal":"Make OIO's managed-file integrity contract line-ending independent so a correct install passes its own required `--check` gate on a Linux checkout, whether the installer ran on Windows or Linux.","id":"OIO-0007","issue_url":"https://github.com/Pukujan/observational-issue-ops/issues/41","next_action":"None for this task; the fix is merged at 27b954f. Human verification of a Windows-install to Linux-check round trip remains open on issue #41.","owner":"owner/Pukujan","priority":"P5","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"The installer read package files as raw working-tree bytes and hashed them, so a Windows (CRLF) checkout installed CRLF files with CRLF digests; a later LF checkout (Linux CI) then failed both `--check` and re-install with 'managed file changed since OIO installed it' even though the content was identical. Reported as recurring across adopter repositories (issue #41)."} -->

- Status: completed
- Owner: owner/Pukujan
- Priority: P5
- Depends on: none

## Goal

Make OIO's managed-file integrity contract line-ending independent so a correct install passes its own required `--check` gate on a Linux checkout, whether the installer ran on Windows or Linux.

## Why

The installer (`.github/scripts/oio_installer.py`) read the package source files as raw working-tree bytes and recorded their SHA-256 in `.oio/install-manifest.json`. On a Windows checkout with `core.autocrlf=true` (the OIO source repository has no `.gitattributes`, so this is the default there) the working tree is CRLF while the committed blob is LF. The installer therefore wrote CRLF bytes into the adopter's managed files and recorded CRLF digests, and a later LF checkout — a Linux CI runner, or a renormalized worktree — failed both `--check` and re-install with `managed file changed since OIO installed it`, though the content was byte-identical apart from end-of-line. The same class of bug also made a CRLF re-checkout of `AGENTS.md` look like an edited managed block. Because `--check` is the required CI gate, a correctly installed repository could never pass its own gate, and the failure was indistinguishable from genuine tampering (issue #41).

## Allowed files

- `.github/scripts/oio_installer.py` — LF normalization at write time and EOL-insensitive integrity comparison.
- `tests/test_oio.py` — regression coverage for the canonical bytes, the LF-checkout check, the legacy migration, and the tamper refusal.
- `docs/ADOPTER_INSTALL.md` — the line-ending contract statement.
- `.gitattributes` — pin LF checkout for the OIO source so the shipped package bytes are canonical.
- `tasks/**`, `checkpoints/**`, `PROJECT.md`, `HANDOFF.md` — this projection and the checkpoint.

## Human outcome

A Windows operator who installs OIO and then validates it on Linux (or vice versa) gets a passing `--check` instead of a fail-closed gate that accuses the install of tampering, and an existing adopter with a stale manifest recovers by re-running the installer.

## Scope and boundaries

- In scope: LF-canonical writes, an EOL-insensitive integrity comparison with a distinct note for an EOL-only difference, migration of legacy CRLF-digest manifests, the source `.gitattributes`, and regression tests.
- Out of scope: the ontology, the project template, and the triage contract (unchanged); a `--rehash`/`--force` flag (a normal re-install already migrates, so no new flag is needed); any other repository.
- Dependencies/uncertainty: a genuine content edit that happens to equal another file's LF-normalized digest cannot exist without a SHA-256 collision, so the comparison does not weaken tamper detection.

## Acceptance criteria

- [x] Installing OIO writes every managed file with LF and records the digest of those LF bytes; a Windows and a Linux install are byte-identical.
- [x] `--check` passes on a CRLF checkout of identical content and reports the line-ending difference as a note; a real content edit is still refused.
- [x] A legacy manifest that recorded CRLF digests migrates to LF through a normal re-install, without deleting the install or hand-editing the manifest.
- [x] `python -m unittest discover -s tests` passes on Windows and ubuntu CI, with new tests that fail against the pre-fix installer.
- [x] `.gitattributes` pins LF checkout for the OIO source.

## Evidence and sources

- Issue #41 (operational, evidence:confirmed, impact:high): direct reproduction with byte counts — worktree `.oio/ontology/default.json` had 157 CRLF while the committed blob had 157 LF; the adopter's manifest recorded CRLF digests.
- Local reproduction before the fix: the OIO source worktree `.oio/ontology/default.json` had 157 CRLF; the installer wrote 157 CRLF and hashed the CRLF bytes; after normalizing the installed files to LF, `--check` returned exit 2 `managed file changed since OIO installed it: .oio/ontology/default.json` and re-install refused identically.
- The `.gitattributes` and LF-normalization approach matches the reporting adopter's `Pukujan/ai-note-taking-app`, whose `* text=auto eol=lf` is what surfaced the divergence.

## Related records

- Leaf owning issue: `Pukujan/observational-issue-ops#41` (open; parent: none).
- Related: `#32` (native Windows install) and `#37` (stale pin) are distinct but share the Windows-install symptom.
- Primary writer / branch / as-of status: owner session on `task/OIO-0007-lf-canonical-install`, based on `origin/main` at `504d413`; merged to `main` as squash `27b954f` (PR #42). Task complete; issue #41 open pending human verification.

## Checkpoint log

### 2026-10-10 03:05:00 UTC — owner session (LF-canonical install)

Completed:
- Made the managed-file integrity contract line-ending independent: the installer normalizes every managed file to LF before writing and records the digest of those LF bytes, so a Windows (CRLF) install and a Linux (LF) install are byte-identical.
- `--check` compares content after line-ending normalization and reports an EOL-only difference as a note instead of the tamper refusal, while a real content edit is still refused.
- A manifest that recorded CRLF digests migrates to LF through a normal re-install, without deleting the install or hand-editing the manifest.
- Added `.gitattributes` pinning `* text=auto eol=lf` (binary assets excluded) so the shipped package bytes are canonical on every platform.

Evidence:
- Branch `task/OIO-0007-lf-canonical-install` pushed at `74d983c` (base `origin/main` `504d413`); PR #42 merged to `main` as squash `27b954f` at 2026-10-10T02:55:17Z.
- Required check `gates` passed: ubuntu leg (continuity validate/preflight, 45-test suite, adapter validation, secret scan, template parse) and windows leg (all six new regression tests green).
- The six new tests fail against the pre-fix installer (2 failures, 3 errors). Receipt on issue #41 (comment 6093062254).
- `require / mesh` is red but was already red on `main` before this branch and is not a required check; unrelated mesh drift (`agent-custom-setup` pin `efd8e191` behind the train `26411739`).

Decisions:
- Normalize at write time and record LF digests, rather than only comparing EOL-insensitively: this makes a Windows and a Linux install byte-identical and fixes the source, so no adopter-side workaround is needed.
- Report an EOL-only difference as a note rather than a failure; keep the tamper refusal for real content edits. A content edit equalling another file's LF-normalized digest would require a SHA-256 collision, so tamper detection is not weakened.
- No `--rehash`/`--force` flag: a normal re-install already migrates a legacy manifest.

Changed:
- .github/scripts/oio_installer.py, tests/test_oio.py, .gitattributes, docs/ADOPTER_INSTALL.md, tasks/TASK-OIO-0007-line-ending-independent-managed-files.md, checkpoints/CURRENT.md

Blocked/uncertain:
- Human verification of a Windows-install → Linux-`--check` round trip remains open on issue #41 (`needs-human-verification`); the fix is verified by tests and CI, not on a machine outside this session.

Next:
- None for this task; await the human round-trip confirmation on issue #41 before closing it.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
