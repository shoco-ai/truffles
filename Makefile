.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: setup-dev
setup-dev: ## Install poetry and all dev dependencies
	@if ! command -v poetry &> /dev/null; then \
		echo "Installing poetry..."; \
		curl -sSL https://install.python-poetry.org | python3 -; \
	fi
	@echo "Installing dependencies..."
	@poetry install --only dev
	@echo "Installing pre-commit & pre-commit hooks"
	@pip install pre-commit
	@pre-commit install

.PHONY: ruff
ruff: ## Run ruff for linting and formatting. Use fix=1 for autofix or specify path=path/to/file
	@poetry run ruff check $(if $(fix),--fix) $(path)
	@poetry run ruff format $(if $(fix),,--check) $(path)

.PHONY: test
test: ## Run with poetry in the current environment. Use ci=true to run all tests
	@poetry run tox
