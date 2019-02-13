#!/bin/bash

set -o nounset -o pipefail -o errexit

# Prepare environment for building the Python packages

sudo apt-get -qq update
pip install --upgrade pip wheel setuptools
