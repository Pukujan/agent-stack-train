# Observational issue delegation and the stack release-train pin

<!-- pcm:policy {"id":"observational-issue-delegation","policy_version":"1.0.0","protocol_version":"0.1.0-draft"} -->

Two problems are easy to confuse, and keeping them apart is the point of this document. PCM keeps a project's **execution continuity**: what the work is, where it stands, and what the last session proved. A separate repository, [`Pukujan/observational-issue-ops`](https://github.com/Pukujan/observational-issue-ops) (OIO), owns the **diagnostic problem space**: the human observational tickets that describe a problem before anyone has accepted it as work.

This record states the boundary, PCM's pinned role in the stack release train, and where the superseded in-PCM proposal went. It is PCM's answer to [issue #225](https://github.com/Pukujan/project-continuity-modules/issues/225).

## The boundary

| Problem space | Owner | What it covers |
| --- | --- | --- |
| Execution continuity | **PCM** (this repository) | Task creation (`continuity task new`), checkpoint progression (`CURRENT.md`, `TASK-*.md`), immutable push receipts, and required pull-request gates. |
| Diagnostic problem space | **OIO** ([observational-issue-ops](https://github.com/Pukujan/observational-issue-ops)) | The human observational-issue protocol proposed in [#224](https://github.com/Pukujan/project-continuity-modules/issues/224): the 3-plane priority rubric (Owner P1–P20, Collaborator P20–P40, Community P40–P100), its non-binding proposals, the canonical GitHub Issue Form, and the triage automation that stamps and routes them. |

Three consequences follow, and they are the whole reason for the split:

- PCM does **not** vendor, copy, or maintain the observational-issue GitHub Issue Form or the 3-plane triage workflow. OIO is the single upstream source for both. A second copy inside PCM would drift and become a competing source of truth, which is exactly the failure OIO exists to remove.
- PCM's own [`.github/ISSUE_TEMPLATE/task.md`](../.github/ISSUE_TEMPLATE/task.md) is PCM's **task** template — the form for bounded execution work — and stays PCM's. It is not the observational-issue form and does not overlap it.
- When an OIO observational issue is ratified into accepted work, PCM generates the repository task projection and links it to the leaf issue. When the work merges, PCM's push receipt references the original OIO ticket. PCM never has to parse or mutate OIO's issue-form YAML.

## PCM's role in the stack release train

The stack's certified version set lives in one place. [`Pukujan/agent-stack-train`](https://github.com/Pukujan/agent-stack-train) publishes `stack-releases.json`, and every repository that ships with the stack pins that train once in its own `stack-manifest.json` instead of hand-copying component versions into several files. PCM is certified as a component of train `2026-10-01`; OIO and PCM's other siblings are adopters of the same train.

PCM keeps **no copy** of the certified set. The block below is PCM's own checked-in record of the pin that names *this* repository. `tests/test_observational_issue_delegation.py` checks it against PCM's own version sources, offline, with no network access.

<!-- pcm:stack-release-train:start -->
```json
{
  "release_train": "2026-10-01",
  "train_publisher": "https://github.com/Pukujan/agent-stack-train",
  "train_source": "stack-releases.json",
  "component": "project-continuity-modules",
  "version": "0.6.0",
  "cli": "0.6.0",
  "protocol_version": "0.1.0-draft",
  "verified_commit": "4e2385474b4af9249ca009cbdcb38c4498932475",
  "verified_commit_subject": "Mandatory adopter enforcement: gates required check + docs (Refs #211) (#212)",
  "as_of": "2026-10-02"
}
```
<!-- pcm:stack-release-train:end -->

`verified_commit` is the commit this repository resolves for the pin, and `verified_commit_subject` is that commit's message, so the check can confirm the pin names the revision it claims to.

### Where the train is published (as of 2026-10-02)

[Issue #225](https://github.com/Pukujan/project-continuity-modules/issues/225) described the release train as "published by OIO (`stack-releases.json`)". That is no longer where it lives. OIO commit [`2a836a5`](https://github.com/Pukujan/observational-issue-ops/commit/2a836a56597b413f545f5e8375990fb65db8f3bd) (2026-10-02) moved the certified set out of OIO into [`Pukujan/agent-stack-train`](https://github.com/Pukujan/agent-stack-train), and OIO is now an adopter whose `stack-manifest.json` points its `source` at that repository. Both files pin `project-continuity-modules` at the same commit, `4e2385474b4af9249ca009cbdcb38c4498932475`.

This is recorded as an **observed** fact with the moving commit linked, because a delegation record must not keep restating a publisher claim after the publisher has changed.

## Redirect of #224

[Issue #224](https://github.com/Pukujan/project-continuity-modules/issues/224) proposed drafting the 3-plane observational-issue protocol **inside PCM** — a PCM issue form plus a PCM triage workflow. That proposal is **superseded**: the protocol's implementation vehicle is OIO, as recorded on [#225](https://github.com/Pukujan/project-continuity-modules/issues/225). No part of the 3-plane protocol is implemented in PCM, and none should be added here. #224 stays open only as provenance for the OIO protocol; it is not a PCM implementation mandate.

## What PCM deliberately does not do

- No `observational-issue.yml` (or equivalent) Issue Form under `.github/ISSUE_TEMPLATE/`. Only PCM's own `task.md` lives there.
- No `issue-triage.yml` (or equivalent) 3-plane triage workflow under `.github/workflows/`.
- No copy of the priority rubric, the plane ranges, or the triage labels.
- No vendored copy of the certified release train or of any adopter's `stack-manifest.json`.

`tests/test_observational_issue_delegation.py` checks the first two, so the boundary is enforced rather than merely stated.

## Related records

- Leaf owning issue: [#225](https://github.com/Pukujan/project-continuity-modules/issues/225) (this boundary and the release-train pin); parent: none.
- Superseded proposal: [#224](https://github.com/Pukujan/project-continuity-modules/issues/224) (3-plane protocol, now owned by OIO).
- Plan of record for the split: [#226](https://github.com/Pukujan/project-continuity-modules/issues/226).
- Upstream protocol owner: [`Pukujan/observational-issue-ops`](https://github.com/Pukujan/observational-issue-ops) — the issue form, the filer stamp, and the triage.
- Train publisher: [`Pukujan/agent-stack-train`](https://github.com/Pukujan/agent-stack-train) — `stack-releases.json` (the certified version set) and `stack-manifest.schema.json`.
- PCM side: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) (ownership model), [`SPEC.md`](../SPEC.md) §10 (implementation boundary), [`docs/ISSUE_LOG_FORMAT.md`](ISSUE_LOG_FORMAT.md) (how PCM writes issue records).

## Changelog

- **1.0.0 (2026-10-01):** initial record. Establishes the PCM/OIO boundary for [#225](https://github.com/Pukujan/project-continuity-modules/issues/225), records PCM's release-train pin, and redirects [#224](https://github.com/Pukujan/project-continuity-modules/issues/224) to OIO.
