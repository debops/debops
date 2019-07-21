#!/bin/bash

set -o nounset -o pipefail -o errexit

make clean-tests
make check
make sdist-quiet
pip3 install dist/*
