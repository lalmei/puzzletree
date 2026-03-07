#######################
#     Quality         #
#######################

.PHONY: format
format: ## Format code using ruff
	@$(call i, Formatting code)
	uv run ruff format src/ tests/ --config=config/ruff.toml

.PHONY: format-check
format-check: ## Check if code is formatted correctly
	@$(call i, Checking code formatting)
	uv run ruff format --check src/ tests/ --config=config/ruff.toml

.PHONY: lint
lint: ## Lint code using ruff
	@$(call i, Linting code)
	uv run ruff check src/ tests/ --config=config/ruff.toml

.PHONY: fix
fix: ## Auto-fix linting issues
	@$(call i, Fixing linting issues)
	uv run ruff check --fix src/ tests/ --config=config/ruff.toml

.PHONY: check-types
check-types: ## Type check code using mypy
	@$(call i, Type checking code)
	uv run mypy src/puzzler/ --config-file=config/mypy.ini

.PHONY: type-check
type-check: check-types ## Alias for check-types

.PHONY: check
check: format-check lint check-types ## Run all quality checks

.PHONY: check-quality
check-quality: format-check lint ## Run formatting and linting checks
