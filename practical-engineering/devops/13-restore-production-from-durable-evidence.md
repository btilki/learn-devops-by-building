# 13 — Restore Production from Durable Evidence

> **Outcome:** Reconstruct Northwind after state and control-plane loss, measure recovery objectives from the executed timeline, and reconcile every accepted order before releasing traffic.

**Current Northwind state:** Chapter 12 coordinates recovery while production state remains available. Northwind has not proved that its backups, identity, infrastructure declarations, queue evidence, and reviewed intent can reconstruct a lost environment.  
**Prerequisites:** Chapters 1–12, PostgreSQL backup fundamentals, infrastructure as code, workload identity, asynchronous processing, and GitOps.  
**Implementation:** `books/practical-engineering/labs/devops/northwind/`  
**Guided time:** approximately 90–120 minutes.

## 1. A successful backup job and no production

Northwind loses its production database and cluster control plane. The newest PostgreSQL backup is ten minutes old and its scheduled job reported success. During restore, its content digest does not match the manifest. An older base backup is valid, archived database changes reach five minutes before the incident, and five accepted orders exist only in the durable queue and payment provider.

Restoring the newest object would be fast and wrong. Restoring only the older database would produce a consistent database while losing accepted business work. Recreating workloads before identity, data, and queue dependencies would turn disaster recovery into an uncontrolled second incident.

> Can Northwind reconstruct production from independently verified evidence and prove every accepted order is correct within its recovery objectives?

> **Practice — Establish the unproved restore baseline**
>
> Check out the start state and prove that useful backup evidence exists while objectives, authority, restore ordering, and recovery validation remain red.

```bash
cd books/practical-engineering/labs/devops/northwind
git switch -c my-chapter-13 chapter-13-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-13-baseline
```

Several evidence checks are already green: the fixture contains a usable older backup, a continuous log chain, and reconcilable business records. That does not prove Northwind has the authority, procedure, or gates to restore them safely.

## 2. The production model: reconstruct, reconcile, release

> *Theory — Recovery objectives measured by restoration*
>
> Decide which evidence can reconstruct the system, how much state and time may be lost, and what must reconcile before traffic returns.

**RPO (Recovery Point Objective)** bounds the acceptable gap between the incident and the latest recoverable state. **RTO (Recovery Time Objective)** bounds the elapsed time to restore the required service outcome. Neither is established by writing a target in a document:

```text
durable evidence → isolated reconstruction → dependency restore
       → business reconciliation → traffic release

measured RPO = incident time − latest verified recovery point
measured RTO = verified recovery time − incident declaration time
```

A backup is an input. Recovery is an observed outcome from a clean restore, integrity validation, log replay, application startup, and business reconciliation. The restore must not destroy its source evidence, and the production identity must not be the only identity capable of reading recovery material.

PostgreSQL continuous archiving combines a base backup with **WAL (Write-Ahead Log)** files and supports **PITR (Point-in-Time Recovery)**. Successful recovery requires an unbroken WAL sequence from the base backup to the selected recovery point; PostgreSQL also recommends inspecting the restored database before normal users connect. [PostgreSQL continuous archiving and PITR](https://www.postgresql.org/docs/17/continuous-archiving.html).

For Kubernetes control-plane loss, official guidance identifies regular etcd snapshots as necessary recovery material. Application resources may instead be reconstructed from reviewed Git intent, but that does not replace database, queue, provider, identity, or cluster-bootstrap evidence. [Operating etcd clusters for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/).

## 3. Make recovery evidence survive production

> **Practice — Define independently recoverable evidence**
>
> Bound recovery objectives and protect backups from the failure or identity compromise that destroyed production.

Edit `recovery/restore-contract.json`. Set the declared RPO to 10 minutes and RTO to 60 minutes, then require both to be measured by the exercise.

Enable encrypted, immutable backup storage, an isolated recovery identity, manifest verification before restore, periodic restore testing, and continuous WAL coverage. Immutability needs a retention and deletion model; otherwise the same production credential or attacker can erase both primary state and recovery evidence. Encryption needs recoverable keys whose ownership and rotation are tested independently of the lost environment.

Set emergency access to `individual-time-bound`, make source evidence read-only during recovery, and audit restore actions. A shared emergency credential provides access but destroys attribution. Copy verified evidence into the recovery environment; do not rewrite the only backup, WAL archive, or Git history to fit the desired result.

## 4. Select evidence before rebuilding

> **Practice — Reject corruption and select a recovery point**
>
> Verify candidate backups by digest, reject the newest corrupted object, and bind an older base backup to a continuous WAL chain.

Inspect:

```text
fixtures/recovery/backup-manifest.json
fixtures/recovery/backups/base-001.json
fixtures/recovery/backups/base-002.json
fixtures/recovery/wal.json
```

The manifest considers the newest candidate first. Its computed digest does not match, so it must remain evidence but cannot become restore input. `base-001` matches its manifest and its WAL chain continues from minute −60 to the last safe database point at minute −5.

The resulting measured RPO is five minutes, not the age of the base backup. The base image supplies a consistent starting point; WAL replay advances it. A missing segment would invalidate the later recovery point even if every other segment and the base backup were healthy.

## 5. Restore dependencies without creating a second writer

> **Practice — Reconstruct in dependency order**
>
> Restore identity, infrastructure, state, workloads, and reconciliation authority while traffic remains blocked.

Set `clean_environment` and declare this order:

1. `emergency-identity`
2. `infrastructure`
3. `postgres-and-wal`
4. `durable-queue`
5. `workloads`
6. `gitops-controller`

Require the GitOps controller to return last and keep traffic blocked until validation. Emergency identity first makes every later action attributable. Infrastructure creates isolated network, compute, storage, and key dependencies. PostgreSQL and WAL establish the database recovery point. The durable queue returns accepted work that may be newer than that point. Workloads start without public traffic and reconcile state. Only then should the controller continuously enforce reviewed intent.

Restoring the controller early can race the recovery operator, prune temporary resources, or start workloads against incomplete dependencies. After bootstrap, reconcile any emergency change back into reviewed intent and revoke break-glass access.

## 6. Reconcile business state and measure recovery

> **Practice — Execute and verify the restore**
>
> Run the restore trace, reconcile durable sources, and release traffic only when measured objectives and business invariants pass.

Enable all five reconciliation gates: database/queue/provider comparison, terminal orders, duplicate charges, inventory, and desired-versus-actual state.

Run:

```bash
make chapter-13-restore
make chapter-13-checkpoint
make chapter-13-break
```

The exercise computes file digests, rejects `base-002`, selects `base-001`, verifies WAL continuity, and executes the dependency timeline. Database recovery produces 995 orders; the durable queue contributes the five accepted after the database recovery point. Provider evidence must show 1,000 payments, with zero duplicate charges and zero inventory discrepancies. Reviewed and restored revisions must match.

The final event measures an RPO of five minutes and derives an RTO of 52 minutes by accumulating the fixture's component restore durations and business-reconciliation time. It compares both results with independent expectations in `recovery/objectives.json`. Traffic release is an output of all gates, not a configured success flag. The `chapter-13-break` target applies additional assertions to this same restore trace: it does not introduce a second failure.

This is a deterministic restore decision and reconciliation simulation. The fixture base images are not real PostgreSQL data directories, the WAL fixture is not binary WAL, and no cluster is created. Production exercises must execute the actual backup client, key recovery, network isolation, PostgreSQL replay, queue restore, provider reconciliation, cluster bootstrap, GitOps recovery, **DNS (Domain Name System)** or routing transition, load validation, and observability path.

The restore trace is the chapter's failure exercise:

**Severity:** production data and control-plane loss with a corrupted newest backup.  
**Potential blast radius:** all Northwind order processing and every state transition after the selected recovery point.  
**Bounded by:** isolated immutable evidence, digest verification, continuous WAL, clean reconstruction, blocked traffic, idempotent reconciliation, and independent recovery objectives.  
**Primary principles:** trustworthy evidence, explicit contracts, reconciliation, blast-radius control, and recovery.

The report rejects the newest candidate, selects the older verified backup, replays through minute −5, and reconciles 995 database orders plus five durable queue orders into 1,000 correct terminal orders. `base-002` has a recorded **SHA-256 (Secure Hash Algorithm 256-bit)** digest for its pre-tamper bytes; its current bytes differ. Do not repair the object or rewrite its expected digest. Preserve both values for diagnosis and retention-policy review.

Restoring a database is an action. Starting Pods is an action. Releasing traffic is safe only after the critical Northwind outcome, external payment evidence, inventory, duplication, desired state, and measured RPO/RTO all pass.

## 7. Production reality

**Best Practice:** define recovery objectives from business tolerance, isolate and protect recovery evidence, verify integrity before use, restore into a clean environment, respect dependencies, block traffic, reconcile independent durable sources, and measure objectives through regular exercises.

**Production Practice:** validate database size and replay rate, backup lag, retention and legal holds, key and identity recovery, region or account isolation, infrastructure-state recovery, DNS and certificate dependencies, queue semantics, external-provider evidence, controller bootstrap, observability availability, staffing, and exercise frequency. Different components may require different objectives and recovery mechanisms.

## 8. What changed

| Before | After |
|---|---|
| Backup-job success implied recoverability. | Integrity and clean restoration establish usable evidence. |
| RPO and RTO were declared aspirations. | The executed recovery point and timeline measure them. |
| Production identity controlled recovery material. | Isolated, attributable authority survives production compromise. |
| The newest backup was selected by age. | Integrity and a continuous WAL chain select the recovery point. |
| Components could start in arbitrary order. | Dependencies restore while public traffic remains blocked. |
| Database availability implied recovery. | Database, queue, provider, inventory, orders, and reviewed intent reconcile. |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Restore contract and independent objectives | `recovery/restore-contract.json` and `recovery/objectives.json` | They separate recovery procedure from the recovery-point and recovery-time limits used to judge it. |
| Executed restoration evidence | `evidence/chapter-13-green.json` | It preserves backup selection, integrity, replay, reconstruction order, business reconciliation, measured objectives, and the traffic-release decision. |

## What You Learned

Disaster recovery is evidence-driven reconstruction, not backup creation. You can now define measurable recovery objectives, protect evidence independently, reject a corrupted recent backup, select a valid base and log chain, restore control dependencies safely, reconcile cross-system business state, and withhold traffic until recovery is proved.

### Prove It

> **Independent Practice — Recover when the WAL archive has a gap**
>
> Redesign the exercise when the newest valid base backup is 45 minutes old and the WAL segment covering minutes −18 to −12 is missing.

Determine the latest defensible recovery point, whether the 10-minute RPO can still be claimed, how queue and payment evidence may reconstruct or compensate for missing database state, which orders require human review, how inventory is protected, what traffic may return, who approves an objective breach, what evidence must be preserved, and which verified change prevents recurrence. Do not invent continuity that the archive cannot prove.

## Next

Northwind can now reconstruct this production environment from durable evidence within the chapter's tested scenario. Defining restore service-level objectives across a service portfolio, designing for regional loss, governing backup programs, and running recurring recovery game days belong to the **SRE (Site Reliability Engineering)** book rather than this DevOps delivery path.
