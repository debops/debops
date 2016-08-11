#!/bin/bash
## Upgrade inventory variables for migration from debops.owncloud v0.2.X to v0.3.X.
## The script is idempotent.

git ls-files -z "$(git rev-parse --show-toplevel)" | xargs --null -I '{}' find '{}' -type f -print0 \
 | xargs --null sed --in-place --regexp-extended '
     s/owncloud__?run_occ_global_commands/owncloud__occ_cmd_list/g;
     s/owncloud__?run_occ_group_commands/owncloud__group_occ_cmd_list/g;
     s/owncloud__?run_occ_host_commands/owncloud__host_occ_cmd_list/g;
     s/owncloud__?packages_group/owncloud__group_packages/g;
     s/owncloud__?packages_host/owncloud__host_packages/g;
     s/owncloud__?config_group/owncloud__group_config/g;
     s/owncloud__?config_host/owncloud__host_config/g;
     s/owncloud__?apps_config_group/owncloud__group_apps_config/g;
     s/owncloud__?apps_config_host/owncloud__host_apps_config/g;
     s/owncloud__?config_role_required/owncloud__role_config/g;
     s/owncloud__?config_role_optional/owncloud__role_recommended_config/g;
     s/owncloud__?ldap_enable([^d])/owncloud__ldap_enabled\1/g;
     s/owncloud__?php5_max_children/owncloud__php_max_children/g;
     s/owncloud__?php5_output_buffering/owncloud__php_output_buffering/g;
     s/owncloud__?php5__pool/owncloud__php__dependent_pools/g;
     s/\<([^.]owncloud)_([^_])/\1__\2/g;
   '
