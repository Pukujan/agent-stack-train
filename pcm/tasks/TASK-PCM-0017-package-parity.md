# TASK-PCM-0017 — Prove package version and installed behavior parity

<!-- continuity:task {"acceptance":["one source-declared CLI/package version feeds Python build metadata and the runtime version diagnostic","wheel and source distribution both install outside the source checkout and report a matching installed distribution, module, and CLI version","both artifacts run the installed CLI on Python 3.11 and 3.12 without importing from the source checkout","fresh minimal and software initialization from each installed artifact matches the source-generated file inventory and bytes, including lifecycle guidance, schemas, and optional GitHub templates, and the generated projects validate","CI runs and clearly names the artifact installation/generation-parity checks before allowing automatic merge","the repository states that artifact build/install verification does not publish a public release; no PyPI publication or target-repository migration occurs","protocol version remains 0.1.0-draft and is not coupled to the package version"],"depends_on":["PCM-0015"],"goal":"Make the installable PCM package report the same version it was built with and prove that the distributed wheel and source archive behave like the checked-in source.","id":"PCM-0017","next_action":"No implementation work remains; continue with the separately scoped PCM-0018 / issue #33 document-discovery proof.","owner":"Codex PCM development session; GitHub issue #31","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"A new adopter installs the built package, not the developer's source tree. The current checkout already reports conflicting versions: package metadata is 0.2.0 while the source module says 0.1.0, so users cannot reliably tell what they installed or whether generated behavior matches the repository."} -->

## Human outcome

When someone installs PCM, its version command should tell them which package they actually have, and its initialized project should match what the repository's checked-in tool produces. A successful build alone is not proof that an install works or that it includes the right guidance.

## Baseline evidence

- GitHub issue [#31](https://github.com/Pukujan/project-continuity-modules/issues/31) is the authoritative bounded scope.
- At activation on `main` commit `ba315af0`, `pyproject.toml` declared package version `0.2.0`, while `src/continuity/__init__.py` declared `__version__ = "0.1.0"`.
- The repository has required `quality`, `test (3.11)`, `test (3.12)`, and `package` checks. Its auto-merge job currently waits for those four jobs. PCM-0017 must add artifact-install parity to the merge gate and make the hosted check required where repository protection permits.
- The protocol remains `0.1.0-draft`; this task changes package metadata/runtime identity only.

## External research and provenance

Checked 2026-09-23 against primary documentation:

- Setuptools' [`pyproject.toml` configuration guide](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html#dynamic-metadata) explicitly supports deriving project `version` from a statically declared Python module attribute with `tool.setuptools.dynamic.version = {attr = "package.__version__"}`. Its `attr` reader first inspects the module AST, making a literal version assignment the documented safe shape.
- The Python Packaging User Guide explains that a wheel and a source distribution are different installation artifacts and documents installing archives with pip into a virtual environment: [package formats](https://packaging.python.org/en/latest/discussions/package-formats/) and [pip/venv installation](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/). This supports testing both artifacts in isolated environments rather than inferring installability from a successful build.
- GitHub's [protected-branch REST API](https://docs.github.com/en/rest/branches/branch-protection) documents the required-status-check update endpoint. The existing protection requires four contexts from the GitHub Actions app; add package-parity contexts without removing the current gates, then inspect the resulting protection object.

## Scope

Make the CLI/package version single-sourced; add a clear `continuity --version`; build and install both wheel and source archive in clean environments outside the checkout on Python 3.11 and 3.12; compare installed initialization output to source output for minimal and software profiles; and enforce the proof in CI before auto-merge.

Do not publish to PyPI, change protocol version or schemas, migrate adopters, implement Node support, or perform unrelated issues. Do not treat an artifact smoke-test pass as a release.

## Verification plan

- Deterministic version-consistency contract: Python source constant, built distribution metadata, installed import, and console-script diagnostic agree.
- Integration checks: wheel and sdist install in isolated environments on each supported Python version and execute outside the repository.
- Generated-output parity: installed artifacts generate identical paths/bytes to the source CLI for minimal and software profiles, including optional GitHub templates; generated targets pass `continuity validate`.
- Full quality gates: Ruff, MyPy, compile, all unit/contract tests on Python 3.11 and 3.12, package build/install checks, continuity validation, and hosted required checks.
- No fresh-agent holdout is planned: this issue promises artifact/package parity, not that a new session can discover or execute handoff guidance. The generated content is checked deterministically against the visible source contract.

## Acceptance

- [x] One source-declared package version feeds build metadata and the runtime version diagnostic.
- [x] Wheel and source archive install outside the checkout and report matching installed distribution, module, and CLI versions.
- [x] Both artifacts run on Python 3.11 and 3.12 without importing from the source checkout.
- [x] Minimal and software initialization match source-generated paths and bytes, including schemas, lifecycle guidance, and optional GitHub templates; generated projects validate.
- [x] CI checks both artifacts on both supported Python versions and auto-merge waits for those checks; main protection requires both package-parity contexts.
- [x] Documentation distinguishes build/install verification from public release; no PyPI publish or adopter migration was performed.
- [x] Protocol version remains `0.1.0-draft` and independent of the package version.

## Checkpoint log

### 2026-09-23 — Task activated

Completed:
- Confirmed issue #31 is open and bounded to package version identity, artifact installation, and generated-resource parity.
- Reproduced a source/metadata mismatch directly from the current repository files.
- Confirmed current GitHub branch protection requires four CI contexts and current auto-merge waits for the same four; adding an install-parity job must update both workflow gating and branch protection when supported.

Evidence:
- Read-only commands: `rg -n "__version__|version|importlib.metadata|continuity init|resources.files|files\\(" src tests pyproject.toml` and `gh api repos/Pukujan/project-continuity-modules/branches/main/protection`.
- Observed values: `pyproject.toml` = `0.2.0`; `src/continuity/__init__.py` = `0.1.0`; required contexts = `quality`, `test (3.11)`, `test (3.12)`, `package`.

Decisions:
- Use the checked-in Python version constant as the package build source of truth, derive project metadata from it, and expose that same value through the CLI. Keep protocol version independent.

Changed:
- Initial task contract and canonical current/handoff pointers.

Blocked/uncertain:
- None. Branch protection can be reconfigured only after the new stable CI context exists and its exact name is verified.

Next:
- Implement the single-source version and isolated artifact parity runner, then run it locally on Python 3.11 and 3.12 before changing hosted CI.

### 2026-09-23 20:50:43 UTC — Codex PCM-0017

<!-- continuity:checkpoint {"agent":"Codex PCM-0017","blocked":["Hosted PR checks and merge are pending. The main branch protection has not yet been extended with the new package-parity contexts; verify the emitted check names and add both as required before opening the PR."],"changed":[".github/workflows/ci.yml, .gitignore, README.md, docs/VERSIONING.md, pyproject.toml, src/continuity/__init__.py, src/continuity/cli.py, tests/test_cli.py, tests/package_smoke.py, tasks/TASK-PCM-0017-package-parity.md, checkpoints/CURRENT.md, HANDOFF.md"],"completed":["Replaced the duplicated package version with a setuptools dynamic value sourced from continuity.__version__, set to 0.2.0, and added continuity --version.","Added an isolated wheel/sdist smoke runner that compares installed version and generated minimal/software projects against the source CLI and validates the generated projects.","Added package-parity jobs for Python 3.11 and 3.12 and made automatic merge wait for both jobs; documented that build/install checks are not public release."],"decisions":["Keep 0.2.0 as the package version and 0.1.0-draft as the independent protocol version; do not publish to PyPI.","Use isolated task-scoped environments and shared download/build caches; do not share mutable environments."],"evidence":["Python 3.12.10: all 47 unittest tests passed; continuity validate reported VALID; Ruff, MyPy, compileall, and diff checks passed.","Python 3.11.15: all 47 unittest tests passed; continuity validate reported VALID; Ruff, MyPy, and compileall passed.","On both Python versions, wheel and source archive each installed into isolated environments outside the checkout; --version matched distribution metadata and module version; minimal/software initialization outputs matched source file inventories and bytes; generated projects validated.","Setuptools dynamic-version documentation, Python Packaging User Guide artifact/venv documentation, and GitHub protected-branch API documentation are cited in the task record."],"next_action":"Run this continuity checkpoint to push the task branch, inspect its CI contexts and results, require package parity in main protection, then open the auto-merge PR; keep issue #31 open until the closeout merge is confirmed.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0017","timestamp":"2026-09-23T20:50:43Z"} -->

Completed:
- Replaced the duplicated package version with a setuptools dynamic value sourced from continuity.__version__, set to 0.2.0, and added continuity --version.
- Added an isolated wheel/sdist smoke runner that compares installed version and generated minimal/software projects against the source CLI and validates the generated projects.
- Added package-parity jobs for Python 3.11 and 3.12 and made automatic merge wait for both jobs; documented that build/install checks are not public release.

Evidence:
- Python 3.12.10: all 47 unittest tests passed; continuity validate reported VALID; Ruff, MyPy, compileall, and diff checks passed.
- Python 3.11.15: all 47 unittest tests passed; continuity validate reported VALID; Ruff, MyPy, and compileall passed.
- On both Python versions, wheel and source archive each installed into isolated environments outside the checkout; --version matched distribution metadata and module version; minimal/software initialization outputs matched source file inventories and bytes; generated projects validated.
- Setuptools dynamic-version documentation, Python Packaging User Guide artifact/venv documentation, and GitHub protected-branch API documentation are cited in the task record.

Decisions:
- Keep 0.2.0 as the package version and 0.1.0-draft as the independent protocol version; do not publish to PyPI.
- Use isolated task-scoped environments and shared download/build caches; do not share mutable environments.

Changed:
- .github/workflows/ci.yml, .gitignore, README.md, docs/VERSIONING.md, pyproject.toml, src/continuity/__init__.py, src/continuity/cli.py, tests/test_cli.py, tests/package_smoke.py, tasks/TASK-PCM-0017-package-parity.md, checkpoints/CURRENT.md, HANDOFF.md

Blocked/uncertain:
- Hosted PR checks and merge are pending. The main branch protection has not yet been extended with the new package-parity contexts; verify the emitted check names and add both as required before opening the PR.

Next:
- Run this continuity checkpoint to push the task branch, inspect its CI contexts and results, require package parity in main protection, then open the auto-merge PR; keep issue #31 open until the closeout merge is confirmed.

### 2026-09-23 20:53 UTC — Delivery merged and task closeout

<!-- continuity:checkpoint {"agent":"Codex PCM-0017 closeout","blocked":[],"changed":["tasks/TASK-PCM-0017-package-parity.md","checkpoints/CURRENT.md","HANDOFF.md","main branch required-status-check protection"],"completed":["PR #49 merged package-version parity and artifact installation/generation checks to main.","All required PR checks succeeded; main protection now requires quality, Python 3.11/3.12 tests, package build, and package parity on Python 3.11/3.12.","Recorded the merged result and verified issue #31 remained open for this final canonical closeout."],"decisions":["Close issue #31 only after this canonical task/checkpoint state is merged; do not treat build/install verification as public release."],"evidence":["PR #49 merged at 2026-09-23T20:53:16Z as merge commit 18f6b510c4de7005cb54ff7bfc016cd0ed67a0b8.","PR CI run 35918854304 succeeded on quality, test (3.11), test (3.12), package, package parity (3.11), package parity (3.12), and auto-merge.","Local Python 3.11.15 and 3.12.10 suites each passed 47 tests; both wheel and sdist passed isolated-install parity for both profiles on both runtimes.","Protected status-check API now returns all six required check contexts, each provided by the GitHub Actions app.","Official sources and the detailed method are linked above and recorded in issue #31 comment https://github.com/Pukujan/project-continuity-modules/issues/31#issuecomment-5802736211."],"next_action":"After this closeout PR passes required checks and merges, verify issue #31 is closed and start the separately scoped PCM-0018 / issue #33 task.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0017","timestamp":"2026-09-23T20:53:16Z"} -->

Completed:
- PR #49 merged package-version parity and artifact installation/generation checks to main.
- All required PR checks succeeded; main protection now requires quality, Python 3.11/3.12 tests, package build, and package parity on Python 3.11/3.12.
- Recorded the merged result and verified issue #31 remained open for this final canonical closeout.

Evidence:
- PR #49 merged at 2026-09-23T20:53:16Z as merge commit `18f6b510c4de7005cb54ff7bfc016cd0ed67a0b8`.
- PR CI run [35918854304](https://github.com/Pukujan/project-continuity-modules/actions/runs/35918854304) succeeded on quality, test (3.11), test (3.12), package, package parity (3.11), package parity (3.12), and auto-merge.
- Local Python 3.11.15 and 3.12.10 suites each passed 47 tests; both wheel and sdist passed isolated-install parity for both profiles on both runtimes.
- Protected status-check API returns all six required contexts, each provided by the GitHub Actions app.
- Official sources and detailed method are linked above and in [issue #31's progress record](https://github.com/Pukujan/project-continuity-modules/issues/31#issuecomment-5802736211).

Decisions:
- Close issue #31 only after this closeout PR passes required checks and merges; build/install verification is not a public release.

Changed:
- This task record, `checkpoints/CURRENT.md`, and `HANDOFF.md`.

Blocked/uncertain:
- No implementation blocker. Issue #31 remains open until this closeout PR passes the required checks and merges.

Next:
- After this closeout PR passes required checks and merges, verify issue #31 is closed and start the separately scoped PCM-0018 / issue #33 task.

### 2026-09-23 20:59:35 UTC — Codex PCM-0017 closeout

<!-- continuity:checkpoint {"agent":"Codex PCM-0017 closeout","blocked":["Closeout PR checks and merge are pending; issue #31 is intentionally still open."],"changed":["tasks/TASK-PCM-0017-package-parity.md, checkpoints/CURRENT.md, HANDOFF.md"],"completed":["Updated task metadata and acceptance evidence to completed after PR #49 merged with all required checks.","Updated CURRENT and HANDOFF to show package parity is merged, the package and runtime both report 0.2.0, the protocol remains 0.1.0-draft, and issue #31 stays open only for this canonical closeout PR."],"decisions":["Keep issue #31 open until this canonical status record itself merges; no issue is closed solely because implementation code is on a local or unmerged branch."],"evidence":["PR #49 merged at 18f6b510c4de7005cb54ff7bfc016cd0ed67a0b8; hosted CI run 35918854304 passed all six required contexts and auto-merge.","Protected branch API confirms quality, test (3.11), test (3.12), package, package parity (3.11), and package parity (3.12) are required from GitHub Actions.","Continuity validation returned VALID after the closeout task/checkpoint/handoff updates."],"next_action":"Push this checkpoint, open the closeout PR with Closes #31, let all six required checks and auto-merge complete, verify the issue closure, then start PCM-0018 / issue #33.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0017","timestamp":"2026-09-23T20:59:35Z"} -->

Completed:
- Updated task metadata and acceptance evidence to completed after PR #49 merged with all required checks.
- Updated CURRENT and HANDOFF to show package parity is merged, the package and runtime both report 0.2.0, the protocol remains 0.1.0-draft, and issue #31 stays open only for this canonical closeout PR.

Evidence:
- PR #49 merged at 18f6b510c4de7005cb54ff7bfc016cd0ed67a0b8; hosted CI run 35918854304 passed all six required contexts and auto-merge.
- Protected branch API confirms quality, test (3.11), test (3.12), package, package parity (3.11), and package parity (3.12) are required from GitHub Actions.
- Continuity validation returned VALID after the closeout task/checkpoint/handoff updates.

Decisions:
- Keep issue #31 open until this canonical status record itself merges; no issue is closed solely because implementation code is on a local or unmerged branch.

Changed:
- tasks/TASK-PCM-0017-package-parity.md, checkpoints/CURRENT.md, HANDOFF.md

Blocked/uncertain:
- Closeout PR checks and merge are pending; issue #31 is intentionally still open.

Next:
- Push this checkpoint, open the closeout PR with Closes #31, let all six required checks and auto-merge complete, verify the issue closure, then start PCM-0018 / issue #33.

## Handoff

Read `PROJECT.md`, `checkpoints/CURRENT.md`, this task, `AGENTS.md`, `SPEC.md`, and `docs/VERSIONING.md`. Do not publish a package or change the protocol version.
