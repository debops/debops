#!/bin/bash

set -o nounset -o pipefail -o errexit

pip list
ansible --version
ansible-lint --version
