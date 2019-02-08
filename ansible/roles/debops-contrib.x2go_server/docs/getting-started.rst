Getting started
===============

.. contents::
   :local:

.. include:: includes/all.rst


Example inventory
-----------------

To setup and manage the X2Go server, add the hosts to the
``debops_service_x2go_server`` Ansible inventory host group:

.. code:: ini

    [debops_service_x2go_server]
    hostname

If you are using debops.sshd_ for configuring your OpenSSH server, you will
need to adopt some of the defaults of this role to allow X2Go clients to
connect to the X2Go server via SSH.
The recommended way to do this adaption is to symlink the
:file:`docs/inventory/debops_service_x2go_server_global_role_vars` file shipped
with this role into your inventory under
:file:`ansible/inventory/group_vars/debops_service_x2go_server_global_role_vars`
and include all hosts from the ``debops_service_x2go_server`` in the
``debops_service_x2go_server_global_role_vars`` host group by adding this:

.. code:: ini

   [debops_service_x2go_server_global_role_vars:children]
   debops_service_x2go_server

into your host inventory which makes the following adjustments to the defaults
variables of other roles:

.. literalinclude:: inventory/debops_service_x2go_server_global_role_vars
   :language: yaml

Example playbook
----------------

Here's an example playbook that can be used to setup and manage X2Go server:

.. literalinclude:: playbooks/x2go_server.yml
   :language: yaml

This playbooks is shipped with this role under
:file:`docs/playbooks/x2go_server.yml` from which you can symlink it to your
playbook directory. In case you use multiple `DebOps Contrib`_ roles, consider
using the `DebOps Contrib playbooks`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::x2go_server``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
