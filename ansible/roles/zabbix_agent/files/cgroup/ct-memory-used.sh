#!/bin/bash
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-only
#
# Report LXC container memory "pressure" in bytes, defined as
# 'MemTotal - MemAvailable' as seen through LXCFS inside the container.
#
# This is intentionally *not* based on the cgroup v2 'memory.current' value,
# which includes reclaimable page cache. Workloads that make heavy use of
# the page cache (for example a database server) can make
# 'memory.current' approach the cgroup memory limit while the system is not
# actually under memory pressure, producing misleading near-100% alerts.
# 'MemAvailable' already accounts for reclaimable cache, matching what
# 'free -h' and the kernel's own memory pressure heuristics report.
#
# Meant to be used as a Zabbix UserParameter ('ct.memory.used') on LXC
# guests only.
set -euo pipefail
export LC_ALL=C

awk '
    /^MemTotal:/     { total = $2 }
    /^MemAvailable:/ { available = $2 }
    END {
        if (total < 1) { print 0; exit }
        used = total - available
        if (used < 0) { used = 0 }
        print used * 1024
    }
' /proc/meminfo
