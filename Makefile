# Copyright (C) 2017-2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017-2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

# DebOps Makefile

# Use the Bash shell by default
SHELL := /bin/bash

SPHINXFLAGS ?= -n -W

.PHONY: all
all: help

.PHONY: help
help:
	@printf "%s\n" "Useful targets:"
	@egrep '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  make %-20s\033[0m %s\n", $$1, $$2}'

.PHONY: check
check:          ## Perform project sanity checks
check: dev-version fail-if-git-dirty

.PHONY: clean
clean:          ## Clean up project directory
clean: clean-tests clean-sdist clean-wheel clean-collections

.PHONY: clean-git
clean-git:      ## Clean up directories and files ignored by git
clean-git:
	@git clean -X -d -f

.PHONY: collection
collection:     ## Build collection of Ansible artifacts with ansible-galaxy
collection: make-collection

.PHONY: credits
credits:        ## Generate the CREDITS file from git history
credits: test-credits
	@git add -f CREDITS

.PHONY: test-credits
test-credits:   ## Generate the CREDITS file without staging it
test-credits:
	@lib/credits/generate-credits

.PHONY: spdx
spdx:          ## Check copyright and license information (REUSE, SPDX)
spdx: test-spdx

.PHONY: versions
versions:       ## Check versions of upstream software
versions: check-versions

.PHONY: dev-version
dev-version:    ## Stamp the generated version files from git describe
dev-version:
	@lib/ansible-galaxy/stamp-version

.PHONY: git-hooks
git-hooks:      ## Enable the git hooks for this development tree
git-hooks:
	@git config core.hooksPath lib/git-hooks

.PHONY: docker
docker:         ## Check Docker image build
docker: test-docker-build

.PHONY: spell
spell:          ## Check common misspellings using codespell
spell: test-spell

.PHONY: docs
docs:           ## Build Sphinx documentation
docs: test-docs

.PHONY: man
man:            ## Build manual pages from Sphinx documentation
man: test-man

.PHONY: links
links:          ## Check external links in documentation
links: check-links

.PHONY: pep8
pep8:           ## Test Python PEP8 compliance
pep8: test-pep8

.PHONY: shell
shell:           ## Test shell script syntax
shell: test-shell

.PHONY: syntax
syntax:         ## Check Ansible playbook syntax
syntax: test-playbook-syntax

.PHONY: lint
lint:           ## Check Ansible roles using ansible-lint
lint: test-ansible-lint

.PHONY: test
test:           ## Perform all DebOps tests
test: test-all

.PHONY: yaml
yaml:           ## Test YAML syntax using yamllint
yaml: test-yaml

.PHONY: unit
unit:           ## Run unit tests
unit: test-unit

.PHONY: integration
integration:    ## Run integration tests
integration: test-integration

.PHONY: coverage
coverage:       ## Run all tests with a combined coverage report
coverage: test-coverage

.PHONY: sdist
sdist:          ## Create Python sdist package
sdist: clean-sdist man test-credits
	@python3 setup.py sdist

.PHONY: sdist-quiet
sdist-quiet: clean-sdist test-credits
	@python3 setup.py --quiet sdist

.PHONY: sdist-sign
sdist-sign:     ## Create signed Python sdist package
sdist-sign: sdist
	@gpg --detach-sign --armor dist/debops-*.tar.gz

.PHONY: make-collection
make-collection: clean clean-git
	@if [ ! -f CREDITS ] ; then lib/credits/generate-credits ; fi
	@lib/ansible-galaxy/make-collection

.PHONY: clean-sdist
clean-sdist:
	@rm -vrf debops.egg-info dist/debops-*.tar.gz*

.PHONY: clean-collections
clean-collections:
	@rm -vrf dist/collections

.PHONY: wheel
wheel:          ## Create Python wheel package
wheel: clean-wheel man test-credits
	@python3 setup.py bdist_wheel

.PHONY: wheel-quiet
wheel-quiet: clean-wheel test-credits
	@python3 setup.py --quiet bdist_wheel

.PHONY: wheel-sign
wheel-sign:     ## Create signed Python wheel package
wheel-sign: wheel
	@gpg --detach-sign --armor dist/debops-*.whl

.PHONY: clean-wheel
clean-wheel:
	@rm -vrf build dist/debops-*.whl*

.PHONY: twine-upload
twine-upload:    ## Upload Python packages to PyPI
	@twine upload dist/*

.PHONY: test-all
test-all: clean-tests test-spdx test-pep8 test-unit test-integration test-debops-ansible_plugins test-spell test-docs test-man test-playbook-syntax test-ansible-lint test-yaml test-shell

.PHONY: test-unit
test-unit:
	@printf "%s\n" "Running unit tests using pytest..."
	@PYTHONPATH=src python3 -m pytest src/tests \
		--ignore=src/tests/integration \
		--cov=debops --cov-branch --cov-report=term-missing

.PHONY: test-integration
test-integration:
	@printf "%s\n" "Running integration tests using pytest..."
	@PYTHONPATH=src python3 -m pytest src/tests/integration

.PHONY: test-coverage
test-coverage:
	@printf "%s\n" "Running all tests with a combined coverage report..."
	@PYTHONPATH=src python3 -m pytest src/tests \
		--cov=debops --cov-branch --cov-report=term-missing \
		--cov-fail-under=94

.PHONY: test-pep8
test-pep8:
	@printf "%s\n" "Testing PEP8 compliance using pycodestyle..."
	@pycodestyle --show-source --statistics .
	@./lib/tests/check-pep8

.PHONY: test-shell
test-shell:
	@printf "%s\n" "Testing shell syntax using shellcheck..."
	@./lib/tests/check-shell

.PHONY: test-docker-build
test-docker-build:
	@./lib/tests/check-docker-build

.PHONY: test-smoke
test-smoke:     ## Test an installed DebOps wheel or sdist package
	@printf "%s\n" "Running the installed DebOps package smoke test..."
	@./lib/tests/check-installed-package

.PHONY: test-metadata
test-metadata:  ## Check the metadata of a built DebOps package
	@printf "%s\n" "Checking the built DebOps package metadata..."
	@./lib/tests/check-package-metadata

.PHONY: test-smoke-collection
test-smoke-collection:  ## Test an installed DebOps Ansible Collection
	@printf "%s\n" "Running the installed DebOps Collection smoke test..."
	@./lib/tests/check-installed-collection

.PHONY: test-spdx
test-spdx:
	@reuse lint

.PHONY: clean-tests
clean-tests:
	@rm -vrf .coverage docs/_build/* docs/ansible/roles/*/defaults.rst docs/ansible/roles/*/defaults
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} +

.PHONY: check-versions
check-versions:
	@./lib/tests/check-watch

.PHONY: test-spell
test-spell:
	@printf "%s\n" "Checking common misspellings using codespell..."
	@codespell

.PHONY: test-docs
test-docs:
	@printf "%s\n" "Testing HTML documentation generation..."
	@cd docs && sphinx-build $(SPHINXFLAGS) -b html -d _build/doctrees . _build/html

.PHONY: test-man
test-man:
	@printf "%s\n" "Testing man documentation generation..."
	@cd docs && sphinx-build -j auto -t manpages -n -W -b man \
		-d _build/doctrees . _build/man

.PHONY: check-links
check-links:
	@printf "%s\n" "Checking external links in documentation..."
	@cd docs && sphinx-build -n -b linkcheck -d _build/doctrees . _build/linkcheck

ansible.cfg:
	@printf "%s\n" "Generating new ansible.cfg file..."
	@./lib/tests/ansible-cfg-generator

.PHONY: install-collections
install-collections: ansible.cfg
	@printf "%s\n" "Installing Ansible Collection dependencies..."
	@ansible-galaxy collection install -v -r requirements.yml

.PHONY: test-playbook-syntax
test-playbook-syntax: ansible.cfg install-collections
	@printf "%s\n" "Testing Ansible playbook syntax..."
	@ANSIBLE_HOST_PATTERN_MISMATCH=ignore \
	 ansible-playbook --syntax-check ansible/playbooks/bootstrap.yml \
		                         ansible/playbooks/bootstrap-ldap.yml \
		                         ansible/playbooks/bootstrap-sss.yml \
		                         ansible/playbooks/site.yml

.PHONY: test-ansible-lint
test-ansible-lint: ansible.cfg
	@printf "%s\n" "Checking Ansible content using ansible-lint..."
	@ansible-lint -v

.PHONY: test-yaml
test-yaml:
	@printf "%s\n" "Testing YAML syntax using yamllint..."
	@yamllint .

.PHONY: test-debops-ansible_plugins
test-debops-ansible_plugins:
	@printf "%s\n" "Testing debops-ansible_plugins filter plugins..."
	@diff -q ansible/plugins/filter/debops_filter_plugins.py ansible/roles/ansible_plugins/filter_plugins/debops_filter_plugins.py
	@python3 ansible/plugins/filter/debops_filter_plugins.py

.PHONY: fail-if-git-dirty
fail-if-git-dirty:
	@git diff --quiet && git diff --cached --quiet || ( \
		printf "%s\n" "Sanity check: uncommitted git changes detected" ; \
		git status --short ; exit 1 )

.PHONY: pc precommit pre-commit
precommit:      ## Run pre-commit on all files
pc precommit pre-commit:
	@pre-commit run --all
