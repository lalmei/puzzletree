#######################
#      Setup          #
#######################

.PHONY: setup
setup: ## Install dependencies using uv
	@$(call i, Setting up development environment)
	uv sync

.PHONY: install
install: setup ## Alias for setup

.PHONY: sync
sync: ## Sync dependencies
	uv sync

.PHONY: lock
lock: ## Update lock file
	uv lock

.PHONY: lock-upgrade
lock-upgrade: ## Upgrade lock file
	uv lock --upgrade


.PHONY: add-dev
add-dev: ## Add a development dependency (usage: make add-dev PACKAGE=package-name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Usage: make add-dev PACKAGE=package-name"; \
		exit 1; \
	fi
	uv add group dev $(PACKAGE)

.PHONY: tree
tree: ## Show dependency tree
	uv tree

.PHONY: run
run: ## Run a command (usage: make run CMD="python script.py")
	@if [ -z "$(CMD)" ]; then \
		echo "Usage: make run CMD=\"python script.py\""; \
		exit 1; \
	fi
	uv run $(CMD)
