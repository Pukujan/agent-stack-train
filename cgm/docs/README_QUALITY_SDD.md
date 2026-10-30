# System design: story spine and evidence lineage

Status: contract proposal for Content Generation Modules `0.4.0`.

## Agent workflow

1. **Confirm the target and task.** Read its instructions, current README, project brief, design records, tests, examples, tracking issue or handoff, visual adapter, and relevant prior reviewed outputs. Record the target repository and exact inspected revision.
2. **Build the evidence map.** Separate repository facts, user observations, owner decisions, external sources, experimental results, inferences, hypotheses, and unknowns. Give each source a stable ID and a precise locator.
3. **Draft the story spine.** Record the primary reader and job, the triggering situation, friction, consequence, desired outcome, project response, plain-language mechanism, evidence boundary, and next action.
4. **Choose the reader path.** Put the main story first. Add a distinct developer/researcher path when those readers need commands, architecture, datasets, or reproducibility details.
5. **Write and cite.** Explain the problem with a concrete repository-grounded example. Introduce the project's response and mechanism after the reason to care. Place direct citations beside material factual claims; use a compact evidence section for deeper verification.
6. **Apply the target's visual contract.** Keep the target's identity and the existing CGM image-generation/use rules. Visuals explain the same story; they do not substitute for the prose or its evidence.
7. **Review and validate.** Run the deterministic contract, the heading-and-bold scan, the reader tasks, source-resolution checks, image checks, and the human review. Label unresolved evidence plainly.

## Reader story model

Use this causal chain as the default, adapting headings to the target rather than copying fixed text:

```text
reader and job
  -> recognizable moment
  -> friction or failure
  -> consequence for the person or work
  -> useful outcome the project offers
  -> plain-language mechanism
  -> evidence, current status, and limits
  -> smallest useful next action
```

Each link answers a different reader question. A generic category or a “Why this exists” heading alone does not establish that the chain is present. At least one concrete example should show how the situation unfolds; keep examples faithful to target evidence and mark hypothetical examples as hypothetical.

## Claim evidence record

Keep CGM's existing audience/problem/solution/mechanism/boundaries story inputs and existing `claim`, `source`, and `status` evidence fields. Project-brief v2 adds bounded explanations and time lineage to each material claim:

- `supports`: one plain-language sentence explaining what the cited evidence actually establishes;
- `limits`: one plain-language sentence explaining what it does not establish;
- `source_revision`: a precise, reproducible source identity;
- `recorded_at`: the timezone-aware time this evidence record was entered or superseded.

For time-bound facts, add optional `valid_time.start` and `valid_time.end` bounds (either endpoint may be open). This is valid time: when the claim applies. `recorded_at` is transaction time: when the repository recorded this version of the claim. Keep it distinct from `observed_at`, `published_at`, and `accessed_at`, which describe source events. Record corrections as a new issue/PR/commit event; do not silently rewrite historical claims. The GitHub issue owns the change, and PR plus commit history carries its operational record, so CGM does not create a parallel issue database.

For a repository source, `source_revision` identifies `owner/repository`, a full commit ID, path, and line range or stable heading/record locator, plus a direct immutable permalink. For external material or an experiment result, identify the direct URL and access date; experiment results also require a run or artifact locator. For an owner observation or decision, cite an appropriate durable record where one exists; never copy private conversation text into a public output. A hash can verify source bytes, but a hash alone is not a readable citation.

Keep source provenance and claim truth separate. If the source only qualifies the claim, record the qualification. If sources conflict or cannot be recovered, preserve that fact and weaken the claim or mark it unknown. Do not cite the claim's own generated prose as proof of the underlying product behavior.

## Public copy and technical depth

The first screen explains the human situation and value in ordinary language. Follow CGM's current narrative order with a concrete, source-grounded example: what a person is trying to do, where the current path fails, what consequence follows, and how the project helps. The next sections answer what the project does, how the useful path works, and what the evidence establishes and leaves open. Detailed setup, schemas, architecture, model settings, and research protocol follow where they help a developer reproduce or extend the work.

Use separate “try it” and “build/reproduce it” paths when one combined path would burden the primary reader. Keep each path verb-first and link directly to its evidence or guide.

## Visual contract boundary

The target repository owns its visual identity. The existing CGM `docs/IMAGE_GUIDE.md`, `docs/BRAND_DIRECTION.md`, image-generation instructions, exact in-image title/subtitle rules, narrative raster requirements, prompt records, and reviewed assets remain unchanged by this story/evidence upgrade. The target's visual adapter determines whether CGM's own anime-inspired human-and-companion direction applies; never copy it into a target with a different accepted brand.

## Provenance model

Keep the model small and interoperable: a source is an entity, the research/writing pass is an activity, and the human or software agent is an agent responsible for it. Record which sources the activity used, which brief/README it generated, and which claims derive from which sources. This follows PROV-O's entity/activity/agent starting point without requiring a full RDF deployment. Provenance describes lineage; it does not certify truth.
