#!/bin/bash

set -o nounset -o pipefail -o errexit

sudo apt-get -qq update
sudo apt-get -yq install graphviz
pip3 install --upgrade pip wheel setuptools
pip3 install \
     sphinx \
     sphinx-autobuild \
     sphinx_rtd_theme
