# Choose the proof that matches the promise

## Start with the person's outcome

A change is not complete just because the test suite is green. The issue should say what becomes easier, safer, clearer, or newly possible for a person—and how we will know that result was delivered. Tests support that outcome; they do not replace it.

Give each issue enough human context for a new reader to understand the problem, consequence, intended outcome, scope/non-goals, and observable acceptance checks. Keep that opening skimmable, then link the canonical task, source evidence, PR, and CI result rather than copying their full contents. Progress updates explain what changed, evidence, what remains, and the next action. Create a sub-issue only when a piece of work can be independently owned and delivered. See docs/CONTINUITY_RECORDS_POLICY.md for the full writing and provenance contract.

PDD, SDD, and TDD are useful ways to think about the problem, the behavior contract, and tests. They are not three required documents for every change. Keep the test plan in the issue or bounded task. Keep executable tests and reusable fixtures in the repository.

## Use the lightest test that can prove the claim

- **Ordinary code or bug fix:** add a deterministic regression test for the reported behavior and run the normal CI gates.
- **Invariant or repeatable operation:** add a property/metamorphic check when the important claim is a relationship—for example, retrying is idempotent or changing an unrelated file does not change the result.
- **Compatibility or migration:** use a differential check only against a trusted, named contract or reference version. The old implementation is not automatically correct.
- **Fresh-agent promise:** add an isolated fresh-session holdout only when the change promises that a new session can discover, interpret, hand off, or safely carry out repository guidance. Pair it with deterministic contract tests.

Do not require every test style for every issue. Do not create one sub-issue per test type. Run expensive or stochastic holdouts for high-risk behavior, not as a routine tax on ordinary changes.

## Make a blind test fair

A holdout is a blind rehearsal of the visible contract, not a surprise exam. The participant receives the repository and ordinary issue prompt, but not the suspected failure or evaluator answer key.

- Before the run, write each pass/fail check and link it to a visible issue or repository requirement. Hide the diagnosis, not the requirement.
- Score observable results where possible: files, task/checkpoint links, command results, changed-path inventories, and cleanup state. An LLM opinion alone cannot decide correctness.
- If the issue, repository instructions, and rubric conflict—or leave a required behavior unclear—mark that criterion **inconclusive** and fix the contract. Do not fail the agent for an undisclosed expectation.
- Use an isolated, pinned repository snapshot. The participant cannot publish, merge, or touch the canonical checkout. A test agent does not need to spawn child agents.
- Compare an independent baseline with a corrected candidate. Add a fresh variant for important behavior; repeat independent runs when the behavior is high-risk or stochastic. One pass proves possibility, not repeatability.
- Capture the result, evidence, changed paths, and uncertainty, then close the worker and clean only test-owned disposable resources.

## Keep the record short and useful

The issue/task keeps the human problem, outcome, scope, and acceptance checks. The holdout record captures only what is needed to reproduce and judge the run:

```text
Issue / task:
Starting repository commit and fixture identifier:
Prompt and prompt revision:
Model/runtime and permitted context:
Isolation boundary and evaluator-rubric revision:
Actions, files changed, and commands run:
Objective checks and evidence:
Human-visible outcome:
Result: pass | fail | inconclusive; reason and uncertainty:
Elapsed time / added setup cost:
Worker closed and disposable resources cleaned:
```

Keep the detailed rubric outside the participant's context during the run, but preserve it for maintainers afterward. After a confirmed failure, promote the needed behavior into a visible deterministic regression where possible. CI, lint/type checks, package validation, and continuity validation remain separate gates; a holdout pass cannot excuse a failing gate or a missing deliverable.

## Record the result in human language

Lead updates with the person's problem and what changed. Then link the evidence and tests, label what is shipped versus still planned or unknown, state any boundary, and give one next action. Technical names belong after that orientation. Keep a PR's opening summary skimmable and place detailed reproduction/provenance in linked or expandable evidence. Pictures are not needed for an issue log unless a visual genuinely explains the outcome.
