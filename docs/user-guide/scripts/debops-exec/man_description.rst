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
