#!/bin/bash
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-only
#
# Report LXC container memory "pressure" as a percentage, defined as
# '100 * (MemTotal - MemAvailable) / MemTotal' as seen through LXCFS inside
# the container. See 'ct-memory-used.sh' for the rationale behind using
# 'MemAvailable' instead of the cgroup v2 'memory.current' value.
#
# Meant to be used as a Zabbix UserParameter ('ct.memory.util') on LXC
# guests only.
set -euo pipefail
export LC_ALL=C

awk '
    /^MemTotal:/     { total = $2 }
    /^MemAvailable:/ { available = $2 }
    END {
        if (total < 1) { print "0.00"; exit }
        used = total - available
        if (used < 0) { used = 0 }
        printf "%.2f", 100 * used / total
    }
' /proc/meminfo
