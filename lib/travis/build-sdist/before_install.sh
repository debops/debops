#!/bin/bash

# Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2018 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

set -o nounset -o pipefail -o errexit

# Prepare environment for building the Python packages

sudo apt-get -qq update
sudo apt-get -yq install pandoc graphviz
pip3 install --upgrade pip wheel setuptools pypandoc
pip3 install \
     sphinx \
     sphinx-autobuild \
     sphinx_rtd_theme
