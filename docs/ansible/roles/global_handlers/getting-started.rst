.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example usage in Ansible playbooks
----------------------------------

The ``debops.global_handlers`` role does not have its own Ansible playbook and
does not contain any tasks. It only defines handlers, therefore it is included
in DebOps playbooks as the first role of a play that uses DebOps roles:

.. code-block:: yaml

    - name: Manage nginx webserver
      hosts: [ 'debops_service_nginx' ]
      become: True

      roles:

        - role: 'global_handlers'

        - role: 'nginx'

This way the shared handlers are defined before the handlers of any other role
in the play, and all roles in the play can notify them. In playbooks that
import roles through tasks, the role is imported as the first task:

.. code-block:: yaml

      tasks:

        - name: Import DebOps global handlers
          ansible.builtin.import_role:
            name: 'debops.debops.global_handlers'
          tags: [ 'role::nginx', 'skip::nginx' ]

        - name: Import nginx role
          ansible.builtin.import_role:
            name: 'debops.debops.nginx'
          tags: [ 'role::nginx', 'skip::nginx' ]

Custom Ansible playbooks that use DebOps roles directly need to include the
``debops.global_handlers`` role in the same way, otherwise notifications of
the shared handlers will fail with an error at the end of the play.

Common use case for this "pattern" is adding :file:`conf.d/` configuration
snippets to services maintained by other roles - this sometimes requires
a given service to be restarted to enable new configuration. With the handlers
defined by the playbook, the "application" role can modify its own
configuration and restart the external service without the need to involve its
corresponding role in its entirety. For example, let's add a custom
:command:`rsyslog` configuration and restart the service on any changes:

.. code-block:: yaml

   - name: Add ryslog configuration snippet
     template:
       src: 'etc/rsyslog.d/application.conf.j2'
       dest: '/etc/rsyslog.d/application.conf'
       mode: '0644'
     notify: [ 'Check and restart rsyslogd' ]
     when: (ansible_local.rsyslog.installed | d()) | bool

Ansible will restart the :command:`rsyslog` daemon on any changes as long as
the configuration is parsed correctly. Note that the task will only be executed
if the :ref:`debops.rsyslog` role has been used on the host to configure the
:command:`rsyslog` service, which is indicated by a custom Ansible local fact
- if that is not the case, or the :command:`rsyslog` service has been
uninstalled in the meantime, the task and the handlers will be skipped
automatically.


How to add new handlers
-----------------------

Handlers specific to a single role belong in that role's
:file:`handlers/main.yml` file. They can use the role's default and effective
variables as well as registered variables from the role's tasks. If a handler
depends on the information from the remote hosts passed via register
variables, the command that registered them needs to be a part of the "handler
chain" which notifies subsequent handlers on changes.

Handlers needed by more than one role go in the ``debops.global_handlers``
role, in a separate :file:`handlers/<role_name>.yml` file imported from the
:file:`handlers/main.yml` file. The order of the imports in that file defines
the execution order of the shared handlers relative to each other. Handlers in
the ``debops.global_handlers`` role must be self-contained: they should not
use variables from the roles that notify them, because the importing role
might not be present in the play at all. A few handlers use variables in the
``handlers__*`` role namespace to lookup information from the :file:`secret/`
directory maintained by the :ref:`debops.secret` role, but even that should be
avoided if possible.

If a shared service is optional or may not be available on a host, the service
role should provide an ``ansible_local.<role>.installed`` or similar boolean
Ansible local fact. This fact can then be checked by a given handler to
determine if the service is available and can be acted upon.

Handlers are executed in the order in which they are defined in a play. The
``debops.global_handlers`` role is included first in DebOps playbooks, so its
handlers execute **before** the handlers defined by the roles in the play. If
a role needs its handler to run in a different position, it can define its own
copy of the handler - such copies need to have unique names to not clash with
the originals.
