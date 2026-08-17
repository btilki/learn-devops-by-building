#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from tools.config_contract import analyze as analyze_config
except ModuleNotFoundError:
    from config_contract import analyze as analyze_config

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "k8s/base/runtime.yaml"


def analyze(dependency_down: bool = False) -> dict[str, bool]:
    text = MANIFEST.read_text(encoding="utf-8")
    liveness_local = "livenessProbe:" in text and "path: /health/live" in text
    readiness_dependency = "readinessProbe:" in text and "path: /health/ready" in text
    checks = {
        "digest_pinned": "@sha256:" in text,
        "replicated": "replicas: 3" in text,
        "requests_and_limits": all(value in text for value in ("requests:", "limits:", "cpu:", "memory:")),
        "startup_probe": "startupProbe:" in text,
        "liveness_is_process_local": liveness_local,
        "readiness_checks_dependencies": readiness_dependency,
        "dedicated_service_account": "serviceAccountName: storefront-api" in text,
        "graceful_termination": "terminationGracePeriodSeconds:" in text,
        "bounded_rollout": "maxUnavailable: 1" in text and "maxSurge: 1" in text,
        "non_secret_configuration_boundary": "kind: ConfigMap" in text
        and "configMapKeyRef:" in text,
        "restricted_container": all(
            value in text
            for value in (
                "runAsNonRoot: true",
                "allowPrivilegeEscalation: false",
                "readOnlyRootFilesystem: true",
                'drop: ["ALL"]',
                "type: RuntimeDefault",
            )
        ),
        "writable_tmp_is_explicit": "mountPath: /tmp" in text and "emptyDir: {}" in text,
        "topology_spread": "topologySpreadConstraints:" in text
        and "topologyKey: kubernetes.io/hostname" in text,
        "disruption_budget": "kind: PodDisruptionBudget" in text and "minAvailable: 2" in text,
        "default_deny_ingress": "kind: NetworkPolicy" in text and "policyTypes:" in text,
        "service_port_matches_container": "containerPort: 8080" in text
        and "targetPort: http" in text,
        "gateway_ingress_is_explicit": "name: storefront-api-allow-gateway" in text
        and "app.kubernetes.io/component: gateway" in text
        and "port: http" in text,
        "selectors_align": text.count("app: storefront-api") >= 5,
    }
    checks.update(analyze_config())
    if dependency_down:
        checks["dependency_failure_withdraws_traffic"] = readiness_dependency
        checks["dependency_failure_does_not_restart"] = liveness_local
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dependency-down", action="store_true")
    args = parser.parse_args()
    checks = analyze(args.dependency_down)
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
