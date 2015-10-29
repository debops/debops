#!/bin/bash

# Generate directories used by the firewall

root="/etc/ferm"

rules="${root}/rules"

hooks="${root}/hooks"

directories=(

  "${root}"
  "${rules}"
  "${hooks}"

  "${root}/ferm.d"

  "${root}/filter-input.d"

  "${rules}/filter"
  "${rules}/filter/input"
  "${rules}/filter/forward"
  "${rules}/filter/output"

  "${rules}/nat"
  "${rules}/nat/prerouting"
  "${rules}/nat/input"
  "${rules}/nat/output"
  "${rules}/nat/postrouting"

  "${rules}/mangle"
  "${rules}/mangle/prerouting"
  "${rules}/mangle/input"
  "${rules}/mangle/forward"
  "${rules}/mangle/output"
  "${rules}/mangle/postrouting"

  "${hooks}/pre-start.d"
  "${hooks}/post-start.d"
  "${hooks}/pre-stop.d"
  "${hooks}/post-stop.d"
  "${hooks}/pre-reload.d"
  "${hooks}/post-reload.d"
)

install -o root -g adm -m 2750 -d ${directories[@]}

if [ $# -gt 0 ] ; then
  for directory in "${@}" ; do
    install -o root -g adm -m 2750 -d ${rules}/${directory}
  done
fi

