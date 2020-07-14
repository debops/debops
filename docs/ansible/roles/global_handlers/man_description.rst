.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.global_handlers`` role is a central place to define `Ansible
handlers`__ used by different Ansible roles. Keeping the handlers centralized
allows them to be used in different Ansible roles without the need to add
dependent roles to the playbook, making execution faster and the codebase
easier to modify and maintain.

.. __: https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html#handlers-running-operations-on-change
