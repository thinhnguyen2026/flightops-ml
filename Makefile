.PHONY: install test lint format

install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check src tests
	mypy src

format:
	ruff format src tests
