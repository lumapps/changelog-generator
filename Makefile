PYTHON ?= python3.7
VIRTUAL_ENV ?= ./venv

$(VIRTUAL_ENV): setup.cfg setup.py dev-requirements.txt requirements.txt
	$(PYTHON) -m venv $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python -m pip install -e . -r dev-requirements.txt
	$(VIRTUAL_ENV)/bin/python -m pip install -e . -r requirements.txt
	touch $(VIRTUAL_ENV)  # Update venv mtime to tell make it's up to date

lint: check_format check_imports check_types check_pylint

check_types: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/mypy changelog_generator

check_imports: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/isort --check changelog_generator tests

check_format: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/black --check changelog_generator tests

check_pylint: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pylint changelog_generator tests

tests: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pytest

clean:
	rm -fr build/ dist/ .eggs/ changelog_generator.egg-info/

.PHONY: lint check_format check_types tests clean
