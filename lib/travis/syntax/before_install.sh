#!/bin/sh

sudo apt-get -qq update
pip install --upgrade pip wheel setuptools
pip install \
    pycodestyle \
    yamllint
