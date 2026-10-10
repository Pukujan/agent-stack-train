# TASK-OIO-0007 — Line-ending independent managed files

<!-- continuity:task {"acceptance":["Installing OIO writes every managed file with LF line endings and records the digest of those LF bytes, so a Windows (CRLF) install and a Linux (LF) install produce byte-identical files","`--check` passes on a checkout that renders the same content with CRLF, and reports the line-ending difference as a note rather than the 'managed file changed' tamper refusal; a real content edit is still refused","An existing install whose manifest recorded CRLF digests (from an installer that hashed a Windows worktree) migrates to LF through a normal re-install, without deleting the install or hand-editing the manifest","`python -m unittest discover -s tests` passes on Windows and on ubuntu CI, with new regression tests that fail against the pre-fix installer","A `.gitattributes` in the OIO source pins LF checkout so the shipped package bytes are canonical on every platform"],"depends_on":[],"goal":"Make OIO's managed-file integrity contract line-ending independent so a correct install passes its own required `--check` gate on a Linux checkout, whether the installer ran on Windows or Linux.","id":"OIO-0007","issue_url":"https://github.com/Pukujan/observational-issue-ops/issues/41","next_action":"Push the branch, open a PR that Refs #41, arm auto-merge after the final push, and confirm the required gates before marking complete.","owner":"owner/Pukujan","priority":"P5","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The installer read package files as raw working-tree bytes and hashed them, so a Windows (CRLF) checkout installed CRLF files with CRLF digests; a later LF checkout (Linux CI) then failed both `--check` and re-install with 'managed file changed since OIO installed it' even though the content was identical. Reported as recurring across adopter repositories (issue #41)."} -->

- Status: active
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

- [ ] Installing OIO writes every managed file with LF and records the digest of those LF bytes; a Windows and a Linux install are byte-identical.
- [ ] `--check` passes on a CRLF checkout of identical content and reports the line-ending difference as a note; a real content edit is still refused.
- [ ] A legacy manifest that recorded CRLF digests migrates to LF through a normal re-install, without deleting the install or hand-editing the manifest.
- [ ] `python -m unittest discover -s tests` passes on Windows and ubuntu CI, with new tests that fail against the pre-fix installer.
- [ ] `.gitattributes` pins LF checkout for the OIO source.

## Evidence and sources

- Issue #41 (operational, evidence:confirmed, impact:high): direct reproduction with byte counts — worktree `.oio/ontology/default.json` had 157 CRLF while the committed blob had 157 LF; the adopter's manifest recorded CRLF digests.
- Local reproduction before the fix: the OIO source worktree `.oio/ontology/default.json` had 157 CRLF; the installer wrote 157 CRLF and hashed the CRLF bytes; after normalizing the installed files to LF, `--check` returned exit 2 `managed file changed since OIO installed it: .oio/ontology/default.json` and re-install refused identically.
- The `.gitattributes` and LF-normalization approach matches the reporting adopter's `Pukujan/ai-note-taking-app`, whose `* text=auto eol=lf` is what surfaced the divergence.

## Related records

- Leaf owning issue: `Pukujan/observational-issue-ops#41` (open; parent: none).
- Related: `#32` (native Windows install) and `#37` (stale pin) are distinct but share the Windows-install symptom.
- Primary writer / branch / as-of status: owner session on `task/OIO-0007-lf-canonical-install`, based on `origin/main` at `504d413`.

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
