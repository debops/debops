.. _docker_gen__ref_upgrade_nodes:

Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
changelog for more details about what has changed.

From v0.1.0 to v0.2.0
---------------------

All inventory variables have been renamed so you might need to update your
inventory.
This script can come in handy to do this:

.. literalinclude:: scripts/upgrade-from-v0.1.x-to-v0.2.x
   :language: shell

The script is bundled with this role under
:file:`docs/scripts/upgrade-from-v0.1.x-to-v0.2.x` and can be invoked from
there.
