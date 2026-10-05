# Adopter enforcement (mandatory)

**Every repository that adopts PCM must enforce the GitHub delivery gates below.** This is not optional guidance. PCM treats missing, failed, skipped, stale, or unverified gates as fail-closed: do not mark work complete or clean up until they pass.

PCM reference implementation: [`Pukujan/project-continuity-modules`](https://github.com/Pukujan/project-continuity-modules) (`main`).

## Required policy

| Rule | Exact expectation |
| --- | --- |
| PR-only to default branch | Direct pushes to `main` (or the repo default) are blocked for normal contributors. Changes land only through a pull request. |
| Required status check `gates` | When GitHub Actions can run, a required check named exactly **`gates`** must pass before merge. Prefer a single aggregate job named `gates` that depends on real lint/test/package jobs. |
| Prefer auto-merge-when-green | Enable repository `allow_auto_merge`. Require the `gates` check (and PR rules) so squash/merge auto-merge waits until green. |

If Actions cannot run (minutes exhausted, Actions disabled, or org policy), **do not invent a fake green check**. Keep PR-only enforcement, document the Actions blocker, and defer requiring `gates` until Actions can run. Coordinate shared-account Actions capacity separately (for this org, see ACS capacity issues when relevant); do not weaken PCM policy to paper over missing CI.

## Apply on a GitHub adopter repo

### 1. CI job named `gates`

Add or rename so the **job `name:` is exactly `gates`** (GitHub required-check names usually match the job name). Minimal aggregate over existing jobs:

```yaml
  gates:
    name: gates
    if: always()
    needs: [quality, test]   # list your real jobs
    runs-on: ubuntu-latest
    steps:
      - name: Require upstream jobs green
        run: |
          set -euo pipefail
          test "${{ needs.quality.result }}" = "success"
          test "${{ needs.test.result }}" = "success"
```

Trigger the workflow on `pull_request` (and usually `push`) so the check appears on PRs targeting `main`.

### 2. Repository ruleset on `main` (preferred)

Prefer a **repository ruleset** over classic branch protection alone:

- Target: `refs/heads/main` (or `~DEFAULT_BRANCH`)
- Enforcement: Active
- Rules:
  - **Pull request** — require a PR before merging (approvals may be 0 if the project uses CI-only gates; dismiss stale reviews as appropriate)
  - **Required status checks** — include context `gates`, with strict policy (require branch up to date) when you use that setting
  - **Block force pushes** (`non_fast_forward`) and **block deletions** of `main`
- Bypass actors: leave empty to match “everyone uses a PR,” or add admin bypass only if you must avoid lockout — still keep PR-only for normal contributors

Example create via API (`gh`):

```bash
gh api --method POST "repos/OWNER/REPO/rulesets" -f name='main protection' -f target='branch' -f enforcement='active' \
  --input - <<'EOF'
{
  "name": "main protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/heads/main"], "exclude": [] } },
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "required_status_checks": [{ "context": "gates" }],
        "strict_required_status_checks_policy": true
      }
    },
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
EOF
```

UI path: **Settings → Rules → Rulesets → New branch ruleset** → include `main` → enable “Require a pull request before merging” and “Require status checks to pass” → add `gates`.

### 3. Enable auto-merge on the repository

```bash
gh api --method PATCH "repos/OWNER/REPO" -f allow_auto_merge=true
```

UI: **Settings → General → Pull Requests → Allow auto-merge**.

On each PR, enable auto-merge (squash recommended) after opening, or have CI request it once `gates` is green. Auto-merge only helps when required checks / PR rules are actually configured.

## Verify checklist

Run these after applying. Replace `OWNER/REPO` as needed.

```bash
# Rulesets targeting main
gh api "repos/OWNER/REPO/rulesets" --jq '.[] | {id,name,enforcement,target}'

# Inspect one ruleset (confirm pull_request + required_status_checks context gates)
gh api "repos/OWNER/REPO/rulesets/RULESET_ID"

# Classic branch protection still present? (may coexist; both apply)
gh api "repos/OWNER/REPO/branches/main/protection" 2>/dev/null || echo "no classic protection"

# Auto-merge enabled?
gh api "repos/OWNER/REPO" --jq '{allow_auto_merge,default_branch,delete_branch_on_merge}'

# Recent Actions runs (gates must be able to run)
gh run list --repo OWNER/REPO --limit 5
```

UI verify: **Settings → Rules → Rulesets** (active ruleset on `main` with PR + `gates`) and open a test PR → Checks tab shows **gates**.

PCM reference (as applied for #211): ruleset name `main protection`, required check `gates`, `allow_auto_merge: true`.

## Workspace layout (project folder)

PCM adopters use one project folder per repository under the dev root: the
canonical checkout at `<repo>/main`, and managed task worktrees only under
`<repo>/worktrees/<TASK-ID>`. A repo that never uses worktrees can just have
`<repo>/main`. PCM refuses to create a worktree inside the main checkout or
directly in the dev root, and `continuity validate` flags a stray checkout of the
same repository under the dev root. An existing flat `<dev-root>/<repo>` checkout
is adopted with `continuity worktree migrate --root <dev-root>/<repo>` (dry run)
and `--yes` to perform the move; it refuses when anything is dirty or unpushed.
See [`TARGET_ADOPTION.md`](TARGET_ADOPTION.md#workspace-layout-project-folder).

## Relation to existing PCM docs

- [`TARGET_ADOPTION.md`](TARGET_ADOPTION.md) — how to overlay PCM files on a mature repo; **this file** is the mandatory GitHub enforcement contract those adopters must also apply.
- [`HANDOFF_PROTOCOL.md`](HANDOFF_PROTOCOL.md) / SPEC §8 — required CI and auto-merge fail closed; this doc names the exact check (`gates`) and ruleset shape.
- Do not treat templates or offline `continuity validate` as a substitute for these GitHub gates.

## Out of scope notes

- Fixing another adopter’s broken PR is that adopter’s responsibility unless explicitly assigned.
- Shared Actions-minute / org capacity problems are coordinated separately; they may delay requiring `gates` but do not cancel PR-only policy.