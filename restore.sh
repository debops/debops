#!/bin/sh

# Use this script to restore data backed up by 'backup.sh'. The best moment to
# restore the data on the remote host is just after installation and
# configuration of sudo access (either after running 'newhost.sh' script, or
# after host reboot when using automatic Debian preseeding (see 'apt' role),
# before the launch of main 'site.sh' script.

# After restoring the data you might need to remove old host fingerprint from
# ~/.ssh/known_hosts, if IP address of the remote host has been changed.

[ $# -le 0 ] && echo "$0: error: missing list of hosts to restore." && exit 1

if [ -z "${TOO_MANY_SECRETS}" ] ; then
	ansible-playbook -i inventory playbooks/secret.yml --extra-vars="secret_mode=open"
	trap "ansible-playbook -i inventory playbooks/secret.yml" EXIT
fi

ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory playbooks/system_restore.yml --extra-vars="hosts=$@"

