ifneq ($(wildcard .venv/bin/python),)
PYTHON ?= .venv/bin/python
else
PYTHON ?= python3
endif

.PHONY: bootstrap test lint audit chapter-14-open lab-reset
.PHONY: chapter-01-baseline chapter-01-checkpoint chapter-02-baseline chapter-02-checkpoint chapter-03-baseline chapter-03-checkpoint chapter-04-baseline chapter-04-checkpoint chapter-04-attack chapter-04-contain chapter-04-recover chapter-05-baseline chapter-05-checkpoint chapter-05-attack chapter-05-contain chapter-05-recover chapter-06-baseline chapter-06-checkpoint chapter-06-attack chapter-06-contain chapter-06-recover chapter-07-baseline chapter-07-checkpoint chapter-07-attack chapter-07-contain chapter-07-recover chapter-08-baseline chapter-08-checkpoint chapter-08-challenge chapter-09-baseline chapter-09-checkpoint chapter-09-attack chapter-09-contain chapter-09-recover chapter-10-baseline chapter-10-checkpoint chapter-10-attack chapter-10-contain chapter-10-recover chapter-11-baseline chapter-11-checkpoint chapter-11-attack chapter-11-contain chapter-11-recover chapter-12-baseline chapter-12-checkpoint chapter-12-attack chapter-12-contain chapter-12-recover chapter-13-baseline chapter-13-checkpoint chapter-13-attack chapter-13-contain chapter-13-recover chapter-14-open chapter-14-baseline chapter-14-checkpoint chapter-14-attack chapter-14-contain chapter-14-recover chapter-15-baseline chapter-15-checkpoint chapter-15-attack chapter-15-contain chapter-15-recover chapter-15-verify-recovery chapter-16-baseline chapter-16-checkpoint chapter-16-challenge

bootstrap:
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

audit:
	$(PYTHON) tools/verify_inherited.py
	$(PYTHON) tools/validate_artifacts.py

lab-reset:
	$(PYTHON) tools/reset_lab.py

chapter-01-baseline:
	$(PYTHON) checkpoints/chapter-01/baseline.py

chapter-01-checkpoint:
	$(PYTHON) checkpoints/chapter-01/checkpoint.py

chapter-02-baseline:
	$(PYTHON) checkpoints/chapter-02/baseline.py

chapter-02-checkpoint:
	$(PYTHON) checkpoints/chapter-02/checkpoint.py

chapter-03-baseline:
	$(PYTHON) checkpoints/chapter-03/baseline.py

chapter-03-checkpoint:
	$(PYTHON) checkpoints/chapter-03/checkpoint.py

chapter-04-baseline:
	$(PYTHON) checkpoints/chapter-04/baseline.py

chapter-04-checkpoint:
	$(PYTHON) checkpoints/chapter-04/checkpoint.py

chapter-04-attack:
	$(PYTHON) checkpoints/chapter-04/attack.py

chapter-04-contain:
	$(PYTHON) checkpoints/chapter-04/contain.py

chapter-04-recover:
	$(PYTHON) checkpoints/chapter-04/recover.py

chapter-05-baseline:
	$(PYTHON) checkpoints/chapter-05/baseline.py

chapter-05-checkpoint:
	$(PYTHON) checkpoints/chapter-05/checkpoint.py

chapter-05-attack:
	$(PYTHON) checkpoints/chapter-05/attack.py

chapter-05-contain:
	$(PYTHON) checkpoints/chapter-05/contain.py

chapter-05-recover:
	$(PYTHON) checkpoints/chapter-05/recover.py

chapter-06-baseline:
	$(PYTHON) checkpoints/chapter-06/baseline.py

chapter-06-checkpoint:
	$(PYTHON) checkpoints/chapter-06/checkpoint.py

chapter-06-attack:
	$(PYTHON) checkpoints/chapter-06/attack.py

chapter-06-contain:
	$(PYTHON) checkpoints/chapter-06/contain.py

chapter-06-recover:
	$(PYTHON) checkpoints/chapter-06/recover.py

chapter-07-baseline:
	$(PYTHON) checkpoints/chapter-07/baseline.py

chapter-07-checkpoint:
	$(PYTHON) checkpoints/chapter-07/checkpoint.py

chapter-07-attack:
	$(PYTHON) checkpoints/chapter-07/attack.py

chapter-07-contain:
	$(PYTHON) checkpoints/chapter-07/contain.py

chapter-07-recover:
	$(PYTHON) checkpoints/chapter-07/recover.py

chapter-08-baseline:
	$(PYTHON) checkpoints/chapter-08/baseline.py

chapter-08-checkpoint:
	$(PYTHON) checkpoints/chapter-08/checkpoint.py

chapter-08-challenge:
	$(PYTHON) checkpoints/chapter-08/challenge.py

chapter-09-baseline:
	$(PYTHON) checkpoints/chapter-09/baseline.py

chapter-09-checkpoint:
	$(PYTHON) checkpoints/chapter-09/checkpoint.py

chapter-09-attack:
	$(PYTHON) checkpoints/chapter-09/attack.py

chapter-09-contain:
	$(PYTHON) checkpoints/chapter-09/contain.py

chapter-09-recover:
	$(PYTHON) checkpoints/chapter-09/recover.py

chapter-10-baseline:
	$(PYTHON) checkpoints/chapter-10/baseline.py

chapter-10-checkpoint:
	$(PYTHON) checkpoints/chapter-10/checkpoint.py

chapter-10-attack:
	$(PYTHON) checkpoints/chapter-10/attack.py

chapter-10-contain:
	$(PYTHON) checkpoints/chapter-10/contain.py

chapter-10-recover:
	$(PYTHON) checkpoints/chapter-10/recover.py

chapter-11-baseline:
	$(PYTHON) checkpoints/chapter-11/baseline.py

chapter-11-checkpoint:
	$(PYTHON) checkpoints/chapter-11/checkpoint.py

chapter-11-attack:
	$(PYTHON) checkpoints/chapter-11/attack.py

chapter-11-contain:
	$(PYTHON) checkpoints/chapter-11/contain.py

chapter-11-recover:
	$(PYTHON) checkpoints/chapter-11/recover.py

chapter-12-baseline:
	$(PYTHON) checkpoints/chapter-12/baseline.py

chapter-12-checkpoint:
	$(PYTHON) checkpoints/chapter-12/checkpoint.py

chapter-12-attack:
	$(PYTHON) checkpoints/chapter-12/attack.py

chapter-12-contain:
	$(PYTHON) checkpoints/chapter-12/contain.py

chapter-12-recover:
	$(PYTHON) checkpoints/chapter-12/recover.py

chapter-13-baseline:
	$(PYTHON) checkpoints/chapter-13/baseline.py

chapter-13-checkpoint:
	$(PYTHON) checkpoints/chapter-13/checkpoint.py

chapter-13-attack:
	$(PYTHON) checkpoints/chapter-13/attack.py

chapter-13-contain:
	$(PYTHON) checkpoints/chapter-13/contain.py

chapter-13-recover:
	$(PYTHON) checkpoints/chapter-13/recover.py

chapter-14-open:
	$(PYTHON) checkpoints/chapter-14/open.py

chapter-14-baseline:
	$(PYTHON) checkpoints/chapter-14/baseline.py

chapter-14-checkpoint:
	$(PYTHON) checkpoints/chapter-14/checkpoint.py

chapter-14-attack:
	$(PYTHON) checkpoints/chapter-14/attack.py

chapter-14-contain:
	$(PYTHON) checkpoints/chapter-14/contain.py

chapter-14-recover:
	$(PYTHON) checkpoints/chapter-14/recover.py

chapter-15-baseline:
	$(PYTHON) checkpoints/chapter-15/baseline.py

chapter-15-checkpoint:
	$(PYTHON) checkpoints/chapter-15/checkpoint.py

chapter-15-attack:
	$(PYTHON) checkpoints/chapter-15/attack.py

chapter-15-contain:
	$(PYTHON) checkpoints/chapter-15/contain.py

chapter-15-recover:
	$(PYTHON) checkpoints/chapter-15/recover.py

chapter-15-verify-recovery:
	$(PYTHON) checkpoints/chapter-15/verify_recovery.py

chapter-16-baseline:
	$(PYTHON) checkpoints/chapter-16/baseline.py

chapter-16-checkpoint:
	$(PYTHON) checkpoints/chapter-16/checkpoint.py

chapter-16-challenge:
	$(PYTHON) checkpoints/chapter-16/challenge.py
