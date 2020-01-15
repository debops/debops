#!/bin/bash
## Upgrade inventory variables for migration from debops.swapfile v0.3.X to v0.4.X.
## The script is idempotent.

git ls-files -z "$(git rev-parse --show-toplevel)" | xargs --null -I '{}' find '{}' -type f -print0 \
 | xargs --null sed --in-place --regexp-extended '
     s/swapfile__swappiness/sysctl__swappiness/g;
     s/swapfile__cache_pressure/sysctl__vfs_cache_pressure/g;
   '
