.. Copyright (C) 2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

The `debconf`__ database is a Debian configuration management system meant to
ease configuration of applications packaged using the :file:`.deb` file format.
Debconf allows system administrators to pre-seed the answers to the questions
asked by a given package during installation, allowing for automated and
non-interactive configuration of said package.

.. __: https://wiki.debian.org/debconf

The :ref:`debops.debconf` role is built around using :command:`debconf` to
pre-configure applications installed using :file:`.deb` packages. The role is
executed late in the configuration order defined in the :file:`site.yml` Ansible
playbook, so that other services required by a given application can be prepared
before its installation.
