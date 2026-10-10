# Install OIO in one repository

OIO installs its observational/operational issue-log ontology, project extension, issue form, and triage workflow into one explicitly selected Git repository. The target keeps its own issues, project priorities, account map, and implementation/release decisions.

## From a pinned OIO checkout

Use an OIO checkout at the release or full commit your project has approved. Install the pinned validator dependency, then pass the absolute path of the one target repository:

```bash
python3 -m pip install -r requirements.txt
python3 /absolute/path/to/OIO/.github/scripts/oio_installer.py \
  --target /absolute/path/to/target-repository
```

The installer infers `OWNER/REPOSITORY` from the target's `origin` remote. If that remote is unavailable, pass `--project-id OWNER/REPOSITORY`. It refuses a relative target, a non-Git directory, the OIO source repository itself, a symlink or junction in a managed path, or an unmanaged file collision. On macOS and Linux, package writes and recovery use descriptor-relative no-follow operations and verify the opened parent directory before creating temporary files and again before atomic replacement; a managed-directory symlink swap detected at those checks fails closed instead of redirecting a write. On Windows, which exposes no descriptor-relative operations, the installer refuses a symlink, junction, or other reparse point at every managed path component and re-verifies the parent directory's identity immediately before and after each replacement, so a managed-directory swap detected at those checks fails closed there too; junctions are treated exactly like symlinks. Keep the target worktree and managed directories stable during installation. Neither control defends against another same-user process that races the verification window or relocates an already-open managed directory outside the target. It changes only its documented files under `.oio/`, `.github/`, and the marked OIO block in `AGENTS.md`; it does not create issues or contact other repositories. A platform that supports neither control fails closed rather than installing with a weaker guarantee.

The project scaffold contains generic paths `1` through `100`. Replace their generic descriptions with meanings that fit the adopter before relying on priority for product decisions. Maintain `account_authority` using authenticated GitHub numeric account IDs; unknown accounts remain at the end pending owner review. Project-specific terms must use the generated namespace and extend, not redefine, OIO core terms.

Run the installed copy in read-only check mode to confirm its own current package matches:

```bash
python3 /absolute/path/to/target-repository/.github/scripts/oio_installer.py \
  --target /absolute/path/to/target-repository --check
```

For an upgrade, rerun the installer from a newer pinned OIO checkout against the same explicit target. The installer refuses to overwrite edited managed files or project-owned extension data; review conflicts and migrate deliberately. Installation does not grant permission to file issues. In particular, an agent may prepare a local draft but must not submit an issue or write files in OIO, ACS, CGM, or PCM without explicit human direction naming the destination and action.

## Line endings

OIO writes its managed files with LF line endings regardless of the platform that ran the installer, and records the digests of those LF bytes. The integrity check compares content after line-ending normalization, so a checkout that renders the same content with CRLF — for example a Windows worktree of a repository whose `.gitattributes` commits LF — passes `--check` and is reported with a note that the content matches and the line endings differ, while a real content edit is still refused. An existing install whose manifest recorded CRLF digests from an older installer migrates through a normal re-install; the managed files are rewritten as LF and the manifest is regenerated, without deleting the install.

## Validation

The installer validates the default ontology and adopter extension. CI tests fresh and repeated installation in a disposable local repository, path confinement, preservation of adopter data, explicit conflict refusal, and interrupted-install recovery. OIO's issue triage validates observational/operational records and labels source class, authenticated account tier, project priority, evidence dimensions, release relevance, and an advisory review lane. Risk labels do not grant authority or make an automatic release decision.
