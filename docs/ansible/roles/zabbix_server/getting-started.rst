.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
================

.. only:: html

   .. contents::
      :local:


General deployment notes
-------------------------

The role is designed to bootstrap a brand new Zabbix installation from an
empty PostgreSQL database, without any manual steps through the web
interface. On the first run it will:

- install the ``zabbix-server-pgsql`` package and the official
  :envvar:`zabbix_server__version` APT repository,
- create the PostgreSQL role and database via the :ref:`debops.postgresql`
  role (see :envvar:`zabbix_server__postgresql__dependent_roles` and
  :envvar:`zabbix_server__postgresql__dependent_databases`),
- import the SQL schema shipped in the ``zabbix-sql-scripts`` package,
  detecting an already initialized database by checking for the
  ``dbversion`` table rather than a local marker file, so that the check
  stays correct even if the database is later restored from a backup,
- configure the PHP-FPM pool and nginx vhost for the web frontend, with
  a :file:`/etc/zabbix/web/zabbix.conf.php` file that skips the interactive
  setup wizard,
- log in via the API using the stock ``Admin``/``zabbix`` credentials
  created by the schema, change the ``Admin`` password to a value generated
  by the DebOps ``secret/`` mechanism, and create a long-lived API token
  used for all further API management (see
  :envvar:`zabbix_server__api_admin_password_path` and
  :envvar:`zabbix_server__api_token_path`),
- enable the built-in "Report problems to Zabbix administrators" action,
  which is created by the database schema but left disabled - without this
  step, no notification is ever sent regardless of configured media types
  and users,
- import the "LXC container" template shipped with the role, and apply any
  :envvar:`zabbix_server__host_item_overrides` (see below).

On subsequent runs, since the ``Admin`` password might have been changed
manually through the web interface after the initial bootstrap, the role
uses the previously bootstrapped API token instead of the password. If
neither the stock default password, the ``secret/``-generated password, nor
an existing token work, the role fails with an explicit message instead of
silently resetting the account.

The database schema import and the API bootstrap/management steps can be
disabled independently with :envvar:`zabbix_server__deploy_state` set to
``absent`` (removes everything) or :envvar:`zabbix_server__api_enabled` set
to ``False`` (keeps Zabbix Server installed, skips the API management
tasks).


Notifications: media types, actions and users
-----------------------------------------------

By default the role only ensures that the "Report problems to Zabbix
administrators" action is enabled; no media types or users are configured,
since these require access to credentials (SMTP server, Pushover
application tokens, ...) that should not be hardcoded in a public
repository. Define them at the Ansible inventory level, sourcing secrets
via the ``lookup('password', ...)`` mechanism or from your own encrypted
variables. Example:

.. code-block:: yaml

   zabbix_server__media_types:

     - name: 'Email'
       type: 0
       smtp_server: 'smtp.example.org'
       smtp_helo: '{{ ansible_domain }}'
       smtp_email: 'zabbix@example.org'
       status: 0

   zabbix_server__user_groups:

     - name: 'Zabbix administrators'

   zabbix_server__users:

     - username: 'jdoe'
       passwd: "{{ lookup('password', secret + '/zabbix/users/jdoe/password length=32') }}"
       roleid: 3
       usrgrps: [ { usrgrpid: '{{ zabbix_server__register_api_usrgrpid_jdoe | d(omit) }}', name: 'Zabbix administrators' } ]
       medias:
         - mediatypeid: 'Email'
           sendto: [ 'jdoe@example.org' ]

See :ref:`zabbix_server__ref_media_types` for the full parameter reference
(the media type, action and user list variables map directly onto the
Zabbix API method parameters, see the `Zabbix API reference
<https://www.zabbix.com/documentation/current/en/manual/api/reference>`__).


LXC container metrics
-----------------------

The role imports a custom "LXC container" template
(:file:`files/templates/zabbix_template_lxc_container.json`) which defines
``ct.cpu.util``, ``ct.memory.used`` and ``ct.memory.util`` items, based on
cgroup accounting rather than host-wide ``/proc`` values that are
misleading inside an LXC container (see the
:ref:`debops.zabbix_agent` role documentation for the corresponding
``zabbix_agent__cgroup_metrics`` UserParameters). The role also
disables the host-wide ``system.cpu.load*``/``system.cpu.util*`` items on
any host linked to this template, via
:envvar:`zabbix_server__host_item_overrides`, since they would otherwise
show the whole host's load average instead of the individual container's
resource usage.


Example inventory
-------------------

The Zabbix Server application uses a PostgreSQL database as its backend and
a PHP-FPM/nginx web frontend. To deploy it on a given host, add it to the
``[debops_service_zabbix_server]`` Ansible inventory group. Complete example
inventory:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_postgresql_server]
   hostname

   [debops_service_zabbix_server]
   hostname

   [debops_service_zabbix_agent]
   hostname


Example playbook
-------------------

If you are using this role without DebOps, here's an example Ansible
playbook that uses the ``debops.zabbix_server`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/zabbix_server.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
-------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after the host is
first configured to speed up playbook execution, when you are sure that
most of the configuration has not been changed.

Available role tags:

``role::zabbix_server``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::zabbix_server:schema``
  Check and, if needed, import the PostgreSQL database schema.

``role::zabbix_server:frontend``
  Generate the web frontend configuration file.

``role::zabbix_server:api``
  Bootstrap the API credentials and manage the global Zabbix API objects
  (media types, actions, users, templates, host item overrides).
