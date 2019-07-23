#!/bin/bash

set -o nounset -o pipefail -o errexit

# Prepare environment for building the Python packages

sudo apt-get -qq update
pip3 install --upgrade pip wheel setuptools
