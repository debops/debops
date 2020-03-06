.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.apt_mark`` Ansible role can be used to set the desired state of
APT packages using :man:`apt-mark(8)` command. It might be useful if a new
Debian/Ubuntu install results in many packages which should be installed are
marked for autoremoval, or if you want to hold certain APT packages in their
current state. The role operates only on packages that are already installed.
