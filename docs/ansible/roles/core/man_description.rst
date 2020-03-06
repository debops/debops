.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.core`` Ansible role takes care of variables that are shared among
different roles and are useful to keep in a central location. This is done by
leveraging functionality of `Ansible local facts`_ stored on remote hosts to
ensure that the variables are always evaluated by Ansible, even when playbook
is run with or without different sets of role tags.

.. _Ansible local facts: https://docs.ansible.com/ansible/playbooks_variables.html#local-facts-facts-d
