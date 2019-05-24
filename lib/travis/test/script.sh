#!/bin/bash

set -o nounset -o pipefail -o errexit

make clean-tests
make test-debops-tools test-debops-ansible_plugins
make check
