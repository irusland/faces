VENV = .venv
init:
	python3.9 -m venv $(VENV)
	poetry install
