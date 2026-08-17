# References

The chapter text cites sources at the decision they support. This consolidated list is organized by chapter for review and maintenance. Product behavior and documentation change; verify version-specific details before applying an example to production.

## Chapter 2 — Verifiable artifacts

- [**SLSA (Supply-chain Levels for Software Artifacts)** build requirements](https://slsa.dev/spec/v1.2/build-requirements)
- [SLSA artifact verification guidance](https://slsa.dev/spec/v1.2/verifying-artifacts)
- [Docker build attestations](https://docs.docker.com/build/metadata/attestations/)
- [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)

## Chapter 3 — Infrastructure reconciliation

- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [Terraform remote state](https://developer.hashicorp.com/terraform/language/state/remote)
- [Terraform state locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [Terraform import](https://developer.hashicorp.com/terraform/cli/import)
- [Terraform **S3 (Simple Storage Service)** backend](https://developer.hashicorp.com/terraform/language/backend/s3)
- [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Create and apply a saved Terraform plan](https://developer.hashicorp.com/terraform/tutorials/cli/plan)
- [Manage Terraform resource drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift)
- [AWS Certificate Manager managed renewal](https://docs.aws.amazon.com/acm/latest/userguide/managed-renewal.html)
- [AWS Certificate Manager EventBridge events](https://docs.aws.amazon.com/acm/latest/userguide/supported-events.html)

## Chapter 4 — Kubernetes runtime

- [Kubernetes resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kubernetes probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/)
- [Kubernetes disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Kubernetes networking](https://kubernetes.io/docs/concepts/services-networking/)

## Chapter 5 — Workload identity

- [Kubernetes service accounts](https://kubernetes.io/docs/concepts/security/service-accounts/)
- [Kubernetes projected volumes](https://kubernetes.io/docs/concepts/storage/projected-volumes/)
- [Amazon **IAM (Identity and Access Management)** roles for service accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)

## Chapter 6 — Observability

- [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/)
- [OpenTelemetry instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/)
- [OpenTelemetry context propagation](https://opentelemetry.io/docs/concepts/context-propagation/)
- [OpenTelemetry deployment attributes](https://opentelemetry.io/docs/specs/semconv/registry/attributes/deployment/)

## Chapter 7 — Progressive delivery

- [Google **SRE (Site Reliability Engineering)** Workbook: Canarying Releases](https://sre.google/workbook/canarying-releases/)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

## Chapter 8 — Data compatibility

- [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)

## Chapter 9 — Asynchronous work

- [Amazon **SQS (Simple Queue Service)** at-least-once delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html)
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests)

## Chapter 10 — GitOps

- [OpenGitOps principles](https://opengitops.dev/)
- [Argo **CD (Continuous Delivery)** sync waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/)

## Chapter 11 — Cost and capacity

- [FinOps Framework](https://www.finops.org/framework/)
- [Kubernetes Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)

## Chapter 12 — Incident response

- [Google SRE Workbook: Incident Response](https://sre.google/workbook/incident-response/)
- [Google SRE Book: Managing Incidents](https://sre.google/sre-book/managing-incidents/)

## Chapter 13 — Durable reconstruction

- [PostgreSQL continuous archiving and point-in-time recovery](https://www.postgresql.org/docs/17/continuous-archiving.html)
- [Kubernetes: Operating etcd clusters](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
