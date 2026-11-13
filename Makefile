SHELL := /bin/bash
.DEFAULT_GOAL := help
export PYTHONPATH := src

help: ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[1m%-12s\033[0m %s\n", $$1, $$2}'

demo: ## triage a ticket in mock mode (no key, deterministic)
	@python3 -m foundry run --case evals/cases/01-refund.json --mock

demo-live: ## same, against the configured provider
	@python3 -m foundry run --case evals/cases/01-refund.json

eval: ## run the golden set and print a pass/fail table
	@python3 -m foundry eval

trace: ## pretty-print the most recent trace
	@python3 -m foundry trace --last

test: ## unit tests (no network)
	python3 -m unittest discover -s tests -v

lint: ## byte-compile + shell syntax
	@python3 -m compileall -q src tests && echo "compile: ok"
	@bash -n scripts/*.sh 2>/dev/null || true

clean: ## remove traces and caches
	@rm -f traces/*.jsonl; find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "cleaned"

.PHONY: help demo demo-live eval trace test lint clean
