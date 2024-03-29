.. Copyright (C) 2016-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


OpenLDAP features enabled by default
------------------------------------

The ``debops.slapd`` role enables and configures some of the OpenLDAP features
that otherwise are enabled dynamically and could have different names in the
LDAP directory on different installations due to the order in which they were
enabled. If you are planning to apply the role on an existing installation, you
should review the configuration before doing so - the OpenLDAP server usually
refuses the incorrect configuration outright, which should not affect the
existing installation, but that's not a 100% guarantee.

.. only:: html

   - :ref:`slapd__ref_overlays`
   - :ref:`slapd__ref_ldap_schemas`
   - :ref:`slapd__ref_acl`


Access to service denied by default
-----------------------------------

The default configuration denies access to the OpenLDAP service from anywhere
through the firewall and TCP Wrappers, although the :command:`slapd` daemon
will listen for connections on all interfaces. You can use the
``slapd__*_allow`` variables to define what IP addresses or subnets have access
to the LDAP service.

If you don't use the :ref:`debops.ferm` and the :ref:`debops.tcpwrappers`
Ansible roles to control access to services, keep in mind that the OpenLDAP
service will be available publicly. This might be important while designing the
LDAP Access Control List and password policies.

You can control the default behaviour using the :envvar:`slapd__accept_any`
boolean variable. Another option is to use an external firewall with IDS/IPS
systems that can analyze LDAP traffic. Access through a VPN connection, for
example using the :ref:`debops.tinc` Ansible role, can also be a good option
for limiting the exposure of LDAP directory directly to the Internet.


SASL authentication
-------------------

The role uses the :ref:`debops.saslauthd` Ansible role to configure the
:command:`saslauthd` service which provides SASL authentication capability. PAM
authentication is used by default to authenticate LDAP access via the UNIX
accounts. If LDAP support is configured on the host by the :ref:`debops.ldap`
role, the directory will be used for authentication instead.

Humans can authenticate themselves by specifying their account names without
a domain part, which are defined by the ``uid`` attribute of their
``inetOrgPerson`` LDAP objects, looked up in the ``ou=People`` subtree of the
LDAP directory.

Computers can authenticate to the LDAP directory by specifying an UNIX account
name and their FQDN domain name, for example ``sshd@host.example.org``, which
corresponds to the ``uid`` and ``host`` attributes of the ``account`` LDAP
objects. Only hosts that have been registered in the LDAP directory
``ou=Hosts`` subtree can authenticate with this method.

The :ref:`debops.saslauthd` role defines the ``slapd`` LDAP profile which
contains the LDAP search query and filtering rules which can be used for access
control to the OpenLDAP directory itself.


Authentication debugging and logs
---------------------------------

By default the :command:`slapd` log output is set to ``none``, which results in
minimal logs. If you need to debug or keep track of LDAP authentication and
search queries, you can easily configure :command:`slapd` to do that through
the Ansible inventory, by adding a configuration file, for example in a cluster
of LDAP hosts:

.. code-block:: yaml

   ---
   # ansible/inventory/group_vars/slapd_cluster/slapd.yml

   slapd__group_tasks:

     - name: 'Configure the OpenLDAP server log level'
       dn: 'cn=config'
       attributes:
         olcLogLevel: 'stats'
       state: 'exact'

Make sure that the ``name`` parameter corresponds to the correct
:command:`slapd` option defined in the :envvar:`slapd__default_tasks` variable,
to modify it using :ref:`universal_configuration` mechanism included in DebOps.

You can use :command:`journald` to view the :command:`slapd` logs:

.. code-block:: console

   journald -f -u slapd.service


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
   :lines: 1,5-

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

``role::slapd:tasks``
  Run the LDAP tasks generated by the role to apply OpenLDAP ``cn=config``
  configuration. This will also include the ACL tests.

``role::slapd:slapacl``
  Run tasks that maintain the :command:`slapacl` test suite script and perform
  OpenLDAP ACL tests when enabled.


Other resources
---------------

List of other useful resources related to the ``debops.slapd`` Ansible role:

- Manual pages: :man:`slapd(8)`, :man:`slapd-config(5)`

- `LDAP for Rocket Scientists`__, an excellent book about LDAP and OpenLDAP

  .. __: http://www.zytrax.com/books/ldap/

- `Debian LDAP Portal`__ page in the Debian Wiki

  .. __: https://wiki.debian.org/LDAP
