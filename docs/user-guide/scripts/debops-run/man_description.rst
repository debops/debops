.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

DebOps roles can store encrypted secrets (passwords and other confiential data)
in a project directory, under :file:`ansible/secret/` subdirectory. For normal
operation, the secrets need to be unlocked so that Ansible roles and playbooks
can access and manipulate them. To make this process easier, DebOps provides
the :command:`debops run` and :command:`debops check` commands which will
automatically unlock and lock the encrypted secrets as needed.

An additional benefit of using these commands is that the user does not have to
provide a full path to the playbooks - the script will try to find the correct
playbook in a set of different directories or even inside Ansible Collections.

The commands connect to the hosts through SSH. With the ``--accept``
option, the first connection to a host accepts an unseen SSH host key and
stores it. Without the option, :command:`ssh` refuses an unseen key and the
connection fails.

The option composes the ``ANSIBLE_SSH_ARGS`` variable. The ``ssh_args``
options of the project configuration carry over to the connection.
