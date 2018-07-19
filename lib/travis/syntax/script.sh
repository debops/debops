#!/bin/sh

make clean-tests
make test-pep8 test-yaml test-shell
make check
