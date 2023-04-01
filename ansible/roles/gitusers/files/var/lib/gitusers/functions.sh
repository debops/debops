# Copyright (C) 2014-2019 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2015-2019 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-only

# Helper function which checks if a given element is in array
in_array () {
    local array="$1[@]"
    local seeking=$2
    local in=1
    for element in "${!array}"; do
        if [[ $element == $seeking ]]; then
        in=0
        break
    fi
    done
    return $in
}
