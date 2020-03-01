#!/bin/bash

# Copyright (C) 2015-2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
# Copyright (C) 2015-2017 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

## Upgrade inventory variables for migration from debops.ifupdown v0.2.X to v0.3.X.
## The script is idempotent.

git ls-files -z "$(git rev-parse --show-toplevel)" | xargs --null -I '{}' find '{}' -type f -print0 \
 | xargs --null sed --in-place --regexp-extended '
     s/ifupdown_reconfigure_auto/ifupdown__reconfigure_auto/g;
     s/ifupdown_packages/ifupdown__base_packages/g;
     s/ifupdown_interface_weight_map/ifupdown__interface_weight_map/g;
   '
