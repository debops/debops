#!/bin/bash

set -o nounset -o pipefail -o errexit

pip3 list
ansible --version
ansible-lint --version
