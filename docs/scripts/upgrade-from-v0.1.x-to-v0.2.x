#!/bin/bash

# Upgrade inventory variables for migration from debops.docker_gen v0.1.x to v0.2.x.
# The script is idempotent.

git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 \
    | xargs --null sed --in-place --regexp-extended '
        s/docker_etc_services_/docker__etc_services__/g;
        s/docker_ferm_/docker__ferm__/g;
        s/\<(docker)_([^_])/\1__\2/g;
    '
git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 \
    | xargs --null sed --in-place --regexp-extended '
        s/\<(DOCKER_GEN)_([^_])/\1__\2/g;
        s/\<(docker_gen)_([^_])/\1__\2/g;
    '

