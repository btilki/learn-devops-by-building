# Glossary and abbreviations

On first use in each chapter, the book writes **ABBR (Full Form)** with the complete expression bold. This glossary lists those terms plus book-local names. Do not treat it as a Kubernetes tutorial.

| Term | Full form / meaning |
|------|---------------------|
| **ACL** | Access Control List (Key Vault network rules in Topic 19 scaffold) |
| **ACR** | Azure Container Registry |
| **ADO** | Azure DevOps (pipelines only; not the Git remote) |
| **ADR** | Architecture Decision Record |
| **AKS** | Azure Kubernetes Service |
| **CI** | Continuous Integration |
| **CD** | Continuous Delivery / Deployment (context: CI/CD) |
| **CNI** | Container Network Interface (Azure CNI in this repo) |
| **CSI** | Container Storage Interface (Secrets Store CSI) |
| **CVE** | Common Vulnerabilities and Exposures |
| **DAST** | Dynamic Application Security Testing |
| **DevSecOps** | Development, Security, and Operations |
| **DNS-01** | ACME DNS challenge type used by cert-manager |
| **DR** | Disaster recovery |
| **eBPF** | Extended Berkeley Packet Filter (Falco driver, scaffold) |
| **Entra** | Microsoft Entra ID (Azure AD) |
| **FQDN** | Fully qualified domain name |
| **FR** | Functional requirement (`docs/architecture/01-requirements.md`) |
| **GAR** | Google Artifact Registry (upstream Boutique images) |
| **GitOps** | Desired state in Git, reconciled by Argo CD |
| **HSM** | Hardware Security Module (out of scope for cosign keys) |
| **HTTP-01** | ACME HTTP challenge (not the pilot's default) |
| **IaC** | Infrastructure as Code |
| **IR** | Incident response |
| **KV** | Azure Key Vault |
| **Kyverno** | Kubernetes-native policy engine used for admission |
| **Loki** | In-cluster log store (ADR-0012) |
| **NPM** | Azure Network Policy Manager (`network_policy=azure`) |
| **NSG** | Network Security Group |
| **OIDC** | OpenID Connect |
| **OTLP** | OpenTelemetry Protocol |
| **OTel** | OpenTelemetry |
| **OWASP** | Open Worldwide Application Security Project |
| **PAT** | Personal access token (avoided for Azure auth) |
| **PEM** | Privacy-Enhanced Mail (cosign public key format) |
| **PR** | Pull request |
| **PSA** | Pod Security Admission |
| **PSS** | Pod Security Standards (Kyverno baseline rules) |
| **PVC** | PersistentVolumeClaim |
| **RBAC** | Role-based access control |
| **Rekor** | Sigstore transparency log (not used; `--tlog-upload=false`) |
| **RG** | Resource group |
| **RPO** | Recovery Point Objective |
| **RTO** | Recovery Time Objective |
| **SBOM** | Software Bill of Materials (Topic 17 scaffold) |
| **SC** | ADO service connection |
| **SIEM** | Security Information and Event Management |
| **SLI** | Service Level Indicator |
| **SLO** | Service Level Objective |
| **SOC** | Security Operations Center |
| **SP** | Service principal |
| **SPDX** | Software Package Data Exchange (SBOM format) |
| **SRE** | Site Reliability Engineering (sister book) |
| **SSOT** | Single source of truth |
| **STRIDE** | Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege |
| **TLS** | Transport Layer Security |
| **UAMI** | User-assigned managed identity |
| **VNet** | Virtual Network |
| **WAF** | Web Application Firewall (out of scope) |
| **WI** | Workload Identity |
| **ZAP** | Zed Attack Proxy (Topic 20 scaffold) |

## Book-local names

| Name | Meaning |
|------|---------|
| **Lived** | Setup Topics 00–13 ran on Azure, then torn down |
| **Scaffold** | Topics 14–20 and ADRs 0013–0017 exist in Git; not live-validated on this pilot |
| **Inactive** | Public DNS/URLs after teardown; use `assets/images/setup/` |
| **Online Boutique v0.10.5** | Upstream microservices-demo tag this platform mirrors |
| **boutique-dev / stage / prod** | Namespaces on **one** AKS cluster |
| **germanywestcentral** | Lived and documented rebuild region |
| **biroltilki.art** | Lived DNS zone (inactive until rebuild) |
| **Phase 15+** | Fuller DevSecOps packages; scaffold-first (ADR-0013) |
| **production pilot** | Maturity label — **not** production-ready |
