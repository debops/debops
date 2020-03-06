.. Copyright (C) 2016-2018 Robin Schneider <ypid@riseup.net>
.. Copyright (C)      2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.etckeeper`` Ansible role will install `etckeeper`__, which puts
the :file:`/etc` directory under version control. To do this,
:program:`etckeeper` hooks into the package management and from now on
automatically will commit changes to a local git repository under
:file:`/etc/.git/` directory. This makes it easy to see which changes are
applied on a specific host and quickly revert them, if something breaks.

.. __: https://etckeeper.branchable.com/

The role will install a special Ansible local fact which will commit any
changes in the :file:`/etc` directory as well, usually at the moment the
Ansible facts are gathered.
