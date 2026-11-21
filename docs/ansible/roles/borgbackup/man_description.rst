.. Copyright (C) 2019-2023 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2023 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2019-2023 DebOps https://debops.org/
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

BorgBackup (short: Borg) is a deduplicating backup program. Optionally, it
supports compression and authenticated encryption.

The main goal of Borg is to provide an efficient and secure way to backup data.
The data deduplication technique used makes Borg suitable for daily backups
since only changes are stored. The authenticated encryption technique makes it
suitable for backups to not fully trusted targets.

Borg stores a set of files in an archive. A repository is a collection of
archives. The format of repositories is Borg-specific. Borg does not
distinguish archives from each other in any way other than their name, it does
not matter when or where archives were created (e.g. different hosts).

The :ref:`debops.borgbackup` Ansible role can be used to install and configure
hosts to act as servers (where backups are stored) and clients (which perform
backups and send them to server(s) for storage). The role will also generate
configuration for the :command:`borgmatic` Python-based wrapper script for Borg
backup, which is designed to simplify and automate backups
