ifneq ($(wildcard .venv/bin/python),)
  ifeq ($(shell .venv/bin/python -c 'print("ok")' 2>/dev/null),ok)
    PYTHON ?= .venv/bin/python
  else
    PYTHON ?= python3
  endif
else
  PYTHON ?= python3
endif

.PHONY: bootstrap test lint audit matrix
.PHONY: chapter-01-baseline chapter-01-checkpoint
.PHONY: chapter-02-baseline chapter-02-checkpoint
.PHONY: chapter-03-baseline chapter-03-checkpoint
.PHONY: chapter-04-baseline chapter-04-checkpoint
.PHONY: chapter-05-baseline chapter-05-checkpoint
.PHONY: chapter-06-baseline chapter-06-checkpoint
.PHONY: chapter-07-baseline chapter-07-checkpoint
.PHONY: chapter-08-baseline chapter-08-checkpoint
.PHONY: chapter-09-baseline chapter-09-checkpoint
.PHONY: chapter-10-baseline chapter-10-checkpoint
.PHONY: chapter-11-baseline chapter-11-checkpoint
.PHONY: chapter-12-baseline chapter-12-checkpoint
.PHONY: chapter-13-baseline chapter-13-checkpoint
.PHONY: chapter-14-baseline chapter-14-checkpoint

bootstrap:
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

audit:
	$(PYTHON) tools/verify_inherited.py
	$(PYTHON) tools/validate_artifacts.py

matrix: test lint audit
	$(PYTHON) tools/matrix.py

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

chapter-05-baseline:
	$(PYTHON) checkpoints/chapter-05/baseline.py

chapter-05-checkpoint:
	$(PYTHON) checkpoints/chapter-05/checkpoint.py

chapter-06-baseline:
	$(PYTHON) checkpoints/chapter-06/baseline.py

chapter-06-checkpoint:
	$(PYTHON) checkpoints/chapter-06/checkpoint.py

chapter-07-baseline:
	$(PYTHON) checkpoints/chapter-07/baseline.py

chapter-07-checkpoint:
	$(PYTHON) checkpoints/chapter-07/checkpoint.py

chapter-08-baseline:
	$(PYTHON) checkpoints/chapter-08/baseline.py

chapter-08-checkpoint:
	$(PYTHON) checkpoints/chapter-08/checkpoint.py

chapter-09-baseline:
	$(PYTHON) checkpoints/chapter-09/baseline.py

chapter-09-checkpoint:
	$(PYTHON) checkpoints/chapter-09/checkpoint.py

chapter-10-baseline:
	$(PYTHON) checkpoints/chapter-10/baseline.py

chapter-10-checkpoint:
	$(PYTHON) checkpoints/chapter-10/checkpoint.py

chapter-11-baseline:
	$(PYTHON) checkpoints/chapter-11/baseline.py

chapter-11-checkpoint:
	$(PYTHON) checkpoints/chapter-11/checkpoint.py

chapter-12-baseline:
	$(PYTHON) checkpoints/chapter-12/baseline.py

chapter-12-checkpoint:
	$(PYTHON) checkpoints/chapter-12/checkpoint.py

chapter-13-baseline:
	$(PYTHON) checkpoints/chapter-13/baseline.py

chapter-13-checkpoint:
	$(PYTHON) checkpoints/chapter-13/checkpoint.py

chapter-14-baseline:
	$(PYTHON) checkpoints/chapter-14/baseline.py

chapter-14-checkpoint:
	$(PYTHON) checkpoints/chapter-14/checkpoint.py
