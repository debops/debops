.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
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
- when :envvar:`zabbix_server__frontend_enabled` is ``True`` (the default),
  configure the PHP-FPM pool and nginx vhost for the web frontend, with
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
- import templates from the :envvar:`zabbix_server__templates` lists, and
  apply the :envvar:`zabbix_server__host_item_overrides` lists; both are
  empty by default.

On subsequent runs, since the ``Admin`` password might have been changed
manually through the web interface after the initial bootstrap, the role
uses the previously bootstrapped API token instead of the password. If
neither the stock default password, the ``secret/``-generated password, nor
an existing token work, the role fails with an explicit message instead of
silently resetting the account.

When the token file in ``secret/`` is missing, the role looks up the
existing :envvar:`zabbix_server__api_token_name` token of the ``Admin``
account and generates a new string for it. If that token is disabled or
expired, the role stops instead; enable it and clear its expiry date in
the frontend, or delete it so that the role creates a new one.

Set :envvar:`zabbix_server__api_enabled` to ``False`` to skip the API bootstrap
and management and keep Zabbix Server installed. The API is provided by the web
frontend, so the API management is also disabled by default when
:envvar:`zabbix_server__frontend_enabled` is ``False``.

Setting :envvar:`zabbix_server__deploy_state` to ``absent`` removes Zabbix
Server with its frontend, but keeps the database and its PostgreSQL role.
Setting :envvar:`zabbix_server__frontend_enabled` to ``False`` does not remove
a frontend which is already installed; its package, PHP-FPM pool and nginx
configuration have to be removed manually.


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
       usrgrps: [ { usrgrpid: '7' } ]
       medias:
         - mediatypeid: '1'
           sendto: [ 'jdoe@example.org' ]

The ``roleid: 3`` in the example is the built-in "Super admin role", which has
full access to Zabbix. An account with a lower role receives notifications only
about hosts which its user groups have permission to read, so grant that
permission first when you use such a role.

``usrgrps`` and ``medias`` are passed to the ``user.create``/``user.update``
Zabbix API methods as-is, without any name-to-id lookup by the role, so they
require real numeric IDs. The :envvar:`zabbix_server__user_groups` and
:envvar:`zabbix_server__media_types` lists create missing objects or update
existing ones by name. ``7`` and ``1`` above are the well-known IDs of the
built-in "Zabbix administrators" user group and "Email" media type present
on every fresh Zabbix installation; the example entries use those names, so
the role updates the built-in objects and the IDs stay stable. A new name
creates a new object with a new ID -- look that ID up first, for example with
``debops exec HOSTNAME -m ansible.builtin.uri -a "url=https://.../api_jsonrpc.php ..."``
or the Zabbix frontend, and use that value instead.

The role sets the Frontend URL in the Zabbix settings and the
``{$ZABBIX.URL}`` global macro to :envvar:`zabbix_server__frontend_url`, so
that notifications sent by the built-in webhook media types, like Pushover or
Slack, link to the events in the frontend.

See :ref:`zabbix_server__ref_media_types` for the full parameter reference
(the media type, action and user list variables map directly onto the
Zabbix API method parameters, see the `Zabbix API reference
<https://www.zabbix.com/documentation/current/en/manual/api/reference>`__).


Firewall
--------

The trapper port (``10051``) is opened in the firewall only for the
addresses in the :envvar:`zabbix_server__allow`,
:envvar:`zabbix_server__group_allow` and :envvar:`zabbix_server__host_allow`
lists. When all of them are empty, which is the default, the port is closed
and only the passive checks, for which the server connects to the agents,
work. Agents with active checks, hosts which send values to trapper items
and Zabbix proxies need to be allowed. This is different from the
:ref:`debops.zabbix_agent` role, where an empty list allows connections from
any address.

.. code-block:: yaml

   zabbix_server__allow: [ '192.0.2.0/24' ]


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

The database schema creates a "Zabbix server" host, which monitors the
server itself with the "Zabbix server health" template and checks an agent on
``127.0.0.1`` without encryption. When the :ref:`debops.zabbix_agent` role
registers the same host through the API, the host is present in Zabbix twice,
and the agent interface of the default host is unavailable if the agent
requires TLS. The role does not manage hosts, so link the template to the
registered host and delete the default host in the frontend afterwards:

.. code-block:: yaml

   zabbix_agent__api_host_link_templates: [ 'Zabbix server health' ]
   zabbix_agent__api_host_host_groups: [ 'Zabbix servers' ]

Deleting the default host also deletes its items, and the server health
history collected on them is removed by the housekeeper; the template linked to
the registered host starts with new items. Back up the database first if you
need that history.

The template has its own "Zabbix server health" dashboard. The global
dashboard with the same name and the "Global view" dashboard still select the
"Zabbix server" host by name, so change or remove them.


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
  Bootstrap the API credentials and manage the Zabbix settings and global
  Zabbix API objects (global macros, media types, actions, users, templates,
  host item overrides).
