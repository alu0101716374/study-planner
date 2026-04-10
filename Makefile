.PHONY: tests run

.PHONY: tests run clean lint help

help:
	@echo "Available commands:"
	@echo "  make tests   - Run all unit tests"
	@echo "  make run     - Start the Streamlit app"
	@echo "  make clean   - Remove cached files and logs"
	@echo "  make lint    - Check code with flake8"

tests:
	@echo "Running tests..."
	python3 -m pytest -v --tb=short

run:
	@echo "Running the app..."
	streamlit run app.py

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete."

lint:
	@echo "Running flake8 linter..."
	flake8 lib services pages --max-line-length=100 --ignore=E501,W503 || true