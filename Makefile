.PHONY: check FORCE_MAKE

## help {{{
.PHONY: list
# https://stackoverflow.com/a/26339924/2239985
list:
	@echo "This Makefile has the following targets:"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^(:?[^[:alnum:]]|FORCE_MAKE$$)' -e '^$@$$' | sed 's/^/    /'
## }}}

## Fail when git working directory for the Make prerequisites has changed.
check: tests/api_data
	git diff --quiet --exit-code HEAD -- $^

tests/api_data: bin/debops-api tests/example_roles FORCE_MAKE
	"$<" --test-mode --role-path tests/example_roles/ \
		--docs-url-pattern 'http://docs.debops.org/en/latest/ansible/roles/ansible-{name}/docs/index.html' \
		--role-owner debops \
		--api-dir "$@"
