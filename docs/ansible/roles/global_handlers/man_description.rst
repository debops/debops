.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.global_handlers`` role provides a small set of `Ansible
handlers`__ shared by multiple DebOps roles: refreshing the Ansible local
facts, reloading the :program:`systemd` service manager, as well as handlers
for services whose handlers are notified across role boundaries without a role
dependency, like :program:`rsyslog`, :program:`xinetd` or the
:ref:`debops.postfix` chroot maintenance.

.. __: https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html#handlers-running-operations-on-change

Handlers specific to a single role are defined in that role's
:file:`handlers/main.yml` file, where they can freely use the role's default
and effective variables. The handlers in the ``debops.global_handlers`` role
are the exception: they are shared, therefore they need to be self-contained
and cannot rely on variables from the roles that notify them.

The role does not have its own playbook and does not contain any tasks.
DebOps playbooks include it as the first role of every play that uses DebOps
roles, so that the shared handlers are defined before the role handlers and
are available to all of them.
