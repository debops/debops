.PHONY : default all check fail-when-git-dirty

.PHONY: FORCE_MAKE

default: all

all: galaxy

check: all fail-when-git-dirty

fail-when-git-dirty:
	git diff --quiet && git diff --cached --quiet

galaxy: galaxy/requirements galaxy/requirements-testing
	@echo 'You need to `git add` all files in order for this script to pick up the changes!'

galaxy/requirements: galaxy/requirements.txt galaxy/requirements.yml

galaxy/requirements.txt: scripts/get_all_referenced_roles FORCE_MAKE
	"$<" > "$@"

galaxy/requirements.yml: scripts/get_all_referenced_roles FORCE_MAKE
	"$<" | sed --regexp-extended 's/^(.*)$$/- src: \1\n/' > "$@"


galaxy/requirements-testing: galaxy/requirements-testing.txt galaxy/requirements-testing.yml

galaxy/requirements-testing.txt: scripts/get_all_referenced_roles FORCE_MAKE
	"$<" | sed --regexp-extended 's/^(.*)$$/\1,testing/' > "$@"

galaxy/requirements-testing.yml: scripts/get_all_referenced_roles FORCE_MAKE
	"$<" | sed --regexp-extended 's/^(.*)$$/- src: \1\n  version: testing\n/' > "$@"
