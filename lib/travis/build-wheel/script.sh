#!/bin/bash

set -o nounset -o pipefail -o errexit

make clean-tests
make check
make wheel-quiet
pip3 install dist/*
