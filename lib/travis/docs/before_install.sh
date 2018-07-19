#!/bin/sh

sudo apt-get -qq update
sudo apt-get -yq install graphviz
pip install --upgrade pip wheel setuptools
pip install \
    sphinx \
    sphinx-autobuild \
    sphinx_rtd_theme
