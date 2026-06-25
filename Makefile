PYTHON ?= python3

install:
	$(PYTHON) -m pip install .

build:
	rm -rf build
	$(PYTHON) -m build

test:
	$(PYTHON) -m unittest customerio/analytics/test/*.py -v

lint:
	$(PYTHON) -m pylint --rcfile=.pylintrc --reports=y --exit-zero customerio/analytics
	$(PYTHON) -m flake8 --max-complexity=10 --statistics --exit-zero customerio/analytics

lint-ci:
	$(PYTHON) -m pylint --rcfile=.pylintrc --exit-zero --fail-on=E customerio/analytics
	$(PYTHON) -m flake8 --max-complexity=10 --max-line-length=100 --statistics customerio/analytics

clean:
	rm -rf MANIFEST build dist customerio.egg-info

clean-venv:
	rm -rf .venv
	mise deps

.PHONY: install build test lint lint-ci clean clean-venv
