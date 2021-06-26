VENV = .venv
init:
	python3.9 -m venv $(VENV)
	poetry install

pretty:
	isort .
	black --line-length 79 .

lint:
	flake8 --exclude $(VENV) --ignore E203,W503
	mypy --exclude $(VENV) .

plint: pretty lint

test:
	PYTHONPATH='.' pytest --cov-config=.coveragerc  --cov-report=html --cov=. .
	open -a Safari htmlcov/index.html
