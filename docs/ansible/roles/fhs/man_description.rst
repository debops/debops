.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

By default various DebOps application roles install their data in directories
designated by the `Filesystem Hierarchy Standard`__ for locally-installed
software - for example :file:`/usr/local/bin/` for binaries,
:file:`/usr/local/src/` for source code, and so on. To allow system
administrators to easily change the preferred location of various resources
without the need to modify multiple roles separately, the :ref:`debops.fhs`
role is a central place which defines base directories for other roles to use.

.. __: https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard

The base directories are created by the role, and a special
:file:`/etc/ansible/facts.d/fhs.fact` script is generated on the host. It
serves dual purpose - the facts are used to ensure that any changes in the
directory paths don't affect existing installations, and can be used by other
Ansible roles to define various resource paths in their variables.
