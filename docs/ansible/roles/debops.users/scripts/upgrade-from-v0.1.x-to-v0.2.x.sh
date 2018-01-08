#!/bin/bash

## Upgrade inventory variables for migration from debops.users v0.1.x to v0.2.x.
## The script is idempotent.

git ls-files -z "$(git rev-parse --show-toplevel)" | xargs --null -I '{}' find '{}' -type f -print0 \
 | xargs --null sed --in-place --regexp-extended '
     s/\<users__?default_dotfiles\>/users__dotfiles_enabled/g;
     s/\<users__?default_dotfiles_key\>/users__dotfiles_name/g;
     s/\<users__?default_shell\>/users__default_shell/g;
     s/\<users__?dotfiles\>/users__dotfiles_default_map/g;
     s/\<users__?list\>/users__accounts/g;
     s/\<users__?group_list\>/users__group_accounts/g;
     s/\<users__?host_list\>/users__host_accounts/g;
     s/\<users__?root\>/users__root_accounts/g;
     s/\<users__?admins\>/users__admin_accounts/g;
     s/\<users__?default\>/users__default_accounts/g;
     s/\<users__?groups\>/users__groups/g;
     s/\<([^.]users)_([^_])/\1__\2/g;
   '
