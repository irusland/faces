VENV = .venv
TESTS = tests
CODE = code
STUBS = ./stubs
init:
	python3.9 -m venv $(VENV)
	poetry install

pretty:
	poetry run isort --profile "black" --line-length 79 .
	poetry run black --line-length 79 .

lint:
	poetry run flake8 --exclude $(VENV) --ignore E203,W503
	MYPYPATH=$(STUBS) poetry run mypy --exclude $(VENV) --exclude $(TESTS) $(CODE)

plint: pretty lint

test:
	PYTHONPATH='.' poetry run pytest --cov-config=.coveragerc $(PYTEST_ADDOPTS) .

html-test:
	make test PYTEST_ADDOPTS="--cov-report=html --cov=."

xml-test:
	make PYTEST_ADDOPTS="--cov-report=xml --cov=." test

hopen:
	open -a Safari htmlcov/index.html

prepare:
	docker run --name redis-db --publish=6379:6379 --hostname=redis --restart=on-failure --detach redis

redis:
	docker stop redis-db
	docker start redis-db

redis-save:
	docker cp redis-db:/data/dump.rdb /dump.rdb
