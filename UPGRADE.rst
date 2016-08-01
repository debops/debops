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
This script can come in handy to do this:

.. literalinclude:: scripts/upgrade-from-v0.2.X-to-v0.3.X
   :language: shell

The script is bundled with this role under
:file:`docs/scripts/upgrade-from-v0.2.X-to-v0.3.X` and can be invoked from
their.

For more details refer to `What’s New for Admins in ownCloud 9.0 <https://doc.owncloud.org/server/9.0/admin_manual/whats_new_admin.html>`__.

From v0.1.0 to v0.2.0
---------------------

The upgrade path has not been extensively tested. Some manual work might be
required. It is recommended to upgrade to v0.3.0 directly to avoid this manual
work.
