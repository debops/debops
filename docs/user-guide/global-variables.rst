.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _global_variables:

Global role variables
=====================

In DebOps there's a strictly controlled separation between Ansible roles.
Different roles cannot use variables from another role directly [#]_ to allow
mixing and matching of roles on the playbook level and preserve soft
dependencies. The reason for that is that if a role is not included in the
currently executed playbook, its variables are not available and this can lead
to broken or not idempotent execution.

One place where users can define variables that are always guaranteed to be
present is the Ansible inventory. However roles cannot modify the inventory
directly because inventories come with many shapes and sizes - a YAML file,
dynamic script, etc. But since inventory is always available, it can be used to
define global variables that are shared between different Ansible roles.

The ``debops__`` variable namespace has been designated to be used for global
variables. Roles can reference the ``debops__*`` variables in their tasks and
templates, however their presence is not guaranteed - a default should always
be provided.

Below you can find a list of ``debops__*`` variables which are used across the
DebOps roles and playbooks. The variables might not be used everywhere yet,
however they will be added or will replace other variables in the future.


.. envvar:: debops__no_log

:Type:    Boolean
:Value:   ``True``, ``False``

This boolean variable is meant to be used with the ``no_log`` `Ansible
keyword`__ in tasks that might operate on sensitive information like passwords,
encryption keys, and the like. Setting the value to ``True`` will prevent
Ansible from logging the sensitive contents or displaying any changes made to
the files in the ``--diff`` output.

.. __: https://docs.ansible.com/ansible/latest/reference_appendices/logging.html#protecting-sensitive-data-with-no-log

For example, use the :envvar:`debops__no_log` variable to control when a task
can send log messages and diff output about its operation:

.. code-block:: yaml

   - name: Create an UNIX account
     user:
       name:     'example-user'
       password: '{{ "example-password" | password_hash('sha512") }}'
       state:    'present'
     no_log: '{{ debops__no_log | d(True) }}'

This is a similar case, but adds support for lists and automatically shows or
hides task output depending on presence of a specific parameter:

.. code-block:: yaml

   - name: Create an UNIX account
     user:
       name:     '{{ item.name }}'
       password: '{{ item.password | d(omit) }}'
       state:    '{{ item.state    | d("present") }}'
     loop: '{{ users__accounts }}'
     no_log: '{{ debops__no_log
                 | d(item.no_log
                     | d(True
                         if item.password|d()
                         else False)) }}'

An example use on the command line to debug an issue without changing the
inventory variables:

.. code-block:: console

   ansible-playbook -i <inventory> -l <hostname> -e 'debops__no_log=false' play.yml


.. envvar:: debops__unsafe_writes

:Type:    Boolean
:Value:   ``True``

Many Ansible modules related to file operations support the `unsafe_writes
parameter`__ to allow operations that might be dangerous or destructive in
certain conditions, but allow Ansible to work in specific environments, like
bind-mounted files or directories. The :envvar:`debops__unsafe_writes` variable
allows activation of this mode per-host using Ansible inventory, for all roles
that implement it.

.. __: https://docs.ansible.com/ansible/latest/modules/copy_module.html#parameter-unsafe_writes

To have an effect, roles that depend on the unsafe writes to function, should
use the parameter in relevant tasks, like this:

.. code-block:: yaml

   - name: Generate configuration file
     template:
       src: 'etc/application.conf.j2'
       dest: '/etc/application.conf'
       mode: '0644'
       unsafe_writes: '{{ debops__unsafe_writes | d(omit) }}'


.. rubric:: Footnotes

.. [#] There are exceptions like the :ref:`debops.secret` role; in this case
   the :envvar:`secret` variable is used in Ansible lookup plugin paths and
   needs to be accessible in other roles.
