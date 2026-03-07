#######################
#   IDE Setup         #
#######################

.PHONY: setup-cursor
setup-cursor: ## Copy Cursor config from config/cursor to .cursor
	@mkdir -p .cursor
	@cp -r config/cursor/* .cursor/
	@echo "Cursor configuration synced to .cursor/"

.PHONY: setup-vscode
setup-vscode: ## Copy VS Code config from config/vscode to .vscode
	@mkdir -p .vscode
	@cp -r config/vscode/* .vscode/
	@echo "VS Code configuration synced to .vscode/"

.PHONY: setup-ide
setup-ide: setup-cursor setup-vscode ## Copy Cursor and VS Code config from config/ to project root
