#!/bin/bash

# Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2015-2016 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-only

# Upgrade inventory variables for migration from debops.docker_gen v0.1.x to v0.2.x.
# The script is idempotent.

git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 \
    | xargs --null sed --in-place --regexp-extended '
        s/\<(DOCKER_GEN)_([^_])/\1__\2/g;
        s/\<(docker_gen)_([^_])/\1__\2/g;
    '
