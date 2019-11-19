.. _postldap__ref_guides:

Postfix configuration guides
============================

Here you can find a few guides that can help you configure more advanced
Postfix features. Some of these can and are implemented as separate Ansible
roles, here you can see the configuration specific to ``debops.postfix`` role.

.. contents:: Sections
   :local:

.. _postldap__ref_guides_virtual_user_mail:

Configure Postfix as a Virtual User Mail System
-----------------------------------------------

This guide describes how to set up a virtual user mail system, i.e.
where the senders and recipients do not correspond to the Linux system users.

It requires a working LDAP infrastructure (See :ref:`debops.ldap` and
:ref:`debops.slapd`) in order to manage and authenticate the users and get
the corresponding email address and aliases.
It is also possible to configure accounts with `wildcard` (catch-all)
email addresses. The default configuration uses first the aliases set by
:ref:`debops.etc_aliases` and then queries the LDAP server, if no match was found.

See also :ref:`debops.dovecot` and :ref:`debops.roundcube` for an IMAP server
and Email-Webclient correspondingly.

The following example shows a real-world™ setup on the Hetzner Cloud. It consists of two servers,
one ``controller`` and a ``mail-server``. The LDAP directory is hosted also in the ``controller``.
``mail-server`` has access to LDAP over an internal network (10.10.10.0/28) attached directly to the VMs.
This setup has no internal DNS server (no split-DNS), thus internal IPs are mapped to DNS entries in the form ``$service.hetzner.mydomain.net``.

.. code-block:: yaml
  :caption: ansible/inventory/group_vars/hetzner/ldap.yml

  ---

  # Enable LDAP, as is deactivated by default
  ldap__enabled: True

  ldap__domain: 'mydomain.net'

.. code-block:: yaml
  :caption: ansible/inventory/host_vars/skynet.mydomain.net/slapd.yml

  ---

  ## Network access to OpenLDAP server
  # Firewall Settings
  #   Block connections to the OpenLDAP via system firewall and TCP Wrappers from any host (aka Internet);
  #   Hosts that can connect must be specified via the slapd__*_allow variables.
  slapd__accept_any: false

  slapd__group_allow:
    # Hetzner internal network
    - '10.10.10.0/28'

.. code-block:: yaml
  :caption: ansible/inventory/host_vars/mail-server.mydomain.net/pki.yml

  ---

  ### Create TLS Certs for the mail server
  #
  # In order to sign the cert by Let's Encrypt CA install nginx in the 'mail-server',
  # so that the acme script can work.
  pki_host_realms:
    - name: 'mail.mydomain.net'
      acme: false
      domains:
        - 'mail.mydomain.net'
        - 'smtp.mydomain.net'
        - 'imap.mydomain.net'
        - 'mail-server.mydomain.net'

.. code-block:: yaml
  :caption: ansible/inventory/host_vars/mail-server.mydomain.net/postfix.yml

  ---

  # basic Postfix SMTP server with configuration similar to the "Internet Site"
  # MTP service listens for connections on port 25 from all hosts.
  # Mail relay is authorized from localhost, other hosts are deferred.

  postfix__domain: 'mydomain.net'

  postfix__pki_realm: 'mail.mydomain.net'
