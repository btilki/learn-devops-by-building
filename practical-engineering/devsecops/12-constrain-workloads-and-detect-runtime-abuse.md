# Constrain Workloads and Detect Runtime Abuse

Chapter 11 placed policy at explicit boundaries. A policy-admitted artifact can still behave maliciously after startup through an exploitable path, compromised dependency, stolen identity, or undeclared runtime input. Northwind must bound what each workload can do and observe meaningful contract violations independently.

## 1. Healthy service, malicious behavior

The order worker remains available and processes orders while a malicious dependency searches for credentials, launches a shell, and attempts outbound command-and-control traffic. Health checks answer whether the process responds; they do not answer whether its behavior remains authorized.

Work from the lab working tree using the How to Use This Book procedure. From the DevSecOps lab root, run:

```bash
make chapter-12-baseline
```

```text
chapter 12 baseline: detection-only runtime policy allowed shell execution to proceed
```

Detection is necessary but cannot substitute for prevention where a high-confidence action has no legitimate runtime use.

## 2. The production model: constrain and observe complementary behavior

> *Theory — Runtime contracts, sandbox boundaries, and behavioral evidence*
>
> This model enables Northwind to preserve required workload behavior while bounding compromise.

A workload contract defines identity, artifact, process, privilege, filesystem, and network behavior expected for one workload. A sandbox enforces some boundaries; a runtime sensor observes behavior. Neither is complete alone.

| Dimension | Contract question | Failure consequence |
|---|---|---|
| Identity | Which workload subject may act? | Stolen or confused authority |
| Privilege | Which capabilities and escalation are required? | Host or neighboring workload impact |
| Process | Which executables and children are expected? | Shells, tooling, or injected processes |
| Filesystem | Which paths may be read or written? | Credential discovery or persistence |
| Egress | Which destinations serve declared dependencies? | Exfiltration or command and control |
| Artifact | Which admitted digest owns this behavior? | Events cannot be tied to a release |

Prevention suits narrow, high-confidence prohibitions such as privilege escalation, undeclared egress, and shell execution in this worker. Detection suits behavior that may have legitimate variants or where blocking could destroy evidence. Defense in depth means one control's failure does not silently grant the full workload authority.

Behavioral baselines are hypotheses, not universal normality. Too broad a baseline normalizes attacker behavior; too narrow a baseline produces false positives and operational bypass. Evasion remains possible when sensors lack visibility or attackers mimic permitted actions.

## 3. Define and verify the runtime contract

> **Practice — Bound workload authority**
>
> Declare identity, digest, processes, writable paths, egress, capabilities, escalation, and root-filesystem behavior.

Open `runtime/contracts/order-worker.yaml`. The worker has no Linux capabilities, cannot escalate, uses a read-only root filesystem, writes only to declared ephemeral paths, and reaches only PostgreSQL, payment, and email dependencies. The required dependency list is part of the contract, so removing any declared operational dependency fails verification without hardcoded evaluator knowledge.

> **Practice — Separate prevention from detection**
>
> Assign an explicit response mode to each meaningful violation.

Open `runtime/policies/behavior.yaml`. Shell execution, privilege escalation, root writes, and undeclared egress are prevented. Credential discovery is detected so evidence remains available for investigation. Every event requires subject and deployment context.

Run:

```bash
make audit
make chapter-12-checkpoint
```

The checkpoint sends a declared process, an allowed ephemeral write, and all required egress destinations through the same behavior evaluator used by the attack. Each must produce `allowed`, while static contract checks retain identity and privilege constraints. This model does not exercise a kernel sensor, container runtime, or cluster network; production must verify actual enforcement, sensor completeness, performance, evasion resistance, and false-positive behavior.

## 4. Test the design under failure

### Cumulative attack — Discover credentials, execute a shell, and call outbound

> **Practice — Exercise the malicious dependency's runtime behavior**
>
> Generate inert observations without executing a shell, reading credentials, or making network traffic.

**Severity:** critical; the behavior seeks credentials, execution capability, and external control.  
**Plausible harm:** secret exposure, payment authority misuse, data exfiltration, persistence, and production manipulation.  
**Potential blast radius:** order-worker authority plus any reachable dependency not bounded by runtime policy.  
**Bounded by:** least privilege, read-only filesystem, process policy, egress allowlist, workload identity, artifact attribution, isolation, and revocation.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Order outcomes, payment authority, secrets, and customer data drive confinement.
- **Trust and authority:** Admission authorizes one artifact to perform its workload contract, not arbitrary execution or egress.
- **Detection after prevention fails:** Runtime events bind subject, claim, action, resource, outcome, policy, deployment, digest, correlation, and sensitivity.
- **Evidence of restored trust:** Not yet applicable. Chapter-local recovery: the workload is isolated, identity revoked in generated state, replacement digest admitted, legitimate processing verified, and related behavior absent under active monitoring.

#### Diagnosis

Run `make chapter-12-attack`. Raw observations name behavior type and resource, not a preselected violation label. The evaluator compares `/bin/sh` with allowed processes, the secret path with filesystem expectations, and `c2.invalid` with allowed egress. Credential discovery is detected; shell execution and undeclared egress are blocked. The command emits `runtime/events.jsonl` from the mechanism so Chapter 13 can consume the runtime evidence rather than recreate it.

#### Containment

Run `make chapter-12-contain`. The `order-worker` subject already exists in the Chapter 4 identity inventory. Containment requires all three runtime events, reads that active subject, writes `build/chapter-12-contained-subjects.yaml` with the subject revoked, records the exact compromised claim, isolates the worker, preserves evidence, and requires artifact replacement. It does not mutate the operational identity register.

#### Recovery

Run `make chapter-12-recover`. Recovery binds the runtime contract to Chapter 7’s admitted deployment digest, then evaluates a replacement process, allowed write, and every required egress destination. The generated record retains those allowed observations, derives a zero violation count, and states that coverage is limited to the declared observations under active monitoring.

## 5. Production reality

**Best Practice:** build workload-specific contracts from required behavior, prevent high-confidence prohibited actions, and retain independently attributable runtime evidence.

**Production Practice:** remove capabilities, prohibit escalation, use read-only roots and bounded writable volumes, restrict egress by identity and destination, protect metadata endpoints, correlate events with deployment digests, and test enforcement during rollout. Stage new rules in observation mode, measure false positives, then promote only well-understood prohibitions to blocking. Kubernetes documents `securityContext` controls for capabilities, privilege escalation, and a read-only root filesystem. [Configure a security context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/). Cloud instance-metadata endpoints are a common credential source; AWS, for example, documents that **IMDSv2 (Instance Metadata Service version 2)** requires a session-oriented request rather than an unauthenticated GET. [Instance metadata and user data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html).

## 6. What changed

| Before | After |
|---|---|
| Container admission implied runtime trust. | **One admitted digest receives one bounded runtime contract.** |
| Generic hardening applied equally to every service. | **Identity, process, filesystem, privilege, and egress are workload-specific.** |
| Detection covered whatever the sensor happened to emit. | **Meaningful behaviors have explicit prevent or detect outcomes.** |
| Runtime alerts lacked release context. | **Events bind workload claims to deployment and artifact digest.** |
| Restarting the worker implied recovery. | **Isolation, revocation, replacement, behavior, and monitoring prove recovery.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Runtime security contract | `runtime/contracts/order-worker.yaml` and `runtime/policies/behavior.yaml` | They preserve required authority and explicit prevent/detect behavior. |
| Containment mini-runbook | `runtime/isolation-runbook.md` | It preserves isolation, exact identity revocation, evidence, replacement, behavioral verification, and coverage obligations across fresh clones. |

## What You Learned

Runtime trust is conditional behavior, not successful deployment. Workload identity, privilege, process, filesystem, egress, and artifact context form one contract. Prevention bounds high-confidence abuse; detection preserves evidence for behavior that cannot safely be blocked. Recovery replaces compromised authority and verifies legitimate operation under continued observation.

### Prove It

> **Independent Practice — Contract notification-service runtime behavior**
>
> Permit email delivery without granting shell execution, payment access, broad filesystem writes, or unrestricted egress.

Specify identity, digest, processes, destinations, writable paths, capabilities, prevented actions, detected actions, event context, containment, and recovery evidence.

## Next

Runtime events now exist with identity and deployment context. Chapter 13 normalizes cross-system evidence, builds detection hypotheses, exposes telemetry gaps, and connects actionable detections to response.
