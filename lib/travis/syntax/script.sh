#!/bin/bash

set -o nounset -o pipefail -o errexit

make clean-tests
make test-pep8 test-yaml test-shell
make check
