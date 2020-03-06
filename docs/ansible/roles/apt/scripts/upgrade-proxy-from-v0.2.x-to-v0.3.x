#!/bin/bash

# Copyright (C) 2013-2018 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
# Copyright (C) 2014-2018 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-only

# Upgrade inventory variables related to APT proxy settings for migration from
# debops.apt v0.2.x to v0.3.x.
# The script is idempotent.

git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 \
    | xargs --null sed --in-place --regexp-extended '
        s/apt__proxy_url:(.*)http:(.*)/apt__http_proxy_url:\1http:\2/g;
        s/apt__proxy_url:(.*)https:(.*)/apt__https_proxy_url:\1https:\2/g;
        s/apt__http_proxy_url/apt_proxy__http_url/g;
        s/apt__https_proxy_url/apt_proxy__https_url/g;
    '
