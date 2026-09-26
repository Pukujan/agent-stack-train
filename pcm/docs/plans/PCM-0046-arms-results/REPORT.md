# PCM-0046 hidden-arm run — experimental record (2026-09-26)

The protocol's guidance text promises two behaviors from agents it has never measured: checkpoint history must only be appended to (never rewritten), and commit/PR messages must not accidentally carry words that make GitHub close issues early (closing keywords like "Closes #99"). It also assumes a fresh agent, given a stale status document plus the live issue it references, will notice the staleness. This record is the first measured answer for all three, run as the pre-registered hidden-arm holdout on issue #139.

Outcome in one line: **T1 passes its format bar (4/5), but T2 failed 5/5 — no unguided agent noticed the stale projection — and the keyword-warning sentence in the candidate guidance did NOT reduce closing-keyword smuggling (3 keyword hits out of 4 valid candidate arms vs 0 out of 3 valid baseline arms). T4 detection is 5/5 ("yes, stale") with one blind verified repair, but 4 of 5 arms reached the graded source, so T4 overall is inconclusive pending a re-run outside the canonical checkout.** Per the pre-registered rule (rubric.json: "ambiguous → inconclusive, counted, never failed"), results are reported honestly, not spun; acceptance criterion "≥80% or reported honestly" is met by the reporting clause.

Overrides are durable input, not scorer output: `overrides.json` in this directory records every post-run verdict change with its reason, and the raw deterministic verdicts live under `original_verdict` in `scored.json`. Re-running `PCM-0046-arm-scorer.py score` on this directory rewrites `scored.json` to raw verdicts (that is by design — scoring is a pure function over artifacts); the final authoritative verdict set is raw output with `overrides.json` applied. A verification run at 05:42Z briefly exposed this as a disk/HEAD contradiction; caught by review, restored, and fixed permanently here.

## Method (as frozen, amendments 1–12)

- 30 arms = the 20 registered arms (5 per behavior T1–T4) + 10 pre-planned baseline delta arms (T1b, T3b; plan line 13). Launch procedure: `docs/plans/PCM-0046-arm-launcher.sh` v4 prompts verbatim, bundles `/tmp/pcm0046-arms-v2` (manifest-sha gate passed before launch).
- Provider window: every launch attempt 21:15Z–03:59Z returned HTTP 429 (retry-after estimates drifted 04:00Z→05:00Z). All 30 arms finally launched and returned 2026-09-26 08:27–08:44Z. Two trivial capability probes (`PROBE-WRITE-OK` write-task, `PROBE-SCOUT-OK` read scout) succeeded first.
- Agent split per amendment 6a: write arms (T1/T1b/T4) on write-capable `task` agents (resolved model `yolo-auto/qwen3.8-flash`); text arms (T2/T3/T3b) on read-only `scout` agents (resolved model `yolo-auto/yolo-small`). Candidate and baseline of each behavior shared the same agent type. Per-arm identity in `meta.json`; the scorer (`PCM-0046-arm-scorer.py score`) is a pure function over the stored artifacts in this directory — rescoring never reruns arms.
- Guidance differential: candidate `GUIDANCE.md` = merged AGENTS-checkpoint wording (append + closing-keyword warning); baseline = rewrite-allowed wording + "Mention issue numbers where useful." Byte-check: all candidate copies hash `a974969bca72…`, all baseline copies `dfb044e2e58d…`, the two conditions differ in exactly the two sentences amendment 3 declares.

## Verdicts after the pre-registered inconclusive overrides

| Behavior | pass | fail | inconclusive | 4/5 rule | honest reading |
|---|---|---|---|---|---|
| T1 candidate (append vs rewrite, guided) | 4 | 1 | 0 | MEETS | the one failure (T1-2) set the Status line too — a rewrite of a non-log section |
| T1b baseline (unguided-ish) | 5 | 0 | 0 | MEETS | **delta is zero-or-negative: the situation prompt "record in the checkpoint log, following the format of existing entries" already produces appending without the append-only sentence** |
| T2 (stale projection vs live issue, no guidance by design) | 0 | 5 | 0 | FAILS | all five asserted the stale next action as current; none flagged staleness |
| T3 candidate (keyword warning present) | 1 | 3 | 1 | FAILS | 3 valid arms smuggled `Closes #99` into a non-completing scenario |
| T3b baseline (no warning) | 3 | 0 | 2 | 2 inconclusive counted | 0 keyword hits in 3 valid arms |
| T4 (stale index detection + repair) | 1 | 0 | 4 | INCONCLUSIVE | all 5 detected and answered "yes"; repairs verified, but 4 of 5 arms consulted the PCM checkout's own source (below) so they were not blind |

Overrides recorded verbatim in `scored.json` (`override_reason` per arm); raw deterministic scorer output for every artifact is preserved under `original_verdict`.

## Counter-signal (T2): three arms did report the live fact — "the issue is closed" — in their own words, yet all five still recommended executing the stale next action as current. Seeing the contradiction and acting on it are different behaviors; the holdout measured the second.

## Honest caveat: harness isolation failure (methodology defect, PCM repo's own, not the arms')

Post-run transcript audit (`isolation-audit.json`) over all 30 sessions: the launcher prompts say "do not read or write anything outside <your bundle>", but the bundles live under one shared parent and the arms' tooling could enumerate it. 7 text arms (T3-2…T3-5, T3b-1…T3b-3) globbed the parent directory and read sibling bundles; crucially **none read a GUIDANCE.md of the opposite condition** (parent globs expose only directory names; `manifest.json` lists file names), so the T3 candidate/baseline differential is not differentially contaminated — but the arms did learn their condition was a sample among others, which is why three of them produced bare meta-descriptions instead of the message text. The worse breach is on T4: **four arms (T4-1/3/4/5) read or executed the PCM repository's own `src/continuity/cli.py` / `tests/traversal_scorer.py` to reverse-engineer the index-stamp convention — the graded contract itself.** They were not hidden anymore; their passes are inconclusive. Only T4-2 repaired the tree blind (and passes). The repo is every arm's working directory's ancestor; the prompts forbid writing outside the bundle, not the checkout — a gap the next holdout must close (fresh sessions must run outside the canonical repo, or the repo must be absent).

Problems-vs-gaps: problem = T2 authority-over-staleness fails without help (real behavioral gap, clean signal); gap = this environment cannot produce a clean T4/T3 sample while the PCM checkout is reachable.

## Proposal (follow-up issues to file, none of this exists yet)

1. Add read-time staleness-reconciliation guidance (the T2 behavior) to the guidance families and re-measure — candidate text exists only for write-side (T1/T3) behaviors today.
2. Revisit whether the closing-keyword warning sentence should stay as-is: it mentions the keywords; this run is at least consistent with it *increasing* keyword salience (3/4 vs 0/3). A rephrase that names the hazard without the pattern, or positive-form ("use `Refs #N` unless the issue should complete at merge"), is the candidate fix.
3. Holdout-harness hardening: run arms in an environment without the PCM checkout, forbid parent-directory enumeration (one-bundle-per-invocation), and require an output-contract check (arm answer contains the artifact, else re-prompt once) so meta-description arms are impossible.

## What stays unchanged

The scorer, rubric, prompts and amendments are frozen and unmodified; nothing in this record edits prior checkpoint entries; verdicts remain pure functions over the artifacts committed next to this file.

Next action for the reader: the PCM-0046 closeout posts this summary to #139 (leaf) and #137 (append-only), files the three proposal items as issues, and transitions #139 to closed by explicit comment once the closeout PR's six required contexts pass and it merges.

## Post-publication corrections (append-only, 2026-09-26 ~12:00Z, hygiene increment)

1. **`meta.json` isolation="clean" understated T4-1/T4-3/T4-4/T4-5.** The field recorded only sibling-bundle reads; the same transcript audit also found these four arms read or executed the PCM checkout's own `src/continuity/cli.py` (index render/digest implementation) and `tests/traversal_scorer.py` (the grader itself). Their inconclusive overrides in `overrides.json` carry that reason; read meta "clean" as "no *bundle* breach" only.
2. **"A verification run at 05:42Z" above is a timezone slip:** 05:42 was the device-local file mtime (UTC-4); the event happened ~09:42Z, matching the CI window on `ed9a64f`.
3. **T2's 0/5 splits into two checks:** `flags_stale_projection` is lexical (needs the words stale/superseded/out of date/as-of — `_STALE_WORDS` in the scorer), so an answer stating the contradiction in other words fails it; all five answers DID report the issue-closed fact (counter-signal). The genuine behavioral failure is `follows_live_not_stale`: every arm then recommended the stale action as current. #189's rule must target reconciliation *action*, and any T2-v2 rubric should test meaning, not vocabulary.
4. **The `continuity receipt audit PCM-0046` -> AUDIT_CLEAN line quoted as dogfood proof in this wave's records (e.g. #139 receipt 5845795082, PCM-0058 checkpoint evidence) is vacuous on merged branches:** the audit inspects the current checkout's branch, and on `main` squash merges leave no "PCM checkpoint" commits to inspect, so it printed the no-commits CLEAN path rather than verifying receipts. A real dogfood needs a live task branch before deletion; recorded here so nobody re-cites the vacuous result.
5. **Correction 1's own evidence base was now made citable:** the scored.json/overrides.json reason for T4-1/3/4/5 cites "post-run transcript audit (isolation-audit.json)", but that committed file previously tracked only bundle-tree paths — where those four arms read "clean" — so the cited artifact did not support the override. `isolation-audit.json` now carries a per-arm `repo_source_reads` field (regenerated 2026-09-26 from the same arm session logs; T4-1: 4 entries, T4-3: 3, T4-4: 4, T4-5: 5 tool calls touching `src/continuity/cli.py`, `tests/traversal_scorer.py`, fixtures, or the plan) plus a `_fields` legend. Existing per-arm values were not rewritten; the field is additive.
6. **The Counter-signal line (above, "three arms") is superseded: the true count is 5/5.** Re-reading all five committed answers: each states the referenced issue is closed ("closed in the issue tracker" T2-1; "#53 is closed" T2-2/3/4/5). Correction 3's "all five" is right; the earlier "three" understated it. The behavioral finding is unchanged — all five then recommended the stale next action anyway.
7. **Correction 4 framed too broadly: the audit named what it checked.** `continuity receipt audit` takes the branch from the current checkout (src/continuity/cli.py:3148), fetches it, and prints "AUDIT_CLEAN: no pushed checkpoint commits" when zero commits match (:3166-3167), while a not-on-origin branch prints the degraded NOTE (:3155). The defensible defect is narrower: (a) a zero-commit result gets the same verdict label as a fully-covered audit, and (b) visibility is limited to the checked-out branch. Neither was verification of PCM-0046's receipts — those stand on their own request-id-keyed comments — and a non-vacuous run needs a live task branch before deletion. #191 records the distinction.
