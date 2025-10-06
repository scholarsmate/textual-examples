# Makefile for setting up and running the Textual examples

# Uses a virtual environment in .venv
VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
PIPCOMPILE=$(VENV)/bin/pip-compile
# Windows fallback
ifeq ($(OS),Windows_NT)
	PY=$(VENV)/Scripts/python.exe
	PIP=$(VENV)/Scripts/pip.exe
	PIPCOMPILE=$(VENV)/Scripts/pip-compile.exe
endif

# Phony targets to avoid conflicts with files of the same name
.PHONY: venv install lint test task budget clean

venv:
	python -m venv $(VENV)

requirements.txt: venv requirements.in
	$(PIP) install pip-tools
	$(PIPCOMPILE) requirements.in

install: venv requirements.txt
	$(PY) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

task:
	$(PY) task_app.py

budget:
	$(PY) budget_app.py

test: install
	$(PY) -m pytest

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache htmlcov .coverage

lint: venv requirements.txt
	$(PIP) install -r requirements.txt
	$(PIP) install pre-commit
	$(PY) -m pre_commit run --all-files || true
