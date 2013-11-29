#!/bin/sh

if [ -z "${TOO_MANY_SECRETS}" ] ; then
	ansible-playbook -i inventory playbooks/secret.yml --extra-vars="secret_mode=open"
	trap "ansible-playbook -i inventory playbooks/secret.yml" EXIT
fi

ansible-playbook -i inventory playbooks/site.yml $@

