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

zabbix_server__media_types, zabbix_server__actions, zabbix_server__user_groups, zabbix_server__users
--------------------------------------------------------------------------------------------------------

These four variables manage global Zabbix objects via the JSON-RPC API,
using respectively the ``mediatype``, ``action``, ``usergroup`` and ``user``
API method families (``*.get``, ``*.create``, ``*.update``). Each list item
is a dictionary of the parameters accepted by the corresponding ``create``/
``update`` API methods directly - see the `Zabbix API reference
<https://www.zabbix.com/documentation/current/en/manual/api/reference>`__
for the exact fields available for each object type. The role looks up
existing objects by their natural key (``name`` for media types, actions
and user groups; ``username`` for users) to decide whether to create a new
object or update an existing one; fields left unspecified on an update are
not modified by Zabbix.

Passwords and API tokens used in these variables (SMTP credentials,
Pushover application tokens, user passwords, ...) should always come from
the DebOps ``secret/`` directory via a ``lookup('password', ...)``
expression, not be hardcoded in the inventory.

Example, an Email media type and a user in the built-in "Zabbix
administrators" user group with Email notifications enabled:

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

.. _zabbix_server__ref_templates:

zabbix_server__templates
--------------------------

List of custom Zabbix templates imported via the ``configuration.import``
JSON-RPC API method (createMissing/updateExisting enabled for templates,
items, triggers, graphs, template dashboards and value maps). Each item
should define:

``name``
  Used only as the Ansible task label, does not have to match the actual
  template name.

``source``
  Contents of a Zabbix template export file in JSON format, usually
  provided via a Jinja ``lookup('file', ...)`` expression pointing at a file
  in the role's or the playbook project's ``files/`` directory.

By default the role imports the "LXC container" template shipped in
:file:`files/templates/zabbix_template_lxc_container.json`, used together
with ``zabbix_agent__cgroup_metrics`` on the :ref:`debops.zabbix_agent`
side. Add your own custom templates by extending this list at the
inventory level.

.. _zabbix_server__ref_host_item_overrides:

zabbix_server__host_item_overrides
-------------------------------------

List of item status overrides applied to all hosts linked to a given
template, used to disable host-wide metrics which become misleading once a
more specific template is linked to the same host - for example
``system.cpu.load*``/``system.cpu.util*`` items from the "Linux by Zabbix
agent" template are not meaningful on LXC containers once the "LXC
container" template is linked, since ``/proc/loadavg`` and ``/proc/stat``
inside an LXC container reflect the whole host, not the individual
container's cgroup.

Each list item is a dictionary with:

``template``
  Technical name of the Zabbix template (the API ``host`` field, not the
  human-readable ``name`` shown in the web interface) whose linked hosts
  should be affected.

``key_regex``
  Regular expression (Python ``re.search()`` syntax) matched against the
  item key.

Example, disabling host-wide disk I/O metrics on hosts using network
storage where they are not meaningful:

.. code-block:: yaml

   zabbix_server__host_item_overrides:

     - template: 'Some template name'
       key_regex: '^vfs\.dev\.'
