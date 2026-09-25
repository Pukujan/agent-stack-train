# TASK-PCM-0050 — Epistemic bitemporal records decision

<!-- continuity:task {"acceptance": ["Owner selects O1/O2/O3/O4 (or combination) for claim provenance, bitemporal supersession, actor identity, classification, and adopter ticket placement, recorded on #144.", "The five open questions in docs/research/PCM-0050-epistemic-bitemporal-records.md receive a recorded answer or explicit deferral.", "Follow-up implementation issues filed per selection; this task closes as the decision record."], "depends_on": [], "goal": "Decide PCM's epistemic/bitemporal record model from researched options; no normative change in this slice.", "id": "PCM-0050", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/144", "next_action": "Owner reads the research note and answers the five open questions on #144; implementation slices fan out only after that.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "Prose records are consumed as ground truth; without per-claim provenance, valid/transaction time and supersession links, fresh sessions re-litigate settled disagreements."} -->

- Status: active (research delivered; awaiting owner decision)
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none; related #142/#143 (intake gaps that motivated this research), #67 (actor identity precedent), #137 (evidence-vs-claim holdouts)

## Checkpoint log

### 2026-09-25 — research delivered

Completed: external research (Snodgrass bitemporal model; event-sourcing supersession; W3C PROV/PROV-AQ; MITRE provenance-based belief — all cited in note); in-repo audit of claim/provenance/supersession/identity/classification/pile-up handling; four options O1-O4 with a recommended O2+O4 stance; five open questions for the owner.

Evidence: docs/research/PCM-0050-epistemic-bitemporal-records.md at this commit; issue #144 body.

Decisions: trust derives from epistemic status + evidence + independence class, never filer identity alone; GitHub ID recorded for auditability, not ranking.

Blocked/uncertain: owner decision pending; no SPEC/AGENTS/template edits authorized.

Next: owner answers the five open questions on #144.

## Handoff

Read PROJECT -> CURRENT -> this task -> #144 -> docs/research/PCM-0050-epistemic-bitemporal-records.md. Decision slice only.
