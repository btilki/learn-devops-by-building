# Practical Platform Engineering — Editorial Conventions

**Status:** Frozen  
**Effective date:** 2026-08-16

## Dedicated challenge and failure structure

Use this hierarchy in every core chapter that contains a dedicated scenario:

```text
## 4. Test the model/design under failure
### Cumulative product failure | Connected consequence | Independent control failure — Scenario name
Practice box when the reader performs meaningful diagnosis or correction
Severity
Plausible harm
Potential blast radius
Bounded by
Primary principles
Platform questions that materially apply
Diagnosis
Correction, containment, or recovery as distinct headings when they are distinct outcomes
```

- Concept-led chapters use `Test the model under failure`.
- Decision-led chapters use `Test the decision under failure`.
- Implementation-led and hybrid chapters use `Test the design under failure`.
- Never omit the scenario classification.
- Do not merge diagnosis with correction, containment, or recovery.
- State when a platform question is not yet applicable rather than manufacturing evidence.
- Include only the series principles and platform questions that genuinely apply.
- Do not call tenant isolation recovery **Evidence of restored trust**. That phrase belongs to DevSecOps compromise recovery. Use **Evidence of restored isolation** or **Evidence of bounded platform-product recovery**.
- Do not call platform-product indicators portfolio **SLOs (Service Level Objectives)**. Those belong to SRE.
- Call unreliability against platform-product job time a **job-time budget**. Reserve **error budget** for SRE portfolio governance. Do not rename the lab key `error_budget_indicators`.

## Recurring platform questions

1. Who is the user, and what job must finish?
2. What isolation boundary limits tenant blast radius?
3. What contract can a team rely on, and how do they leave it?
4. What evidence proves the platform product is healthy—not only a tenant workload?
