.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install-deps
install-deps: ## Install dependencies for contributing
	@echo "Installing pre-commit & pre-commit hooks"
	@pip install pre-commit
	@pre-commit install
	@echo "Basic dependencies for contributing installed."

.PHONY: ruff
ruff: ## Run ruff for linting and formatting. Use fix=1 for autofix or specify path=path/to/file
	@echo "Linting with ruff"
	@ruff check $(if $(fix),--fix) $(path)
	@echo "Formatting with ruff"
	@ruff format $(if $(fix),,--check) $(path)
