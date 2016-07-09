.. _owncloud__ref_upgrade_nodes:

Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
:ref:`owncloud__ref_changelog` for more details about what has changed.

From v0.2.0 to unreleased
-------------------------

All inventory variables have been renamed so you might need to update your
inventory.
This oneliner can come in handy to do this:

.. code:: shell

   git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 \
     | xargs --null sed --in-place --regexp-extended '
         s/owncloud__?run_occ_global_commands/owncloud__occ_cmd_list/g;
         s/owncloud__?run_occ_group_commands/owncloud__group_occ_cmd_list/g;
         s/owncloud__?run_occ_host_commands/owncloud__host_occ_cmd_list/g;
         s/owncloud__?packages_recommended/owncloud__packages_recommended/g;
         s/owncloud__?packages_optional/owncloud__optional_packages/g;
         s/owncloud__?packages_group/owncloud__group_packages/g;
         s/owncloud__?packages_host/owncloud__host_packages/g;
         s/owncloud__?config_group/owncloud__group_config/g;
         s/owncloud__?config_host/owncloud__host_config/g;
         s/owncloud__?apps_config_group/owncloud__group_apps_config/g;
         s/owncloud__?apps_config_host/owncloud__host_apps_config/g;
         s/owncloud__?config_role_required/owncloud__required_config/g;
         s/owncloud__?config_role_optional/owncloud__optional_config/g;
         s/owncloud__?ldap_enable([^d])/owncloud__ldap_enabled\1/g;
         s/\<([^.]owncloud)_([^_])/\1__\2/g;
       '

From v0.1.0 to v0.2.0
---------------------

The upgrade path has not been extensively tested. Some manual work might be
required. It is recommended to upgrade to v0.3.0 directly to avoid this manual
work.
