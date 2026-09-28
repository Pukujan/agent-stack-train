# CGM operational issue intake

Machine twin: [`docs/issue-log-contract.json`](issue-log-contract.json)
(`content-generation.issue-log.v1`).

This is the ticketing contract for **operational** failures against CGM — cases
where an adopter pinned or used CGM and a documented MUST / default still did
not happen automatically (install ≠ enforcement).

Alex standing practice (baked into the contract):

1. **Reproduce first** — do not believe the report alone.
2. **Product defect for every CGM adopter** — not one consumer’s special case.
3. **Fix pin / contract / validate** so automation lands for all adopters.
4. **Never** open ACS-only or single-adopter tickets for that class of failure.

ACS (or Study-os, or any other pin) may be named as the *failure case*. The
issue title, scope, and done-when must still speak to **every repo that uses
CGM**.

## When this contract applies

- Alex (or an agent forwarding his ask) logs an operational failure against CGM.
- Pinning CGM did not automatically enforce a documented MUST / default.
- Hotload / install succeeded but human-facing outputs still skipped a writing
  or naming module (example: HSW skipped on compare HTML after a 0.5.6 pin).

Ordinary feature asks and one-off adopter wiring still use normal issues. Do
not stretch this contract to cover every ticket.

## Intake checklist

Copy into the issue body (or use the GitHub issue template):

- [ ] Reproduced on the reported pin (or recorded why reproduce failed).
- [ ] Framed as a CGM product defect for **every adopter**.
- [ ] Scope fixes pin / contract / validate (and adopter-facing docs).
- [ ] Ticket is **not** ACS-only or single-adopter for this failure class.
- [ ] Done-when includes **validate needles** + **adopter-facing docs**.
- [ ] Work lands via PR that `Refs` this issue; no direct commit to `main`.

## Done when

From the JSON `done_when` / `done_when_must_include`:

- Reproduce notes are in the issue or linked PR.
- Fix is framed for every CGM adopter.
- Machine contract keys exist; `validate_content_system` fails closed without them.
- Adopter-facing docs state the automation rule.
- PR references the tracking issue; CI green; left for owner merge unless asked.

## Forbidden shapes

- ACS-only ticket for a class of failure any CGM pin can hit.
- Single-adopter ticket when the defect is missing CGM pin/contract/validate automation.
- Docs-only acknowledgment without reproduce + contract/validate fix.

## Reference example

**0.5.7 HSW always-on:** ACS compare HTML stayed jargon-heavy after pinning
0.5.6. That was treated as a universal CGM automation gap (always-on inject +
`verify_hsw_applied` + validator needles), not an ACS-only hotload ticket.
