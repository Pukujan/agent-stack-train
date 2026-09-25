# PCM-0050 research note — epistemic, bitemporal continuity records

Status: research input for owner decision; no normative change proposed here.
Date: 2026-09-25. Trigger: owner direction that PCM currently promotes prose into
"truth" — agent-filed tickets, self-verified claims, and passing self-written tests
are consumed downstream as ground truth without provenance, confidence, or
supersession state.

## 1. The problem, in owner terms

1. Where do adopter / potential-adopter tickets live? One append-only issue log with sub-issues?
2. Provenance and citation: does PCM already require enough that a reader can validate a claim, or is an agent's "I verified this" consumed as fact?
3. Should PCM's own issue log be treated as *epistemic* (what was believed, by whom, on what evidence, when) rather than *truth*?
4. Bitemporality: records should carry what-the-claim-is-valid-for vs when-it-was-recorded, plus superseded / superseded-by / what-changed / what-we-believed-at-the-time.
5. Ranking: does filer identity (GitHub ID, own-project vs external) set priority or trust? Do we keep recording who filed what?
6. Classification: feature / bug / missing-claim / decision-request — machine-readable, stable.
7. Pile-up control: how do logs stay navigable as append-only records grow, for PCM and all future adopters?
8. Does this actually improve multi-agent / multi-person collaboration, or add ceremony?

## 2. External research (observed sources)

### Bitemporal data model (Snodgrass et al.)

Two independent timelines per fact: **valid time** (when true in the modeled world) and **transaction time** (when the record was learned/stored). Queries can ask "what was true on date X" *and* "what did we believe on date X" — the two differ exactly in the correction/late-arrival cases PCM hits constantly (agent reports success; verification later fails). Transaction-time history is append-only: a correction creates a new version rather than rewriting the old one. Source: Snodgrass, "Resolution of time concepts in temporal databases" (Information Sciences 1994), <https://www.sciencedirect.com/science/article/pii/0020025594900590>; overviews: <https://en.wikipedia.org/wiki/Bitemporal_modeling>, <https://www2.cs.arizona.edu/~rts/pubs/TRmerged.pdf>.

Key design rule from the literature: NEVER collapse `occurred_at` and `recorded_at` into one timestamp unless genuinely identical — retroactive and late-arriving information breaks that assumption.

### Event sourcing + supersession

Append-only event log with `effective_from/effective_to` (valid time) and `recorded_at/recorded_by` (transaction time), plus explicit `supersedes` / `correction_of` links and `correlation_id`/`causation_id`. Event sourcing alone is NOT bitemporal: replay gives implied state, not what the system believed at each point. Supersession is not deletion: "this assertion no longer applies" preserves the old assertion as a historical record of a belief. This maps onto PCM's existing append-only checkpoint log + correction/supersession policy (AGENTS.md GitHub-owned progression: "Append correction/supersession evidence; never rewrite checkpoint history"). PCM already has transaction time (commit dates, request IDs, receipt keys); it is missing explicit valid time and per-claim epistemic status.

### W3C PROV (provenance)

PROV gives entity/activity/agent + attribution/derivation/delegation and bundles ("provenance of provenance"); PROV-AQ explicitly warns that provenance records themselves must be trusted/verified. PROV deliberately does NOT define confidence, truth, or epistemic status — those are domain extensions (statuses like Observed / Quoted / Inferred / Hypothesized / Verified / Disputed / Refuted / Retracted). Sources: <https://www.w3.org/TR/prov-primer/>, <https://www.w3.org/TR/prov-o/>, <https://www.w3.org/TR/prov-aq/>. PCM's evidence rule (observed result / repository state / external artifact / agent claim / inference) is already a five-level epistemic taxonomy in prose; PROV formalizes attribution. The missing piece is making the level machine-readable per claim instead of per-document.

### Independence of evidence

A recurring multi-agent failure in the literature: N agents repeating one agent's claim is one datum, not N votes. Any ranking or trust scheme must key on evidence independence class (original observation vs derived assertion), not actor count. Sources: Chapman, Blaustein & Elsaesser, "Provenance-Based Belief" (TaPP 2010), <https://www.mitre.org/news-insights/publication/provenance-based-belief> (HTTP 403 this session; content UNVERIFIED, cited by title/author); separately, Friedman, Rye, LaVergne, Thomsen, Allen & Tunis, "Provenance-Based Interpretation of Multi-Agent Information Analysis" (TaPP 2020), <https://www.usenix.org/system/files/tapp2020-paper-friedman.pdf>.

## 3. PCM current-state audit (observed in-repo)

| Question | Today | Gap |
|---|---|---|
| Provenance of claims | Evidence rule (AGENTS.md) demands 5-way classification; issue-log-format 1.1.0 demands "Observed facts vs interpretation" with inferences labelled | Prose-level only; no machine-readable field; nothing blocks a claim asserting "verified" without a linked command/CI run/artifact |
| Actor identity | Receipts record authenticated actor (#89); OWNER-06 refuses a receipt when actor is not an assignee (#96) | Issue *filers* are not recorded in any PCM projection; `gh` returns author.login for free but no PCM template/validator captures it |
| Bitemporality | Checkpoints are append-only (transaction time implicit); "as-of" language exists in AGENTS.md ("as-of status", "stale projections yield") | No valid-time field: nothing records *when the claimed fact was true* or *until when it was believed*; supersession is prose convention ("Append correction/supersession evidence") with no structured link |
| External/adopter tickets | TARGET_ADOPTION.md: adopters keep their own issue semantics; PCM issues live in the PCM repo only; #143 documents there is no supported creation path | No defined home for adopter-filed *feedback to PCM*; today it lands ad hoc (hades filed #142/#143 by hand directly into PCM's tracker — which worked, but only because hades read the format) |
| Classification | Labels exist on GitHub (unused: all recent issues have empty labels) | No taxonomy (bug/feature/missing-claim/decision-request), no enforcement |
| Pile-up | Issues #15–#143, many frozen/deferred; #110 explicitly "frozen research, no slice released" | No closeout/aging policy; no distinction between open-work, parked-decision, and historical-record issue |

## 4. Options considered (proposal labels; none exists unless built)

**O1 — Status quo + discipline.** Keep prose tiers; rely on writers. Cheapest; demonstrably failing: #142/#143 were hand-assembled, and this session has already seen agent claims (RESULT-0x series) that needed owner adjudication twice (OWNER-11, OWNER-12).

**O2 — Claim-ledger overlay (recommended research direction).** Introduce a small structured record type — the *claim* — embedded in issue logs/checkpoints as a fenced JSON block (`pcm:claim`): {id, about (issue/commit/doc), assertion, epistemic_status ∈ observed|repo-state|external|agent-claim|inferred, actor (GitHub login or agent id), recorded_at (transaction), valid_from/valid_to (valid time), evidence (command+exit, CI URL, commit SHA), supersedes/superseded_by, independence_class}. Validator (extend `continuity validate`/`issue verify`) checks: evidence present for `verified` claims; supersession links resolve; no claim marked observed without a reproducible command or artifact link. Prose stays primary; the ledger is the machine-checkable skeleton.

**O3 — Full bitemporal store.** Move task state into a SQLite bitemporal table (as OWNER-13's isolated harness prototyped for receipts). Strongest guarantees; heaviest; conflicts with "GitHub owns durable state" unless the store is a projection like CURRENT.md today. Treat as implementation detail of O2's validator, not as authority.

**O4 — Adopter ticket channel.** Define `docs/ADOPTER_FEEDBACK.md`: external adopters file into PCM's tracker with a third template tier (Core tier + `filer: <github-id>`, `adopter-project`, `classification`); PCM mirrors accepted items to its own issue log as decision-requests. This answers "where do their tickets live" without a parallel system, and gives ranking a provenance key (owner-vs-external-vs-agent is recorded, not inferred).

**Ranking/priority stance (inferred, for owner decision):** priority stays human-owned (labels/milestones on the owning issue); *trust* is separate and derives from epistemic_status + evidence + independence_class, never from filer identity alone. Recording GitHub ID (O2 `actor`, O4 `filer`) is required to make that auditable later, but identity must not auto-set trust — otherwise PCM encodes privilege where it should encode evidence.

**Pile-up control (O2 companion):** claims are cheap and append-only; issues are expensive and must age. Policy: every open issue gets `decision: pending|blocked|parked` in its identity block; parked items link a superseding record or are closed with the record retained (closing an issue never deletes its claims — bitemporal transaction history survives closure).

## 5. Multi-agent / multi-person collaboration — does it help?

Yes, conditionally (inferred): the failure modes PCM actually hit this month — two writers clobbering files, agents asserting completion that wasn't merged, owner reversing a design twice — are all *belief-desync* problems. Bitemporal claims make "what did we believe at the time, and on what" queryable, so a fresh session re-derives the disagreement instead of re-litigating it. The cost is one structured block per claim; the guard is that O2 never replaces prose, so a writer who ignores the ledger still produces a readable (if unvalidated) record.

## 6. Open questions for the owner decision issue

1. Is O2's `pcm:claim` block the right granularity (per-claim vs per-issue-tier)?
2. Does PCM require evidence links for `observed` claims at validation time, or warn-only for v1?
3. Adopter channel: O4 (PCM tracker with filer field) vs adopter-owned trackers + PCM-only decision-requests?
4. Do agent actors get stable identities (e.g. `astra/codex`, `hades/qwen`) recorded in claims, and who owns the alias registry?
5. Aging policy: which of #15/#30/#33/#35/#100/#110/#127/#128/#129 become `parked` with links under O2?

## 7. Next action

File the bounded decision research issue (owner-approved), record this note as its evidence, and let the owner select O1–O4 before any normative change. No SPEC/AGENTS edits in this slice.

## Addendum 2026-09-25 — delta over PCM-0015 prior art (advisory-driven; append-only)

This note was drafted without first running the mandated `continuity docs find` lookup. The advisor caught what that lookup should have surfaced: **PCM-0015 already designed most of O2.** Observed in merged history:

- `docs/plans/PCM-0015-implementation-plan.md` slice **S9 "scoped assertions"** (line 135): origin classes (user requirement / observation / external source / model proposal / inference), author/reviewer, evidence refs, independent assessment (supported/unknown/contradicted), freshness + supersession, "preserve historical observations", explicit anti-goals (no bulk extraction, no global truth score, stop if maintenance exceeds routine budget).
- `docs/research/PCM-0015-epistemic-context.md` "Epistemic labels for planning": Fact / Reported / Standard / External / Recommendation / Inference / Open taxonomy.
- `docs/research/PCM-0015-provenance.ttl`: a PROV-O record already using `pcm:epistemicStatus` (`user_requirement`, `prior_agent_proposal`, `observed_repo_fact`, `external_source`, …).

**Consequence for the owner decision:** O2 is not new design work — it is *adopting and completing S9*, which PCM-0015 deliberately deferred ("not part of the minimum path; defer them unless the S7-S8 trial reveals a specific failure they solve", plan line 21). The S7-S8 trials have since run (holdouts #63, #126); this session's belief-desync incidents are the candidate "specific failure" trigger S9 named. The decision on #144 should therefore be framed as: promote S9 as specified, plus only the genuine deltas below.

**Genuine deltas beyond S9 (new in this note):** (1) explicit **bitemporal** valid-time fields (`valid_from/valid_to`) — S9 has freshness/supersession but no valid-time interval; (2) **independence class** for the N-repeating-agents problem; (3) the **O4 adopter channel** with recorded filer identity; (4) **classification + pile-up aging** for issues; (5) the discovery finding below.

**Discovery defect (observed):** `continuity docs find "epistemic provenance bitemporal scoped assertions claims" --task PCM-0050` returned NO_MATCHES even after `git fetch`, while the same terms without `--task` match `pcm-0015-research`. Cause is by design (`search_document_catalog`, cli.py:1293-1294: a task filter restricts to records whose `tasks` array names the task, plus declared neighbors): a brand-new task's mandated lookup is structurally guaranteed to miss prior art until someone registers the link. Chicken-and-egg — the anti-duplication lookup cannot prevent duplication at exactly the moment duplication happens. Candidate fix for a follow-up slice: when the task-filtered set is empty, fall back to unfiltered matches labelled `TASK_UNLINKED`, or have the task-creation flow seed the query against the unfiltered catalog.

**Citation corrections (this addendum supersedes §2's original attribution; §2 line 38 has been rewritten in place to match):**
- The MITRE page originally cited as "Friedman et al., Provenance-Based Belief" is **Chapman, Blaustein & Elsaesser, "Provenance-Based Belief", TaPP 2010** (https://www.mitre.org/news-insights/publication/provenance-based-belief ; fetch returned HTTP 403 this session — content UNVERIFIED, cited by title/author only). The independence claim ("N reports derived from one source are one datum") traces to **this** work.
- The USENIX URL is a **different paper**: Friedman, Rye, LaVergne, Thomsen, Allen & Tunis, **"Provenance-Based Interpretation of Multi-Agent Information Analysis"**, TaPP 2020 (https://www.usenix.org/system/files/tapp2020-paper-friedman.pdf).
- Both are provenance-for-belief work; neither is the other.
