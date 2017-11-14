# DebOps Makefile

.PHONY: all
all:

.PHONY: help
help:
	@printf "%s\n" "Useful targets:"
	@egrep '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  make %-20s\033[0m %s\n", $$1, $$2}'

.PHONY: check
check:          ## Perform project sanity checks
check: fail-if-git-dirty

.PHONY: clean
clean:          ## Clean up project directory
clean: clean-tests

.PHONY: docker
docker:         ## Check Docker image build
docker: test-docker-build

.PHONY: docs
docs:           ## Build Sphinx documentation
docs: test-docs

.PHONY: pep8
pep8:           ## Test Python PEP8 compliance
pep8: test-pep8

.PHONY: syntax
syntax:         ## Check Ansible playbook syntax
syntax: test-playbook-syntax

.PHONY: test
test:           ## Perform all DebOps tests
test: test-all

.PHONY: yaml
yaml:           ## Test YAML syntax using yamllint
yaml: test-yaml

.PHONY: test-all
test-all: clean-tests test-pep8 test-debops-tools test-docs test-playbook-syntax test-yaml test-docker-build

.PHONY: test-pep8
test-pep8:
	@printf "%s\n" "Testing PEP8 compliance using pycodestyle..."
	@pycodestyle --show-source --statistics .
	@./lib/tests/check-pep8 || true

.PHONY: test-docker-build
test-docker-build:
	@./lib/tests/check-docker-build

.PHONY: clean-tests
clean-tests:
	@rm -vrf .coverage docs/_build/*

.PHONY: test-docs
test-docs:
	@printf "%s\n" "Testing HTML documentation generation..."
	@cd docs && sphinx-build -n -W -b html -d _build/doctrees . _build/html

.PHONY: test-playbook-syntax
test-playbook-syntax:
	@printf "%s\n" "Testing Ansible playbook syntax..."
	@ANSIBLE_ROLES_PATH="ansible/roles" ansible-playbook --syntax-check \
		ansible/playbooks/bootstrap.yml \
		ansible/playbooks/site.yml

.PHONY: test-yaml
test-yaml:
	@printf "%s\n" "Testing YAML syntax using yamllint..."
	@yamllint . || true

.PHONY: test-debops-tools
test-debops-tools:
	@printf "%s\n" "Testing debops-tools using nose2..."
	@nose2 --start-dir=lib/debops-tools --with-coverage

.PHONY: fail-if-git-dirty
fail-if-git-dirty:
	@git diff --quiet && git diff --cached --quiet || ( \
		printf "%s\n" "Sanity check: uncommited git changes detected" ; \
		git status --short ; exit 1 )
