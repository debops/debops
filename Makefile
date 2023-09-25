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
check: fail-if-git-dirty

.PHONY: clean
clean:          ## Clean up project directory
clean: clean-tests clean-sdist clean-wheel

.PHONY: clean-git
clean-git:      ## Clean up directories and files ignored by git
clean-git:
	@git clean -X -d -f

.PHONY: collection
collection:     ## Build collection of Ansible artifacts with ansible-galaxy
collection: make-collection

.PHONY: spdx
spdx:          ## Check copyright and license information (REUSE, SPDX)
spdx: test-spdx

.PHONY: versions
versions:       ## Check versions of upstream software
versions: check-versions

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

.PHONY: sdist
sdist:          ## Create Python sdist package
sdist: clean-sdist man
	@python3 setup.py sdist

.PHONY: sdist-quiet
sdist-quiet: clean-sdist
	@python3 setup.py --quiet sdist

.PHONY: sdist-sign
sdist-sign:     ## Create signed Python sdist package
sdist-sign: sdist
	@gpg --detach-sign --armor dist/debops-*.tar.gz

.PHONY: make-collection
make-collection: clean clean-git
	@lib/ansible-galaxy/make-collection

.PHONY: clean-sdist
clean-sdist:
	@rm -vrf debops.egg-info dist/debops-*.tar.gz*

.PHONY: wheel
wheel:          ## Create Python wheel package
wheel: clean-wheel man
	@python3 setup.py bdist_wheel

.PHONY: wheel-quiet
wheel-quiet: clean-wheel
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
test-all: clean-tests test-spdx test-pep8 test-debops-tools test-debops-ansible_plugins test-spell test-docs test-man test-playbook-syntax test-ansible-lint test-yaml test-shell

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

.PHONY: test-spdx
test-spdx:
	@reuse lint

.PHONY: clean-tests
clean-tests:
	@rm -vrf .coverage docs/_build/* docs/ansible/roles/*/defaults.rst docs/ansible/roles/*/defaults

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
	@cd docs && sphinx-build -t manpages -n -W -b man -d _build/doctrees . _build/man

.PHONY: check-links
check-links:
	@printf "%s\n" "Checking external links in documentation..."
	@cd docs && sphinx-build -n -b linkcheck -d _build/doctrees . _build/linkcheck

.PHONY: test-playbook-syntax
test-playbook-syntax:
	@printf "%s\n" "Testing Ansible playbook syntax..."
	@ANSIBLE_ROLES_PATH="ansible/roles" ANSIBLE_HOST_PATTERN_MISMATCH=ignore \
	 ANSIBLE_COLLECTIONS_PATH="ansible/collections" \
	 ansible-playbook --syntax-check ansible/playbooks/bootstrap.yml \
		                         ansible/playbooks/bootstrap-ldap.yml \
		                         ansible/playbooks/bootstrap-sss.yml \
		                         ansible/playbooks/site.yml

.PHONY: test-ansible-lint
test-ansible-lint:
	@printf "%s\n" "Checking Ansible content using ansible-lint..."
	@ansible-lint -v

.PHONY: test-yaml
test-yaml:
	@printf "%s\n" "Testing YAML syntax using yamllint..."
	@yamllint .

.PHONY: test-debops-tools
test-debops-tools:
	@printf "%s\n" "Testing debops-tools using nose2..."
	@type nose2-3 > /dev/null && ( nose2-3 --with-coverage ) || nose2 --with-coverage

.PHONY: test-debops-ansible_plugins
test-debops-ansible_plugins:
	@printf "%s\n" "Testing debops-ansible_plugins using nose2..."
	@python3 ansible/roles/ansible_plugins/filter_plugins/debops_filter_plugins.py

.PHONY: fail-if-git-dirty
fail-if-git-dirty:
	@git diff --quiet && git diff --cached --quiet || ( \
		printf "%s\n" "Sanity check: uncommitted git changes detected" ; \
		git status --short ; exit 1 )

.PHONY: pc precommit pre-commit
precommit:      ## Run pre-commit on all files
pc precommit pre-commit:
	@pre-commit run --all
