install:
	pip install --edit .[test]

test:
	pylint --rcfile=.pylintrc --reports=y --exit-zero customerio/analytics
	flake8 --max-complexity=10 --statistics customerio/analytics || true
	python -m unittest customerio/analytics/test/*.py -v

.PHONY: install test
