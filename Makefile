install:
	pip install -r dev-requirements.txt

format:
	black .
	isort .

lint:
	ruff check .
	flake8
	mypy .

check: format lint

pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files

.PHONY: install format lint check pre-commit-install pre-commit-run
