#!/bin/bash

# newhost.sh: ansible-playbook wrapper for ginas project
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


# newhost.sh is a special version of 'host.sh' script which asks for user
# password. Currently `ansible-playbook --ask-pass` option cannot be specified
# in the playbook, when that will be possible, this script will be replaced by
# 'site.sh'.

# See 'site.sh' for more information about usage of this script with different
# inventories and playbooks.


# Enable debugging (set to 1)
[ -z "${DEBUG}" ] && DEBUG=0

# Disable 'secret' role (set to 0)
[ -z "${SECRET}" ] && SECRET=1

playbook_dir="playbooks"

# What Ansible-specific subdirectory of inventory to look for
inventory_subdirectory="ansible"

# Clean up script name
scriptname=$(basename ${0})
scriptname=${scriptname%%.*}

# Get playbook and inventory from script name
prefix=${scriptname%%-*}
suffix=${scriptname##*-}

# If name has only one part...
if [[ "${prefix}" == "${scriptname}" ]]; then

	# Look for corresponding inventory and use it
	if [ -d "inventory-${prefix}" ]; then
		playbook="${playbook_dir}/host.yml"
		inventory="inventory-${prefix}"

	# or, run specified playbook with default inventory
	else
		playbook="${playbook_dir}/${prefix}.yml"
	fi

# Or, name has two parts, use the specified playbook
else
	playbook="${playbook_dir}/${prefix}.yml"
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

# Debugging enabled, print commands and exit
if [ $DEBUG -gt 0 ]; then

	cat <<EOF
#!/bin/bash

DEBUG=$DEBUG
SECRET=$SECRET

[ \$# -le 0 ] && echo "\$0: error: missing list of hosts to work with" && exit 1

if [ \$SECRET -gt 0 ] ; then
	set -e
	ansible-playbook -i ${inventory} ${playbook_dir}/secret.yml --extra-vars="encfs_mode=open"
	trap "ansible-playbook -i ${inventory} ${playbook_dir}/secret.yml" EXIT
	set +e
fi

ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ${inventory} ${playbook} -k --extra-vars="hosts=\$@"
EOF

# Main script
else
	[ $# -le 0 ] && echo "$0: error: missing list of hosts to work with" && exit 1

	if [ $SECRET -gt 0 ] ; then
		set -e
		ansible-playbook -i ${inventory} ${playbook_dir}/secret.yml --extra-vars="encfs_mode=open"
		trap "ansible-playbook -i ${inventory} ${playbook_dir}/secret.yml" EXIT
		set +e
	fi

	ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ${inventory} ${playbook} -k --extra-vars="hosts=$@"
fi


