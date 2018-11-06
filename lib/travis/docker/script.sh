#!/bin/bash

set -o nounset -o pipefail -o errexit

make clean-tests
make test-docker-build
make check
