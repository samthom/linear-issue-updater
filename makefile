.PHONY: run

run:
	uv run main.py

test:
	uv run pytest test_app.py --verbose

