.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Preseeding`_ is a way to configure the Debian Installer non-interactively.
During installation, a special text file can be downloaded over HTTP, this file
can provide answers to the installer questions.

After installation, a custom shell script will be downloaded and run in the
target environment to prepare host for remote use (an admin account will be
created, SSH keys will be configured, optionally a Salt Minion will be
installed and will start on the next boot).

.. _Preseeding: https://wiki.debian.org/DebianInstaller/Preseed
