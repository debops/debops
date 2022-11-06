.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2016-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _dovecot__ref_backup_restore:

Backup and restore procedures
=============================

Here you can find information about the backup procedure for the Dovecot
service configured by the :ref:`debops.dovecot` Ansible role as well as tips
about restoring the backed-up data.


Disabled by default
-------------------

.. warning:: The backup script is, per default, *disabled*. The reason is that
             many sites already have backup policies in place and that mail
             servers are often already operating at close to full capacity.

Enabling the backup script will, in the default configuration, mean that the
storage requirements will increase by an order of magnitude (daily, weekly and
monthly snapshots, plus temporary scratch space while writing a backup, albeit
the actual snapshots will be compressed, which makes it difficult to give an
exact estimate).


Backup snapshots
----------------

The :ref:`debops.dovecot` role installs the :command:`debops-dovecot-snapshot`
shell script that can be used to create periodic backups of the mailboxes for
all or some users.

By default, three :command:`cron` jobs will be configured by the role to create
daily (7 days), weekly (4-5 weeks) and monthly (12 months) snapshots of all
users' mailboxes. This can be controlled using the
:envvar:`dovecot__snapshot_deploy_state`, :envvar:`dovecot__snapshot_cron_jobs`
and :envvar:`dovecot__snapshot_user_filter` default variables. Alternatively,
the periodic :command:`cron` jobs can be disabled, and the
:command:`debops-dovecot-snapshot` script can be executed as ``root`` to create
a current snapshot of the Dovecot mailboxes; previous snapshots are
automatically removed in this case with assumption that they have been
transferred to a remote storage by other means.

The snapshots are stored in the :file:`/var/backups/dovecot/` directory as
tarballs containing per-user compressed tarballs (using ``zstd`` compression,
which can cut the time needed to create backups in half, compared to e.g.
``gzip``). After finishing the snapshot, the :command:`debops-dovecot-snapshot`
script will change ownership of the created tarballs to the ``backup:backup``
UNIX account and group. This account can then encrypt the tarballs via its own
set of scripts, using GnuPG asymmetric encryption, to prepare them to be sent
to a remote location (this functionality is not implemented by the
:ref:`debops.dovecot` role). The :command:`debops-dovecot-snapshot` script will
automatically remove periodic :file:`*.gz.asc` or :file:`*.gz.gpg` files before
creating new iterations to preserve disk space.


Restore procedure
-----------------

The Dovecot server has crashed and burned, but you have the backup snapshots
available, how to restore them? The approach described here assumes that all
Dovecot server configuration was performed using the :ref:`debops.dovecot` role
and is still available in the inventory; only the backup of the mailboxes
managed by Dovecot is needed.

.. note::
   This procedure can also be used to migrate Dovecot from one storage format
   to an alternative storage format or to migrate users between Dovecot
   clusters.

tl;dr version
~~~~~~~~~~~~~

Set up a new Dovecot server (or cluster), and select one host as the restore
point.

.. code-block:: console

   scp backup.tar dovecot-host:
   ssh dovecot-host

   sudo -i
   mkdir /srv/dovecot-restore
   tar -C /srv/dovecot-restore -xvf backup.tar
   cd /srv/dovecot-restore/dovecot_*

   # For each user
   tar -axvf <user>.tar.zst
   chown -R vmail:vmail /srv/dovecot-restore
   doveadm sync -u <user> mdbox:/srv/dovecot-restore/dovecot_*/<user>/

Detailed explanation
~~~~~~~~~~~~~~~~~~~~

1. Create a new Dovecot server and configure it using DebOps. If it's
   a cluster of servers, make sure that after applying the configuration the
   synchronization happens correctly, for example by sending a test mail to
   a user, and noticing it appear on all servers.

2. Select one host as the backup importer. Copy a recent backup to it with
   :command:`scp` to have the data available on the host locally.

3. Unpack the backup archive to a temporary location. This will create a number
   of per-user compressed tarballs.

4. For each user, extract the corresponding compressed tarball. This will
   create a directory hierarchy under ``<user>``.

5. Since :command:`doveadm` will change to the user/group which is normally
   used to maintain mailboxes, the filesystem permissions must allow access
   to that user (usually ``vmail``) to the newly extracted backup.

6. Import the user's data using :command:`doveadm`.

   .. warning::
      Note that ``sync`` is used rather than ``backup -R``, as the Dovecot
      server may already be accepting new emails for users, and ``backup -R``
      will make the destination (in this case, the live Dovecot mailboxes) look
      exactly like the source (i.e. the backup), meaning that new emails would
      be deleted.

   Note that the backups are created in Dovecot's native ``mdbox`` format,
   for performance reasons. This does not affect the format which is used
   by Dovecot for the live mailboxes.

   .. code-block:: console

      doveadm sync -u <user> mdbox:/srv/dovecot-restore/dovecot_*/<user>/

7. Repeat steps 4-6 for each user.
