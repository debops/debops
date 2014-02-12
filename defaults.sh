#!/bin/bash

# Simple defaults browser for ginas project
# https://github.com/drybjed/ginas/

# Run without options to browse all defaults
# Specify list of role names separated by spaces to see only those role
# defaults

# Script uses 'view' command from vim package as convinient pager

# Tips:
#  - you can search for "role:" to jump between roles


(
	if [ $# -gt 0 ]; then
		for role in ${@}; do
			cat playbooks/roles/${role}/defaults/main.yml
		done
	else
		cat playbooks/roles/*/defaults/main.yml
	fi
) | view '+set ft=yaml' -


