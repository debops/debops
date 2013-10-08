#!/bin/sh

[ $# -le 0 ] && echo "$0: error: missing list of hosts to initialize." && exit 1

ansible-playbook -i inventory playbooks/newhost.yml -k --extra-vars="hosts=$@"
