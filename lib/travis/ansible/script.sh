#!/bin/bash

set -o nounset -o pipefail -o errexit

make clean-tests
make test-playbook-syntax
make test-ansible-lint
make check
