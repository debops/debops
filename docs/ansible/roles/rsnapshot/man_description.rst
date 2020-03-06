.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The `rsnapshot`__ script is a wrapper around the `rsync`__ command that allows
creation and management of snapshotted backups of local or remote filesystems.
Periodic snapshots are created using :command:`cron` jobs and use `hard
links`__ to perform deduplication.

The ``debops.rsnapshot`` Ansible role acts as another "layer" above
:command:`rsnapshot`. The role can configure snapshotted backups of the local
host to internal or removable storage, as well as create snapshotted backups of
remote hosts over SSH.

.. __: https://rsnapshot.org/
.. __: https://rsync.samba.org/
.. __: https://en.wikipedia.org/wiki/Hard_link
