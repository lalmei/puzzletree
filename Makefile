SHELL := bash


version := 0.8.1

# ----------------
# Image Tagging
# ----------------
# Prefer an explicit repo tag (e.g. vX.Y.Z). If none exists for HEAD, fall back to <version>-<short-sha>.
# Works both locally and in CI (e.g. GitLab provides CI_COMMIT_TAG / CI_COMMIT_SHA).

git.tag := $(strip $(or $(CI_COMMIT_TAG),$(shell git describe --tags --exact-match 2>/dev/null)))
git.sha := $(strip $(or $(CI_COMMIT_SHORT_SHA),$(shell git rev-parse --short=8 HEAD 2>/dev/null)))

# Final docker image tag
image.tag := $(if $(git.tag),$(git.tag),$(version)-$(git.sha))

src.python := $(shell find ./src -type f -name "*.py" || :)
test.unit.python := $(shell find ./tests -type f -name "*.py" || :)
src.python.pyc := $(shell find ./src -type f -name "*.pyc")
cache.dir := $(shell find . -type d -name __pycache__)
checkpoint.dir := $(shell find . -type d -name .ipynb_checkpoints)
mypy.cache.dir := $(shell find . -type d -name ".mypy_cache")
pytest.cache.dir := $(shell find . -type d -name ".pytest_cache" )


deployments.dir := deployment
uv.project.enviroment := .venv
dist.dir := dist

build.wheel := $(dist.dir)/puzzletree-$(version).tar.gz

docker.image := puzzletree_base
docker.image.deploy := puzzletree

docker.image.registry := docker.io

# deployments.instances := $(shell find $(deployments.dir) -type d -mindepth 1 -maxdepth 2)
# Containerization: build each deployment subfolder via Make
# subdirs := $(patsubst $(deployments.dir)/%,%,$(deployments.instances))


build.wheel := $(dist.dir)/puzzletree-$(version).tar.gz


uv.project.enviroment := .venv

include make_cmds/uv.mk
include make_cmds/setup-ide.mk
include make_cmds/quality.mk
include make_cmds/tests.mk
include make_cmds/documentation.mk
include make_cmds/build.mk

.PHONY: checks
checks: check ## Alias for check

.PHONY: tests
tests: test ## Alias for test

##############
# Versioning #
##############

.PHONY: bump-patch
bump-patch: ## Bump the patch version (_._.X) everywhere.
	@$(call i, Bumping the patch number)
	poetry run bump2version patch --allow-dirty --verbose --config-file config/.bumpversion.cfg

.PHONY: bump-minor
bump-minor: ## Bump the minor version (_.X._) everywhere.
	@$(call i, Bumping the minor number)
	poetry run bump2version minor --allow-dirty --verbose --config-file config/.bumpversion.cfg

.PHONY: bump-major
bump-major: ## Bump the major version (X._._) everywhere.
	@$(call i, Bumping the major number)
	poetry run bump2version major --allow-dirty --verbose --config-file config/.bumpversion.cfg

.PHONY: bump-release
bump-release: ## Convert the version into a release variant (_._._).
	@$(call i, Converting to release)
	poetry run bump2version release --allow-dirty --verbose --config-file config/.bumpversion.cfg

.PHONY: bump-dev
bump-dev: ## Convert the version into a dev variant (_._._-dev__).
	@$(call i, Converting to dev)
	poetry run bump2version dev --allow-dirty --verbose --config-file config/.bumpversion.cfg

.PHONY: bump-build
bump-build: ## Bump the build number (_._._-____XX) everywhere.
	@$(call i, Bumbing the build number)
	poetry run bump2version build --allow-dirty --verbose --config-file config/.bumpversion.cfg




#####################
# Docker Unit Tests #
#####################

.PHONY: docker-build
docker-build: clean ## Build docker image (tag = vX.Y.Z if repo is tagged, else <version>-<sha>).
	docker build -t ${docker.image}:${image.tag} \
		--label org.label-schema.vcs-ref=${CI_COMMIT_SHA} \
		--label org.label-schema.vcs-url=${CI_PROJECT_URL} \
		--label com.climate.ci.job-url=${CI_JOB_URL} -f Dockerfile.dev .

.PHONY: docker-test
docker-test: clean ## Test in a clean container in your local machine.
	$(call i, Running tests in container)
	docker run --rm  \
		--mount type=bind,source=${PWD}/,target=/root/project,bind-propagation=private \
		--mount type=bind,source=${HOME}/.ssh,target=/root/.ssh,bind-propagation=private \
		--mount type=bind,source=${HOME}/.aws,target=/root/.aws,bind-propagation=private \
		${docker.image}:${image.tag} make release


.PHONY: docker-env
docker-env: clean ## Run an interactive container in your local machine.
	$(call i, Jumping in base docker env)
	docker run --rm  -it  \
		--mount type=bind,source=${PWD}/,target=/root/project,bind-propagation=private \
		--mount type=bind,source=${HOME}/.ssh,target=/root/.ssh,bind-propagation=private \
		--mount type=bind,source=${HOME}/.aws,target=/root/.aws,bind-propagation=private \
		${docker.image}:${image.tag} bash

.PHONY: help
help: ## Print the help screen.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":|:[[:space:]].*?##"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

##################
# User Functions #
##################

define BROWSER_PYSCRIPT
import os, webbrowser, sys
from urllib.request import pathname2url

webbrowser.open(sys.argv[1])
endef
export BROWSER_PYSCRIPT
BROWSER := uv run python -c "$$BROWSER_PYSCRIPT"

define i
echo
python3 scripts/colors.py INFO "$1"
echo
endef

define w
echo
python3 scripts/colors.py WARN "$1"
echo
endef

define e
echo
python3 scripts/colors.py ERROR "$1"
echo
endef
