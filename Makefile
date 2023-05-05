install:
	pip install --edit .[test]

test:
	pylint --rcfile=.pylintrc --reports=y --exit-zero analytics
	flake8 --max-complexity=10 --statistics analytics || true
	python -m unittest customerio/analytics/test/*.py analytics/test/*.py

.PHONY: install test
