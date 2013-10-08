#!/bin/sh

ansible-playbook -i inventory site.yml $@

