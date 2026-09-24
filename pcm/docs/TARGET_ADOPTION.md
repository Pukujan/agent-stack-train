# Target Repository Adoption

Project Continuity Modules is tooling. The repository being worked on is the target and owns its own continuity state.

## Identity gate

When PCM is used as a helper for another repository:

1. Name the target repository/root explicitly.
2. Run `continuity preflight --root <target>`.
3. Do not use PCM's own PROJECT, CURRENT, TASK, or checkpoints as target-project state.
4. Do not create a second continuity repository for the target.
5. Do not treat similarly named handwritten files as an integration. The target must pass `continuity validate --root <target>`.

`MODE: TARGET_VALID` is the only successful target preflight state.

## Fresh target

For a GitHub repository that does not already own conflicting PCM-managed paths, GitHub Issues are the required task authority. Create or identify an issue before creating each active task; pass its canonical URL with `continuity task new --issue https://github.com/OWNER/REPO/issues/NUMBER`. Existing task/status files are a cached working view linked to that issue. Before resuming, run `continuity issue verify <TASK-ID>` and resolve any conflict from the live issue.

For a repository that does not already own conflicting PCM-managed paths:

```bash
continuity init --root /path/to/target --profile software --name "Target Project" --task-prefix APP
continuity validate --root /path/to/target
```

To install PCM's optional issue/PR writing prompts, opt in with the extra initialization flag:

    continuity init --root /path/to/target --profile software --name "Target Project" --task-prefix APP --github-templates

These templates guide human-readable, evidence-linked records; they do not synchronize issues or capture conversations. Initialization refuses conflicting files before writing anything. For an existing template, preserve its owner and merge only the relevant PCM guidance deliberately.

## Mature target with existing contracts

A mature repository may already have authoritative PROJECT, AGENTS, README, HANDOFF, status, or design documents. Preserve those semantics.

`continuity init` intentionally refuses conflicting content. That refusal is a safety gate, not permission to invent a parallel format.

Use a non-destructive overlay:

1. Read the target's existing agent/project/handoff contracts and identify which files already serve the PROJECT and CURRENT roles.
2. Keep those files authoritative; do not replace their domain content.
3. Materialize PCM's exact `schemas/v1/**` in the target.
4. Write a schema-conformant `.continuity/config.json` whose canonical paths point at the target's chosen PROJECT, CURRENT, and task directory.
5. Add the required single-line `continuity:project` and `continuity:current` metadata markers to those canonical files without changing their semantic ownership.
6. Ensure target task files use PCM task metadata/checkpoint structure when they participate in continuity.
7. Run `continuity validate --root <target>`.
8. Only after validation succeeds should an agent rely on PCM handoff/checkpoint state.

If the overlay cannot be completed without changing the target's established semantics, stop and make the incompatibility an explicit bounded PCM task instead of improvising.

## Cold-start rule

A fresh agent using PCM as a helper should be able to answer these before editing:

- Which repository is the target?
- Which repository is only the PCM helper?
- What exact target root was preflighted?
- Did `continuity validate --root <target>` pass?
- Which target files are canonical PROJECT, CURRENT, and TASK state?

If any answer is unknown, continuity has not been established yet.

## Required GitHub progression contract

For PCM-governed project work, GitHub Issues are required even if offline fixture/schema generation is possible. Issues own task scope, acceptance, priority, ownership, dependencies, lifecycle and durable progression. Merged history owns accepted code/domain documents; PR/check/merge records own delivery facts. Preserve target-owned domain contracts while treating task/status fields in repository docs as mandatory versioned projections. Local files, chat and packs never become task authority.

Carry [SPEC section 8](../SPEC.md#8-authority) into existing guidance without overwriting different files: leaf/parent/dependency links in every issue update; owner corrections on GitHub; one primary writer and shared-document coordination; disputed evidence preserved with sources; upstream corrections triggering affected descendant re-planning/revalidation.

Before every push synchronize applicable docs/checkpoint/catalog/index and record as-of/pending status; after the synchronous checkpoint push publish the request-ID/SHA leaf receipt and linked parent update. Required CI and GitHub auto-merge are mandatory; missing, failed or unverified gates prohibit completion/cleanup. Verify exact candidate checks and merge, fetch and reconcile live issue status. Material doc corrections require another gated increment; receipt-only transitions need no recursive doc commit. Templates are optional installation aids, not an exemption from these requirements. `--receipt-repo` and `--receipt-issue` are opt-in; omit them and the primary writer posts receipts manually. Automatic issue-comment synchronization is not implemented.
