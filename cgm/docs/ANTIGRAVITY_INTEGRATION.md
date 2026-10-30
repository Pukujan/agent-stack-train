# Antigravity integration

**Audience:** Google Antigravity coding-agent sessions working in a repository
that pins CGM. Antigravity reads `.content-system/` on its own, but that alone
produced shallow adopter READMEs — a single SVG sketch instead of the
hero/problem/supporting narrative, and a developer spec instead of a
human-first showcase (see issue #35). This page is the bootstrap that closes
that gap.

The rule is the same one every adopter follows, and it is always on. Antigravity
does not get a lighter path because it started from `.content-system`.

## Bootstrap at session start

Paste the canonical block before the agent writes anything human-facing. It
lives at `acs_prompt_inject.system_block` in
[`docs/writing-routing.json`](writing-routing.json); the machine-readable
pointer is `agent_bootstrap.antigravity` in the same file. The block is short
enough to keep in context for the whole session, and it is not optional and not
per-report.

Three loads cover the work Antigravity does in an adopter repo:

| Surface | Load | Why |
| --- | --- | --- |
| `README.md` / product entry | `writing-direction` | Human-first story and the README scanability contract. |
| PR / issue / commit prose, docs, HTML reports, compare UIs | `human-sounding-writing` (**hsw**) | Human voice, AI-tell scrub, restrained bold. Default ON. |
| Generated filenames, asset-manifest paths, media basenames, legends | `human-output-naming` (**hon**) | Speakable basenames via `scripts/human_filename`, per-feature legend. |

Load the module `SKILL.md` files from the pinned CGM checkout — do not read the
helper's moving `main`. If the checkout is missing or the skill file cannot be
read, stop and report that instead of drafting a tool-dump README.

## Full-depth adopter README, not a spec

The failure in #35 was structural, not just tone. A complete adopter README
carries the narrative roles other adopters ship:

- a **hero** image that is a generated PNG raster (an SVG sketch is a layout
  wireframe, never the public banner);
- a **problem** visual and a **supporting**/system-cycle visual, each with a
  prompt record and image notes in `.content-system/asset-manifest.json`;
- a problem narrative with human-first stakes before any architecture;
- a grounded evidence or status table that maps claims to
  `project-brief.json` and labels shipped, experimental, planned, or unknown;
- a distinct boundaries section that says what the project does not claim.

Antigravity should generate all three narrative images and register each in the
manifest, rather than defaulting to one visual or an SVG wireframe.

## Verify before handoff

Run the adopter README gate, which enforces the PNG hero, the problem
narrative, the status/evidence table, and the boundaries section:

```bash
python scripts/validate_content_system.py \
  --root /path/to/content-generation-modules \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter \
  --check-adopter-readme
```

That flag includes the freshness and asset-reference checks from
[`docs/ACS_VERIFY.md`](ACS_VERIFY.md). For content-only checks without the
README structure gate:

```bash
python scripts/verify_adopter_content.py \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter
```

## Related contracts

- Always-on inject: `acs_prompt_inject` in
  [`docs/writing-routing.json`](writing-routing.json)
- Soft router: [`docs/WRITING_ROUTING.md`](WRITING_ROUTING.md)
- Adopter verify: [`docs/ACS_VERIFY.md`](ACS_VERIFY.md)
- README contract: [`templates/readme-contract.json`](../templates/readme-contract.json)
