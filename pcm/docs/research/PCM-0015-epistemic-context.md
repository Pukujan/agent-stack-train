# PCM-0015 — Verbatim discussion and epistemic context

This is the durable source record for PCM-0015. The dialogue excerpts below preserve the user and assistant wording available in this task. They are evidence of requirements and prior proposals, not proof that a proposed design is implemented or effective. Provenance relationships are also recorded in `PCM-0015-provenance.ttl` using W3C PROV-O.

## Verbatim discussion

### User: cross-session continuity, versions, and checkpointing

> so does pcm.  make it enforceable for every agent coming across pcm for future projects?   also is there a way to make this retroactive too such as if there is an update and version bump to pcm repo itself ans our pcm package, other projects have an option to update it and make all the changes locally
>
> also how does proper checkpointing work right now
>
> let’s say we finish a significant checkpoint
>
> i usually like to make sure agents dont use same sessions too long due to accumulating contrxt and context rot
>
> exactly why i made pcm so any new session can do the same tasks
>
> pass around tasks communicate through it
>
> while of course git remains the main canonical wah that owns the project not local
>
> but the checkpoint handoff passing context updating docs requirement after each checkpoint so keeping track of project over long term is easy
>
> and then AFTER. a big checkpoint js done how do we make it so a new session can takeover with fresh context and from the checkpoint and handoff method, reads only required things for the task and then can take ownership of the project until the next checkpoint
>
> is there any kind of research and system that follows this kind of work methodologies ans prevents things like context rot and context management and prevent things like lost in the middle?

### Assistant: answer on enforcement and handoffs

> Yes, but there are two different levels of enforcement.
>
> ### What PCM enforces today
>
> PCM-0014 is now merged. Current PCM templates and guidance require agents to:
>
> - Keep delegated work temporary.
> - Close completed, failed, cancelled, or unnecessary agents.
> - Record the result in the parent task/checkpoint.
> - Treat Git, CI, and the project task files as the lasting record—not the chat session or local agent thread.
>
> New projects created from the current PCM templates inherit this policy.
>
> However, an old project does not automatically change just because PCM released a new version. Also, a README alone cannot physically close a ChatGPT agent. The repository can require the rule through validation and CI; the runtime must perform the actual close operation. OpenAI’s agent systems separately provide controls for concurrency, interruption, waiting, and closing agents. [Official subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents)
>
> ### What PCM still needs
>
> The complete system should have:
>
> 1. A PCM version recorded in every adopting project.
>
> 2. `continuity audit` to report outdated or incomplete PCM adoption.
>
> 3. `continuity upgrade` to update a project to a newer PCM release.
>
> 4. CI checks that fail if required PCM files, checkpoint records, lifecycle rules, or handoff information are missing.
>
> 5. Automatic tests, push, CI, and merge when everything passes.
>
> 6. Automatic cleanup after merge:
>    - delete the temporary worktree;
>    - delete the temporary branch;
>    - close completed agents;
>    - leave Git and the checkpoint as the permanent record.
>
> The upgrade command should only modify PCM-owned sections and files. It should preserve project-specific content, show conflicts clearly, and create a normal commit that is pushed and merged automatically after CI passes.
>
> ### How retroactive updates should work
>
> When PCM releases version 0.3, for example:
>
> 1. Each project records that it currently uses PCM 0.2.
> 2. PCM publishes the new version and migration instructions.
> 3. An automated updater finds projects using the older version.
> 4. It opens an update branch or applies the update locally.
> 5. It updates PCM-managed files.
> 6. It runs linting, formatting, type checking, unit tests, integration tests, and continuity validation.
> 7. If everything passes, it pushes and auto-merges.
> 8. The temporary branch and worktree are deleted.
>
> Projects with custom changes to PCM guidance should receive a clearly reported conflict instead of having their files overwritten.
>
> ### How checkpointing should work
>
> A proper checkpoint is not merely a note in the chat. It is a durable Git-backed handoff containing:
>
> - What was completed.
> - Which files changed.
> - Which tests passed.
> - The commit and branch containing the work.
> - Remaining risks or unanswered questions.
> - The exact next action.
> - Which files the next session should read.
>
> The normal flow should be:
>
> `work → run tests → update checkpoint → commit → push → CI → auto-merge → close agents → delete temporary local resources`
>
> The important rule is:
>
> > A checkpoint is not complete until the information and code exist on the remote Git repository.
>
> A local worktree is only a temporary workspace. It is never the permanent source of truth.
>
> ### How a fresh session should take over
>
> After a significant checkpoint, the current session should write a fresh-session handoff. The next session should read only:
>
> 1. Project rules.
> 2. Current project status.
> 3. The active task.
> 4. The latest checkpoint.
> 5. The handoff file.
> 6. Only the specific design/specification files needed for that task.
>
> Then it should:
>
> 1. Fetch the latest remote Git state.
> 2. Confirm the checkpoint commit.
> 3. Run continuity validation.
> 4. Read the listed files.
> 5. Take ownership of the next action.
> 6. Work until the next checkpoint.
>
> It should not need the old conversation transcript or every historical checkpoint.
>
> ### Why this helps with context rot
>
> Your approach is sound: long-running sessions should not be the permanent memory of the project.
>
> Research shows that models often perform worse when the important information is buried in the middle of a long context, even when they technically have access to it. This is known as the “lost in the middle” problem. [Lost in the Middle research](https://arxiv.org/abs/2307.03172)
>
> OpenAI also provides automatic context compaction for long sessions, which is useful as a safety net. But compaction is still an automatically generated summary and is not a replacement for a human-readable, Git-versioned checkpoint. [OpenAI context compaction documentation](https://developers.openai.com/api/docs/guides/compaction)
>
> The best design is therefore:
>
> - Short current-status files.
> - Small task-specific handoffs.
> - Append-only checkpoints.
> - Explicit next actions.
> - Fresh sessions after major milestones.
> - Git and CI as the permanent authority.
> - Automatic closure of completed agents.
> - No dependence on old chat history.
>
> So the final PCM model should be:
>
> > Work in isolation temporarily, checkpoint to Git, verify through CI, merge automatically, clean up local resources, close the agents, and let a fresh session continue from the checkpoint.

### User: add idempotency, paired documents, and institutional memory

> work → run tests → update checkpoint → commit → push → CI → auto-merge → close agents → delete temporary local resources
>
> i think it’s missing idempotent and auto updating docs  and manifests
>
> i usually like keeping 2 docs of the same version 1 for fast human reading and 1 fast machine readable and verifiable, is this a good trick can we enforce it with policy or ci too can u pls research if there is anything like this available? also agent hands offs and these auto updating docs and context package
>
> how are they made are they epistemic to avoid long horizon context rot and error accumulation?
>
> how is problems like this handled?
>
> and when new session keeps taking over tasks
>
> let’s say session 1 made durable docs regarding the system
>
> but session 20 when received take from session 19 was not able to find the docs written by session 1
>
> which has happened to me many many times
>
> and session 20 assumed the docs didn’t exist and did the same tasks session 1 already did wrote a new docs only to find out the doc already existed
>
> hence wasting time as well as missing neighboring docs written by session 1
>
> now did this make the agent smart as it starts dieth fresh session and less error accumulation
>
> but the doc tracking itself got lost
>
> and it still didn’t reliably fix the agent claim system
>
> is there anything research behind epistemic knowledge graph or knowledge accumulation for long running project and verification system
>
> how is it handled?

### Assistant: answer on dual documents, idempotency, and evidence

> Yes. You identified a real failure mode:
>
> > Fresh sessions reduce context rot, but without reliable document discovery they create “institutional amnesia.”
>
> Session 20 may have less conversation baggage, but it can also forget that session 1 already created an important document.
>
> The solution is not merely “write better handoffs.” PCM needs a small, verifiable project memory system.
>
> ## The best structure
>
> Use four layers:
>
> ```text
> Git checkpoint history
>         ↓
> machine-readable project manifest
>         ↓
> human-readable project documents
>         ↓
> task-specific context package
> ```
>
> Git remains the permanent source of truth. The other files are organized views of Git-backed state.
>
> ## Two documents are a good idea
>
> Your idea of having two versions of important project information is good:
>
> 1. A human document that is quick to read.
> 2. A machine-readable document that can be checked automatically.
>
> But they should not be maintained independently. That creates drift.
>
> The machine-readable document should own the structured facts:
>
> - current task;
> - task status;
> - checkpoint IDs;
> - latest commit;
> - tests passed;
> - next action;
> - required reading;
> - document registry;
> - claims and evidence;
> - PCM version.
>
> The human document should be generated from that data, with an optional human-written explanation section.
>
> For example:
>
> ```text
> .continuity/state.yaml       machine-readable source
> docs/CURRENT.md              human-readable generated view
> .continuity/context-pack.md  task-specific handoff
> .continuity/index.yaml       document registry
> ```
>
> Each generated document should contain:
>
> - state version;
> - source commit;
> - generation timestamp;
> - source manifest hash.
>
> CI can then fail if the human document is stale compared with the machine document.
>
> This is an established pattern. OpenAPI uses a structured description that can be consumed by computers and also used to generate human documentation and tests. [OpenAPI specification](https://spec.openapis.org/oas/latest.html) JSON Schema provides the standard way to validate the machine-readable file. [JSON Schema specification](https://json-schema.org/specification)
>
> ## Idempotency must be part of PCM
>
> You are right that the workflow is incomplete without idempotency.
>
> Every PCM operation should be safe to run twice.
>
> For example:
>
> - Running `checkpoint` twice must not create two checkpoints.
> - Running `upgrade` twice must not duplicate files.
> - Running `handoff` twice must update the same handoff.
> - Running `claim` twice must not create two owners.
> - Running document discovery twice must not create duplicate registry entries.
>
> This requires stable IDs:
>
> - task ID;
> - checkpoint ID;
> - document ID;
> - claim ID;
> - migration ID;
> - session ID.
>
> PCM should update existing records by ID instead of creating new records based only on filenames or titles.
>
> The CI tests should include metamorphic tests such as:
>
> ```text
> run checkpoint
> run checkpoint again
> assert repository state is unchanged
> ```
>
> and:
>
> ```text
> run PCM upgrade
> run PCM upgrade again
> assert no duplicate files or changes appear
> ```
>
> ## How automatic document updating should work
>
> A checkpoint command should automatically:
>
> 1. Record the checkpoint event.
> 2. Update the machine manifest.
> 3. Update the human-readable current-status document.
> 4. Update the document index.
> 5. Generate the next-session context package.
> 6. Record the Git commit and test evidence.
> 7. Commit and push everything together.
>
> CI should verify that agents did not manually edit the generated files incorrectly.
>
> The repository should fail CI if:
>
> - a manifest is invalid;
> - a document is missing from the index;
> - two documents claim the same stable ID;
> - the human document is out of date;
> - the context package points to nonexistent files;
> - the checkpoint refers to a commit that does not exist;
> - the current task has no owner or next action;
> - a completed task is still claimed as active.
>
> GitHub already supports required CI checks before merge, so PCM can make this a real merge gate rather than just advice. [GitHub required status checks](https://docs.github.com/en/pull-requests/reference/status-checks)
>
> ## How session 20 finds session 1’s documents
>
> Every PCM project needs a durable document index.
>
> The index should say:
>
> - document ID;
> - file path;
> - purpose;
> - related tasks;
> - current status;
> - authoring checkpoint;
> - latest update;
> - superseded documents;
> - related documents.
>
> Then every new session begins with:
>
> 1. Read the PCM rules.
> 2. Read the machine manifest.
> 3. Read the document index.
> 4. Search the index for the task and related concepts.
> 5. Read the active task and the relevant neighboring documents.
> 6. Run validation before creating anything new.
>
> The agent should not be allowed to create a new design document merely because it did not see one in the handoff. It must first run a document lookup.
>
> PCM should have commands similar to:
>
> ```text
> continuity inventory
> continuity find --task PCM-0010
> continuity find --topic bootstrap-contract
> continuity validate --strict
> ```
>
> `inventory` scans the repository and finds documents that are not registered. `validate` fails if the index is incomplete.
>
> This changes the rule from:
>
> > “Read the handoff and hope it mentions everything.”
>
> to:
>
> > “Read the handoff, then verify against the project-wide document index.”
>
> That is the important difference.
>
> ## The claim system also needs stronger guarantees
>
> Git is excellent for permanent history, but Git by itself is not a reliable live lock. Two agents can create two branches at nearly the same time and both believe they own the task.
>
> A claim should therefore contain:
>
> - task ID;
> - agent/session ID;
> - branch;
> - starting commit;
> - claimed timestamp;
> - lease expiration;
> - status;
> - takeover rules.
>
> There must be only one active claim for a task.
>
> A second agent attempting to claim the same task should be forced to either:
>
> - resume the existing owner;
> - wait;
> - take over after the lease expires;
> - or receive a clear conflict.
>
> The claim should be recorded durably in Git, but the live exclusivity check may need a remote task ledger such as the GitHub issue/PR state. If PCM uses Git only, CI can detect duplicate claims before merge, but it cannot always prevent two agents from working in parallel.
>
> ## Epistemic tracking
>
> “Epistemic” simply means recording not only what the system says, but how it knows it.
>
> A PCM claim should have a status such as:
>
> - confirmed by code or a passing test;
> - observed but not yet verified;
> - inferred;
> - proposed;
> - contradicted;
> - stale;
> - superseded;
> - unknown.
>
> Every important claim should point to evidence:
>
> - file and line;
> - test;
> - Git commit;
> - issue;
> - CI result;
> - external source.
>
> For example:
>
> ```text
> Claim: canonical checkpoint state must be pushed before completion
> Status: confirmed
> Evidence: test_checkpoint_requires_remote_commit
> Commit: abc123
> Checked: 2026-09-23
> ```
>
> If the evidence changes or a test starts failing, the claim should become stale and require rechecking.
>
> This prevents an old agent summary from silently turning into permanent “truth.”
>
> ## Knowledge graph, but keep it practical
>
> PCM does not need a large graph database at first.
>
> It needs stable objects and links:
>
> ```text
> task → checkpoint
> checkpoint → commit
> commit → changed files
> claim → evidence
> document → task
> document → supersedes document
> test → verifies claim
> session → handoff
> ```
>
> That is already a knowledge graph in a practical sense.
>
> The W3C PROV standard models exactly this kind of history: entities, activities, agents, derivation, and evidence. It is designed to show where something came from and whether it can be trusted. [W3C provenance model](https://www.w3.org/TR/prov-primer/)
>
> W3C SHACL provides a way to validate graph rules, such as “every confirmed claim must have evidence” or “every active task must have exactly one owner.” [W3C SHACL](https://www.w3.org/TR/shacl/)
>
> PCM can begin with YAML or JSON plus JSON Schema and later export the relationships into a graph format if needed.
>
> ## Context packages should be generated, not improvised
>
> A context package for a new session should contain only:
>
> - project purpose;
> - current task;
> - current checkpoint;
> - latest verified claims;
> - unresolved contradictions;
> - related documents;
> - required tests;
> - exact next action;
> - repository and branch;
> - source commit;
> - handoff version.
>
> It should not include the entire chat history.
>
> The package should be generated from the manifest and document index, then committed to Git. The next session can independently regenerate it and compare the result. That catches missing or stale handoffs.
>
> Research systems such as MemGPT use layered memory rather than putting everything in one context window. Other agent-memory work uses an event history, retrieval, reflection, and selective recall. [MemGPT research](https://arxiv.org/abs/2310.08560) [Generative Agents research](https://arxiv.org/abs/2304.03442) [Reflexion research](https://arxiv.org/abs/2303.11366)
>
> These systems support the general direction, but they do not guarantee truth. PCM’s difference should be that project memory is tied to Git, tests, and evidence.
>
> ## The tests PCM should add
>
> PCM should test the continuity system itself:
>
> - human document and machine manifest stay synchronized;
> - checkpoint is idempotent;
> - upgrade is idempotent;
> - duplicate documents are detected;
> - unregistered documents are detected;
> - stale claims are detected;
> - broken document links fail validation;
> - session 20 can discover a document created by session 1;
> - a new agent cannot duplicate an already-completed task;
> - competing claims are rejected;
> - context packages contain only relevant documents;
> - a fresh session can continue from a checkpoint without chat history;
> - a failed test invalidates the related claim;
> - all generated files are reproducible.
>
> ## Bottom line
>
> Your proposed workflow should become:
>
> ```text
> work
> → run tests
> → update claims, manifests, and documents
> → generate context package
> → checkpoint idempotently
> → commit
> → push
> → CI validates code and project memory
> → auto-merge
> → close agents
> → delete temporary worktrees
> → start a fresh session from the verified context package
> ```
>
> Current PCM has the checkpoint, handoff, Git, and agent-lifecycle pieces. It does not yet have the complete document registry, machine-readable manifest, epistemic claim layer, idempotent upgrade system, and fresh-session discovery command.
>
> Those are the pieces needed to prevent the exact session-20 failure you described. Fresh sessions reduce context rot, but the manifest and document index prevent them from losing the project’s accumulated knowledge.

### User: current request and delegation instructions

> will this really work, how is future agents that tries to use pcm gonna be able to enforce it as well as make it versionable, can pcm really enforce it with a package and package manager? what about for future python or nod reversion? what exactly does pcm use for its management and versioning and update policy how do we even test it if it works here before we claim it works?
>
> also doesnt this make the whole checkpointing pipeline too big and too long?
>
> what about scope control and slices? this already seems like a huge upgrade to pcm but it doesn’t sound like ocm is gonna stay thing anymore
>
> before you reason on all do this can u write everything we talked about verbatim or hse w3prov itself to write epistemic contrxt in this got repo itself
>
> after that can u summon an astra subagent to take ownership of it and come up with a durable plan slices scope control policy and tests for how future agents will handle it using pcm, and then continue using luna here to keep going?

## Repository facts observed for this planning task

These observations were read from the PCM checkout at `388df1f057832d99b7c72d8022be5d1dae9a9946` on 2026-09-23:

- `pyproject.toml` declares the Python distribution `project-continuity` at version `0.2.0`, requiring Python `>=3.11`, with a `continuity` console script and no runtime dependencies.
- `.continuity/config.json` declares protocol `0.1.0-draft` and schema `project-continuity.config.v1`.
- `SPEC.md` already distinguishes CLI/package version from protocol version and describes JSON Schema plus Markdown state.
- The current CLI implements `init`, `validate`, `preflight`, `task new`, `checkpoint`, `pack`, and recovery commands (inspect `src/continuity/cli.py` before planning changes).
- Current CI runs Ruff, MyPy, compileall, Python 3.11 and 3.12 tests, package build, continuity validation, and auto-merge after required jobs.
- The checked-in workflow directory contains only `.github/workflows/ci.yml`; it builds the Python distribution but has no package publishing step. `gh release list` returned no GitHub releases.
- Opening `https://pypi.org/project/project-continuity/` returned HTTP 404 on 2026-09-23. Therefore public PyPI publication is not established; treat `0.2.0` as repository package metadata/build version, not as a confirmed installable release.
- CI installs the repository editable with `pip install -e ".[dev]"`; it does not lock or publish a separate PCM CLI installation for adopting projects.
- No Node/npm package, Node version declaration, or Node CI matrix was found in the bounded targeted search.
- Current PCM has no observed document registry, generated paired human/machine project-state view, package upgrade/audit command, or provenance-backed claim ledger. This is a bounded inspection, not a claim that no related concept exists anywhere in the repository; the planning agent must verify with targeted searches.
- The working tree was clean before this task. The task branch is `task/PCM-0015-versioned-project-memory`.

## Distribution research added during PCM-0015

- PyPA documentation says `requires-python` declares the supported minimum interpreter version in package metadata. This repository currently uses `>=3.11`; compatibility still needs actual CI coverage for every claimed minor version.
- `uv` provides `uvx` for isolated one-off CLI execution and `uv tool install` / `uv tool upgrade` for a persistent user-level tool environment. This can keep PCM separate from per-project Python environments, but it still requires a usable Python runtime and does not migrate each repository's protocol files by itself.
- npm can publish executable packages using `package.json` `bin` and declare runtime compatibility with `engines`. npm documents `engines` as advisory for dependency installs unless `engine-strict` is enabled. A Node-native PCM wrapper/port would be a separate product surface and could duplicate protocol logic.
- npm dependency update commands update installed dependencies within declared semver ranges; updating a project-level pin alone would not automatically run PCM's repository-content migration. A migration runner and repository CI gate remain separate requirements.

Sources: <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>; <https://docs.astral.sh/uv/concepts/tools/>; <https://docs.npmjs.com/cli/v11/configuring-npm/package-json/>; <https://docs.npmjs.com/cli/v11/commands/npm-update/>.

## Epistemic labels for planning

| Label | Meaning | Current examples |
|---|---|---|
| `user_requirement` | Directly requested or repeatedly described by the user | Git is canonical; fresh sessions should resume from checkpoints; avoid lost documents; require bounded slices and tests |
| `observed_repo_fact` | Directly inspected repository or tool state | Package 0.2.0; protocol 0.1.0-draft; current CI matrix; no active task at the start |
| `external_source` | A claim supported by a linked research/specification source | PROV models provenance relations; JSON Schema validates structured data; context placement can affect model performance |
| `observed_external_state` | A time-bounded check of an external service or publication surface | The current PyPI project URL returned 404; no GitHub releases were listed |
| `prior_agent_proposal` | Suggested design from the previous assistant answer, not yet adopted or verified | manifest, index, claim statuses, commands, and proposed end-to-end tests |
| `inference` | Reasoned conclusion that needs a test or explicit acceptance | Requiring registry lookup before documentation creation could reduce repeated docs |
| `open_question` | Decision not yet made | whether PCM ships only as Python CLI, adds a Node entry point, or uses a language-neutral bootstrap; which files are generated; how much state every checkpoint updates |

Do not silently upgrade any `prior_agent_proposal` or `inference` into a PCM requirement. The Astra plan must cite repository evidence and classify decisions as recommendation, assumption, or unresolved choice.

## Research sources to evaluate

- W3C PROV Primer: <https://www.w3.org/TR/prov-primer/> — provenance of entities, activities, agents, derivation, and plans.
- W3C PROV-O: <https://www.w3.org/TR/prov-o/> — OWL ontology encoding of the PROV model.
- W3C SHACL: <https://www.w3.org/TR/shacl/> — validation of RDF graphs against declared shapes; not by itself a general truth engine.
- JSON Schema: <https://json-schema.org/specification> — structural validation for JSON-compatible manifests.
- OpenAPI: <https://spec.openapis.org/oas/latest.html> — a machine-readable contract can drive human docs, code generation, and tests; analogous pattern, not a direct PCM project-memory solution.
- OpenAI Subagents guidance: <https://learn.chatgpt.com/docs/agent-configuration/subagents> — Codex can explicitly spawn, steer, wait for, and close delegated agent threads; runtime behavior is separate from repository policy.
- OpenAI context compaction: <https://developers.openai.com/api/docs/guides/compaction> — in-session context management does not replace Git-backed project state.
- “Lost in the Middle”: <https://arxiv.org/abs/2307.03172> — long-context position effects; supports selective retrieval as a hypothesis to test, not a proof that any particular PCM format will work.
- MemGPT: <https://arxiv.org/abs/2310.08560>; LongMemEval / ICLR 2025 paper: <https://proceedings.iclr.cc/paper_files/paper/2025/file/d813d324dbf0598bbdc9c8e79740ed01-Paper-Conference.pdf> — adjacent long-term memory research. Evaluate benchmarks and limitations before borrowing mechanisms.

## Provenance interpretation

`PCM-0015-provenance.ttl` uses W3C PROV-O to connect source dialogue and inspected repository state to this planning record. The local `pcm:epistemicStatus` annotations are PCM-specific labels; they are not terms standardized by W3C PROV and do not establish truth. Claims still need resolvable evidence and validation.
