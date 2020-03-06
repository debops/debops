.. Copyright (C) 2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.debops_fact`` Ansible role can be used to read JSON data from
a set of INI configuration files and make them available as Ansible local
facts. This mechanism can be used to maintain common facts between separate
Ansible roles without the need for them to know about the specific file
structures, using ``ini_file`` Ansible module.
