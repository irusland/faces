VENV = .venv
init:
	python3.9 -m venv $(VENV)
	poetry install

pretty:
	python -m isort .
	python -m black --line-length 79 .

lint:
	python -m flake8 --exclude $(VENV) --ignore E203,W503
	python -m mypy --exclude $(VENV) .

plint: pretty lint

ctest:
	PYTHONPATH='.' python -m pytest --cov-config=.coveragerc --cov-report=html --cov=. .

copen:
	open -a Safari htmlcov/index.html
