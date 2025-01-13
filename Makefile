PYTHON ?= python3.12
VIRTUAL_ENV ?= ./venv

$(VIRTUAL_ENV): setup.cfg setup.py dev-requirements.txt requirements.txt
	$(PYTHON) -m venv $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python -m pip install uv
	$(VIRTUAL_ENV)/bin/python -m uv pip install -e . -r dev-requirements.txt -r requirements.txt
	touch $(VIRTUAL_ENV)  # Update venv mtime to tell make it's up to date

requirements.txt: requirements.in
	$(VIRTUAL_ENV)/bin/python -m uv pip compile --quiet --generate-hashes --strip-extras --python-platform=linux $< -o $@

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
