PYTHON ?= python

.PHONY: check structure test

check: structure test

structure:
	$(PYTHON) scripts/validate_project_structure.py

test:
	$(PYTHON) -m pytest
