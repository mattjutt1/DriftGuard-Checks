.PHONY: install dev test clean

install:
	pip install -e .

dev:
	pip install -e .[dev]

test:
	pytest -q tests/

clean:
	rm -rf __pycache__ .pytest_cache *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
