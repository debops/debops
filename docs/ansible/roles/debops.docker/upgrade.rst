.. _docker__ref_upgrade_nodes:

Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
changelog for more details about what has changed.

From v0.3.0 to v0.4.0
---------------------

The :command:`ferment` script is now installed in a Python virtualenv, and
symlinked in the :file:`/usr/local/bin/` directory. On existing installation
you will need to remove the existing :file:`/usr/local/bin/ferment` script to
not cause an error when Ansible creates the symlink.

From v0.2.1 to v0.3.0
---------------------

This role should not be run on a system where docker-engine or docker.io is already
installed either manually or through running a previous version of this role. If you
want to upgrade to docker-ce or docker-ee through this role, manually remove
docker-engine or docker.io. Make sure to backup your docker data first.

From v0.1.2 to v02.0
--------------------

All inventory variables have been renamed so you might need to update your
inventory.
This script can come in handy to do this:

.. literalinclude:: scripts/upgrade-from-v0.1.x-to-v0.2.x
   :language: shell

The script is bundled with this role under
:file:`docs/scripts/upgrade-from-v0.1.x-to-v0.2.x` and can be invoked from
there.
