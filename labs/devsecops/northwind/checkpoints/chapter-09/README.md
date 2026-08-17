# Chapter 9 checkpoint

The baseline proves that a plaintext synthetic credential passes a permissive reference policy.

The completed checkpoint verifies reference-only manifests, bounded rotation overlap, and attributable secret use.

Attack writes `build/chapter-09-exposure.yaml` and `build/chapter-09-provider-compromised.yaml`. Containment writes `build/chapter-09-revocations.json`.

It cannot prove that a real secret broker, CI system, or payment provider enforces the modeled custody and revocation.
