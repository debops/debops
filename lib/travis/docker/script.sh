#!/bin/sh

make clean-tests
make test-docker-build
make check
