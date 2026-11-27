.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
==========================

Some of ``debops.zabbix_server`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation
and examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _zabbix_server__ref_configuration:

zabbix_server__configuration
------------------------------

The ``zabbix_server__*_configuration`` variables define the contents of the
:file:`/etc/zabbix/zabbix_server.d/ansible.conf` configuration drop-in file.
The variables are combined in the order defined in the
:envvar:`zabbix_server__combined_configuration` variable using the
:ref:`universal_configuration` format (the same format used by the
:ref:`debops.zabbix_agent` role), and rendered via the
``debops.debops.parse_kv_config`` filter, which merges entries with the same
``name``, later entries taking precedence.

Entries in the ``absent``, ``ignore`` and ``init`` states are not written to
the file. When the ``value`` is a list, the option is repeated for each of
its elements. An entry which does not set ``state`` inherits it from the
previous entry with the same name, so options which are commented out by
default need ``state: 'present'`` to be enabled.

Example, enabling verbose debug logging:

.. code-block:: yaml

   zabbix_server__configuration:

     - name: 'DebugLevel'
       value: 4
       state: 'present'

See :envvar:`zabbix_server__default_configuration` for the list of options
defined by the role itself, most of which are rendered as documentation-only
comments (``state: 'comment'``) reflecting the built-in Zabbix Server
defaults.

.. _zabbix_server__ref_media_types:

Zabbix API objects
------------------

The ``zabbix_server__*_global_macros``, ``zabbix_server__*_media_types``,
``zabbix_server__*_actions``, ``zabbix_server__*_user_groups`` and
``zabbix_server__*_users`` lists manage global Zabbix objects via the JSON-RPC
API, using respectively the ``usermacro`` (``createglobal``, ``updateglobal``
and ``deleteglobal``), ``mediatype``, ``action``, ``usergroup`` and ``user``
API methods. Each entry is a dictionary of the parameters accepted by the
``create`` and ``update`` methods - see the `Zabbix API reference
<https://www.zabbix.com/documentation/current/en/manual/api/reference>`__
for the fields of each object type. The role looks up existing objects by
their ``name``, ``username`` in the case of users, or ``macro`` in the case of
global macros, to decide whether to create a new object or update an existing
one. Fields which are not specified are not modified in an existing object.

The role defines the ``{$ZABBIX.URL}`` global macro, which the built-in webhook
media types use to link to events in the frontend, with the value of
:envvar:`zabbix_server__frontend_url`.

Existing objects are updated on every run. The role does not compare them with
the API first, so only creation and removal of objects is reported as a change.
The check mode does not predict changes in these objects.

An action which does not exist is created only when its entry contains the
``eventsource`` parameter, which is required by the API. The entries without it,
like the default one, can only change an existing action.

The ``passwd`` parameter of a user is sent only when the user is created,
because the API ends all sessions of the user on each update with a password.
Change the password of an existing user in the Zabbix frontend.

For each object type the lists are combined in this order:
``zabbix_server__default_*``, ``zabbix_server__*``,
``zabbix_server__group_*``, ``zabbix_server__host_*``. Entries with the same
``name`` (``username`` for users, ``macro`` for global macros) are merged, and the parameters from a later
entry replace the ones from an earlier entry. The merge is shallow: lists
like ``parameters`` of a media type or ``medias`` of a user are replaced as
a whole.

The role also recognizes these parameters, which are not sent to the API:

``state``
  Optional. If not specified or ``present``, the object is created or
  updated. If ``absent``, the object is removed from Zabbix. Entries with
  ``init`` state do not change anything in Zabbix until a later entry sets
  the state to ``present``. Entries with ``ignore`` state are not taken into
  account when the lists are merged, so they do not disable an earlier entry.

  An entry without ``state`` inherits it from an earlier entry with the same
  name. To restore an object which is ``absent`` on the group level, its
  entry on the host level has to set ``state: 'present'``.

``weight``, ``comment``
  Optional. The order of the entries, and a comment.

Passwords and API tokens used in these variables should always come from the
DebOps ``secret/`` directory via a ``lookup('password', ...)`` or
``lookup('file', ...)`` expression, not be hardcoded in the inventory.

Examples
~~~~~~~~

An Email media type and a user in the built-in "Zabbix administrators" user
group with Email notifications enabled. The ``roleid: 3`` is the built-in "Super
admin role" with full access to Zabbix:

.. code-block:: yaml

   zabbix_server__media_types:

     - name: 'Email'
       type: 0
       smtp_server: 'smtp.example.org'
       smtp_helo: 'example.org'
       smtp_email: 'zabbix@example.org'
       status: 0

   zabbix_server__users:

     - username: 'jdoe'
       passwd: "{{ lookup('password', secret + '/zabbix/users/jdoe/password length=32') }}"
       roleid: 3
       usrgrps: [ { usrgrpid: '7' } ]
       medias:
         - mediatypeid: '1'
           sendto: [ 'jdoe@example.org' ]
           active: 0
           severity: 63
           period: '1-7,00:00-24:00'

A global macro used by templates, and a secret one (``type: 1``) with its
value from the ``secret/`` directory:

.. code-block:: yaml

   zabbix_server__global_macros:

     - macro: '{$SNMP_COMMUNITY}'
       value: 'monitoring'

     - macro: '{$HTTP.PASSWORD}'
       value: "{{ lookup('password', secret + '/zabbix/macros/http_password length=32') }}"
       type: 1
       description: 'Password for the HTTP checks'

On a specific host, use a different SMTP server in the media type defined
above, disable the default action and remove a user:

.. code-block:: yaml

   zabbix_server__host_media_types:

     - name: 'Email'
       smtp_server: 'smtp.example.net'

   zabbix_server__host_actions:

     - name: 'Report problems to Zabbix administrators'
       status: 1

   zabbix_server__host_users:

     - username: 'jdoe'
       state: 'absent'

.. note:: Since object IDs (``mediatypeid``, ``usrgrpid``, ...) are only
   known after the referenced object is created by the API, cross-references
   between the lists above (for example a user's ``usrgrps``/``medias``)
   currently need to use IDs that are stable in a fresh installation (Zabbix
   creates built-in user groups and media types with predictable IDs), or be
   looked up separately with the API token stored in the DebOps ``secret/``
   directory at :envvar:`zabbix_server__api_token_path` and the
   ``ansible.builtin.uri`` module in a custom task. After this role has
   run, the same token is available in the current play as
   ``zabbix_server__register_api_token_content``.

.. _zabbix_server__ref_settings:

zabbix_server__settings
-----------------------

The :envvar:`zabbix_server__settings` dictionary contains the parameters of
the ``settings.update`` API method, which correspond to the "Administration ->
General" pages of the Zabbix frontend. It is merged with
:envvar:`zabbix_server__default_settings`, which sets the Frontend URL
(``url``) to :envvar:`zabbix_server__frontend_url`. When that variable is
empty, the role does not send ``url`` and a Frontend URL set earlier stays in
Zabbix; set ``url`` to an empty string in :envvar:`zabbix_server__settings` to
clear it. The ``{$ZABBIX.URL}`` global macro is also left in place and can be
removed with an ``absent`` entry in :envvar:`zabbix_server__global_macros`.

The role reads the current settings and sends only the parameters which
differ, so a change is reported also in the check mode. The API returns all
values as strings, so use the same form as the API, for example ``1`` and not
``True``. Parameters which are not specified are not modified.

Example, setting the default time zone and the working time of the frontend:

.. code-block:: yaml

   zabbix_server__settings:
     default_timezone: 'Europe/Warsaw'
     work_period: '1-5,08:00-17:00'

.. _zabbix_server__ref_templates:

zabbix_server__templates
------------------------

The ``zabbix_server__*_templates`` lists define Zabbix templates imported via
the ``configuration.import`` JSON-RPC API method. Missing templates, items,
triggers, graphs, template dashboards and value maps are created, and
existing ones are updated. A template is imported when it differs from the one
in Zabbix, which is also reported in the check mode. The lists are empty by default. They are merged
in the same way as the other objects, with these parameters:

``name``
  Required. An identifier of the entry, does not have to match the actual
  template name.

``source``
  Required. Contents of a Zabbix template export file in JSON format,
  usually provided via a Jinja ``lookup('file', ...)`` expression.
  The file should be exported from Zabbix. Default values of properties written
  explicitly, for example ``value_type`` set to ``UNSIGNED``, or a different
  order of dashboard widgets and their fields are reported as a difference on
  each run. To avoid that, import a template edited by hand and export it again.

``state``
  Optional. If not specified or ``present``, the template is imported. With
  ``init`` state the template is not imported. The ``absent`` state is not
  supported and stops the role, because removal of a template would also
  remove its items and their data from all linked hosts; such a template has
  to be removed in the Zabbix frontend.

Example:

.. code-block:: yaml

   zabbix_server__templates:

     - name: 'Custom application'
       source: "{{ lookup('file', inventory_dir + '/../files/zabbix/application.json') }}"

.. _zabbix_server__ref_host_item_overrides:

zabbix_server__host_item_overrides
----------------------------------

The ``zabbix_server__*_host_item_overrides`` lists define item status
overrides applied to all hosts linked to a given template. They are used to
disable metrics which become misleading once a more specific template is
linked to the same host. For example, the load average from the "Linux by
Zabbix agent" template can show the load of the whole host instead of the
container in which the agent runs. The lists are empty by default and are
merged in the same way as the other objects, with these parameters:

``name``
  Required. An identifier of the entry.

``template``
  Required. Technical name of the Zabbix template (the API ``host`` field,
  not the human-readable ``name`` shown in the web interface) whose linked
  hosts should be affected.

``key_regex``
  Required. Regular expression (Python ``re.search()`` syntax) matched
  against the item key.

``state``
  Optional. If not specified or ``present``, the matching items are disabled.
  If ``absent`` or ``init``, the override is not applied. Items which are
  already disabled are not enabled again, because the role does not know
  which of them were disabled in a different way.

Example, disabling host-wide disk I/O metrics on hosts using network storage
where they are not meaningful:

.. code-block:: yaml

   zabbix_server__host_item_overrides:

     - name: 'network-storage'
       template: 'Some template name'
       key_regex: '^vfs\.dev\.'

The variables for the group and host levels are named
:envvar:`zabbix_server__group_host_item_overrides` and
:envvar:`zabbix_server__host_host_item_overrides`.
