# Contributor mode — working on a repository you do not administer

**Status:** first slice, delivered under issue [#247](https://github.com/Pukujan/project-continuity-modules/issues/247). The issue is an explicit *proposal*; this document records what exists today and names what does not.

**Who this is for:** an agent or human using the stack's discipline — journal, checkpoints, receipts, naming, prose — on a repository they have **no right to administer**. An upstream open-source project, a client repository, a partner's closed-source repo. Every install surface in the stack (PCM's init templates, OIO's installer, ACS's hotload pack) writes *into* the target repository. That is correct for an owner or an adopter and impossible for a contributor.

## The three relationships

| Relationship | You administer the repo | The stack installs into it | Ledger |
| --- | --- | --- | --- |
| **owner** | yes | yes (dogfooded) | that repo's git |
| **adopter** | yes | yes (`continuity init`, OIO installer, ACS hotload) | that repo's git |
| **contributor** | **no** | **no — zero writes** | a private sidecar, keyed by `owner/repo` + upstream SHA |

Integration is a property of the **task**, not the checkout: the same dev root can hold a home repository on one task and a foreign target on the next. `continuity preflight --root <target>` keeps answering for owner/adopter targets; contributor mode is chosen per task and recorded in the task's descriptor (below), never inferred from the checkout.

## What exists in this slice

### 1. The leak guard — `continuity contributor guard --root <foreign-checkout>`

The control that turns "remember not to commit it" into an enforced rule. Exit 0 (`CLEAN`) when no stack-owned path appears in the foreign checkout's `git status`; exit 1 (`LEAK:` lines + `LEAKED:` count) when any does; exit 2 when the guard itself cannot run — a non-repository root or an unusable Git fails closed and is **never** reported clean.

Guarded path set (`continuity.contributor.STACK_PATHS`, derived from each component's own install manifest, not from memory):

| Component | Paths |
| --- | --- |
| PCM | `.continuity`, `schemas/v1`, `.github/ISSUE_TEMPLATE/task.md`, `.github/pull_request_template.md` |
| OIO | `.oio`, `.github/ISSUE_TEMPLATE/observational-issue.yml`, `.github/workflows/issue-triage.yml`, `AGENTS.md` (the OIO-managed block's file) |
| ACS | `.coord`, `stack-manifest.json` |
| CGM | `.content-system` |

Semantics:

- Staged, unstaged, and untracked entries all leak. Renames are judged by their destination path.
- A stack path inside the foreign repository's own `.gitignore` **still leaks** (reported as `ignored`): the working tree carries stack state regardless of upstream's ignore rules.
- Upstream's own committed stack paths do **not** leak — if upstream is itself an adopter, that is upstream's business; the guard polices the working tree, not history.
- Untracked directories are expanded (`--untracked-files=all`) so a leak names the actual files.

### 2. The task descriptor — `continuity contributor describe`

Records a contributor task's identity **on the owner's side of the boundary**, as a small JSON document (`contributor.json`, schema `project-continuity.contributor.v1`) written to a store root you name — in real use the task's private sidecar checkout, never the foreign repository:

```bash
continuity contributor describe \
  --root <sidecar-or-helper-root> \
  --foreign-root <foreign-checkout> \
  --repo upstream/project \
  --anchor-sha <full 40-char upstream commit or PR-head SHA> \
  --anchor pr \
  --sidecar <private sidecar location>
```

Fields, exactly five: `schema`, `repository` (`owner/name`), `anchor_kind` (`pr` | `commit`), `anchor_sha` (full 40-hex), `sidecar`. The upstream SHA is the **anchor** — the one-way link: the sidecar references upstream; upstream never references the sidecar. Reading it back (`continuity.cli.load_contributor_descriptor`) fails closed on missing, malformed, partial, or unknown-schema documents rather than resolving to a plausible-looking stale record. The write is refused when the store root is inside the guarded foreign checkout — that is exactly the leak the guard exists to prevent — and refuses to overwrite differing existing content, like `continuity init`.

## What does not exist yet (open under #247)

- **The private sidecar repository itself.** Where journal, checkpoint, and receipt state for a contributor task actually lives, and how it is keyed per task (`owner/repo` + SHA).
- **Journal/checkpoint/receipt storage inside the sidecar** — contributor tasks currently cannot run `continuity checkpoint` against a sidecar.
- **The coordination database** (atomic lease/claim state) and the **cross-repo index** ("what am I working on upstream, across all targets, right now").
- **Guard integration into checkpoint/publish flows** — today the guard is a command you run; it does not yet refuse a push on its own.
- **The OIO sub-gap**: where an observational issue *about* a foreign repository is filed (the owner's private tracker or sidecar — never the upstream tracker).
- **The adopter-mandate qualifier**: "mandatory for every PCM adopter" in `docs/TARGET_ADOPTION.md` still reads as unscoped; qualifying it to owner/adopter repositories is a governance change to be decided explicitly, not inherited from this mode.

## Rules that hold in contributor mode

- Upstream's standards — issue template, commit conventions, PR format, CI, review — govern anything crossing into their repository, per pull request. The stack's prose and continuity discipline apply on the owner's side of the boundary and to the private journal only.
- A sidecar record is the record of the *work*, never the governance of the *decision*: upstream's PR review and maintainer decision stay authoritative.
- Contributor mode is a different storage location, not an exemption from discipline.
