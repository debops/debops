.. Copyright (C) 2016-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.authorized_keys`` role can be used to manage SSH keys centrally in
the :file:`/etc/ssh/authorized_keys/` directory. The role only manages the keys
themselves, you should configure the ``sshd`` service to use them separately,
for example by using the :ref:`debops.sshd` Ansible role.
