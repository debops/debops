.PHONY: check FORCE_MAKE

## help {{{
.PHONY: list
# https://stackoverflow.com/a/26339924/2239985
list:
	@echo "This Makefile has the following targets:"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^(:?[^[:alnum:]]|FORCE_MAKE$$)' -e '^$@$$' | sed 's/^/    /'
## }}}

check: tests/api_data
	## Fail when git working directory for the Make prerequisites has changed.
	git diff --quiet --exit-code HEAD -- $^

tests/api_data: bin/debops-api FORCE_MAKE
	"$<" -r tests/example_roles/ -D 'http://docs.debops.org/en/latest/ansible/roles/ansible-{name}/docs/index.html' -a "$@" -o debops
