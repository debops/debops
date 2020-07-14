.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example usage in other Ansible roles
------------------------------------

The ``debops.global_handlers`` role does not have its own Ansible playbook. It
is meant to be used by importing it in other Ansible roles:

.. code-block:: yaml

   - import_role:
       name: 'global_handlers'

Afterwards, the role can notify the known handlers in its tasks. The handlers
will be executed in the order defined in the ``debops.global_handlers`` role,
notification order in the calling roles does not matter.

Common use case for this "pattern" is adding :file:`conf.d/` configuration
snippets to services maintained by other roles - this sometimes requires
a given service to be restarted to enable new configuration. With the handlers
always available, the "application" role can modify its own configuration and
restart the external service without the need to involve its corresponding
role in its entirety. For example, let's add a custom :command:`rsyslog`
configuration and restart the service on any changes:

.. code-block:: yaml

   - name: Add ryslog configuration snippet
     template:
       src: 'etc/rsyslog.d/application.conf.j2'
       dest: '/etc/rsyslog.d/application.conf'
       mode: '0644'
     notify: [ 'Check and restart rsyslogd' ]
     when: (ansible_local.rsyslog.installed|d())|bool

Ansible will restart the :command:`rsyslog` daemon on any changes as long as
the configuration is parsed correctly. Note that the task will only be executed
if the :ref:`debops.rsyslog` role has been used on the host to configure the
:command:`rsyslog` service, which is indicated by a custom Ansible local fact
- if that is not the case, or the :command:`rsyslog` service has been
uninstalled in the meantime, the task and the handlers will be skipped
automatically.


How to add new handlers
-----------------------

If a given Ansible role provides handlers for its service(s), they should be
put in a separate :file:`handlers/<role_name>.yml` file in the
``debops.global_handlers`` role. This file can then be imported in the
:file:`handlers/main.yml` file in a specific place to ensure the desired order
of service notifications.

The handlers should not use the role default variables from its role directly
because they might not be available at all times. Some handlers may use
variables in the ``handlers__*`` role namespace to lookup information from the
:file:`secret/` directory maintained by the :ref:`debops.secret` role, but it
should be avoided if possible. If handers depend on the information from the
remote hosts passed via register variables, the command that registered them
needs to be a part of the "handler chain" which notifies subsequent handlers on
changes.

If a service is optional or may not be available on a host, the service role
should provide an ``ansible_local.<role>.installed`` or similar boolean Ansible
local fact. This fact can then be checked by a given handler to determine if
the service is available and can be acted upon.

If a role has an internal :file:`handlers/main.yml` file with additional
handlers defined within, they will be executed **after** the handlers defined
in the :ref:`debops.global_handlers` role.
