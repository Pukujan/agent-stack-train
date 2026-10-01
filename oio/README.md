# observational-issue-ops

The single upstream source for the **observational-issue protocol** shared across
the OIO / CGM / PCM / ACS / Octo stack.

## Why this repository exists

The same governance rule is currently copied into more than one repository:

- the 3-plane observational issue template,
- the triage workflow that derives `plane:*` and `priority:p*` labels, and
- the coordination rules (join-order roles, boss lease, GitHub claim queue).

Copies drift. This repository is the one place those rules live, so each adopter
consumes them instead of maintaining its own copy.

## What this repository owns

| Artifact | Path | Status |
|---|---|---|
| 3-plane observational issue template | `.github/ISSUE_TEMPLATE/observational-issue.yml` | seeded |
| Issue triage workflow | `.github/workflows/issue-triage.yml` | seeded |
| Release-train manifest (`stack-releases.json`) | `stack-releases.json` | planned |

## Status

Scaffold created 2026-10-01. The audit, the duplication map, the loose-file
inventory, and the target folder tree for all five repositories are recorded in
the plan of record: **[Pukujan/project-continuity-modules#226](https://github.com/Pukujan/project-continuity-modules/issues/226)**.

Adoption is deliberately not done yet. The adopter repositories switch to these
files only after the owner approves the migration phases in #226.

## Provenance

Seeded from the copies already in use, so behaviour is unchanged:

- template and triage workflow: `Pukujan/octo-database` (`.github/`)
- surrounding proposal: PCM #224, #225, #226; CGM #45; ACS #51, #52; Octo #54
