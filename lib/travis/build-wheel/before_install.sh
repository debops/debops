#!/bin/bash

set -o nounset -o pipefail -o errexit

# Prepare environment for building the Python packages

sudo apt-get -qq update
sudo apt-get -yq install pandoc
pip3 install --upgrade pip wheel setuptools pypandoc
