#!/bin/bash

# Copyright (C) 2013-2018 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
# Copyright (C) 2014-2018 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

# Upgrade inventory variables for migration from debops.apt v0.3.x to v0.4.x.
# The script is idempotent.

git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 \
    | xargs --null sed --in-place --regexp-extended '
        s/apt__update_cache_early/apt__cache_valid_time/g;
        s/apt__sources_types/apt__source_types/g;
    '
