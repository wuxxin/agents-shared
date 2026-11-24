# Makefile for agents-shared

SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c
.DEFAULT_GOAL := help

VENV ?= .venv
VENV_BIN = $(VENV)/bin
PYTHON = $(if $(wildcard $(VENV_BIN)/python),$(VENV_BIN)/python,python3)
MKDOCS_DEPS = mkdocs mkdocs-material mkdocs-include-markdown-plugin pymdown-extensions

.PHONY: help buildenv docs docs-online-build docs-serve docs-clean clean cleanenv

help: ## Show this help message and list available targets
	@echo "========================================================================"
	@echo "                 agents-shared Build & Docs Targets"
	@echo "========================================================================"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Active Runtime Configuration:"
	@echo "  Virtualenv:       $(VENV)"
	@echo "  Python Binary:    $(PYTHON)"
	@echo "========================================================================"

buildenv: ## Provision local virtual environment with uv and install docs dependencies
	@if [ ! -d "$(VENV)" ]; then \
		echo "==> Creating virtual environment in $(VENV)..."; \
		uv venv $(VENV); \
	fi
	@if [ ! -x "$(VENV_BIN)/mkdocs" ]; then \
		echo "==> Installing MkDocs dependencies..."; \
		uv pip install --python $(VENV_BIN)/python $(MKDOCS_DEPS); \
	fi

docs: buildenv ## Build docs for local file:// browsing
	@echo "==> Building MkDocs site for local usage..."
	@mkdir -p build/docs
	@$(VENV_BIN)/mkdocs build --no-directory-urls -d build/docs -f mkdocs.yml
	@echo "Finished. Browse at file://$(CURDIR)/build/docs/index.html"

docs-online-build: buildenv ## Build docs for HTTP serving
	@echo "==> Building MkDocs site for HTTP serving..."
	@mkdir -p build/docs-online
	@$(VENV_BIN)/mkdocs build -d build/docs-online -f mkdocs.yml
	@echo "Finished. Serve with: $(PYTHON) -m http.server --directory build/docs-online"

docs-serve: buildenv ## Rebuild and serve docs with autoreload
	@$(VENV_BIN)/mkdocs serve -f mkdocs.yml

docs-clean: ## Remove generated MkDocs output
	@rm -rf build/docs build/docs-online

clean: docs-clean ## Remove build outputs and Python caches
	@find . \( -name .git -o -path ./scratch -o -path ./$(VENV) \) -prune -o \
	    -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache \) \
	        -exec rm -rf {} + \
	    -o -type f \( -name '*.py[cod]' -o -name '*$$py.class' \) -print0 2>/dev/null \
	    | xargs -0 -r rm -f

cleanenv: clean ## Remove virtual environment and all caches
	@echo "==> Removing virtual environment $(VENV)..."
	@rm -rf $(VENV)
