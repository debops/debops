#!/bin/bash
## Upgrade inventory variables for migration from debops.owncloud v0.3.X to v0.4.X.
## The script is idempotent.

git ls-files -z "$(git rev-parse --show-toplevel)" | xargs --null -I '{}' find '{}' -type f -print0 \
 | xargs --null sed --in-place --regexp-extended '
     s/owncloud__nginx__servers\>/owncloud__nginx__dependent_servers/g;
     s/owncloud__nginx__upstream_php\>/owncloud__nginx__dependent_upstreams/g;
     s/owncloud__theme_entitiy_name\>/owncloud__theme_entity_name/g;
     s/owncloud__user\>/owncloud__app_user/g;
     s/owncloud__group\>/owncloud__app_group/g;
     s/owncloud__home\>/owncloud__app_home/g;
   '
