.. _tor__ref_getting_started:

Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

To manage `changeme/FIXME** on a given host or set of hosts, they need to
be added to the ``[debops_service_tor]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_tor]
   hostname

It is proposed to change some of the nusenu.relayor defaults to better match DebOps Standards.
The recommended way to do this adaption is to symlink the
:file:`docs/inventory/debops_service_tor_global_role_vars` file shipped
with this role in the documentation (:file:`ansible/roles/debops-contrib.tor/docs/inventory/debops_service_tor_global_role_vars`)` into your inventory under
:file:`ansible/inventory/group_vars/debops_service_tor_global_role_vars`
and include all hosts from the ``debops_service_tor`` in the
``debops_service_tor_global_role_vars`` host group by adding this:

.. code:: ini

   [debops_service_tor_global_role_vars:children]
   debops_service_tor

into your host inventory which makes the following adjustments to the defaults
variables of other roles:

.. literalinclude:: inventory/debops_service_tor_global_role_vars
   :language: yaml

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops-contrib.tor`` role:

.. literalinclude:: playbooks/tor.yml
   :language: yaml

The playbook is shipped with this role under
:file:`./docs/playbooks/tor.yml` from which you can symlink it to your
playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider using the
`DebOps Contrib playbooks`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::tor``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::tor:pkgs``
  Tasks related to system package management like installing or
  removing packages.
