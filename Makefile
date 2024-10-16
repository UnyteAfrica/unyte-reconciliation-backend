LINT_PATHS = agents/ insurer/ user/ reconciliation_backend/ merchants/ loader.py manage.py

ifneq (,$(wildcard ./.env.local))
    include .env.local
    export
endif

lint:
	@ruff check

lint-fix:
	@ruff check $(LINT_PATHS) --fix

format:
	@ruff format $(LINT_PATHS)