.. Copyright (C) 2016-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2016-2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _bind__ref_backup_restore:

Backup and restore procedures
=============================

Here you can find information about the backup procedure for the BIND
server configured by the :ref:`debops.bind` Ansible role and instructions
for restoring the backed-up data.


Backup snapshots
----------------

The :ref:`debops.bind` role installs the :command:`debops-bind-snapshot` shell
script that can be used to create periodic :file:`.tar.gz` archives of the
configuration and zone files used by the BIND server.

By default, three :command:`cron` jobs will be configured by the role to create
daily (7 days), weekly (4-5 weeks) and monthly (12 months) snapshots of all
zones, keys and configuration files. Ephemeral data (i.e. files under the
:file:`/var/cache/bind/` directory) which can be recreated by the server on its
own (e.g. secondary zones, root keys, database dumps, etc) is not backed up.
This can be controlled using the :envvar:`bind__snapshot_enabled` and
:envvar:`bind__snapshot_cron_jobs` default variables. Alternatively, the
periodic :command:`cron` jobs can be disabled, and the
:command:`debops-bind-snapshot` script can be executed as ``root`` to create
snapshots manually; previous snapshots are automatically removed in this case
with assumption that they have been transferred to a remote storage by other
means.

The :command:`debops-bind-snapshot` script will enable and disable read-only
mode for the :command:`named` server (i.e. disabling dynamic DNS updates) and
also attempts to determine whether :command:`named` is already in read-only
mode (in which case dynamic DNS updates will *not* be automatically disabled,
under the assumption that the administrator has manually disabled such
updates).

The snapshots are stored in the :file:`/var/backups/bind/` directory as
compressed tarballs. After finishing the snapshot, the
:command:`debops-bind-snapshot` script will change ownership of the created
tarballs to the ``backup:backup`` UNIX account and group. This account can then
encrypt the tarballs via its own set of scripts, using GnuPG asymmetric
encryption, to prepare them to be sent to a remote location (this functionality
is not implemented by the :ref:`debops.bind` role). The
:command:`debops-bind-snapshot` script will automatically remove periodic
:file:`*.gz.asc` or :file:`*.gz.gpg` files before creating new iterations to
preserve disk space.

In general, the :command:`debops-bind-snapshot` script works in a manner
similar to that of the :command:`slapd-snapshot` script from the
:ref:`debops.slapd` role.


Restore procedure
-----------------

The BIND server has crashed and burned, but you have the backup snapshots
available, how to restore them? The approach described here assumes that all
configuration was performed using the :ref:`debops.bind` role and is still
available in the inventory; only the backup of the zones, keys and
configuration is needed (strictly speaking, the configuration data should be
possible to recreate from the Ansible inventory, but the :file:`/etc/bind/`
directory is anyway backed up since BIND keys and associated data, including
any manual configuration, is kept under said directory).

tl;dr version
~~~~~~~~~~~~~

*Before* running the :ref:`debops.bind` role on the new host, copy a backup
file to the host and extract it:

.. code-block:: console

   # scp bind_month08_August.tar.gz new-bind-host:
   # ssh new-bind-host

   # sudo systemctl stop named.service
   # sudo rm -rf /etc/bind /var/cache/bind /var/lib/bind
   # sudo tar zxfv /home/user/bind_month08_August.tar.gz -C /
   # exit

   # debops run service/bind -l new-bind-host

Once :command:`debops run` finishes, the new BIND installation should contain
all the old zones and configuration. It might take some time before all
secondary zones, etc, have been transferred.

Detailed explanation
~~~~~~~~~~~~~~~~~~~~

1. The ``tl;dr`` version above includes
   :command:`sudo systemctl stop named.service` as a precaution. Ideally, BIND
   should not be installed at all when you restore the backup. The reason for
   this is that as part of executing the :ref:`debops.bind` role, missing keys
   will be detected, new ones will be regenerated and copied to the server.
   Restoring the backup before running the :ref:`debops.bind` role means that
   the old keys will be detected and new ones will not be created. Should the
   keys get out of sync between the BIND host and the Ansible controller, the
   best solution is probably to remove the keys on the controller (under the
   :file:`secret/bind/` hierarchy) and on the remote host (under the
   :file:`/etc/bind/keys/` hierarchy).

2. Unpacking the compressed tarball with the ``-C /`` option means that
   :command:`tar` will ``chdir`` to the root directory before unpacking the
   tarball, which means that the backup (which uses relative paths) will
   be unpacked to the correct location.

3. If BIND isn't running after :command:`debops run service/bind` finishes,
   start :command:`named` manually on the remote host:

   .. code-block:: console

      # systemctl start named.service

4. Monitor the output from :command:`named` to make sure that it accepted
   the new configuration and did not refuse to load any zones:

   .. code-block:: console

      # journalctl -u named
