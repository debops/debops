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
clean: clean-tests clean-sdist clean-wheel

.PHONY: docker
docker:         ## Check Docker image build
docker: test-docker-build

.PHONY: docs
docs:           ## Build Sphinx documentation
docs: test-docs

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
sdist: clean-sdist
	@python setup.py sdist

.PHONY: sdist-quiet
sdist-quiet: clean-sdist
	@python setup.py --quiet sdist

.PHONY: sdist-sign
sdist-sign:     ## Create signed Python sdist package
sdist-sign: sdist
	@gpg --detach-sign --armor dist/debops-*.tar.gz

.PHONY: clean-sdist
clean-sdist:
	@rm -vrf debops.egg-info dist/debops-*.tar.gz*

.PHONY: wheel
wheel:          ## Create Python wheel package
wheel: clean-wheel
	@python setup.py bdist_wheel

.PHONY: wheel-quiet
wheel-quiet: clean-wheel
	@python setup.py --quiet bdist_wheel

.PHONY: wheel-sign
wheel-sign:     ## Create signed Python wheel package
wheel-sign: wheel
	@gpg --detach-sign --armor dist/debops-*.whl

.PHONY: clean-wheel
clean-wheel:
	@rm -vrf build debops.egg-info dist/debops-*.whl*

.PHONY: twine-upload
twine-upload:    ## Upload Python packages to PyPI
	@twine upload dist/*

.PHONY: test-all
test-all: clean-tests test-pep8 test-debops-tools test-docs test-playbook-syntax test-yaml test-ansible-lint test-shell test-docker-build

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

.PHONY: clean-tests
clean-tests:
	@rm -vrf .coverage docs/_build/* docs/ansible/roles/*/defaults.rst

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

.PHONY: test-ansible-lint
test-ansible-lint:
	@printf "%s\n" "Checking Ansible roles using ansible-lint..."
	@ansible-lint roles/*

.PHONY: test-yaml
test-yaml:
	@printf "%s\n" "Testing YAML syntax using yamllint..."
	@yamllint .

.PHONY: test-debops-tools
test-debops-tools:
	@printf "%s\n" "Testing debops-tools using nose2..."
	@nose2 --with-coverage

.PHONY: fail-if-git-dirty
fail-if-git-dirty:
	@git diff --quiet && git diff --cached --quiet || ( \
		printf "%s\n" "Sanity check: uncommited git changes detected" ; \
		git status --short ; exit 1 )
