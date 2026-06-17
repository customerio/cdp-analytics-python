install:
	pip install --edit .[test]

test:
	python -m unittest customerio/analytics/test/*.py -v

lint:
	pylint --rcfile=.pylintrc --reports=y --exit-zero customerio/analytics
	flake8 --max-complexity=10 --statistics customerio/analytics || true

.PHONY: install test lint
