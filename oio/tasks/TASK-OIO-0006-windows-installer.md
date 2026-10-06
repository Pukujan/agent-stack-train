# TASK-OIO-0006 — Windows Installer

<!-- continuity:task {"acceptance":["`python -m unittest discover -s tests` passes on Windows (all 36 tests), where 15 failed before the port","The Windows control refuses a junction or reparse point at a managed path component and leaves the outside tree byte-unchanged; a metamorphic check proves the guard is load-bearing (neutering the parent-identity re-verification lets the same swap redirect the write)","POSIX behavior is unchanged: the `_PosixTargetFS` body is byte-identical and the ubuntu CI leg stays green","CI runs the installer suite on `windows-latest` and the required `gates` context fails when it does not pass","`docs/ADOPTER_INSTALL.md` states the per-platform control (POSIX dir_fd/O_NOFOLLOW; Windows reparse-point refusal plus parent-identity re-verification) and that junctions are treated like symlinks","ACS `oio_platform_supported()` stops pre-refusing Windows and the OIO pin is bumped to the ported commit, tracked as the follow-up that lets a Windows operator reach a full install"],"depends_on":[],"goal":"Let OIO's installer run on Windows with its no-follow anti-redirection control preserved, so a Windows operator reaches a full stack install instead of a PARTIAL one.","id":"OIO-0006","issue_url":"https://github.com/Pukujan/observational-issue-ops/issues/32","next_action":"Land the port on `main` through the required `gates` PR, then open the ACS follow-up (platform check plus OIO pin bump).","owner":"owner/Pukujan","priority":"P5","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"ACS SPEC.md section 6 requires every installer to run on Windows, macOS, and Linux, and marks OIO 'port required'; Windows lacks dir_fd/O_NOFOLLOW, so the installer refuses to start and ACS reports PARTIAL (OIO issue #32)."} -->

- Status: active
- Owner: owner/Pukujan
- Priority: P5
- Depends on: none

## Goal

Let OIO's installer run on Windows with its no-follow anti-redirection control preserved, so a Windows operator reaches a full stack install instead of a PARTIAL one.

## Why

ACS `SPEC.md` section 6 ("Platform matrix") states that every installer must run on Windows, macOS, and Linux, marks the OIO installer `✅ (port required)` for Windows, and requires its security control — refusing symlink/reparse-point redirection of a managed write outside the target — to be preserved on every platform, using descriptor-relative `O_NOFOLLOW` operations on POSIX and `os.lstat` reparse-point checks and/or `CreateFileW` with `FILE_FLAG_OPEN_REPARSE_POINT` on Windows. Windows exposes none of the `dir_fd` operations, so the installer refuses to start there and the ACS hotload reports a PARTIAL install with no OIO issue-log surface (OIO issue #32).

## Allowed files

- `.github/scripts/oio_installer.py` — the platform-dispatched filesystem layer.
- `tests/test_oio.py` — the Windows-runnable regression and swap-race coverage.
- `.github/workflows/ci.yml` — the Windows CI job and its aggregation into `gates`.
- `docs/ADOPTER_INSTALL.md` — the per-platform control statement.
- `tasks/**`, `checkpoints/**` — this projection and the checkpoint.

## Human outcome

A Windows operator runs the ACS hotload and gets the OIO issue-log surface instead of a documented partial install, with the same guarantee that a managed-directory swap cannot redirect a write outside the target that POSIX operators already have.

## Scope and boundaries

- In scope: a platform-dispatched `_TargetFS` with an equivalent Windows control, tests that exercise it on Windows without administrator privilege, a Windows CI leg, and the doc statement.
- Out of scope: changing POSIX behavior; ACS's platform check and pin bump (a separate, coupled PR); any other repository's installer.
- Dependencies/uncertainty: the Windows control is path-based, so a swap inside the post-verification window is the same documented same-user residual as POSIX; Windows has no directory `fsync`, which is a durability, not a security, difference.

## Acceptance criteria

- [ ] `python -m unittest discover -s tests` passes on Windows (all 36 tests), where 15 failed before the port.
- [ ] The Windows control refuses a junction or reparse point at a managed path component and leaves the outside tree byte-unchanged; a metamorphic check proves the guard is load-bearing (neutering the parent-identity re-verification lets the same swap redirect the write).
- [ ] POSIX behavior is unchanged: the `_PosixTargetFS` body is byte-identical and the ubuntu CI leg stays green.
- [ ] CI runs the installer suite on `windows-latest` and the required `gates` context fails when it does not pass.
- [ ] `docs/ADOPTER_INSTALL.md` states the per-platform control and that junctions are treated like symlinks.
- [ ] ACS `oio_platform_supported()` stops pre-refusing Windows and the OIO pin is bumped to the ported commit (tracked follow-up).

## Evidence and sources

- ACS `SPEC.md` section 6 (Platform matrix), lines 153–167: every installer runs on Windows/macOS/Linux; OIO is `✅ (port required)`; the control is preserved per platform via `os.lstat` reparse-point checks on Windows.
- Windows 11 build 26200, CPython 3.12.10: `os.supports_dir_fd` lacks `mkdir, open, rename, stat, unlink`; `os.O_NOFOLLOW` and `os.O_DIRECTORY` absent; `os.open(<dir>, O_RDONLY)` raises `PermissionError`.
- `os.lstat(...).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT` (1024) detects both symlinks and junctions; `os.stat(path, follow_symlinks=False)` returns distinct `st_dev`/`st_ino` for a junction and its target. Junctions are creatable without privilege via `_winapi.CreateJunction(target, link)` (also `mklink /J`).
- Baseline before the port: `python -m unittest discover -s tests` → 36 tests, 2 failures + 13 errors, all `InstallerTests`, all reporting "this platform lacks descriptor-relative no-follow filesystem operations". After the port: 36 tests, OK.
- Control effectiveness (metamorphic): with the control in place the mid-write junction swap raises `InstallError: managed target path changed during installation` and the outside sentinel is unchanged; with `_verify_parent`/`_verify_root` neutered the write succeeds and the outside sentinel is overwritten with the attacker-controlled bytes.

## Reproduction details (only when needed)

- Runtime: CPython 3.12.10 on Windows 11; `jsonschema==4.23.0` from `requirements.txt`; standard library only otherwise.
- `python -m unittest discover -s tests -v` (all platforms).
- The Windows tests create directory links with `_winapi.CreateJunction`, so they need no Developer Mode or administrator privilege.

## Related records

- Leaf owning issue: `Pukujan/observational-issue-ops#32` (open).
- Coupled follow-up: `Pukujan/agent-custom-setup` — `oio_platform_supported()` and the OIO pin in `stack-mesh.json`.
- Primary writer / branch / as-of status: owner session on `task/OIO-0006-windows-installer`.
- Related PR/CI evidence and push receipt (request ID / SHA): recorded in the checkpoint log below as the work lands.

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
