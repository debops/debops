#!/bin/bash

set -o nounset -o pipefail -o errexit

sudo apt-get -qq update
sudo apt-get -yq install python3-future
pip install --upgrade pip wheel setuptools
pip install \
    unittest2 \
    nose2 \
    cov-core
