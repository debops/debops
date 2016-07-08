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

   git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/owncloud_ldap_enable/owncloud__ldap_enabled/g;s/\<(owncloud)_([^_])/\1__\2/g'

From v0.1.0 to v0.2.0
---------------------

The upgrade path has not been extensively tested. Some manual work might be
required. It is recommended to upgrade to v0.3.0 directly to avoid this manual
work.
