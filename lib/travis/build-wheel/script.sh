#!/bin/sh

make clean-tests
make check
make wheel-quiet
pip install dist/*
