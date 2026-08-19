# Practical DevSecOps Engineering — Editorial Conventions

**Status:** Active implementation convention  
**Effective date:** 2026-08-15

## Dedicated challenge, attack, and failure structure

Use this hierarchy consistently in every core chapter that contains a dedicated scenario:

```text
## 4. Test the model/design under failure
### Cumulative attack | Connected consequence | Independent control failure — Scenario name
Practice box when the reader performs meaningful diagnosis or correction
Severity
Plausible harm
Potential blast radius
Bounded by
Primary principles
Security questions that materially apply
Diagnosis
Correction, containment, or recovery as distinct headings when they are distinct outcomes
```

- Concept-led chapters use `Test the model under failure`.
- Decision-led chapters use `Test the decision under failure`.
- Implementation-led and hybrid chapters use `Test the design under failure`.
- Never omit the scenario classification.
- Do not merge diagnosis with correction, containment, or recovery.
- Keep containment and recovery separate when active harm can be bounded before trust is restored.
- State when a security question is not yet applicable rather than manufacturing evidence.
- Include only the series principles and security questions that genuinely apply.
- Reserve **Evidence of restored trust** for Chapter 15's bounded recovery claim, or state that it is not yet applicable. Chapter-local correction, containment, or recover-target evidence uses that local wording instead of implying production trust was restored.
