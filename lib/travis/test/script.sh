#!/bin/bash

# Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2018 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

set -o nounset -o pipefail -o errexit

make clean-tests
make test-debops-tools test-debops-ansible_plugins
make check
