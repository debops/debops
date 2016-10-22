#!/bin/bash
## Upgrade inventory variables for migration from debops.apt_cacher_ng v0.1.X to v0.2.X.
## The script is idempotent.

git ls-files -z "$(git rev-parse --show-toplevel)" | xargs --null -I '{}' find '{}' -type f -print0 \
 | xargs --null sed --in-place --regexp-extended '
     s/apt_cacher_ng__nginx_upstream_servers/apt_cacher_ng__upstream_servers/g;
     s/apt_cacher_ng__nginx_upstream/apt_cacher_ng__nginx__upstream/g;
   '
