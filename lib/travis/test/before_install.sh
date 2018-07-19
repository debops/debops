#!/bin/sh

sudo apt-get -qq update
pip install --upgrade pip wheel setuptools
pip install \
    unittest2 \
    nose2 \
    cov-core
