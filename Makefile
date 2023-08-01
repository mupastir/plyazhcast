.PHONY: all \
		setup-venv \
		setup-base \
		setup-lint \
		setup-mypy \
		setup-tests \
		setup-dev \
		clean \
		lint \
		run \
		dev

PIP_VERSION = 23.2.1

venv/bin/activate: ## alias for virtual environment
	python -m venv venv

all: setup-dev ## project setup

setup-venv: venv/bin/activate ## base venv setup
	. venv/bin/activate; pip install pip==${PIP_VERSION} wheel setuptools

setup-base: setup-venv ## project setup for instances
	. venv/bin/activate; pip install --exists-action w -Ur requirements/base.txt

setup-lint: setup-venv ## project setup for instances
	. venv/bin/activate; pip install --exists-action w -Ur requirements/lint.txt

setup-mypy: setup-venv ## project setup for instances
	. venv/bin/activate; pip install --exists-action w -Ur requirements/mypy.txt

setup-test: setup-venv ## project setup for instances
	. venv/bin/activate; pip install --exists-action w -Ur requirements/testing.txt

setup-dev: setup-base ## project setup for development
	. venv/bin/activate; pip install --exists-action w -Ur requirements/development.txt
	. venv/bin/activate; pre-commit install

run: venv/bin/activate ## Local Run Flask App
	export FLASK_APP=plyazhcast
	export FLASK_ENV=development
	. venv/bin/activate; flask run

t: venv/bin/activate ## Run tests
	. venv/bin/activate; pytest -vv -W ignore

tw: venv/bin/activate ## Run tests with Warnings
	. venv/bin/activate; pytest -vv

clean: clean-build clean-pyc clean-test clean-merge ## remove all build, test, coverage and Python artifacts
clean-merge: ## remove merge artifacts
	find . -name '*.orig' -exec rm -fr {} +
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
clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	find . -name '.pytest_cache' -exec rm -fr {} +

dev: venv/bin/activate ## Run Flask App localy
	export FLASK_APP=plyazhcast
	. venv/bin/activate; flask run

lint: venv/bin/activate ## linter. TODO: make linter 0 errors
	. venv/bin/activate; \
	MYPY_ERR=$$(flake8 | wc -l); \
	if [ $$MYPY_ERR -gt 0 ]; then\
		echo "Too many lint errors $$MYPY_ERR" && exit 1;\
	else\
		echo "ZERO!";\
	fi

mypy: venv/bin/activate ## mypy.
	. venv/bin/activate; \
	MYPY_ERR=$$(mypy --allow-redefinition app | wc -l); \
	if [ $$MYPY_ERR -gt 1 ]; then\
		echo "Too many lint errors $$MYPY_ERR" && exit 1;\
	else\
		echo "ZERO!";\
	fi

file_to_black = ./app
black: venv/bin/activate ## isort and black
	. venv/bin/activate; isort $(file_to_black); black $(file_to_black)

help: ## Display this help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
