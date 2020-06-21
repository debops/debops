#!/bin/bash

# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

set -o nounset -o pipefail -o errexit

sudo apt-get -qq update
sudo apt-get -yq install pandoc pandoc-data
pip3 install --upgrade pip wheel setuptools
pip3 install galaxy-importer ansible ansible-lint reuse
