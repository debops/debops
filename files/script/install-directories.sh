#!/bin/bash

# Generate directories used by the firewall

root="/etc/ferm"

hooks="${root}/hooks"

directories=(

  "${root}"
  "${hooks}"

  "${root}/ferm.d"

  "${root}/filter-input.d"

  "${hooks}/pre-start.d"
  "${hooks}/post-start.d"
  "${hooks}/pre-stop.d"
  "${hooks}/post-stop.d"
  "${hooks}/pre-reload.d"
  "${hooks}/post-reload.d"
)

install -o root -g adm -m 2750 -d ${directories[@]}

