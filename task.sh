#!/bin/bash

# task.sh: ansible wrapper for ginas project
# Copyright 2014 Maciej Delmanowski <drybjed@gmail.com>
# Homepage: https://github.com/drybjed/ginas/


# This program is free software; you can redistribute
# it and/or modify it under the terms of the
# GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General
# Public License along with this program; if not,
# write to the Free Software Foundation, Inc., 59
# Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# An on-line copy of the GNU General Public License can
# be downloaded from the FSF web page at:
# http://www.gnu.org/copyleft/gpl.html


# task.sh allows you to easily maintain multiple ansible inventories and run
# ansible modules ("tasks") with them. This function is achieved by using
# symlinks with specific names and a specific inventory directory structure.
# Script also supports 'secret' role (see playbooks/roles/secret/README.md)
#
# Inventory directories are located in the project's root directory (usually
# current directory) and their naming scheme is: 'inventory-<name>/'. You can
# also create a directory called 'inventory/' which will be the default.
# Iventories can be symlinked from outside of the git repository (or inside of
# it) and will be ignored by default (see .gitignore)

# Symlinks to task.sh script should be created in project's root directory.
# They can have an optional '.sh' extension, in which case they will be
# automatically ignored by git. Format of the symlink names:
#
#     <module>.sh or <module>-<inventory>.sh
#
# If a symlink name has only one part, script will first check, if
# corresponding 'inventory-<name>/' directory exists. If it does, script will use
# that directory as the inventory.
#
# If corresponding directory does not exist, script will use 'inventory/'
# directory.
#
# Examples:
#
# Inventory directories:
#    inventory/
#    inventory-production/
#
# Symlinks:
#    task.sh                = -i inventory -m command
#    shell.sh               = -i inventory -m shell
#    task-production.sh     = -i inventory-production -m command
#    apt-production.sh      = -i inventory-production -m apt
#
# You can add ansible options as the script options, and they will be passed
# correctly.
#
# To see what will happen without executing the commands, run the script with
# DEBUG=1 variable at the beginning of the command line.


# Enable debugging (set to 1)
[ -z "${DEBUG}" ] && DEBUG=0

# Disable 'secret' role (set to 0)
[ -z "${SECRET}" ] && SECRET=1

# Allow connections without SSH fingerprint checking (set to 1)
[ -z "${INSECURE_SSH}" ] && INSECURE_SSH=0

playbook_dir="playbooks"

# What Ansible-specific subdirectory of inventory to look for
inventory_subdirectory="ansible"

# Clean up script name
scriptname=$(basename ${0})
scriptname=${scriptname%%.*}

# Get inventory from script name
prefix=${scriptname%%-*}
suffix=${scriptname##*-}

# If name has only one part...
if [[ "${prefix}" == "${scriptname}" ]]; then

	# Look for corresponding inventory and use it
	if [ -d "inventory-${prefix}" ]; then
		module="command"
		inventory="inventory-${prefix}"

	# or, use default inventory
	else
		module="${prefix}"
	fi

# Or, name has two parts, use the specified module
else
	if [ "${prefix}" == "task" ]; then
		module="command"
	else
		module="${prefix}"
	fi
fi

# If inventory hasn't been selected...
if [ -z "${inventory}" ]; then

	# If name has only one part, use default
	if [[ "${suffix}" == "${scriptname}" ]]; then
		inventory="inventory"

	# Or, use specified inventory
	else
		inventory="inventory-${suffix}"
	fi
fi

# Check if inventory is in subdirectory instead of main dir
if [ -d "${inventory}/${inventory_subdirectory}" ]; then
		inventory="${inventory}/${inventory_subdirectory}"
fi

# Define Ansible inventory variable
export ANSIBLE_HOSTS=${inventory}

# Allow insecure SSH connections if requested
if [ $INSECURE_SSH -gt 0 ]; then
	export ANSIBLE_HOST_KEY_CHECKING=False
fi

# Debugging enabled, print commands and exit
if [ $DEBUG -gt 0 ]; then

	cat <<EOF
#!/bin/bash

DEBUG=$DEBUG
SECRET=$SECRET
INSECURE_SSH=$INSECURE_SSH

ANSIBLE_HOSTS=${ANSIBLE_HOSTS}
ANSIBLE_HOST_KEY_CHECKING=${ANSIBLE_HOSTS_KEY_CHECKING}

if [ \$SECRET -gt 0 ] ; then
	set -e
	ansible-playbook ${playbook_dir}/secret.yml --extra-vars="encfs_mode=open"
	trap "ansible-playbook ${playbook_dir}/secret.yml" EXIT
	set +e
fi

ansible "\${@}"
EOF

# Main script
else

	if [ $SECRET -gt 0 ] ; then
		set -e
		ansible-playbook ${playbook_dir}/secret.yml --extra-vars="encfs_mode=open"
		trap "ansible-playbook ${playbook_dir}/secret.yml" EXIT
		set +e
	fi

	ansible "${@}"
fi


