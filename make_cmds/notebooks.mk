#######################
#     Notebooks       #
#######################

.PHONY: kernel
kernel: ## Register the project environment as a Jupyter kernel (display name: fun).
	uv run python -m ipykernel install --user --name "puzzler" --display-name "fun"

.PHONY: check-notebooks
check-notebooks: ## Execute all notebooks to verify they run (uses project venv).
	@for nb in $(notebooks); do \
		uv run jupyter nbconvert --execute --to notebook --inplace "$$nb" || exit 1; \
	done
