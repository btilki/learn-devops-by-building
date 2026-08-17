# How to Use This Book

## Who this book is for

This book is for intermediate-to-advanced DevOps, cloud, infrastructure, platform, and **SRE (Site Reliability Engineering)** practitioners who already work comfortably with Linux, Git, containers, **CI/CD (Continuous Integration and Continuous Delivery)**, cloud infrastructure, Kubernetes fundamentals, infrastructure as code, monitoring, networking, and security fundamentals.

It does not teach those tools from first principles. Each chapter introduces only the conceptual model needed to make a production decision, then guides you through implementing, breaking, diagnosing, and verifying one capability in the cumulative Northwind system.

The book's scope is the production delivery path: from source feedback and artifact identity through deployment, operation, incident recovery, and reconstruction of one environment. Broader software-supply-chain governance belongs to the DevSecOps book. Shared platform products, tenancy, and fleet lifecycle belong to the Platform Engineering book. Portfolio reliability objectives, regional-loss strategy, and recurring recovery programs belong to the SRE book.

## The Northwind system

Northwind Commerce is deliberately small enough to understand and large enough to need production controls:

```text
customer
   │
   ▼
storefront-api ───────► PostgreSQL
   │                       ▲
   │ accepted order        │ order state, inbox, outbox
   ▼                       │
durable queue ───────► order-worker ───────► payment provider
                           │
                           ▼
                    notification-service ──► email provider
```

- `storefront-api` serves catalog reads and accepts orders.
- `order-worker` processes accepted orders asynchronously and must tolerate redelivery without duplicating payment or inventory effects.
- `notification-service` handles non-critical confirmation delivery.
- PostgreSQL is the primary stateful component.
- The durable queue decouples acceptance from asynchronous completion.
- Payment and email providers are external dependencies represented by controllable fixtures.

The critical production outcome is:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

Every chapter changes how Northwind protects or proves that outcome.

## The cumulative delivery path

The chapters form one dependency chain:

```text
fast source feedback
  → verifiable artifact
  → reconciled infrastructure
  → bounded Kubernetes runtime
  → workload identity
  → explainable production behavior
  → progressive release
  → compatible data change
  → safe asynchronous work
  → GitOps reconciliation
  → reliability-constrained cost and capacity
  → coordinated failed-change recovery
  → reconstruction from durable evidence
```

Later chapters consume earlier decisions instead of reteaching them. Artifact digests flow into infrastructure and release policy. Runtime identity becomes dependency authority. Observability becomes rollout evidence. Data compatibility and idempotency become recovery controls. GitOps becomes the normal reconciliation path, while incident and restore chapters define bounded exceptions and return to reviewed intent.

## Repository layout

The reader-facing chapters live under:

```text
books/devops/
```

The one cumulative implementation lives under:

```text
books/labs/devops/northwind/
```

Within the lab:

```text
.github/        workflow and review boundaries
services/       Northwind application behavior used by early checks
checkpoints/    chapter capability verifiers
config/         application runtime configuration contracts
data/           schema-evolution contract
delivery/       pipeline and rollout contracts
finops/         cost and capacity decisions
fixtures/       production-shaped observations and failure evidence
gitops/         reconciliation authority and behavior
incident/       failed-change response contract
infra/          infrastructure intent and backend policy
k8s/            runtime manifests
messaging/      asynchronous processing contract
observability/  telemetry and service-level evidence
recovery/       durable restore contract and objectives
release/        artifact trust expectations
security/       workload-identity contract
tools/          behavioral evaluators used by checkpoints
```

Generated reports, build outputs, simulated cloud state, virtual environments, caches, and backup artifacts are intentionally excluded from version control.

## How chapter tags work

Every chapter has two tags:

```text
chapter-NN-start
chapter-NN-complete
```

These are curated exercise snapshots, not merge milestones. Each start tag contains the cumulative Northwind state needed to begin that chapter and the latest verifier for that exercise. A complete tag is a reference solution and verification target. Because verifier corrections may be applied to both snapshots after a chapter is written, Git ancestry between a start and complete tag is not part of the contract.

Do not merge a complete tag into your working branch and do not infer chapter changes from commit ancestry. Use the tags in one of two ways:

### Guided implementation

Create a working branch from the start snapshot:

```bash
git switch -c my-chapter-NN chapter-NN-start
```

Run the baseline. A successful baseline command means it confirmed the capability is red; it does not mean the production design is already safe.

```bash
make chapter-NN-baseline
```

Follow the chapter's Practice boxes, run its checkpoint, inject the stated failure, and verify recovery.

### Reference comparison

Inspect the complete snapshot without merging it:

```bash
git diff chapter-NN-start chapter-NN-complete
git show chapter-NN-complete:path/to/file
```

The difference is a teaching aid, not a substitute for following the implementation and interpreting its evidence.

## Red, green, and recovery

The lab distinguishes four states:

- **Broken lab:** the verifier cannot run because a required file, dependency, or generated input is unexpectedly missing.
- **Red capability:** the verifier runs successfully and proves the declared production capability is unsafe or incomplete.
- **Green capability:** policy and behavioral evidence satisfy the chapter's independent expectations.
- **Verified recovery:** after the realistic failure, business and system evidence show that the critical outcome is healthy again.

A command completing, a deployment finishing, a rollback executing, a replica count increasing, or a backup restoring is an action. None proves recovery on its own.

## Generated state in Chapters 2 and 3

Most completion checkpoints run directly from their complete snapshot. Two chapters intentionally regenerate ignored state.

Chapter 2 creates the local artifact and evidence set before tampering with it:

```bash
make chapter-02-evidence
make chapter-02-checkpoint
make chapter-02-break
make chapter-02-verify-tamper
```

Chapter 3 recreates the simulated cloud object, imports its state binding, creates a saved plan, and applies it before the completed checkpoint:

```bash
make chapter-03-reset
make chapter-03-import
make chapter-03-plan
make chapter-03-apply
make chapter-03-checkpoint
```

These generated files are excluded because committed build evidence or simulated infrastructure state would make a fresh exercise appear complete without executing the mechanism.

## Best Practice and Production Practice

The book uses two related labels:

- **Best Practice:** a strong default that is broadly useful.
- **Production Practice:** how that default must be validated or adapted for the actual workload, failure modes, security boundaries, cost constraints, dependencies, and organization.

For example, default-deny networking is a strong default. In production, it is useful only when the selected network implementation enforces it, the intended traffic path is explicitly allowed, and operators have proved that policy failure does not make the service silently unreachable.

## How to read the Practice boxes

`Theory` establishes the mental model required for the chapter's decisions. It is not a separate academic survey.

`Practice` tells you what to change or prove, why the change matters, which evidence to inspect, and how to verify the result. Guided implementation is the practical work; you are not expected to rediscover essential production steps without help.

`Independent Practice` is the final retrieval exercise. It changes the constraints and requires a justified design rather than copying the guided implementation.

## Environment

Use Python 3.12 and Git. Docker, Kubernetes, Terraform, and hosted workflow familiarity are assumed where their production behavior is discussed, but the local deterministic exercises do not require a live cloud account or cluster unless a chapter explicitly says otherwise.

From the Northwind lab root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make test
make lint
```

The local exercises model production decisions and verify declared behavior. Their disclaimers matter: a simulator that correctly rejects unsafe policy is not evidence that a real cluster, identity provider, billing export, incident channel, database restore, or external dependency has been exercised.

## Five recurring principles

The chapters repeatedly use five production principles:

1. **Blast-radius control:** expose the smallest defensible scope to uncertain change or failure.
2. **Explicit contracts:** make identity, state, authority, outcomes, and failure behavior reviewable.
3. **Trustworthy evidence:** separate observations and expectations so a mechanism cannot approve itself.
4. **Reconciliation:** compare desired, recorded, external, and actual state, then make disagreement visible and owned.
5. **Recovery:** distinguish performing a corrective action from proving the critical outcome is healthy again.

The dedicated failure in each chapter names the subset it exercises. By Chapter 13, these principles connect source review to reconstruction of the production environment from durable evidence.
