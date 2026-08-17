PYTHON ?= python3

.PHONY: bootstrap test lint chapter-01-baseline chapter-01-template chapter-01-template-drift chapter-01-checkpoint chapter-02-baseline chapter-02-evidence chapter-02-checkpoint chapter-02-break chapter-02-verify-tamper chapter-03-baseline chapter-03-reset chapter-03-import chapter-03-plan chapter-03-apply chapter-03-checkpoint chapter-03-certificate chapter-03-break chapter-04-baseline chapter-04-config chapter-04-checkpoint chapter-04-break chapter-05-baseline chapter-05-checkpoint chapter-05-break chapter-06-baseline chapter-06-checkpoint chapter-06-break chapter-07-baseline chapter-07-checkpoint chapter-07-break chapter-08-baseline chapter-08-checkpoint chapter-08-break chapter-09-baseline chapter-09-checkpoint chapter-09-break chapter-10-baseline chapter-10-trace chapter-10-config chapter-10-checkpoint chapter-10-break chapter-10-game-day chapter-11-baseline chapter-11-evaluate chapter-11-checkpoint chapter-11-break chapter-12-baseline chapter-12-exercise chapter-12-checkpoint chapter-12-break chapter-13-baseline chapter-13-restore chapter-13-checkpoint chapter-13-break

bootstrap:
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check services tools checkpoints

chapter-01-baseline:
	@mkdir -p build-output
	@truncate -s 1400000000 build-output/cache.bin
	$(PYTHON) checkpoints/chapter-01/verify.py --expect red

chapter-01-template:
	$(PYTHON) tools/workflow_conformance.py

chapter-01-template-drift:
	$(PYTHON) tools/workflow_conformance.py --workflow fixtures/pipeline/drifted-ci.yml --expect fail

chapter-01-checkpoint:
	$(PYTHON) checkpoints/chapter-01/verify.py --expect green

chapter-02-baseline:
	$(PYTHON) checkpoints/chapter-02/verify.py --expect red

chapter-02-evidence:
	$(PYTHON) tools/artifact_evidence.py build

chapter-02-checkpoint: chapter-02-evidence
	$(PYTHON) checkpoints/chapter-02/verify.py --expect green

chapter-02-break:
	$(PYTHON) tools/artifact_evidence.py tamper

chapter-02-verify-tamper:
	! $(PYTHON) tools/artifact_evidence.py verify

chapter-03-reset:
	$(PYTHON) tools/reconcile_infra.py reset

chapter-03-baseline: chapter-03-reset
	$(PYTHON) checkpoints/chapter-03/verify.py --expect red

chapter-03-import:
	$(PYTHON) tools/reconcile_infra.py import-existing

chapter-03-plan:
	$(PYTHON) tools/reconcile_infra.py plan

chapter-03-apply:
	$(PYTHON) tools/reconcile_infra.py apply

chapter-03-checkpoint:
	$(PYTHON) checkpoints/chapter-03/verify.py --expect green

chapter-03-certificate:
	$(PYTHON) tools/certificate_lifecycle.py --scenario expiry-without-replacement

chapter-03-break:
	$(PYTHON) tools/reconcile_infra.py drift --replicas 5

chapter-04-baseline:
	$(PYTHON) checkpoints/chapter-04/verify.py --expect red

chapter-04-config:
	$(PYTHON) tools/config_contract.py --scenario invalid-reload

chapter-04-checkpoint:
	$(PYTHON) checkpoints/chapter-04/verify.py --expect green

chapter-04-break:
	$(PYTHON) tools/runtime_contract.py --dependency-down

chapter-05-baseline:
	$(PYTHON) checkpoints/chapter-05/verify.py --expect red

chapter-05-checkpoint:
	$(PYTHON) checkpoints/chapter-05/verify.py --expect green

chapter-05-break:
	$(PYTHON) tools/identity_contract.py --scenario stolen-token-replay

chapter-06-baseline:
	$(PYTHON) checkpoints/chapter-06/verify.py --expect red

chapter-06-checkpoint:
	$(PYTHON) checkpoints/chapter-06/verify.py --expect green

chapter-06-break:
	$(PYTHON) tools/observability_contract.py --scenario payment-degradation

chapter-07-baseline:
	$(PYTHON) checkpoints/chapter-07/verify.py --expect red

chapter-07-checkpoint:
	$(PYTHON) checkpoints/chapter-07/verify.py --expect green

chapter-07-break:
	$(PYTHON) tools/rollout_contract.py --scenario candidate-payment-failure

chapter-08-baseline:
	$(PYTHON) checkpoints/chapter-08/verify.py --expect red

chapter-08-checkpoint:
	$(PYTHON) checkpoints/chapter-08/verify.py --expect green

chapter-08-break:
	$(PYTHON) tools/migration_contract.py --scenario old-writer-during-canary

chapter-09-baseline:
	$(PYTHON) checkpoints/chapter-09/verify.py --expect red

chapter-09-checkpoint:
	$(PYTHON) checkpoints/chapter-09/verify.py --expect green

chapter-09-break:
	$(PYTHON) tools/async_contract.py --scenario payment-succeeded-ack-lost

chapter-10-baseline:
	$(PYTHON) checkpoints/chapter-10/verify.py --expect red

chapter-10-trace:
	$(PYTHON) tools/gitops_trace.py

chapter-10-config:
	$(PYTHON) tools/config_delivery.py

chapter-10-checkpoint:
	$(PYTHON) checkpoints/chapter-10/verify.py --expect green

chapter-10-break:
	$(PYTHON) tools/gitops_contract.py --scenario reviewed-harmful-intent

chapter-10-game-day:
	$(PYTHON) tools/gitops_sync_storm.py

chapter-11-baseline:
	$(PYTHON) checkpoints/chapter-11/verify.py --expect red

chapter-11-evaluate:
	$(PYTHON) tools/capacity_evaluate.py

chapter-11-checkpoint:
	$(PYTHON) checkpoints/chapter-11/verify.py --expect green

chapter-11-break:
	$(PYTHON) tools/capacity_contract.py --scenario cheap-but-slow

chapter-12-baseline:
	$(PYTHON) checkpoints/chapter-12/verify.py --expect red

chapter-12-exercise:
	$(PYTHON) tools/incident_exercise.py

chapter-12-checkpoint:
	$(PYTHON) checkpoints/chapter-12/verify.py --expect green

chapter-12-break:
	$(PYTHON) tools/incident_contract.py --scenario incompatible-queue-release

chapter-13-baseline:
	$(PYTHON) checkpoints/chapter-13/verify.py --expect red

chapter-13-restore:
	$(PYTHON) tools/restore_exercise.py

chapter-13-checkpoint:
	$(PYTHON) checkpoints/chapter-13/verify.py --expect green

chapter-13-break:
	$(PYTHON) tools/restore_contract.py --scenario corrupt-latest-backup
