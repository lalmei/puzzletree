#######################
#     Testing         #
#######################

.PHONY: test
test: clean ## Run all tests
	@$(call i, Running tests)
	uv run pytest -c=config/pytest.ini tests/

.PHONY: test-unit
test-unit: clean ## Run unit tests only
	@$(call i, Running unit tests)
	uv run pytest -c=config/pytest.ini -m "unit" tests/

.PHONY: test-coverage
test-coverage: clean ## Run tests with coverage report
	@$(call i, Running tests with coverage)
	uv run pytest -c=config/pytest.ini --cov=src/puzzler --cov-report=term-missing --cov-report=html tests/

.PHONY: test-coverage-report
test-coverage-report: clean ## Run tests with coverage report (no fail-under; for CI/reporting)
	@$(call i, Running tests with coverage)
	uv run pytest -c=config/pytest.ini --cov=src/puzzler --cov-report=term-missing --cov-report=html --cov-fail-under=0 tests/

.PHONY: test-fast
test-fast: clean ## Run fast tests (skip slow ones)
	@$(call i, Running fast tests)
	uv run pytest -c=config/pytest.ini -m "not slow" tests/

.PHONY: test-parallel
test-parallel: clean ## Run all tests in parallel (faster; use -n 0 for debugging)
	@$(call i, Running tests in parallel)
	uv run pytest -c=config/pytest.ini -n auto tests/
