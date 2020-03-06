.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.salt`` Ansible role can be used to install and configure
`SaltStack <https://saltstack.com/>`_ Master service. It is expected that Salt
Minions are installed using host deployment methods like PXE/preseeding, LXC
template scripts, etc. and contact the Salt Master service over DNS.
