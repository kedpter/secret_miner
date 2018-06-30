.PHONY: clean clean-test clean-pyc clean-build docs help
.PHONY: offline-download offline-install offline-clean binary binary-clean install
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

docs: ## generate Sphinx HTML documentation, including API docs
	python pjutils.py sphinx --quickstart
	python pjutils.py sphinx --gen-code-api
	python pjutils.py sphinx --rst2html
	$(BROWSER) docs/html/index.html

clean: clean-build clean-pyc offline-clean binary-clean

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

offline-download: ## offline distribution download dependent packages
	python pjutils.py offline_dist --freeze-deps
	python pjutils.py offline_dist --download-deps

offline-install: ## offline distribution install dependent packages
	python pjutils.py offline_dist --install-deps

offline-clean: ## clean packages
	python pjutils.py offline_dist --clean-deps

binary: ## convert script to binary code
	python pjutils.py offline_dist --mkbinary cli.py

binary-clean: ## clean binary files
	python pjutils.py offline_dist --clean-binary

install: clean ## install the package to the active Python's site-packages
	python setup.py install

pypi-upload:
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twin upload dist/*

