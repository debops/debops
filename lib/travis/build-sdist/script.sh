#!/bin/sh

make clean-tests
make check
make sdist-quiet
pip install dist/*
