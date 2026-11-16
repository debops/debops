.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops exec` command will run the :command:`ansible` command
inside of the DebOps project directory with its context - environment variables
defined in the configuration, unlocked :file:`ansible/secret/` directory and
with the :file:`ansible.cfg` configuration file used by the project, which
points to the Ansible inventory.

The command connects to the hosts through SSH. With the ``--accept``
option, the first connection to a host accepts an unseen SSH host key and
stores it. Without the option, :command:`ssh` asks about an unseen key the
way it normally does.

The option composes the ``ANSIBLE_SSH_ARGS`` variable. The ``ssh_args``
options of the project configuration carry over to the connection. The
run announces the acceptance before it starts ("Ansible will auto-accept
new SSH host keys") and reports what the store gained afterwards ("Ansible
auto-accepted N SSH host keys during the run"); the report is omitted
when the store gained nothing.
