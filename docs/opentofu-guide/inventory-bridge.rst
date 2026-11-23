.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _debops_tofu_inventory:

OpenTofu - Ansible inventory bridge
===================================

.. contents::
   :local:

OpenTofu creates infrastructure. DebOps manages it. The inventory
bridge closes the loop between the two. The
:command:`debops tofu inventory` operation collects the outputs of a
tofu view and renders them into the inventory of the matching Ansible
view. Plan and apply in the morning, :command:`debops run` against
the new hosts in the afternoon.

The bridge is a static renderer. It runs when you tell it to, not on
every Ansible run. A dynamic inventory source would need the unlocked
store and the state passphrase inside every Ansible run, for outputs
that only change on apply. The rendered files are plain inventory
data afterwards, so a dynamic source buys nothing.


What the bridge renders
-----------------------

The operation pairs the OpenTofu view with the Ansible view of the
same name. For the default ``system`` view,
:command:`debops tofu inventory` renders into the inventory
directory of :file:`ansible/views/system/`.
The Ansible view must exist. The project creation scaffolds the
default one.

The operation renders three surfaces:

1. The hosts file of the inventory directory, in the configured
   format, rewritten on every render.
2. The :file:`host_vars/` and :file:`group_vars/` files which carry
   the variables the hosts file cannot hold.
3. The sensitive content files in the Ansible view's store, referenced
   from the rendered variables through :literal:`lookup("file")`.

The renderer writes a manifest of the files it owns. On the next
render it removes the stale entries. Hosts and groups that dropped
out of the seed lose their files, and a hosts file of a changed
format goes away. The renderer never touches your own files in the
inventory.


The seed contract
-----------------

The bridge reads two outputs from the view. The
:literal:`inventory_seed` output is required. It is a map keyed by
the instance name, one entry per host. The optional
:literal:`inventory_groups` output describes the groups the hosts
join.

.. code-block:: json

   {
     "inventory_seed": {
       "web-1": {
         "address": "192.0.2.11",
         "host": "web-1.example.org",
         "groups": ["web", "frontend"],
         "vars": {"ansible_user": "alice"},
         "sensitive_vars": {"host_token": "..."},
         "jump": "gateway.example.org",
         "status": "Running"
       }
     },
     "inventory_groups": {
       "all": {"vars": {"timezone": "CET"}},
       "web": {"children": ["frontend"]}
     }
   }

A host entry carries:

``address``
  The address of the instance. Required. With no label and no FQDN
  it is also the connection target.

``host``
  The DNS name of the instance, when it differs from the seed key.
  Incus container names cannot carry dots. The DNS name can. With no
  label it names the host in the inventory, and the address is the
  connection target.

``label``
  The name the host carries in the inventory: the inventory
  hostname, the key of its :file:`host_vars/` directory and the
  target of :literal:`debops run -l`. It wins over the ``host``
  attribute and the seed key. With a label, the
  ``tofu.inventory.ansible_host_format`` option picks what the
  ``ansible_host`` variable carries: the DNS name (``fqdn``, the
  default) or the address (``ip``). The identity the connection
  target does not carry renders as a plain variable under its
  seed name. The store paths stay keyed by the seed key, so renaming the
  label or the hostname never orphans the sensitive files.

``groups``
  The groups the host joins. Every host joins ``all`` implicitly.

``vars``
  Plain variables of any JSON type: strings, numbers, booleans,
  lists, maps. The seed's own variables win over the ones the bridge
  records automatically.

``sensitive_vars``
  Variables which land in the store instead of the inventory. See
  the section below.

``jump``
  The bastion host for the connection. See the ProxyJump section.

``status``
  The provider-reported state of the instance, when it has one. See
  the statuses section.

A group entry carries ``children`` (the child group names), ``vars``
and ``sensitive_vars``. The ``all`` key is legal and completes the
``all``/group/host hierarchy: its variables ride
:file:`group_vars/all/`.

The sensitivity model follows OpenTofu's own: a
:literal:`sensitive = true` output masks the value in human output
but carries plaintext in the JSON the bridge reads. Per-entry
sensitivity is therefore expressed by the shape itself: the
``sensitive_vars`` maps hold the store material, and the ``vars``
maps hold the inventory literals. Mark the sensitive variables in your
output definition so that human review of :command:`tofu output`
stays safe, and put the actual values into ``sensitive_vars``.


The render surfaces
-------------------

The hosts file format comes from the
``tofu.inventory.hosts_format`` option: ``ini`` (the classic Ansible
inventory, the default), ``yaml``, ``json`` or ``toml``. Pick one
format per project and stay with it. Different inventory plugins
parse the formats, and mixing them in one inventory directory invites
plugin-order trouble. The rendered file name is the
``tofu.inventory.hosts_filename`` base name with the format's
canonical extension appended: :file:`hosts` for ``ini``,
:file:`hosts.yml`, :file:`hosts.json` and :file:`hosts.toml` for
the rest. The renderer removes the files of the inactive formats
when it owns them.

The formats differ in what they can carry inline:

- The ``ini`` hosts file holds the scalar plain variables on the host
  lines. The vars files carry the lists, the maps and the
  sensitive variables. The ini parser reads the values as Python
  literals, so numbers,
  booleans and quoted strings survive with their types.
- The ``yaml``, ``json`` and ``toml`` hosts files carry the plain
  variables of every type natively. Only the sensitive variables ride
  the vars files.

The ``tofu.inventory.vars_filename`` option names the vars file,
:file:`tofu_inventory.yml` by default -- one file carries the
plain and the sensitive variables of a host or group together.
The files live in the :file:`host_vars/<inventory hostname>/`
and :file:`group_vars/<group>/` directories of the Ansible view's
inventory. Variable files support Jinja, unlike
the hosts files -- which is why the sensitive references live there
and not inline.

Your own :file:`host_vars/` files outrank the rendered ones, and the
inline variables of the ``ini`` hosts file rank below them too. You
can therefore override any rendered value in your own files without
touching the bridge.


Sensitive values
----------------

A ``sensitive_vars`` entry becomes two files: the value lands in the
Ansible view's store, and the rendered variable references it:

.. code-block:: yaml

   ---
   host_token: "{{ lookup('file',
                          inventory_dir + '/../secret/tofu/host_vars/'
                          'web-1/sensitive/host_token/content') }}"

The store path comes from the
``tofu.inventory.secret.host_path`` template, relative to the Ansible
view's root:
``secret/tofu/host_vars/<seed key>/sensitive/<var>/content`` for the
hosts, and ``secret/tofu/group_vars/<group>/sensitive/<var>/content``
for the groups from ``tofu.inventory.secret.group_path``. The host
namespace keys by the seed key, so a hostname or label change never
orphans the values. The two namespaces also keep a group which
shares its name with a host from colliding with it. The store unlock
releases the values, the same way the Ansible secret machinery does.
The bridge does not evaluate the lookups: it
writes them as-is, and a playbook run resolves them inside an
unlocked store.


ProxyJump
---------

The ``jump`` attribute of a host composes
``ansible_ssh_common_args='-o ProxyJump=<jump>'`` on the rendered
host line. The bastion needs no inventory presence of its own —
containers on a bridge network are often reachable only through the
host that runs them.

If you need more SSH arguments than the jump, set
``ansible_ssh_common_args`` in your own :file:`host_vars/` file for
that host. Your file outranks the rendered one. Compose the jump into it
yourself.


Statuses and refresh
--------------------

Providers report the state of an instance: a container can be
``Running`` or ``Stopped``. The ``tofu.inventory.host_status``
option keys the handling by the status value, lowercased: ``include``
renders the hosts, ``skip`` leaves them out. The bridge skips a
status without a configured key and names the hosts in a notice. A
new provider status is skipped until the configuration names it.

The render reads the state as of the last refresh or apply. In-place
changes (a NIC moved, a late DHCP lease) do not reach the state until
a refresh runs. The ``tofu.inventory.state_refresh`` option
(default off) refreshes before every render. The
:literal:`-f/--force` option does it for one render. The refresh
churns the state: its serial bumps even with no changes, so the
default leaves it off. A host whose state carries no address skips
with a notice naming the option.


Configuration options
---------------------

.. list-table::
   :widths: 40 60
   :header-rows: 1

   * - Option
     - Purpose
   * - ``tofu.inventory.hosts_format``
     - The hosts file format: ``ini``, ``yaml``, ``json`` or ``toml``.
   * - ``tofu.inventory.hosts_filename``
     - The base name of the rendered hosts file. The format's
       canonical extension rides implicitly.
   * - ``tofu.inventory.ansible_host_format``
     - What ``ansible_host`` carries for a labelled host: ``fqdn``
       (the default) or ``ip``.
   * - ``tofu.inventory.vars_filename``
     - The name of the rendered variables files, plain and sensitive
       together.
   * - ``tofu.inventory.secret.host_path``
     - The store path template of the host sensitive content files,
       keyed by the seed key.
   * - ``tofu.inventory.secret.group_path``
     - The store path template of the group sensitive content files,
       keyed by the group name.
   * - ``tofu.inventory.state_refresh``
     - Refresh the state before every render.
   * - ``tofu.inventory.host_status.<status>``
     - ``include`` or ``skip``, keyed by the lowercased status value.

The rendered files are data, not configuration: nothing references
them except the inventory itself. When you rename a variable in the
seed, the next render writes the new name and the manifest removes
the old file.


See also
--------

- :ref:`debops_tofu` for the OpenTofu integration the bridge
  runs in
- :ref:`project_infrastructure_views` for the view pairing between
  Ansible and OpenTofu
- :ref:`tofu_incus` for a worked example: a container fleet rendered
  into the inventory and configured with DebOps
