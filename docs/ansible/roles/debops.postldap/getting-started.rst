Getting started
===============

Default configuration
---------------------

The ``debops.postldap`` role configures a Postfix SMTP server with
support for a ``virtual user mail system``, i.e. where the senders and
recipients do not correspond to the Linux system users.
Hence it is possible to host emails for other domains.
The users, email alias and domains will be managed with LDAP.
Local mail is enabled by default, support for mail aliases is provided by
the :ref:`debops.etc_aliases` Ansible role and the LDAP user attribute
``mailAlias``.

This role only works when **LDAP support is explicitly enabled** and the
environment has a working LDAP infrastructure. See the :ref:`debops.ldap` role
and its documentation for more details about setting up LDAP client support on
a host.


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
