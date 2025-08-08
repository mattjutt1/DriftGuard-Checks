.PHONY: dev test run
dev:
	pip install -e .[dev]
test:
	pytest -q
run:
	uvicorn driftguard.main:app --reload
