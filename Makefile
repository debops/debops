PIP_OPTIONS =
NOSE_OPTIONS =

.PHONY: FORCE_MAKE

.PHONY: default
default: list

## list targets (help) {{{
.PHONY: list
# https://stackoverflow.com/a/26339924/2239985
list:
	@echo "This Makefile has the following targets:"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^(:?[^[:alnum:]]|FORCE_MAKE$$)' -e '^$@$$' | sed 's/^/    /'
## }}}

## Fail when git working directory for the Make prerequisites has changed.
.PHONY: check
check: tests/api_data check-nose2
	find tests/api_data -type f -print0 | xargs --null sed --in-place --regexp-extended '/meta name="generator"/d'
	git diff --exit-code HEAD -- "$<"

tests/api_data: bin/debops-api tests/example_roles FORCE_MAKE
	"$<" --test-mode --role-path tests/example_roles/ --api-dir "$@"

.PHONY: pre-commit-hook
pre-commit-hook: hooks/pre-commit
	ln -srf "$<" "$(shell git rev-parse --git-dir)/hooks"

.PHONY: install-dependencies
install-dependencies:
	pip3 install $(PIP_OPTIONS) -r ./docs/_prepare/requirements.txt

.PHONY: check-nose
check-nose:
	nosetests $(NOSE_OPTIONS)

.PHONY: check-nose2
check-nose2:
	(nose2-3 --start-dir tests $(NOSE_OPTIONS) || nose2-3.4 $(NOSE_OPTIONS))
