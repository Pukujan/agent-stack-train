# Adopter merge gates: validation is not merge readiness

**Audience:** anyone who pins Content Generation Modules (CGM) in their own
repository and expects a README pull request to land.

A green CGM validator run and a merged pull request are two different things.
The validator checks the helper contract and your adapter files. GitHub decides
whether a pull request may merge, and that decision belongs to your repository,
not to CGM.

This page separates the gates so a passing check is never mistaken for a
guaranteed merge.

## The four gates

| # | Gate | Who owns it | What a pass means |
| --- | --- | --- | --- |
| 1 | CGM contract validation | CGM (the pinned helper) | The helper tree and your `.content-system/` adapter satisfy the pinned contract. |
| 2 | Target-side checks on the current head | Your repository | Your own factual, link, test, and structural checks pass on the exact commit under review. |
| 3 | Branch-protection readiness | Your repository | The branch is current under your protection rules and every required check is green. |
| 4 | Merge authorization | Your repository | Either a required human approval is present, or auto-merge is enabled and armed. |

A pull request can pass gate 1 and still sit open because gates 2, 3, or 4 are
unmet. That is expected, not a CGM failure.

## Gate 1 — CGM contract validation

Run the pinned helper against your adapter:

```bash
python scripts/validate_content_system.py \
  --root /path/to/content-generation-modules \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter \
  --check-adopter-readme
```

`--check-adopter-readme` also runs the freshness, asset-reference, HON, and HSW
checks. A pass means the helper contract and adapter are intact on the pinned
version. It says nothing about whether your repository will merge the change.

## Gate 2 — target-side checks on the current head

Your repository owns its factual checks, link checks, tests, and README
structure rules. They must pass on the **current head commit**, not on an older
run. If the head moved since the last green run, treat the old result as stale
and re-run. See [strict branch freshness](#gate-3--branch-protection-readiness)
below.

## Gate 3 — branch protection readiness

Three target-repository conditions decide whether the branch is mergeable:

- **Required checks.** Your protection rules name the checks that must pass.
  CGM cannot add, remove, or satisfy them.
- **Up-to-date status.** Under strict protection, the branch must be current
  with the base branch. A branch that has fallen behind must be updated and
  re-checked before merge.
- **Stale source claims.** When the base branch changes, documentation
  snapshots taken earlier can describe code that has since moved. Re-read the
  evidence and re-run gate 2 on the refreshed head; an old green run does not
  carry over.

## Gate 4 — merge authorization

Your repository chooses between two paths:

- **Human approval.** A protection rule requires one or more named reviewers.
  CGM has no opinion here and cannot supply that approval.
- **Auto-merge.** If your policy allows merging without a separate reviewer,
  enable GitHub auto-merge for the required green checks. Auto-merge lands the
  pull request once gates 2 and 3 are satisfied on a current branch.

### Optional automation path

When your own policy permits merging without a separate reviewer, you can wire
the whole path in CI:

1. Run the pinned CGM validator and your target checks as required checks.
2. Keep branch protection's required-check list in sync with those jobs.
3. Enable auto-merge (squash or your chosen strategy) for the pull request.
4. Let auto-merge land it when the branch is current and the checks are green.

```bash
# Enable auto-merge once required checks are configured (adopter-side, optional)
gh pr merge <number> --squash --auto
```

This path still depends on your protection rules and your merge policy. It is a
convenience, not a bypass.

## What CGM does not do

CGM runs inside its own checkout. It does not reach into your repository. It
does **not** approve, push, or merge an adopter's pull request, and a validator
pass does not trigger or guarantee a merge. Branch protection, required checks,
review rules, branch freshness, and the auto-merge setting are all yours to
configure.

A validator pass is evidence that the pinned contract holds. The merge decision
stays with your repository.

## Next action

1. Run gate 1 with `--check-adopter-readme` on the pinned helper.
2. Confirm your target checks pass on the current head.
3. Check whether your protection rules require a reviewer; if not, enable
   auto-merge.
4. Re-run the checks whenever the head or base branch moves.
