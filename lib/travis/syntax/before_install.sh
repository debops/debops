#!/bin/bash

set -o nounset -o pipefail -o errexit

sudo apt-get -qq update
pip3 install --upgrade pip wheel setuptools
pip3 install \
     pycodestyle \
     yamllint
