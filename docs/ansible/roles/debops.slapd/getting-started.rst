Getting started
===============

Example inventory
-----------------

The ``debops.slapd`` role is included by default in the
:file:`service/slapd.yml` DebOps playbook. When using DebOps simply add the
host which should run OpenLDAP to the ``debops_service_slapd`` host group in
the Ansible inventory file :file:`ansible/inventory/hosts`::

    [debops_service_slapd]
    hostname


Example playbook
----------------

If you are using this role without Debops, here's an example Ansible playbook
that uses the ``debops.slapd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/slapd.yml
   :language: yaml

The inclusion of the ``debops.ferm`` and ``debops.tcpwrappers`` roles are
optional. They can be used for managing firewall and access rules to the
LDAP service.

If you further want to enable LDAP transport layer security in ``debops.slapd``,
the ``debops.pki`` and ``debops.dhparam`` roles must also be included in your
Ansible playbook.


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::slapd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
