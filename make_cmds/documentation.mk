#######################
#   Documentation     #
#######################

.PHONY: docs
docs: ## Build documentation
	@$(call i, Building documentation)
	uv run mkdocs build --config-file=config/mkdocs.yml

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	@$(call i, Serving documentation)
	uv run mkdocs serve --config-file=config/mkdocs.yml

.PHONY: docs-check
docs-check: ## Check documentation for issues
	@$(call i, Checking documentation)
	uv run mkdocs build --config-file=config/mkdocs.yml --strict

.PHONY: check-docs
check-docs: docs-check ## Alias for docs-check
