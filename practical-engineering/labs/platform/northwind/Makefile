ifneq ($(wildcard .venv/bin/python),)
PYTHON ?= .venv/bin/python
else
PYTHON ?= python3
endif

.PHONY: bootstrap test lint audit
.PHONY: chapter-01-baseline chapter-01-checkpoint
.PHONY: chapter-02-baseline chapter-02-checkpoint
.PHONY: chapter-03-baseline chapter-03-checkpoint
.PHONY: chapter-04-baseline chapter-04-checkpoint chapter-04-failure
.PHONY: chapter-05-baseline chapter-05-checkpoint chapter-05-failure
.PHONY: chapter-06-baseline chapter-06-checkpoint chapter-06-failure
.PHONY: chapter-07-baseline chapter-07-checkpoint chapter-07-failure
.PHONY: chapter-08-baseline chapter-08-checkpoint chapter-08-failure
.PHONY: chapter-09-baseline chapter-09-checkpoint chapter-09-failure
.PHONY: chapter-10-baseline chapter-10-checkpoint chapter-10-failure
.PHONY: chapter-11-baseline chapter-11-checkpoint chapter-11-failure
.PHONY: chapter-12-baseline chapter-12-checkpoint chapter-12-failure
.PHONY: chapter-13-baseline chapter-13-checkpoint chapter-13-failure
.PHONY: chapter-14-baseline chapter-14-checkpoint chapter-14-failure

bootstrap:
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

audit:
	$(PYTHON) tools/verify_inherited.py
	$(PYTHON) tools/validate_artifacts.py

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

chapter-04-failure:
	$(PYTHON) checkpoints/chapter-04/failure.py

chapter-05-baseline:
	$(PYTHON) checkpoints/chapter-05/baseline.py

chapter-05-checkpoint:
	$(PYTHON) checkpoints/chapter-05/checkpoint.py

chapter-05-failure:
	$(PYTHON) checkpoints/chapter-05/failure.py

chapter-06-baseline:
	$(PYTHON) checkpoints/chapter-06/baseline.py

chapter-06-checkpoint:
	$(PYTHON) checkpoints/chapter-06/checkpoint.py

chapter-06-failure:
	$(PYTHON) checkpoints/chapter-06/failure.py

chapter-07-baseline:
	$(PYTHON) checkpoints/chapter-07/baseline.py

chapter-07-checkpoint:
	$(PYTHON) checkpoints/chapter-07/checkpoint.py

chapter-07-failure:
	$(PYTHON) checkpoints/chapter-07/failure.py

chapter-08-baseline:
	$(PYTHON) checkpoints/chapter-08/baseline.py

chapter-08-checkpoint:
	$(PYTHON) checkpoints/chapter-08/checkpoint.py

chapter-08-failure:
	$(PYTHON) checkpoints/chapter-08/failure.py

chapter-09-baseline:
	$(PYTHON) checkpoints/chapter-09/baseline.py

chapter-09-checkpoint:
	$(PYTHON) checkpoints/chapter-09/checkpoint.py

chapter-09-failure:
	$(PYTHON) checkpoints/chapter-09/failure.py

chapter-10-baseline:
	$(PYTHON) checkpoints/chapter-10/baseline.py

chapter-10-checkpoint:
	$(PYTHON) checkpoints/chapter-10/checkpoint.py

chapter-10-failure:
	$(PYTHON) checkpoints/chapter-10/failure.py

chapter-11-baseline:
	$(PYTHON) checkpoints/chapter-11/baseline.py

chapter-11-checkpoint:
	$(PYTHON) checkpoints/chapter-11/checkpoint.py

chapter-11-failure:
	$(PYTHON) checkpoints/chapter-11/failure.py

chapter-12-baseline:
	$(PYTHON) checkpoints/chapter-12/baseline.py

chapter-12-checkpoint:
	$(PYTHON) checkpoints/chapter-12/checkpoint.py

chapter-12-failure:
	$(PYTHON) checkpoints/chapter-12/failure.py

chapter-13-baseline:
	$(PYTHON) checkpoints/chapter-13/baseline.py

chapter-13-checkpoint:
	$(PYTHON) checkpoints/chapter-13/checkpoint.py

chapter-13-failure:
	$(PYTHON) checkpoints/chapter-13/failure.py

chapter-14-baseline:
	$(PYTHON) checkpoints/chapter-14/baseline.py

chapter-14-checkpoint:
	$(PYTHON) checkpoints/chapter-14/checkpoint.py

chapter-14-failure:
	$(PYTHON) checkpoints/chapter-14/failure.py
