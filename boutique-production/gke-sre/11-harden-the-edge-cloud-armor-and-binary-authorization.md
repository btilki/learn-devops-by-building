# 11. Harden the Edge: Cloud Armor and Binary Authorization

HTTPS and digest pins still leave a public storefront and an admission policy in dry-run. The production question is:

> How do Cloud Armor and **BA (Binary Authorization)** enforce reduce blast radius at the edge and at deploy — without turning restore into a surprise?

Setup topics **15–16** (**Lived**), `terraform/modules/armor`, `docs/security/edge-hardening.md`. Topic 16 smoke is the production-bar checklist, not an SLO month. BA enforce is what game day 03 later collided with.

## 1. An unsafe starting state: open admin UI, dry-run only BA

A public `argocd.boutique.biroltilki.art` without WAF or rate limit is a brute-force and OWASP surface. Boutique Ingress without Armor lets SQLi/XSS reach pods. BA in `DRYRUN_AUDIT_LOG_ONLY` logs violations and still admits unsigned images — a policy that cannot fail closed.

The opposite unsafe state is enforce-without-attestations: every recreate denies. That is not theoretical; 2026-07-04 restore of `redis-cart` was denied because the AR image lacked a trusted cosign attestation.

## 2. The production model: WAF then admit-time signatures

> *Theory — Edge and admission enforcement*
>
> This model enables untrusted internet traffic to be filtered at the load balancer and untrusted images to be rejected at GKE admit time, with documented break-glass — not standing dry-run.

### Cloud Armor on storefront (topic 15)

Topic 15: policy `boutique-owasp-crs`, backend security policy, default allow, **CRS (OWASP ModSecurity Core Rule Set)** preconfigured expressions (`xss-stable`, `sqli-stable`, and additional rules in the guide) with deny 403. Attach to the GCE backend service created by Boutique Ingress. Validate: legitimate `curl` to the storefront still 200; typical attack query 403.

`terraform/modules/armor/main.tf` is the reusable policy: optional CIDR allowlist (priority 500/501), OWASP rules, rate limit, default allow. Topic 15’s storefront path used Console/gcloud against the live backend name (Ingress UID). Argo CD uses `module.armor_argocd` when `enable_argocd_armor` is true.

### Edge-hardening after smoke

`docs/security/edge-hardening.md` is **post topic 16**:

| BA mode | Behavior |
| --- | --- |
| `DRYRUN_AUDIT_LOG_ONLY` | Log; deploy succeeds |
| `ENFORCED_BLOCK_AND_AUDIT_LOG` | Unsigned/un-attested blocked |

`terraform.tfvars`: `binary_authorization_enforcement_mode = "ENFORCED_BLOCK_AND_AUDIT_LOG"`. Apply `-target=module.binary_authorization[0]`.

Platform controllers (Argo CD, Kyverno, ESO, Redis) may use upstream images not yet attested. Module whitelist `platform_image_whitelist_patterns` covers those. **Boutique application images in Artifact Registry are not whitelisted** — they require CI attestation.

Argo CD policy `argocd-edge`: optional admin CIDRs, CRS SQLi+XSS at 1000–1001, rate limit 30 req/min/IP at 2000, default allow. Attach via `scripts/attach-argocd-armor.sh` because Ingress may recreate backend names.

**Best Practice:** CRS priority before rate limit, or SQLi returns 200 (troubleshooting table in edge-hardening.md).

**Production Practice:** Temporary DRYRUN is break-glass with time-box and re-enforce in the same session — used in GD03, then reversed.

### Smoke validation (topic 16)

`docs/setup/16-smoke-validation.md`: HTTPS on both URLs (two static IPs), cluster health, GitOps, Kyverno, SLOs, PagerDuty test, Armor, runbooks. Passing smoke means bootstrap **mechanism** complete. It does not mean monthly SLOs held. It is the gate before treating `boutique-gke` as the canonical demo — historically, then torn down the same day as GD03.

## 3. How this repository implements it

> **Practice — Read Armor as Terraform plus attach scripts**
>
> Open `terraform/modules/armor/main.tf` and `docs/setup/15-cloud-armor.md`. Note backend service names are not stable strings in Git.

Root module:

```hcl
module "armor_argocd" {
  count  = var.enable_argocd_armor ? 1 : 0
  source = "../../modules/armor"
  policy_name             = "argocd-edge"
  rate_limit_count        = 30
  rate_limit_interval_sec = 60
}
```

Armor module (`terraform/modules/armor/main.tf`) optional CIDR allow at priority 500 and deny-others at 501, then CRS, then rate limit. Storefront topic 15 used Console against the live backend because GKE Ingress names the backend after the UID. Do not expect a stable string in Git for `BACKEND_SERVICE`.

> **Practice — Read BA whitelist as a reliability dependency**
>
> Open `docs/security/edge-hardening.md` platform whitelist section and `docs/security/supply-chain.md` enforce mode note.

Screenshot `binary-auth-enforced.png` and `cloud-armor-ingress.png` are inactive lived evidence.

Topic 16 checklist (abridged from the setup guide) is the production bar as **mechanism**:

- Two static IPs match two hostnames; HTTPS 200/302
- Nodes Ready; no unexpected non-Running platform pods
- `boutique-root` has no `automated:` block
- Five Kyverno policies; `:latest` denied
- Boutique images all `@sha256:`
- BA policy export; AR repository exists
- Observability pods; SLO goals 99.9% / 99.95% via Monitoring API

Passing that list on a live day still does not prove a 30-day SLO. The same-day teardown and GD03 are the reminder.

Topic 16 post-smoke hardening points at edge-hardening.md. Order matters: smoke with BA still dry-run may pass; enforce afterward can break the next recreate. Document the order. Game day 03 ran **after** enforce was on.

Armor validation when live: legitimate storefront traffic 200; SQLi-style query 403. Argo CD: `curl -sI https://argocd.boutique.biroltilki.art` 200; SQLi probe 403. After teardown those curls fail because DNS is inactive — that is not an Armor regression.

## 4. Test the design under failure

### Connected consequence — Enforce without attested redis-cart

> **Practice — Use the lived 2026-07-04 facts**
>
> Scale to zero forced a new pod. BA denied `boutique/redis-cart@sha256:18e7e25…`. Storefront stayed HTTP 500 until DRYRUN + restart + re-enforce.

**Severity:** high for the journey (checkout 5xx); the deny was BA working as designed.  
**Plausible harm:** restore runbook that only `kubectl scale` is insufficient; operators leave DRYRUN on.  
**Potential blast radius:** any Deployment recreated under enforce; emergency DRYRUN weakens all image trust while it lasts.  
**Bounded by:** whitelist vs app images distinction; break-glass in setup 08 recovery; postmortem action to sign redis-cart in CI.  
**Primary principles:** Identity is digest, not tag; Lived evidence beats scaffold; Git is the deploy authority (enforcement_mode in tfvars).

#### Diagnosis

Policy worked. Operational readiness failed: unsigned Redis in AR, runbook assumed scale-up enough. Old pod survived because it was not recreated until scale-to-zero.

#### Correction

Sign/attest `redis-cart` in `build-scan-sign`. Document BA in `docs/sre/runbooks/redis-cart-down.md`. Do not disable Armor to debug 403s without checking CRS priority. Keep smoke as a checklist, not a substitute for game days.

That correction changes later decisions:

- Chapter 12 Redis runbook must mention BA recreate.
- Chapter 14 must not mark GD03 as a clean PD drill.
- Chapter 15 rebuild must re-apply enforce after images are attested — not before.

## 5. Production reality

### Common errors

#### CRS rule after rate limit

Edge-hardening troubleshooting: SQLi probe returns 200 if rate-limit priority is 1000. CRS must be 1000–1001; rate limit 2000.

#### Attaching Armor to a backend name that Ingress later replaced

`scripts/attach-argocd-armor.sh` exists because backend service names are not stable. Terraform created the policy; attach is operational.

#### Enforce BA, then scale Redis in a game day, then leave DRYRUN on

GD03 re-enforced at 18:38. Leaving dry-run overnight undoes topic 16 hardening for every image.

#### Smoke pass with BA still DRYRUN, then claiming “supply chain complete”

Topic 16 pass criteria include listing the policy. Enforce is post-smoke hardening. Sequence is part of the bar.

#### Whitelisting `europe-west1-docker.pkg.dev/boutique-gke/boutique/**`

That would exempt Boutique app images from attestations. The module’s intent is the opposite: whitelist platform controllers only.

## 6. What changed

| Before | After |
| --- | --- |
| Open storefront at L7. | OWASP CRS Armor on the Ingress backend. |
| Open Argo CD admin UI. | `argocd-edge` rate limit + CRS (+ optional CIDR). |
| BA dry-run forever. | Enforce after smoke, with platform whitelist. |
| Smoke as SLO month. | Smoke as mechanism checklist. |

## 7. What You Learned

Topic 15 puts OWASP CRS Armor on the storefront backend. Edge-hardening puts Armor on Argo CD and BA into enforce with platform whitelist. Topic 16 smoke proves mechanisms. Enforce without attestations turns the next recreate into an outage. User-visible 5xx is the reliability event; BA deny is a supply-chain event that extended it.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Setup 15–16 | `docs/setup/15-cloud-armor.md`, `16-smoke-validation.md` | WAF + smoke bar |
| Armor module | `terraform/modules/armor/` | Reusable WAF |
| Edge doc | `docs/security/edge-hardening.md` | BA enforce + Argo Armor |
| Supply chain | `docs/security/supply-chain.md` | Enforce after topic 16 |

> **Independent Practice — Decide whitelist vs mirror for Kyverno**
>
> Edge-hardening says extend `mirror-platform-images.yml` then remove whitelist patterns.

**Figure 11.1 — Inactive.** Cloud Armor on the storefront backend.

![Cloud Armor ingress](https://raw.githubusercontent.com/btilki/boutique-gke-sre/main/assets/diagrams/cloud-armor-ingress.png)

**Figure 11.2 — Inactive.** Binary Authorization cluster admission after smoke.

![Binary Authorization enforced](https://raw.githubusercontent.com/btilki/boutique-gke-sre/main/assets/diagrams/binary-auth-enforced.png)

Sources: `assets/diagrams/cloud-armor-ingress.png`, `assets/diagrams/binary-auth-enforced.png`. DNS is inactive.

## Further reading

Playbook article **G3** is the short public argument for private GKE plus Binary Authorization and Cloud Armor as an honest baseline.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/G3.md

1. What blast radius does a broad `ghcr.io/*` whitelist have?
2. What evidence would prove Kyverno images are attested in AR?
3. Should a game day include “recreate kyverno-admission”? Why or why not?
4. How does this interact with error-budget freeze (risky BA change during burn)?

Do not call Armor 403s on attack probes a browse SLO win. They are edge mechanism.
