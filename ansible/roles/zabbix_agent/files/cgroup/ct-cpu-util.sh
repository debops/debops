#!/bin/bash
# Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-only
#
# Report LXC container CPU utilization (%) relative to the number of CPUs
# visible in the container, based on cgroup v2 'cpu.stat' 'usage_usec'.
#
# The host 'loadavg'/'system.cpu.util' items exposed via LXCFS inside an LXC
# container actually reflect the whole physical host, not the container
# itself. This makes per-container CPU alerts on LXC hosts either silent
# (container overloaded, host looks fine) or misleading (one noisy neighbour
# triggers alerts on every container on the host). This script is meant to be
# used as a Zabbix UserParameter ('ct.cpu.util') on LXC guests only.
#
# 'LC_ALL=C' is required so that 'awk' prints a dot as the decimal separator
# regardless of the system locale (locales like 'pl_PL' print a comma, which
# Zabbix Server rejects as an invalid numeric value).
set -euo pipefail
export LC_ALL=C

STAT=/sys/fs/cgroup/cpu.stat

# A merely readable 'cpu.stat' is not enough: cgroup v1's own 'cpu.stat'
# (nr_periods/nr_throttled/throttled_time) has no 'usage_usec' field, which
# would silently turn into a bogus 'delta=0' -> '0.00%' reading below instead
# of a loud failure. Require the cgroup v2 unified hierarchy explicitly.
test -r /sys/fs/cgroup/cgroup.controllers || {
    echo "ct-cpu-util.sh: cgroup v2 not detected (no /sys/fs/cgroup/cgroup.controllers), refusing to guess" >&2
    exit 1
}
test -r "${STAT}"

cpu_count=$(nproc)
usage_1=$(awk '/^usage_usec/ {print $2; exit}' "${STAT}")
: "${usage_1:?ct-cpu-util.sh: 'usage_usec' not found in ${STAT}}"
sleep 1
usage_2=$(awk '/^usage_usec/ {print $2; exit}' "${STAT}")
: "${usage_2:?ct-cpu-util.sh: 'usage_usec' not found in ${STAT} on second read}"

awk -v delta="$((usage_2 - usage_1))" -v cpus="${cpu_count}" 'BEGIN {
    if (cpus < 1) { cpus = 1 }
    printf "%.2f", delta / 10000 / cpus
}'
