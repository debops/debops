.. Copyright (C) 2019 Rainer 'rei' Schuth <devel@reixd.net>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

Default configuration
---------------------

The ``debops.postldap`` role configures a Postfix SMTP server with
support for a ``virtual user mail system``, i.e. where the senders and
recipients do not correspond to the Linux system users.
Hence it is possible to host emails for other domains.
The users, email alias and domains will be managed with LDAP.
This role use the organization defined in the mailservice schema setup by
:ref:`debops.slapd` by default. The schema is designed to use the 'mail' LDAP
attribute as an uniqueness constraint for the ``mailAddress``,
``mailAlternateAddress`` and other attributes across LDAP entries. The 'mail'
attribute itself is not used in e-mail service operation.
For example, the following LDAP entry sets the user ``user1`` with
user1@mydomain.net as main address and alias1@mydomain.net as alias. His
received messages will be distributed into ``/var/vmail/mydomain.net/user1``.

.. code-block:: none

   objectClass: inetOrgPerson
   objectClass: mailRecipient
   objectClass: authorizedServiceObject
   authorizedService: all
   mail: user1@mydomain.net
   mailAddress: user1@mydomain.net
   mailAlternateAddress: alias1@mydomain.net
   mailHomeDirectory: /var/vmail/mydomain.net/user1

Local mail is enabled by default, support for mail aliases is provided by
the :ref:`debops.etc_aliases` Ansible role and the LDAP user attribute
``mailAlternateAddress``.

From a single address it is also possible to deliver the message to several
recipients by using the ``mailAlias`` structural object to define a standalone
e-mail aliases:

.. code-block:: none

   objectClass: mailAlias
   objectClass: authorizedServiceObject
   authorizedService: all
   mail: alias@mydomain.net
   mailAddress: alias@mydomain.net
   mailForwardTo: user1@mydomain.net
   mailForwardTo: user2@mydomain.net

It is also possible to attach an email existing entity using the
'mailDistributionList' auxiliary object:

.. code-block:: none

   objectClass: organizationalUnit
   objectClass: mailDistributionList
   objectClass: authorizedServiceObject
   authorizedService: all
   ou: IT Department
   mail: itdept@mydomain.net
   mailAddress: itdept@mydomain.net
   mailForwardTo: admin1@mydomain.net
   mailForwardTo: admin2@mydomain.net

The ``mailAddress`` attribute of the different objects will ensure that the
addess is unique in the mail system.

This role only works when **LDAP support is explicitly enabled** and the
environment has a working LDAP infrastructure. See the :ref:`debops.ldap` role
and its documentation for more details about setting up LDAP client support on
a host.


Overriding lookup table configuration
-------------------------------------

The Postfix LDAP lookup tables defined by the :ref:`debops.ldap` Ansible role
are designed to work with the LDAP directory set up by the :ref:`debops.ldap`
and :ref:`debops.slapd` roles. If you want to use different LDAP directory
configuration, or tailor the default configuration to your own needs, you can
override specific parameters in the looup table configuration via the Ansible
inventory.

The role defers to the :ref:`debops.postfix` Ansible role for actual looup
table configuration and passes the details via the role dependent variables.
You can find more about the details in the :ref:`postfix__ref_lookup_tables`
documentation.

For example, if you want to change the LDAP filter of the
:file:`ldap_virtual_recipients.cf` lookup table, you can defined in the Ansible
inventory:

.. code-block:: yaml

   # ansible/inventory/host_vars/mail-server/postfix.yml

   postfix__host_lookup_tables:

     - name: 'ldap_virtual_recipients.cf`
       state: 'append'
       query_filter: '(&(|(mail=%s)(mailAlias=%s)))'

Please note that the configuration is defined in the ``postfix__*`` variables,
not ``postldap__*`` variables. It is also important to use the ``append`` state
to make sure that the configuration is only applied when the
:ref:`debops.postldap` configuration is "active".

If you want to disable a part of the LDAP configuration defined in the Ansible
inventory, you can change the state to ``ignore``, which will then use the
definition from the role defaults.

Avoid any other states in this case, because the resulting configuration will
be applied in different contexts, for example when you run the
:ref:`debops.postfix` role directly, and will break your configuration.

After making your changes, you can apply them by running the command:

.. code-block:: console

   debops service/postldap -l mail-server -t role::postfix --diff

This will execute the :ref:`debops.postfix` role in the context of the
:ref:`debops.postldap` role and correct set of variables will be active.


Example inventory
-----------------

To install and configure Postfix Virtual Mail Server on a host,
it needs to be present in the ``[debops_service_postldap]``
Ansible inventory group:

.. code-block:: ini

   [debops_service_slapd]
   ldap-server

   [debops_service_postfix]
   mail-server

   [debops_service_postconf]
   mail-server

   [debops_service_postldap]
   mail-server

The ``debops.postldap`` playbook configures only the LDAP part of postfix
configuration, you should use the :ref:`debops.postfix` role and its playbook
to set up Postfix mail server. Additional useful configuration can be found in
the :ref:`debops.postconf` role.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.postldap`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/postldap.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::postldap``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
