# Practical SRE Engineering — Editorial Conventions

**Status:** Frozen  
**Effective date:** 2026-08-16

## Dedicated challenge and failure structure

Use this hierarchy in every core chapter that contains a dedicated scenario:

```text
## 4. Test the model/design under failure
### Cumulative reliability failure | Connected consequence | Independent control failure — Scenario name
Practice box when the reader performs meaningful diagnosis or correction
Severity
Plausible harm
Potential blast radius
Bounded by
Primary principles
Reliability questions that materially apply
Diagnosis
Correction, containment, or recovery as distinct headings when they are distinct outcomes
```

- Concept-led chapters use `Test the model under failure`.
- Decision-led chapters use `Test the decision under failure`.
- Implementation-led and hybrid chapters use `Test the design under failure`.
- Never omit the scenario classification.
- Do not merge diagnosis with correction, containment, or recovery.
- State when a reliability question is not yet applicable rather than manufacturing evidence.
- Include only the series principles and reliability questions that genuinely apply.

## Recurring reliability questions

1. What user-visible journey is at risk, and for which services?
2. What error budget remains, and what change does it authorize or freeze?
3. What human system absorbs the failure without informal heroics?
4. What evidence proves the portfolio recovered—not only one service, one environment, or one control plane?

## Language that must not collapse

- Call regional fail-over recovery **Evidence of portfolio recovery**. Do not call it **Evidence of restored trust** (DevSecOps), **Evidence of restored isolation**, or **Evidence of bounded platform-product recovery** (Platform).
- Do not call platform-product indicators portfolio **SLOs (Service Level Objectives)**. Platform job proofs `time-to-first-environment`, `paved-road-completion`, and `catalog-freshness` remain a **job-time budget**.
- Reserve **error budget** for SRE portfolio governance. A Platform fleet freeze for an upgrade is not an error-budget freeze. An error-budget freeze may halt that same fleet step for a reason Platform did not own.
- **SLA (Service Level Agreement)** is a customer or legal promise. **SLO** is the internal reliability contract. Do not treat them as synonyms.
- Catalog escalations `storefront-oncall`, `fulfillment-oncall`, and `platform-oncall` are contacts. An **on-call system** adds rotation, load, handoff, and authority.
- One-environment reconstruction and control-plane restore are inherited recoveries. They are not regional fail-over and must be listed as insufficient in Chapters 12–14.
- Do not rename inherited Platform lab keys such as `error_budget_indicators` on fixtures this book only references. Local SRE remaining-budget fields belong on portfolio SLO records.
- A dashboard, alert, page, postmortem, or runbook is mechanism evidence. It is not proof that a journey kept its SLO or that the portfolio recovered.
