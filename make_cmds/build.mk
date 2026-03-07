#######################
#      Build          #
#######################

.PHONY: build
build: clean ## Build the package
	@$(call i, Building package)
	uv build

.PHONY: build-wheel
build-wheel: clean ## Build wheel distribution
	@$(call i, Building wheel)
	uv build --wheel

.PHONY: build-sdist
build-sdist: clean ## Build source distribution
	@$(call i, Building source distribution)
	uv build --sdist

.PHONY: publish
publish: build ## Publish to PyPI
	@$(call i, Publishing to PyPI)
	uv publish

.PHONY: publish-test
publish-test: build ## Publish to TestPyPI
	@$(call i, Publishing to TestPyPI)
	uv publish --publish-url https://test.pypi.org/legacy/

.PHONY: clean
clean: ## Clean up build artifacts and caches
	@$(call i, Cleaning up)
	@rm -rf $(cache.dir) $(checkpoint.dir) $(mypy.cache.dir) $(pytest.cache.dir) $(dist.dir) build/ *.egg-info/ htmlcov/ site/ .coverage .coverage.* coverage.xml
