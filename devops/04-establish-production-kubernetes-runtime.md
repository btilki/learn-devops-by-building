# 04 — Establish a Production Kubernetes Runtime

> **Outcome:** Define when `storefront-api` can start, receive traffic, restart, consume capacity, and tolerate controlled disruption.

**Current Northwind state:** infrastructure is reconciled and carries the verified image digest, but the workload has no production runtime contract.  
**Prerequisites:** Chapters 1–3 and Kubernetes fundamentals.  
**Implementation:** `books/labs/devops/northwind/`  
**Guided time:** approximately 90–120 minutes.

## 1. Running is not ready

Northwind deployed one Pod with no resource requests, the default service account, and a liveness probe that calls dependency-sensitive `/health/ready`. During a temporary dependency outage, Kubernetes restarts a healthy process and concentrates traffic on fewer replicas.

> Which signals should withdraw traffic, which should restart a process, and which controls bound the resulting blast radius?

> **Practice — Establish the unsafe runtime baseline**
>
> Check out the real manifest and prove that its health, capacity, identity, disruption, and traffic contracts are red.

```bash
cd books/labs/devops/northwind
git switch -c my-chapter-04 chapter-04-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-04-baseline
```

## 2. The production model: separate control questions

> *Theory — Scheduling, health, and disruption contracts*
>
> Decide which Kubernetes mechanism should react to each kind of failure before configuring it.

Resource requests are scheduling promises; limits bound consumption. Kubernetes schedules from requests rather than recent usage, so illustrative values must be validated with workload evidence. [Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/).

The three probes answer different questions:

| Probe | Question | Failed action |
|---|---|---|
| Startup | Has initialization completed? | Restart after its startup budget is exhausted. |
| Readiness | Should this Pod receive traffic now? | Remove it from Service endpoints. |
| Liveness | Is this process unrecoverably stuck? | Restart the container. |

A dependency outage usually belongs in readiness, not liveness. Restarting a healthy process does not repair PostgreSQL and may amplify load. Kubernetes explicitly warns that incorrect liveness probes can cause cascading failure. [Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/).

A **PDB (PodDisruptionBudget)** constrains voluntary evictions through the eviction interface; it does not prevent node failure, direct deletion, or Deployment rollout behavior. NetworkPolicy also depends on a network implementation that enforces it. These controls have operational prerequisites, not just valid syntax. [Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/), [networking](https://kubernetes.io/docs/concepts/services-networking/).

## 3. Bound scheduling and rollout behavior

> **Practice — Add capacity and rollout contracts**
>
> Replicate the workload, define measured resource envelopes, and bound rollout unavailability.

Edit `k8s/base/runtime.yaml`:

```yaml
replicas: 3
strategy:
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1
```

Add container requests of `100m` processor capacity and `128Mi` memory, with illustrative limits of `500m` and `256Mi`. These are teaching values. Production should compare throttling, working-set memory, out-of-memory termination, latency, and scheduling headroom before adopting them.

Set `terminationGracePeriodSeconds: 30`. Graceful termination still requires the application to stop accepting work, drain requests, and exit within the measured budget.

## 4. Separate startup, traffic, and restart signals

> **Practice — Implement distinct probe semantics**
>
> Protect startup, withdraw dependency-impaired Pods from traffic, and restart only when process-local health fails.

```yaml
startupProbe:
  httpGet: {path: /health/live, port: http}
  periodSeconds: 2
  failureThreshold: 30
livenessProbe:
  httpGet: {path: /health/live, port: http}
  periodSeconds: 10
  failureThreshold: 3
readinessProbe:
  httpGet: {path: /health/ready, port: http}
  periodSeconds: 5
  failureThreshold: 2
```

The startup budget is 60 seconds. The values express Northwind's current observations, not a universal formula. Readiness can include required dependencies; liveness must remain process-local unless restarting truly repairs the condition.

## 5. Bound configuration, execution, topology, and disruption

> **Practice — Remove ambient authority and constrain placement**
>
> Declare non-secret configuration, restrict the container, spread replicas, use a dedicated identity, preserve availability during voluntary eviction, and default-deny ingress.

Put non-secret environment and structured runtime values in a ConfigMap, but do not treat ConfigMaps as safe storage for credentials. Chapter 5 establishes runtime credential acquisition and rotation; the DevSecOps book owns broader secret governance, detection, policy, and compromise handling.

### Choose configuration interfaces deliberately

Replace the broad `envFrom` import with explicit configuration interfaces. Each mechanism has different observation and change behavior:

| Interface | Northwind use | Change behavior |
|---|---|---|
| Command flags | Listen address and configuration-file path | Startup contract; change requires a reviewed rollout. |
| Environment variables | Deployment environment and configuration version | Explicit startup-only scalar values; change requires a rollout. |
| Read-only mounted file | Structured, non-secret runtime values | May reload only through schema validation and atomic activation. |

Mount `/etc/northwind/runtime.yaml` read-only and pass its path explicitly with `--config`. Avoid importing every ConfigMap key into the process environment: an accidental new key should not silently become application behavior. Record `CONFIG_VERSION` explicitly and attach the same version to the Pod so Chapter 6 can correlate behavior with both artifact and configuration identity.

The application configuration contract lives in `config/runtime-contract.json`. It requires a versioned schema, named required keys, type and range checks, unknown-key rejection, and validation before readiness. A bad startup configuration must prevent the new Pod from becoming Ready. A bad dynamic candidate must be rejected atomically while the process retains the last known good configuration and emits the validation result.

Run the invalid-reload exercise:

```bash
make chapter-04-config
```

The fixture proposes `dependency_timeout_ms: "fast"` and an unknown key. The evaluator must reject `config-v2`, preserve active `config-v1`, keep the already healthy process ready, and emit evidence of the rejected candidate. Keeping readiness is safe here because the active configuration remains verified; partially applying the candidate would make that conclusion false.

This deterministic evaluator proves the declared schema and state transition; it does not run a kubelet projection, filesystem watcher, or application reload loop. Production must test projection delay, watcher loss, rapid successive updates, partial reads, process restart during reload, and telemetry that reports the version actually active in memory.

Chapter 4 defines how the process consumes and validates configuration. Chapter 10 will define how configuration versions are reviewed, promoted, frozen, overridden, and reconciled as desired state.

Run the Pod as non-root with the runtime-default seccomp profile. Disable privilege escalation, use a read-only root filesystem, and drop all Linux capabilities. Provide the required writable path explicitly through an `emptyDir` mounted at `/tmp`; validate actual write requirements rather than copying this path universally.

Add a hostname topology-spread constraint with `maxSkew: 1`. `ScheduleAnyway` expresses a preference without making a small cluster unschedulable. Use stricter scheduling only when enough eligible failure domains exist and pending Pods are an acceptable failure mode.

Add a `storefront-api` ServiceAccount with `automountServiceAccountToken: false`, set `serviceAccountName`, and add a PDB with `minAvailable: 2`. Set the named container port to `8080`, matching the image command, while the Service targets that name.

Add one NetworkPolicy that selects `storefront-api` and denies ingress by omission, then a second policy that allows only gateway Pods from explicitly labelled ingress namespaces to the named `http` port. Default deny without the corresponding allow path would make the application securely unreachable. The complete manifest at `chapter-04-complete` is the reference.

Selectors and named ports are contracts: Deployment, Service, PDB, and NetworkPolicy must select the intended Pods, and the Service and policies must resolve to the port where the image actually listens. Valid configuration with the wrong selector or port protects or routes nothing.

> **Practice — Verify the runtime contract**
>
> Check immutable identity, resources, probes, configuration, restricted execution, topology, rollout, termination, identity, disruption, deny-and-allow policy, selectors, and port alignment together.

```bash
make chapter-04-checkpoint
```

## 6. Test dependency failure

**Severity:** partial traffic withdrawal; restart amplification prevented.  
**Potential blast radius:** one `storefront-api` rollout.  
**Bounded by:** readiness, three replicas, rollout limits, and the disruption budget.  
**Primary principles:** explicit contracts, blast-radius control, and recovery.

> **Practice — Prove dependency failure does not become restart failure**
>
> Simulate a failed required dependency and verify traffic withdrawal while process liveness remains true.

```bash
make chapter-04-break
```

The report must show both `dependency_failure_withdraws_traffic` and `dependency_failure_does_not_restart` as true. Recovery means readiness returns and endpoints rejoin; a restart counter increasing would show the design is still wrong.

## 7. Production reality

**Best Practice:** define resources, distinct probes, narrow identity, graceful termination, disruption tolerance, and network boundaries.

**Production Practice:** validate every value under real startup, peak load, dependency failure, rollout, node drain, topology loss, and policy enforcement. A PDB can block maintenance; a default-deny policy can isolate the service; a read-only filesystem can expose hidden writes; soft topology constraints do not guarantee separation; and a memory limit can turn normal peaks into repeated termination.

## 8. What changed

| Before | After |
|---|---|
| Running implied healthy. | Startup, readiness, and liveness have separate meanings. |
| Scheduling had no workload promise. | Requests and limits define an evidence-tuned envelope. |
| One replica absorbed every disruption. | Replicas, rollout bounds, and PDB constrain availability loss. |
| Configuration, writable paths, and execution privilege were implicit. | Explicit flags, environment keys, a validated mounted file, temporary storage, and restricted security contexts declare them. |
| Replicas could concentrate on one node. | A topology-spread preference reduces correlated placement. |
| Default identity and open ingress were implicit. | Identity, default deny, and a narrow gateway allow path are declared. |
| Dependency failure caused restarts. | Readiness withdraws traffic while liveness preserves healthy processes. |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Workload and configuration runtime contract | `k8s/base/runtime.yaml` and `config/runtime-contract.json` | Together they define artifact and configuration identity, interfaces, validation, resources, probe semantics, execution restrictions, placement, disruption, and network behavior. |
| Runtime conformance evidence | `evidence/chapter-04-green.json` | Retain the report with manifest revision and cluster-policy version so future workload or platform changes can prove the selectors and safety controls still bind to the intended Pods. |

## What You Learned

A running Pod is not automatically schedulable, correctly configured, ready for traffic, safe to restart, or resilient to disruption. You can now choose configuration interfaces by change behavior, reject invalid startup and reload candidates, expose configuration identity, define measured resource boundaries, separate startup/readiness/liveness semantics, constrain execution and network access, preserve availability during voluntary eviction, and verify that selectors and ports connect the intended controls to the intended workload.

### Prove It

> **Independent Practice — Design the worker runtime contract**
>
> Define probes, resources, termination, disruption, identity, and network behavior for `order-worker`, which consumes at-least-once messages and has no web traffic endpoint.

Justify how readiness applies to a queue consumer, how termination stops fetching and finishes or abandons work safely, which failures merit restart, how duplicate processing is bounded, and what evidence tunes its resource envelope.

## Next

The workload now has an enforceable runtime contract. Chapter 5 replaces reusable production credentials with scoped workload identity and a controlled fallback for providers that cannot federate.
