.. _dropbear_initramfs__ref_upgrade_nodes:

Upgrade notes
=============

.. include:: includes/all.rst

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
:ref:`dropbear_initramfs__ref_changelog` for more details about what has changed.

.. _dropbear_initramfs__ref_upgrade_nodes_v0.2.0:

Upgrade from v0.1.0 to v0.2.0
-----------------------------

All inventory variables have been renamed so you might need to update your
inventory.
You will need to read the updated documentation and upgrade your inventory
manually.

.. _dropbear_initramfs__ref_migrating_from_other_roles:

Migrating from other Ansible roles
==================================

This role tries to work for all common use cases and combine similar roles
previously created by independent authors which basically do the same thing.
Refer to `Combine effords <https://github.com/martin-v/ansible-sshpreluks/issues/1>`_ for details.


From martin-v.sshpreluks_
-------------------------

All inventory variables have been renamed so you might need to update your
inventory.
You will need to read the role documentation and upgrade your inventory
manually.

From systemli.rootcrypto_
-------------------------

All inventory variables have been renamed so you might need to update your
inventory.
A subset of them can be automatically updated using this script:

.. literalinclude:: scripts/migrate-from-systemli.rootcrypto-to-debops-contrib.dropbear_initramfs
   :language: shell

The script is bundled with this role under
:file:`./docs/scripts/migrate-from-systemli.rootcrypto-to-debops-contrib.dropbear_initramfs`
and can be invoked from there.

You will need to read the role documentation and upgrade your remaining
inventory manually.
