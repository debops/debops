#!/bin/bash

set -o nounset -o pipefail -o errexit

printf "pycodestyle %s\\n" "$(pycodestyle --version)"
shellcheck --version
yamllint --version
