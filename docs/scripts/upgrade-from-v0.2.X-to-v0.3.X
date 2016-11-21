#!/bin/bash
## Upgrade inventory variables for migration from debops.tinc v0.2.X to v0.3.X.
## The script is idempotent.

git ls-files -z "$(git rev-parse --show-toplevel)" | xargs --null -I '{}' find '{}' -type f -print0 \
 | xargs --null sed --in-place --regexp-extended '
     s/tinc__connect_to_mesh0/tinc__reachable_peer_hosts_mesh0/g;
     s/tinc__compression([^_])/tinc__compression_mesh0\1/g;
     s/tinc__address_family([^_])/tinc__address_family_mesh0\1/g;
   '
