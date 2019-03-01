Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To install and manage the OpenLDAP server on a host, you need to add it to the
``[debops_service_slapd]`` Ansible inventory group:

.. code-block:: none

   [debops_service_slapd]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.slapd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/slapd.yml
   :language: yaml

The included :ref:`debops.ferm` and :ref:`debops.tcpwrappers` Ansible roles are
optional. They can be used for managing firewall and access rules to the LDAP
service.

If you further want to enable LDAP transport layer security in ``debops.slapd``
role, the :ref:`debops.pki` and :ref:`debops.dhparam` roles must also be
applied on the host. The ``debops.slapd`` role will automatically detect and
use their configured environments if available.


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


Other resources
---------------

List of other useful resources related to the ``debops.slapd`` Ansible role:

- Manual pages: :man:`slapd(8)`, :man:`slapd-config(5)`

- `LDAP for Rocket Scientists`__, an excellent book about LDAP and OpenLDAP

  .. __: http://www.zytrax.com/books/ldap/

- `Debian LDAP Portal`__ page in the Debian Wiki

  .. __: https://wiki.debian.org/LDAP
