#!/bin/bash

set -o nounset -o pipefail -o errexit

sudo apt-get -qq update
pip install --upgrade pip wheel setuptools
pip install \
    cov-core \
    future \
    nose2 \
    unittest2 \
    pyyaml
