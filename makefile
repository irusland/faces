VENV = .venv
TESTS = tests
init:
	python3.9 -m venv $(VENV)
	poetry install

pretty:
	poetry run isort .
	poetry run black --line-length 79 .

lint:
	poetry run flake8 --exclude $(VENV) --ignore E203,W503
	export MYPYPATH=./stubs
	poetry run mypy --exclude $(VENV) --exclude $(TESTS) .

plint: pretty lint

test:
	PYTHONPATH='.' poetry run pytest --cov-config=.coveragerc $(PYTEST_ADDOPTS) .

html-test:
	make test PYTEST_ADDOPTS="--cov-report=html --cov=."

xml-test:
	make PYTEST_ADDOPTS="--cov-report=xml --cov=." test

hopen:
	open -a Safari htmlcov/index.html
