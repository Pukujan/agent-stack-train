# Observational Issue Ops

> **One repeatable issue log for the whole stack.** A single way to file, stamp, rate, and route a record of something observed or something broken — so a human working through an agent, and an agent acting on its own, write the same shape of record and any repository handles it the same way.

<p align="center">
  <img src="docs/assets/oio-hero-banner.jpg" alt="A designer and a companion gather loose notes from several project folders onto a single shared ledger." width="100%">
</p>

A multi-repository project can hold strong evidence and still lose the report. When each repository keeps its own issue form and its own copy of the rules, the same observation gets written down differently in every place, and a reader cannot tell which copy is authoritative.

Observational Issue Ops (OIO) is the one source for that protocol. It gives a human or an agent a single, repeatable way to file an **observational issue**, an **operational issue**, or a **proposal**, stamp who filed it, rate it, and follow it from first sighting to a decision.

## Why this exists

**Copied rules drift.** The same issue form, the same triage, and the same version pins get hand-copied into several repositories. Nothing forces the copies to agree, so they quietly diverge.

<p align="center">
  <img src="docs/assets/oio-problem-scattered.jpg" alt="A companion stands puzzled among several folders holding mismatched copies of one note, with no single shared ledger." width="100%">
</p>

The copies were also too narrow. They captured only "I saw something", never "something is broken right now" and never "an agent proposes this change" — and they never recorded *who or what filed the issue*, so a human's direct report and an agent's own proposal looked identical on the record. OIO removes the copy and widens the form: the rule lives in one place, and every repository points at it.

## What an issue is here

One canonical form, with a **type** field choosing between four kinds:

| Type | What it records |
| --- | --- |
| **observational** | Something someone saw — a fact, a symptom, a discrepancy — with provenance and citations. |
| **operational** | Something broken or degraded right now: an outage, a failed run, a blocked pipeline. |
| **proposal** | A proposed change. Every issue is a non-binding proposal; this type is for one whose main content *is* the change. |
| **incident** | An operational issue with a timeline and an impact, filed for the record while it is handled. |

## The filer stamp

Every issue carries a **required filer stamp**, machine-checked by triage. It answers two questions: who initiated the filing, and whose identity is on it.

| Origin | Meaning |
| --- | --- |
| `human-direct` | A human filed the issue themselves. |
| `human-via-agent` | A human directed an agent to file it; the human owns the intent. |
| `agent-initiated` | An agent filed it on its own initiative, without a human asking for this specific issue. |

The stamp also carries the filing identity — the human's handle when a human is involved, the agent's identity and session when an agent filed it, and the timestamp. Triage reads the stamp and flags a filing that does not state its origin.

## What you can make or use

| You want to | OIO gives you | Where it lives |
| --- | --- | --- |
| File anything the same way everywhere | The canonical issue form, with type and filer stamp | `.github/ISSUE_TEMPLATE/observational-issue.yml` |
| Have a filed issue labelled by type, filer, plane, and priority | The triage workflow | `.github/workflows/issue-triage.yml` |
| Understand the protocol before filing | The template's own field descriptions | the issue form itself |
| Point another repository at one source | A single repository to reference | this repository |

## How it works

Every record moves along the same short path, and the plane the reporter chooses sets the priority range the record can carry.

<p align="center">
  <img src="docs/assets/oio-loop-square.jpg" alt="A designer and companion trace one continuous loop of five cards on a shared workflow board." width="50%">
</p>

1. **Observe or hit a problem.** Someone notices something worth recording, or something is broken right now.
2. **File.** The reporter picks the issue type and the filer origin, states the record in plain language with provenance, reproducibility, and citations, and chooses a contributor plane — lead owner, approved collaborator, or community.
3. **Triage.** Automation reads the issue, stamps the type and filer origin, and applies the plane and priority labels, clamping the rating to the plane's range.
4. **Review.** The owner reads the proposal. Every issue is a proposal, not a mandate.
5. **Resolve.** The issue is answered, accepted, or closed, and the trail stays on the issue itself.

## How OIO separates from the rest of the stack

OIO exists separately because the issue log used to live inside the installer. When the install surface owned both the hot-loading and the coordination rules, installing it installed governance — the installer graded itself. OIO takes the governance out. The same reasoning applies to versions: a product repository must not certify its own siblings, so the certified version set lives in its own train repository.

| Repository | Owns | Does not own |
| --- | --- | --- |
| **OIO** (this repository) | The issue-log ticketing system: the form, the filer stamp, the triage, the intake contract, the bootstrap into any repository. | Product code, releases, version pins, narrative, execution continuity, the install surface. |
| **Continuity modules** | Execution continuity: tasks, checkpoints, push receipts, required PR gates. | Issue governance, narrative, versions. |
| **Narrative modules** | Narrative and style authority: writing routing, human-sounding writing, output naming, visual direction, image generation. | Issue governance, execution continuity, versions. |
| **Install surface** | The hot-loader and runtime safety that wires the continuity, narrative, and issue-log modules together. | Issue governance, narrative, execution continuity, versions. |
| **Train repository** | The certified version set of the stack — one place adopters read compatible versions from. | Everything else. |

An adopter pins the train once, consumes OIO's form once, and keeps its own issue history.

## Evidence and boundaries

Each claim below records what the evidence supports and what it leaves open.

| Claim | Status | Evidence | What it does not establish |
| --- | --- | --- | --- |
| The issue form carries an issue type and a required filer stamp, plus required provenance, reproducibility, citations, and priority. | shipped | `.github/ISSUE_TEMPLATE/observational-issue.yml` | That any adopter has switched to consuming it |
| Triage derives the type, filer origin, plane, and priority labels from a filed issue and flags an unstamped filing. | shipped | `.github/workflows/issue-triage.yml` | That the labels are meaningful without a reviewer |
| The certified version set moves to a dedicated train repository. | planned | [plan of record #226](https://github.com/Pukujan/project-continuity-modules/issues/226) | That the train repository exists yet |

## Boundaries

- Every issue filed under this protocol is a **non-binding proposal**, not a literal implementation mandate.
- OIO owns the protocol and its triage. It does **not** own any adopter's product code, issues, releases, or version pins.
- Adopters keep their own issue history. Moving a repository onto this source is a separate, owner-gated step.
- The protocol is deliberately small: a form, a filer stamp, a triage step, and a place to point.

## Try it

The smallest useful next action is to read the form and file one issue against it:

1. Open the issue form at `.github/ISSUE_TEMPLATE/observational-issue.yml`.
2. Read the field descriptions — they are the protocol in short.
3. File an issue on a repository that has adopted the form, and watch the type, filer, plane, and priority labels apply.

## Related work

- **Plan of record:** [Pukujan/project-continuity-modules#226](https://github.com/Pukujan/project-continuity-modules/issues/226) — the audit, the duplication map, the loose-file inventory, and the target folder tree for every repository in the stack.
