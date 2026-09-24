# PCM-0028 design: independently versioned modules and an upgrade path

Status: **accepted by Alex on 2026-09-24** (see [Decisions](#decisions-accepted-by-alex-2026-09-24)). **Accepted design, not implemented: nothing described under "Design" exists in the repository today unless it is named as existing with a path.** Implementation is tracked by phase issues #104-#108 (sub-issues of #100). Tracking issue: [#100 / PCM-0028](https://github.com/Pukujan/project-continuity-modules/issues/100). Depends on [#99 / PCM-0027](https://github.com/Pukujan/project-continuity-modules/issues/99). Evidence base: `main` at `c894f3c` (2026-09-24).

**Implementation waits on #99.** #99's blind test of the `issue-log-format` guidance was running when this was written and has no results yet. This plan uses `issue-log-format` 1.0.0 as the first new module. If the test changes the format, the module text changes but the mechanism in this plan does not. If #99 is dropped, `github-progression` becomes the reference module instead (see [Phase 1](#phase-1-spike-on-a-disposable-fixture-not-merged)).

## The problem in plain words

When one piece of PCM guidance changes (for example, the rules for writing issues), an adopting project can't tell which piece changed, which version it has, or how to update without overwriting its own edits. Today the answer is a careful hand edit, which quietly leaves some projects on old rules.

This plan turns the pieces of PCM guidance that get copied into adopter files into **modules**. Each one has an id and a version, is stamped into the files it owns, is listed in a registry shipped with the CLI, is reported by `continuity validate`, and can be updated by a new `continuity upgrade` command. The command shows a diff first and refuses anything it can't do safely.

**The design is deliberately small.** It reuses the marker that `continuity-records` already uses and the start/end block convention that `github-progression` already uses. It adds no plugin system, no remote downloads, no new runtime dependency and no protocol major bump. Phase 1 is a throwaway spike with a decision gate. If a simple "current vs stale" check per marker turns out to be enough, we stop there (see [Honest caveat](#honest-caveat)).

## What exists today (verified)

Facts below come from reading the code at `c894f3c`, not from the issue text.

- **One package, one file.** All CLI logic is in `src/continuity/cli.py` (3,635 lines). The version is `__version__ = "0.4.0"` in `src/continuity/__init__.py`, read by `pyproject.toml` through `tool.setuptools.dynamic`. CI builds it; nothing publishes it. Runtime dependencies: none (`dependencies = []`).
- **One protocol version.** `PROTOCOL_VERSION = "0.1.0-draft"` (`cli.py:24`). `.continuity/config.json` declares it with schema `project-continuity.config.v1`.
- **Profiles are Python generator functions, not template folders.** `continuity init` builds every file from functions in `cli.py`: `project_template` (474), `current_template` (493), `handoff_template` (537), `agents_template` (568), `github_issue_template` (593), `github_pr_template` (637), `readme_template` (677) and `init_repo` (686). The folders `templates/v1/minimal/` and `templates/v1/software/` are **not read by the CLI**. They are checked-in reference copies that tests compare against. `profile.json` in each folder lists files and `protocol_version` only.
- **The static copies have drifted from generated output.** `templates/v1/software/AGENTS.md` and `templates/v1/minimal/HANDOFF.md` contain agent-lifecycle ("close the worker") and testing-policy ("holdout", "deterministic") text, which `tests/test_agent_lifecycle_policy.py` and `tests/test_agent_facing_testing_policy.py` check. A fresh `continuity init --profile software --github-templates` contains neither. I checked this directly on a scratch directory.
- **Only one piece is versioned.** `CONTINUITY_RECORDS_POLICY_MARKER` (`cli.py:25-27`) is `<!-- pcm:policy {"id":"continuity-records","policy_version":"1.2.0","protocol_version":"0.1.0-draft"} -->`. It is emitted by `handoff_template` (560) and `agents_template` (583), and copied into `docs/CONTINUITY_RECORDS_POLICY.md:3`, `AGENTS.md:100`, `HANDOFF.md:66`, `templates/v1/minimal/HANDOFF.md:45` and `templates/v1/software/AGENTS.md:35`. Git history shows it has already moved 1.0.0 → 1.1.0 → 1.2.0. The text after it is **not delimited**, and the HANDOFF and AGENTS variants are different paragraphs.
- **Only unit tests check that marker.** `tests/test_continuity_records_policy.py` checks it is present. `validate_repo` (`cli.py:1435-1614`) never looks at `pcm:` markers; its marker regex `MARKER_RE` (`cli.py:51`) matches only `continuity:<kind>` markers.
- **`github-progression` is delimited but unversioned.** `GITHUB_PROGRESSION_GUIDANCE` (`cli.py:28-42`) is wrapped in `<!-- pcm:github-progression:start -->` / `:end -->`. It is emitted into six generated files: PROJECT (484), HANDOFF (554), AGENTS (576), the issue template (634), the PR template (674) and README (682). Its text has already changed at least once in git history with no version change, so an adopter can't tell which text they have.
- **`validate` has no warning channel.** `main` prints `ERROR:` lines and `INVALID`, or `VALID` (`cli.py:3280-3289`). #99 plans the first warnings.
- **`init` refuses to overwrite.** `init_repo` refuses the whole run if any planned file exists with different content (`cli.py:736-743`), and `write_file_no_overwrite` (456) does the same per file. There is no upgrade command in `build_parser` (`cli.py:3137-3257`).
- **Config is strict.** The config schema has `additionalProperties: false` (`schemas/v1/config.schema.json`, and `BUILTIN_SCHEMAS["config"]` at `cli.py:78-118`). Adopters get their own copy of `schemas/v1/*.json` from `init` (`cli.py:727-728`), and `load_schema` prefers that local copy (`cli.py:390-401`). The one precedent for adding an optional config key is `workspace`: `load_schema` injects it into old local schemas (`cli.py:394-399`).
- **The document catalog is optional.** `.continuity/documents.json` and `docs/CONTINUITY_INDEX.md` are created by `continuity docs init`, not by `init`. Old validators ignore them (`docs/VERSIONING.md`, PCM-0018 entry).
- **`trackers.beads` does nothing.** It exists only in the config schema and in `init_repo`'s default (`cli.py:101-102`, `717`). No code reads it.

## Inventory of candidate pieces

Classification: **module** = versioned independently and installed into adopter files. **Core** = versioned with the CLI or protocol because it is code or a canonical object. **Out of scope** = not managed by this plan. Starting versions are proposals.

### Policy and guidance blocks

| Proposed id | Class | Start version | Where it lives today | Notes |
| --- | --- | --- | --- | --- |
| `continuity-records` | module | **1.2.0** (keeps its current stamp) | `cli.py:25-27`, `560`, `583`; `docs/CONTINUITY_RECORDS_POLICY.md` | Already stamped. Its paragraph needs start/end delimiters (legacy layout migration below). #99 proposes 1.3.0. |
| `github-progression` | module | 1.0.0 | `cli.py:28-42`, emitted in 6 files | Delimited, needs a stamp. Earlier unstamped texts become known legacy fingerprints. |
| `github-issue-lifecycle` | module | 1.0.0 | `GITHUB_ISSUE_LIFECYCLE_GUIDANCE` `cli.py:44-49`; HANDOFF (552), AGENTS (574), PR template (638) | Closing-keyword safeguard. Undelimited today. |
| `issue-log-format` | module (**first new one**) | 1.0.0 | Not in the repo. Proposed by #99 (`docs/ISSUE_LOG_FORMAT.md`, `ISSUE_LOG_FORMAT_POLICY_MARKER`) | #99 already specifies the target shape: stamp plus start/end block. |
| `workspace-guidance` | module | 1.0.0 | `workspace_policy_text` `cli.py:514-534` | Two variants chosen by `workspace.mode`. The variant is recorded in the stamp. |
| `document-discovery` | module | 1.0.0 | "Finding earlier project documents" paragraph in HANDOFF (558) and AGENTS (589) | Guidance for the catalog feature. |
| `agent-lifecycle` | module | 1.0.0 | `docs/AGENT_LIFECYCLE.md`; text only in static templates and PCM's own `AGENTS.md` | **Missing from `init` output today.** Whether to add it is a separate decision (decision 6). |
| `agent-facing-testing` | module | 1.0.0 | `docs/TESTING_POLICY.md`; text only in static templates | Same drift as `agent-lifecycle`. |
| Degraded-continuity and checkpoint paragraphs | core | follows CLI | HANDOFF (562-564), AGENTS (585-588) | They describe CLI commands, so they must match the installed CLI rather than drift from it independently. |

### Profiles

| Proposed id | Class | Start version | Where | Notes |
| --- | --- | --- | --- | --- |
| `profile:minimal` | module (bundle) | 1.0.0 | `init_repo` (695, 721-726); `templates/v1/minimal/profile.json` | A bundle lists module ids and default versions, plus skeleton files. After `init`, the skeleton files belong to the project. Only the blocks inside them are upgraded. |
| `profile:software` | module (bundle) | 1.0.0 | `init_repo` (729-731); `templates/v1/software/profile.json` (`extends: minimal`) | Adds AGENTS and README. |

### Optional features

| Feature | Class | Where | Notes |
| --- | --- | --- | --- |
| `trackers.github` | core feature, plus the guidance modules `github-progression` and `github-issue-lifecycle` | `validate_repo` (1467, 1537-1553), `issue verify` | Behaviour is code, so it can't be pinned apart from the CLI. The switch stays in config. |
| `trackers.beads` | out of scope | config only | No behaviour to version. Decision 7: leave it. |
| `workspace.mode` | core feature, plus the `workspace-guidance` module | `validate_workspace_layout` (1425), worktree commands | The config switch picks the guidance variant. |
| Document catalog | core feature, plus the `document-discovery` module | `docs` commands (1032-1308); `schemas/v1/documents.schema.json` | The catalog file is a protocol object, not a module. |
| Checkpoint receipts (`--receipt-repo` / `--receipt-issue`) | core | `cli.py:2481-2979` | CLI-only behaviour. The `pcm:receipt-v2` comment markers are receipt data, not module stamps. |
| GitHub templates (`--github-templates`) | module `github-templates` 1.0.0 | `github_issue_template`, `github_pr_template` | Whole-file templates that contain other modules' blocks. #99 adds `issue-log-format` headings to the issue template. |

### Everything else

| Piece | Class | Why |
| --- | --- | --- |
| Package/CLI version (`__init__.py`) | core | Stays the single package identity (`docs/VERSIONING.md`). |
| Protocol version and `continuity:project/current/task/checkpoint/context-pack` markers | core | Canonical objects. Protocol semver already covers them. |
| `schemas/v1/*.json` copied into adopters | core (protocol) | Versioned by protocol and schema id. Refreshing stale local copies is #109 (decision 8). |
| `templates/v1/**` static copies | out of scope as modules | Reference/test copies. Phase 5 regenerates them from the registry so they can't drift. |

This covers #100's minimum: 2 profiles, 6 optional features (4 required), 8 guidance pieces (3 required), and the templates. Each has a proposed id and starting version, or a reason it has none.

## Design

### What makes something a module

A module is a named piece of PCM guidance that PCM writes into adopter files and that can change on its own schedule. Each released version has a **manifest**:

| Field | Meaning |
| --- | --- |
| `id` | Lowercase kebab-case, unique, never reused (`issue-log-format`). Bundles use a `profile:` prefix. |
| `version` | Semver `MAJOR.MINOR.PATCH` for this module only. |
| `kind` | `policy` (guidance block), `templates` (whole-file templates) or `bundle` (profile). |
| `summary`, `doc` | One line, plus the PCM doc that defines it (for example `docs/CONTINUITY_RECORDS_POLICY.md`). |
| `compat.protocol` | Supported protocol versions as `{"min": "0.1.0-draft", "below": "0.2.0"}` (inclusive min, exclusive upper bound). |
| `compat.cli` | Lowest CLI that understands this manifest, for example `{"min": "0.6.0"}`. |
| `depends_on` | `{module id: {"min": ..., "below": ...}}`. Few and shallow by design. |
| `applies_to` | The profiles that install it by default. |
| `blocks` | Each owned block: the file role (`handoff`, `agents`, `project`, `readme`, `issue_template`, `pr_template`), the start/end markers, an `insert_after` anchor used when the block is newly added, the variant key if any (for example `workspace.mode`), and the sha256 of the canonical text for each variant. |
| `checks` | Validator check ids and their severity when the block is missing (`warning` by default, per #99). |
| `migrations` | How to reach this version from earlier ones. Declarative steps only (below). |
| `legacy_fingerprints` | Hashes of known pre-registry texts, harvested from git history, so old adopters are recognised rather than treated as hand-edited. |
| `changelog` | One line per version. |

The manifest describes and stamps text. It never runs code from the manifest.

### The stamp: generalizing the existing marker

Every module that writes text into a file stamps it with the **existing** `pcm:policy` marker format. No second marker family is added:

```
<!-- pcm:issue-log-format:start -->
<!-- pcm:policy {"id":"issue-log-format","policy_version":"1.0.0","protocol_version":"0.1.0-draft"} -->
...module text...
<!-- pcm:issue-log-format:end -->
```

- **Fields.** `id`, `policy_version` and `protocol_version` keep their current meaning. An optional `variant` field is added only where a module has variants (`workspace-guidance`: `"variant":"single-checkout"`). JSON key order doesn't matter when parsing. When writing, keys are sorted, which matches `_json` (`cli.py:346`).
- **Placement.** The stamp is the first line inside the block. For `continuity-records` the stamp sits above an undelimited paragraph today. That is the **legacy layout**, and it stays readable forever.
- **The stamp is the pin.** The version in a file's stamp is the version that file is on. `validate` only reads stamps. `upgrade` is the only thing that changes them. So there is no separate lockfile to keep in sync, and **every adopter carrying today's `continuity-records` 1.2.0 marker is already on the new system for that module**.

### Optional `modules` map in config: declaring intent

Stamps record what is installed. A project sometimes needs to record what it *wants*, so config gets an optional map:

```json
"modules": {
  "continuity-records": "1.2.0",
  "issue-log-format": "1.0.0",
  "agent-lifecycle": false
}
```

- **A version string** means the module is enabled and deliberately pinned. A newer bundled version is shown as an informational "update available" line, not a stale warning.
- **`false`** means the module is deliberately off. It is not reported as missing.
- **No map, or no entry for a module** means "implicit": the enabled set is the profile's default modules plus any stamps found. Stale and missing checks behave as #99 specifies. **All existing configs are in this state and stay valid unchanged.**
- **Conflicts.** If an entry disagrees with the stamps in the files, `validate` reports an error (`contradictory`).
- **Compatibility.** The new CLI injects `modules` into older local config schemas the same way it already injects `workspace` (`cli.py:394-399`). An **older** CLI will reject a config that contains the map (`additionalProperties: false`). So `init` and `upgrade` write the map only when asked (`--pin`), and the docs name the minimum CLI. Decision 1 keeps this: the map is written only with `--pin`.

### Registry: format and location

- **Location:** inside the package, `src/continuity/modules/`:
  - `registry.json`: an index of module ids to released versions;
  - `<id>/<version>/manifest.json`;
  - `<id>/<version>/<block>[.<variant>].md`: the canonical text.
- **Content:** the CLI ships **every released version** of each module, not only the latest. That is what lets it tell "untouched old version" from "hand-edited", and diff old → new offline.
- **Not in `schemas/v1/`**, although #100 suggests it. `init` copies `schemas/v1/` into every adopter and `load_schema` prefers the local copy, so a registry there would go stale inside each adopter. The manifest's JSON Schema lives in the package next to the registry.
- **One source of truth.** Generated templates (`handoff_template` and the others) read their block text from the registry's current versions, so `init` and `upgrade` can't disagree. Package-data configuration makes the files ship in the wheel and sdist, and `tests/package_smoke.py` proves the installed CLI sees them.
- **Local and offline only.** No network fetch and no third-party modules (both are #100 non-goals).

### Versioning rules (semver per module)

- **MAJOR:** a record that complied with the old version may no longer comply, or a block moves to a different file or heading and needs a manual step.
- **MINOR:** new guidance or sections that existing compliant records don't violate, or a new check added at warning severity.
- **PATCH:** wording clarified with the same meaning.
- **The three version lines are independent.** Module versions move separately from the package version and the protocol version. A CLI release that ships new module versions is a package MINOR, because `validate` output changes. Protocol changes only when canonical objects change. `docs/VERSIONING.md` gets a third section, "Module versions", saying this.
- **Pre-release protocol.** `0.1.0-draft` sorts below `0.1.0` under semver. Compat ranges therefore use explicit `min` / `below` bounds, and a comparator of about 40 lines is written in-house to keep zero runtime dependencies. There is no range mini-language.

### Status and resolution rules

For each module in the enabled set, `validate` reports one status:

| Status | Meaning | Severity |
| --- | --- | --- |
| `current` | Stamp equals the newest bundled version that is compatible, and the text matches its canonical hash. | ok |
| `pinned` | The config pins an older version on purpose. | info |
| `stale` | Stamp is older than the newest compatible bundled version, with no pin. | warning (as in #99) |
| `missing` | Enabled but no stamp in a file the module owns. | warning (as in #99; open question 4 of #99 still applies) |
| `modified` | Text inside the block doesn't match the canonical hash for its stamped version or any legacy fingerprint. | warning in `validate`; `upgrade` refuses the block |
| `contradictory` | Different versions across files, a malformed stamp, a start without an end, duplicate or nested blocks, or a disagreement with the config map. | error |
| `ahead` | Stamp is newer than anything this CLI bundles. | warning: "update the CLI" |
| `unknown` | A stamp id this CLI doesn't know. | warning |

Hashes are computed on normalized text: LF line endings and trailing whitespace stripped, so a Windows checkout with CRLF doesn't read as modified.

**Choosing the upgrade target** is deterministic, with no solver:

1. For each module, the candidate is the highest bundled version whose `compat.protocol` includes the project's `protocol_version`, whose `compat.cli` is satisfied, and that stays within the current MAJOR unless `--allow-major` is given.
2. Check every candidate's `depends_on` against the other candidates, or against installed versions for modules not being upgraded.
3. If anything fails, stop and name the module, the needed range and the available versions. Nothing is written. The graph is tiny, so there is no backtracking.

A target lower than the installed stamp is a downgrade. It is refused unless `--allow-downgrade` is given.

### `continuity upgrade`: user experience

```
continuity upgrade [--root .] [--module ID ...] [--to ID@VERSION] [--add ID]
                   [--apply] [--allow-major] [--allow-downgrade]
                   [--adopt-modified ID] [--pin]
```

- **Dry run by default.** Without `--apply`, it prints a plan and unified diffs of only the owned blocks, then exits 0 when the plan is safe and 1 when anything was refused. #100 sketches `--dry-run` as an opt-in; this makes it the default to match `init`'s never-surprise behaviour (decision 2).
- **Per module.** `--module` limits the run to the named modules. `--to` picks an exact version.
- **New modules are never added silently.** `--add issue-log-format` inserts its blocks at the manifest's `insert_after` anchor, or at end of file when the anchor is missing, and shows that in the diff.
- **Refusals.** Each refusal gets one clear line and a next step, and nothing is written:
  - the working tree is dirty (#100);
  - a block is `modified`, unless `--adopt-modified ID` is given, which accepts replacing the edited text after the diff is shown;
  - stamps are missing or contradictory;
  - a downgrade without `--allow-downgrade`, or crossing a MAJOR without `--allow-major`;
  - the CLI is too old or the protocol is incompatible;
  - a dependency is unmet;
  - a module id is unknown.
- **All or nothing.** All new file contents are computed first. They are written only if every step succeeds, the same way `init` preflights conflicts.
- **Only owned text changes.** Bytes outside owned blocks are copied through unchanged, so project edits outside blocks can never change.
- **Migration report.** `--apply` writes `.continuity/migrations/<UTC time>-upgrade.json` recording the CLI version, and for each module: from, to, files, and block hashes before and after. That meets the report requirement in `docs/VERSIONING.md` ("Migration rule"). It doesn't commit or push; the normal checkpoint flow does that.
- **Idempotent.** A second run after `--apply` reports "nothing to do" and writes nothing.

Example dry run (illustrative):

```
PLAN (dry run; use --apply to write)
  continuity-records   1.2.0 -> 1.3.0   HANDOFF.md, AGENTS.md   [wrap-legacy, replace-block]
  issue-log-format     (not installed)  skipped: add with --add issue-log-format
  github-progression   legacy#2 -> 1.0.0  PROJECT.md, HANDOFF.md, AGENTS.md, README.md  [stamp]
REFUSED
  workspace-guidance   AGENTS.md: block text was edited by hand (modified). Review the diff, then rerun with --adopt-modified workspace-guidance.
--- AGENTS.md (continuity-records)
+++ AGENTS.md (continuity-records)
@@ ...
```

### Migrations

Migrations are declarative steps in the manifest. The CLI implements a small fixed set:

- `replace-block`: the default. Swap the canonical old text for the canonical new text.
- `stamp`: add a stamp to a delimited block whose text matches a legacy fingerprint. This is used for `github-progression`.
- `wrap-legacy`: add start/end delimiters around a legacy-layout region. The region runs from the stamp line to the next `## ` heading, and must match a known fingerprint. This is used for `continuity-records`.
- `move-block`: move a block to another anchor.
- `manual`: print instructions and refuse to apply automatically. The module stays reported as stale until a person does the step and re-stamps it.

A MAJOR version with any `manual` step needs `--allow-major`, and still stops at the manual step.

### How `issue-log-format` 1.0.0 fits as the first new module

#99 already specifies exactly the shape this plan generalizes:

- a `pcm:policy` stamp with `id: issue-log-format`;
- `pcm:issue-log-format:start/end` delimiters;
- blocks in HANDOFF (both profiles), AGENTS (software) and the issue template;
- validator statuses missing (warning), contradictory (error) and stale (warning).

So its manifest is written first, from #99's merged text:

- `kind: policy`, `version: 1.0.0`, `compat.protocol` `{min: 0.1.0-draft, below: 0.2.0}`;
- `applies_to: [profile:minimal, profile:software]`;
- three blocks, each with an `insert_after` anchor after the `continuity-records` block;
- `depends_on` `github-progression` `{min: 1.0.0, below: 2.0.0}`, because its lineage section restates that requirement *(proposal)*.

`continuity-records` 1.3.0 (#99's proposed bump) would then depend on `issue-log-format` `{min: 1.0.0, below: 2.0.0}`, because it points to it.

#99's single-module validator check becomes the first instance of the generic status check. **#99's manual update path stays the documented path until `upgrade --apply` is released and tested** (#100 success criterion 5). The implementation must use the text #99's evaluation tested, or rerun the evaluation, as #99 itself requires.

### Migration path for existing projects

| Project state | What happens |
| --- | --- |
| Today's `continuity-records` 1.2.0 marker, no `modules` map (every current adopter) | Stays VALID. `validate` gains informational and warning lines only, and no new errors. `continuity-records` reads as `current` (or `stale` once 1.3.0 ships). Other modules read as `missing` or legacy until upgraded. |
| Unedited output from any earlier `init` | `upgrade` recognises the text through legacy fingerprints and offers `stamp` / `wrap-legacy` / `replace-block`. |
| Guidance edited inside a block (for example PCM's own `AGENTS.md` and `HANDOFF.md`, which are hand-written) | Reported as `modified`. `upgrade` refuses the block until someone reviews it and uses `--adopt-modified`. |
| No PCM markers at all (for example IRE today, per #99) | Nothing changes until that project's owner runs `upgrade --add` under its own issue. |
| Older CLI reading a project upgraded by a newer CLI | Stamps are plain HTML comments, so an older `validate` ignores them. It only fails if `--pin` wrote a `modules` map (see decision 1). |

The existing `workspace_mode` legacy-key refusal (`cli.py:1443-1451`) shows the pattern for real breaking changes. Nothing in this plan needs that.

## Phased rollout

Each phase becomes its own follow-up issue with its own acceptance, as #100 success criterion 4 requires. No implementation merges under #100.

### Phase 0: prerequisite, #99 lands

Issue: #99.

- **Gate:** #99's evaluation results are posted with every success criterion marked, and the `issue-log-format` module is merged (or #99 records that it was revised or dropped).
- **Measure:** the link to #99's results comment, and the merged PR. Nothing else starts before this.

### Phase 1: spike on a disposable fixture (not merged)

Issue: #104 (PCM-0030).

This is #100 success criterion 3 and tests H1 and H2.

- **Build:** a prototype registry for 3 modules (`continuity-records`, `github-progression`, `issue-log-format`; `github-issue-lifecycle` replaces `issue-log-format` if #99 was dropped), stamp parsing, status reporting, and an `upgrade` dry run.
- **Fixtures:** 3 layouts: fresh `init`; an adopter with project edits outside the blocks; an adopter with one hand-edited block. Plus contradictory cases: mismatched versions, a start without an end, malformed JSON.
- **Success conditions:**
  - the validator reports versions for at least 3 modules on every layout;
  - the dry run changes only owned blocks on all 3 layouts (byte-identical outside blocks);
  - 100% of hand-edited and contradictory cases are refused;
  - adding unrelated project text leaves the upgrade diff unchanged (metamorphic check);
  - the prototype is 300 lines of code or fewer outside tests (H1);
  - `tests/fixtures/valid-minimal` and PCM itself stay VALID.
- **Decision gate (owner):** continue to Phase 2, or stop at the smaller design ("current vs stale" per marker, no `upgrade`) if the spike shows that is enough.

### Phase 2: registry, stamps and read-only reporting

Issue: #105 (PCM-0031).

- **Build:** the in-package registry for the 3 spike modules, stamps added to generated output, and generated templates reading block text from the registry. `validate` gets the warning/info channel (reusing #99's) and per-module statuses. Also a read-only `continuity modules status` (list id, installed, bundled, status). Package MINOR.
- **Success conditions:**
  - generated `init` output is byte-identical to the registry's canonical text (parity test);
  - `validate` reports every enabled module on the fixtures and on PCM;
  - 0 new errors on existing fixtures and on a replay of historical `init` output;
  - wheel/sdist parity passes with the registry files present.

### Phase 3: `upgrade` dry run and refusals

Issue: #106 (PCM-0032).

- **Build:** planning, target resolution, diffs and every refusal case. No writes.
- **Success conditions:**
  - 100% of refusal fixtures are refused, with the expected message;
  - the metamorphic invariance holds across 20 generated unrelated edits;
  - the dry run never modifies the tree (checked by hashing the tree before and after);
  - each version downgrade or MAJOR crossing is refused without its flag.

### Phase 4: `upgrade --apply`, migrations and pins

Issue: #107 (PCM-0033).

- **Build:** all-or-nothing writes, the migration report, `stamp`, `wrap-legacy` and `replace-block`, `--add`, `--adopt-modified`, `--pin` and the config `modules` map. `docs/VERSIONING.md` and the existing-adopter update docs switch from manual to the command in this phase, not earlier.
- **Success conditions:**
  - on the 3 layouts, the result validates with every touched module `current`;
  - a second run is a no-op;
  - an injected write failure leaves every file unchanged;
  - the report records correct before and after hashes;
  - a differential check: an unedited legacy fixture upgraded to current matches a fresh `init` byte for byte inside owned blocks.

### Phase 5: remaining modules and ending the drift

Issue: #108 (PCM-0034).

- **Build:** register `github-issue-lifecycle`, `workspace-guidance`, `document-discovery`, `github-templates` and the two profiles. Regenerate `templates/v1/**` from the registry, or replace them with a parity test. Add `agent-lifecycle` and `agent-facing-testing` to `init` output as default modules (decision 6).
- **Success conditions:**
  - every inventory row marked "module" has a manifest;
  - a test fails if any static template differs from generated output;
  - the number of places the same guidance text is hand-maintained drops to 1 per module.

## Testing strategy

This follows `docs/TESTING_POLICY.md`: the lightest test that proves the claim.

- **Deterministic unit tests:**
  - the semver comparator and the `min` / `below` bounds, including `-draft` ordering;
  - stamp parsing (valid, malformed, duplicate, nested, start-without-end);
  - hash normalization (CRLF and trailing spaces);
  - target resolution and dependency errors.
- **Registry self-consistency test:**
  - every released version has a manifest and canonical text whose hash matches;
  - dependencies resolve and contain no cycles;
  - ids are unique;
  - the newest version of each module equals what generated templates emit.
- **Fixture tests:** the 3 layouts from #100 plus refusal cases (dirty tree, modified, contradictory, ahead, unknown, downgrade, major, CLI too old).
- **Metamorphic:** unrelated project edits don't change the diff, and `--apply` twice equals `--apply` once.
- **Differential against history:** fixtures produced by running `init` from earlier commits of `cli.py` (the git history has three `continuity-records` versions and two `github-progression` texts) must be recognised and upgraded to match a fresh `init` inside owned blocks.
- **Backward compatibility:** `tests/fixtures/valid-minimal` (no `workspace` key, no markers) and PCM's own checkout stay VALID in every phase. A config without `modules` validates under old and new CLIs.
- **Packaging:** `tests/package_smoke.py` also checks that the installed CLI lists the bundled registry.
- **No fresh-agent holdout is needed for the command itself**, which is deterministic. A holdout only makes sense if we later promise that agents will choose `upgrade` over hand edits. That is out of scope here.
- **CI:** everything runs in the existing `ci.yml` jobs: Ruff, MyPy, compileall, unittest on 3.11/3.12, `continuity validate`, build, and package parity. No new job.

## Mapping to #100's success conditions

| #100 success condition | Where this design meets it | Status |
| --- | --- | --- |
| 1. Written design covering registry schema, config shape, upgrade semantics, refusal cases, versioning rules, and migration of the current single marker; owner accepts it on #100 | [Module manifest](#what-makes-something-a-module), [Registry](#registry-format-and-location), [Config map](#optional-modules-map-in-config-declaring-intent), [upgrade UX](#continuity-upgrade-user-experience) (refusals listed), [Versioning](#versioning-rules-semver-per-module), [Stamp](#the-stamp-generalizing-the-existing-marker) plus [Migration path](#migration-path-for-existing-projects) (`continuity-records` marker stays valid; `wrap-legacy`) | Done: accepted by Alex 2026-09-24 ([Decisions](#decisions-accepted-by-alex-2026-09-24)). |
| 2. Inventory classifies every current piece (at least 2 profiles, 4 optional features, 3 policy/guidance blocks, templates) with proposed id and starting version | [Inventory](#inventory-of-candidate-pieces): 2 profiles, 6 features, 8 guidance pieces, templates, core items | Done in this doc |
| 3. Spike on a disposable fixture, not merged: validator reports at least 3 modules; dry run changes only owned blocks on 3 layouts; refuses 100% of hand-edited and contradictory cases | [Phase 1](#phase-1-spike-on-a-disposable-fixture-not-merged) with those exact thresholds, plus H1's 300-line bound | **Not started.** Tracked by #104, blocked on #99 (Phase 0). |
| 4. Implementation split into bounded follow-up issues, one per slice, each with its own acceptance; nothing merges under #100 | [Phases 2-5](#phased-rollout), each with measurable success conditions, one issue each | Filed: #104-#108 (plus #109 for decision 8), sub-issues of #100 |
| 5. Existing manual update path stays manual and documented until an upgrade command is implemented and tested | [Phase 4](#phase-4-upgrade---apply-migrations-and-pins) is the only phase that changes the docs; [issue-log-format section](#how-issue-log-format-100-fits-as-the-first-new-module) keeps #99's manual path | Built into the plan |
| H1 (at most 300 lines, at least 3 pieces, no template rewrite or protocol major) | Phase 1 condition; the stamp reuse avoids any template rewrite; the config map is optional, so no protocol major | Tested in the spike |
| H2 (marker-delimited blocks allow safe automated upgrades) | Owned-block-only writes, hash-based `modified` detection, metamorphic test | Tested in the spike and Phase 3 |
| Honest caveat (prefer a smaller design if enough) | Phase 1 decision gate | Built into the plan |

## Honest caveat

Modules add upkeep:

- every guidance edit needs a version bump, a canonical text file, a changelog line and possibly a migration;
- the registry must keep every old version's text.

That is worth it only if adopters really drift and really upgrade. Nobody has measured how many adopters are stale today (#100 calls this an inferred risk). If the Phase 1 spike shows that a per-marker "current vs stale" warning is enough, the right answer is to stop there and keep manual updates.

This plan also doesn't make features that live in code (GitHub authority, worktrees, receipts) independently versionable. They ship with the CLI, and pretending otherwise would add version numbers that mean nothing.

## Decisions (accepted by Alex 2026-09-24)

Alex accepted this design and the recommended answer to each open question. Where the draft gave no recommendation (6 and 7), the answer below is the author's judgment, which Alex accepted with the rest.

1. **Where pins live:** the optional `modules` map in `.continuity/config.json`. `init` and `upgrade` write it only with `--pin`. Stamps stay the real pin. New CLIs inject the key into older local schemas, like `workspace`. Implemented in phase 4 (#107).
2. **Dry run by default:** yes. `continuity upgrade` writes only with `--apply` (#106, #107).
3. **Dirty-tree rule:** refuse when **any** file is dirty, with no override at first (#106).
4. **Protocol version:** no bump. The optional `modules` map follows past practice for optional additions (`workspace`, recovery receipts, the document catalog), so the protocol stays `0.1.0-draft`. `docs/VERSIONING.md` is corrected to describe that practice (#107).
5. **`continuity-records` delimiters:** folded into #99's planned 1.3.0 bump, so adopters do one migration. If #99 lands without that bump, they ship as a 1.2.1 patch in phase 4 (#107).
6. **Agent-lifecycle and testing guidance:** yes, they become default modules in `init` output. PCM's tests already assume adopters carry them, but real `init` output doesn't. Existing adopters opt in with `upgrade --add`. Done in phase 5 (#108). *(Author's judgment.)*
7. **`trackers.beads`:** leave it unchanged. Removing a required config key would touch every adopter's config and schema for no behaviour gain. It stays out of scope, with no issue filed. *(Author's judgment.)*
8. **Stale local schemas:** a separate issue, because it is protocol maintenance, not module versioning: #109 (PCM-0035).
9. **Priority:** P3, after #99. Confirmed.

### Follow-up issues

| Phase | Issue | Blocked by |
| --- | --- | --- |
| 0 | #99 (PCM-0027): `issue-log-format` module and blind test | none |
| 1 | #104 (PCM-0030): spike on a disposable fixture, not merged | #99 |
| 2 | #105 (PCM-0031): registry, stamps and read-only status | #104 plus the owner's continue decision |
| 3 | #106 (PCM-0032): `upgrade` dry run and refusals | #105 |
| 4 | #107 (PCM-0033): `upgrade --apply`, migrations and pins | #106 |
| 5 | #108 (PCM-0034): remaining modules and ending template drift | #107 |
| Decision 8 | #109 (PCM-0035): refresh adopters' copied schemas | #107 |

## Non-goals

- No implementation under #100. This doc and the Phase 1 spike are the deliverables.
- No package publication, protocol major bump, plugin system, remote module download, or edits to adopter repositories.
- No change to #99's scope or its manual update path.
