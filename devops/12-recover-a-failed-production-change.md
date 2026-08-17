# 12 — Recover a Failed Production Change

> **Outcome:** Coordinate a production incident, choose a safe rollback or roll-forward from evidence, and prove recovery rather than merely completing a mitigation.

**Current Northwind state:** Chapters 1–11 prevent, bound, and expose many unsafe changes, but no control eliminates change failure. Northwind still needs an operating model for coordinated response.  
**Prerequisites:** Chapters 1–11, especially artifact identity, observability, progressive delivery, data compatibility, asynchronous processing, and GitOps.  
**Implementation:** `books/labs/devops/northwind/`  
**Guided time:** approximately 90–120 minutes.

## 1. A healthy endpoint and 600 stuck orders

A reviewed `storefront-api` candidate begins publishing queue schema `v2`. The stable `order-worker` understands only `v1`. Order acceptance remains at 99.8%, yet decode errors reach 18%, the oldest message is 20 minutes old, and 600 `v2` messages cannot reach a terminal state.

Rolling the producer back stops new `v2` messages, but it cannot make the stable consumer understand messages already in the queue. Purging the queue would make the dashboard greener by discarding customer work.

> How should Northwind coordinate a mixed recovery when rollback alone is unsafe?

> **Practice — Establish the uncoordinated baseline**
>
> Check out the start state and prove that evidence exists but incident authority, communication, mitigation, and recovery contracts are red.

```bash
cd books/labs/devops/northwind
git switch -c my-chapter-12 chapter-12-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-12-baseline
```

Notice that the baseline already diagnoses a schema mismatch. Detection is not coordination, and a plausible hypothesis is not recovery.

## 2. The production model: incident command as a control system

> *Theory — Coordinated mitigation and verified recovery*
>
> Decide who controls the response, how evidence becomes action, and what must remain true before declaring recovery.

An incident response loop has five transitions:

```text
declare → establish control → test hypotheses → mitigate → verify recovery
                └──────── communicate throughout ────────┘
```

Declaration makes urgency and impact explicit. Named roles prevent one overloaded responder from operating, coordinating, and communicating simultaneously. A change freeze reduces interference while a shared incident record preserves decisions, evidence, and rejected hypotheses.

Mitigation reduces current harm. Recovery proves the critical outcome is healthy and durable. Rollback, failover, scaling, or queue draining are actions; none proves recovery by itself.

Google's incident guidance separates command, operations, and communications, recommends early declaration and regular updates, and prioritizes mitigation before root-cause analysis. It also treats incident training and blameless learning as capabilities that must be practiced. [Incident Response](https://sre.google/workbook/incident-response/) and [Managing Incidents](https://sre.google/sre-book/managing-incidents/).

## 3. Declare impact and separate authority

> **Practice — Establish incident control**
>
> Define impact-based declaration, distinct response roles, a change freeze, an evidence record, and bounded emergency access.

Edit `incident/response-contract.json`. Set declaration criteria to `user-impact` and use **SEV-1 (Severity 1)** as Northwind's local classification.

Assign four distinct owners:

- incident commander: sets priorities, resolves contention, and owns the response rhythm;
- operations lead: executes and verifies technical changes;
- communications lead: sends audience-appropriate updates at the declared cadence;
- scribe: preserves the timeline, hypotheses, decisions, and evidence.

Enable `change_freeze`, `single_source_of_truth`, and `hypothesis_log`. Set break-glass access to `individual-time-bound`. The incident commander should not become a shared administrator; emergency actions still need attributable identity, expiry, and later review.

These roles are responsibilities, not guaranteed headcount. A small incident may combine roles, but Northwind's highest severity requires distinct owners because the coordination load and blast radius justify them.

## 4. Diagnose before selecting rollback

> **Practice — Bind mitigation to the queue evidence**
>
> Reject a full rollback, preserve accepted work, and define a mixed recovery using verified and reviewed artifacts.

Read `fixtures/incident/incompatible-queue-release.json`. The **API (Application Programming Interface)** success ratio is healthy, but three facts support the schema-mismatch hypothesis:

- the candidate producer emits `v2`;
- the stable consumer accepts only `v1`;
- decode failures and pending `v2` messages appeared with the release.

Healthy acceptance therefore does not prove completed orders. Chapter 6's request evidence and Chapter 9's queue evidence describe different stages of the same user journey.

In `incident/response-contract.json`, set mitigation to `rollback-producer-rollforward-consumer`. Preserve the queue, require the producer rollback to use Chapter 2's verified stable digest, and require the compatible consumer roll-forward to pass the reviewed delivery path.

This is not a preference for roll-forward. It follows from state already produced: rollback can stop new incompatible messages, but only a `v1`/`v2` consumer can finish the accepted `v2` work. Do not mutate or purge evidence to make reconciliation appear successful.

## 5. Communicate while recovery runs

> **Practice — Execute the response trace**
>
> Add an owned communication cadence and run the mixed mitigation against independent recovery expectations.

Set a 15-minute cadence, enable internal and external audiences, and require every update to state the next update time. Communicate known impact, current mitigation, uncertainty, and the next decision point; do not wait for a complete root cause.

In the recovery contract, require at least two consecutive passing samples and all five outcomes:

- successful order completion;
- bounded oldest-message age;
- every accepted order reaches a terminal state;
- no duplicate charge;
- reviewed desired state and actual state agree.

Run the exercise:

```bash
make chapter-12-exercise
```

The trace must declare the incident, separate roles, freeze unrelated change, support the schema hypothesis, reject full rollback, execute the mixed mitigation, emit three status updates, and evaluate recovery samples. Each update carries the observed impact, current mitigation state, remaining uncertainty, and an explicit `next_update_minute`; the checkpoint validates the generated content and cadence rather than trusting the communication flags. Thresholds come from `incident/recovery-expectations.json`, not from the response contract that is being evaluated.

This is a deterministic incident exercise. It does not page responders, route production traffic, deploy a real consumer, or update a public status system. Production exercises must validate those integrations, telemetry freshness, access availability, control-plane behavior, stakeholder reachability, and decisions under incomplete evidence.

## 6. Prove that mitigation is not recovery

**Severity:** accepted orders cannot complete after an incompatible asynchronous release.  
**Potential blast radius:** every order published as `v2` while only `v1` consumers are available.  
**Bounded by:** progressive producer exposure, preserved queue state, verified rollback identity, reviewed compatible consumer, idempotent processing, and explicit recovery gates.  
**Primary principles:** trustworthy evidence, blast-radius control, explicit contracts, reconciliation, and recovery.

> **Practice — Diagnose and recover the incompatible release**
>
> Prove that one green observation is insufficient and that all pending work reaches a correct terminal state without purging the queue.

```bash
make chapter-12-break
```

The first recovery sample still fails because the oldest message is 800 seconds old. The following samples pass, but recovery is declared only after two consecutive passes and zero pending messages. The trace must also show zero duplicate charges.

The operational sequence is:

1. stop new `v2` production by reconciling the verified stable producer digest;
2. deploy the reviewed dual-schema consumer;
3. retain and drain the queue under Chapter 9's idempotency controls;
4. observe completion, age, duplicates, and desired-versus-actual identity;
5. maintain the communication cadence until recovery criteria remain satisfied.

If a second symptom appears, record and test a new hypothesis. Do not rewrite the timeline around the eventual explanation.

## 7. Preserve learning and verify the contract

> **Practice — Make incident learning actionable**
>
> Preserve a blameless timeline and require every follow-up action to have an owner, deadline, and verification method.

Enable the four learning controls in `incident/response-contract.json`: blameless review, preserved timeline, contributing conditions, and verifiable actions.

Blameless does not mean consequence-free or vague. It means examining how review, compatibility contracts, rollout ordering, queue visibility, and authority made the action reasonable or the failure possible. “Engineer should be more careful” is not a control. A consumer compatibility test with an owner, delivery date, and failing fixture is verifiable.

Run the complete checkpoint:

```bash
make chapter-12-checkpoint
```

The checkpoint combines declared policy with executed trace evidence. Green fields alone cannot pass it: the incident must actually be declared, the mismatch diagnosed, the unsafe rollback rejected, communications emitted, and recovery sustained.

## 8. Production reality

**Best Practice:** declare early from user impact, separate command from operations and communications, freeze interference, keep one evidence record, mitigate before pursuing full causality, communicate on a cadence, and verify recovery from user and system outcomes.

**Production Practice:** adapt severity, roles, legal and regulatory notification, customer communication, escalation, break-glass access, evidence retention, and recovery windows to the organization. Exercise missing responders, stale telemetry, inaccessible runbooks, failed identity providers, unavailable GitOps controllers, and mitigations that create new state.

## 9. What changed

| Before | After |
|---|---|
| A responder decided informally whether failure was an incident. | User impact triggers a defined severity and response. |
| One person coordinated, operated, and communicated. | Distinct roles own command, operations, communications, and evidence. |
| Healthy acceptance obscured stuck asynchronous work. | Request, schema, queue, and terminal-outcome evidence test one hypothesis. |
| Rollback was the default response. | Existing production state determines rollback, roll-forward, or a mixed recovery. |
| Completing a deployment implied recovery. | Sustained business, queue, duplication, and reconciliation evidence proves it. |
| Learning produced generic recommendations. | A blameless timeline creates owned, dated, verifiable controls. |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Incident response and recovery contract | `incident/response-contract.json` | It records declaration, role authority, change freeze, hypothesis handling, mitigation, communication, recovery, and learning requirements. |
| Executed incident evidence | `evidence/chapter-12-green.json` | It retains the evaluated trace, communications, mitigation decision, and sustained recovery result instead of preserving only a completed checklist. |

## What You Learned

Incident response is a production control system, not an improvised sequence of commands. You can now declare from impact, separate authority, preserve evidence, test hypotheses, choose mitigation from existing state, communicate during uncertainty, distinguish action from recovery, and convert learning into verifiable engineering work.

### Prove It

> **Independent Practice — Recover with a missing control plane**
>
> Redesign the response when the GitOps controller is unavailable while incompatible `v2` messages continue accumulating.

Define declaration and escalation, role ownership, how the change freeze is enforced, independently attributable break-glass access, the verified producer artifact, the reviewed compatible consumer, an auditable temporary apply path, queue preservation, communications, recovery gates, controller restoration, reconciliation back to reviewed intent, evidence retention, and the conditions for removing emergency access. Explain which actions are mitigation and which observations prove recovery.

## Next

Northwind can recover from a failed change while its durable systems remain available. Chapter 13 handles the harder case: reconstructing production service and data from durable evidence after state or control-plane loss.
