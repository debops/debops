## The Makefile is expected to be called from the root of the repository even when it is not stored their.
# PWD := $(shell git rev-parse --show-toplevel)

.PHONY: default
default: help

.PHONY: help
help:
	@echo The test suite that this Makefile contains is consider dangerous!
	@echo Only run it if you know what you are doing.
	@echo The bundled pre-commit hook runs the checks of this Makefile in an isolated environment.

.PHONY: check
check: check-migration-scripts-idempotent \
	fail-when-git-dirty

.PHONY: fail-when-git-dirty
fail-when-git-dirty:
	git diff --quiet

## Run the migration scripts using the role repository itself as test input.
## The scripts are idempotent and thus should not make any changes to the given input.
## If they do, the test fails.
.PHONY: check-migration-scripts-idempotent
check-migration-scripts-idempotent: docs/scripts/
	find "$<" -type f -name 'upgrade-from*' -print0 | xargs --null sh

.PHONY: run-pre-commit-hook
run-pre-commit-hook: docs/_tests/hooks/pre-commit
	"$<"

.PHONY: install-pre-commit-hook
install-pre-commit-hook: docs/_tests/hooks/pre-commit
	ln -srf "$<" "$(shell git rev-parse --git-dir)/hooks"

.PHONY: install-pre-commit-hook
remove-pre-commit-hook: docs/_tests/hooks/pre-commit
	rm -f "$(shell git rev-parse --git-dir)/hooks/pre-commit"
