Default variables: configuration
================================

Some of ``debops.pki`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1

.. _pki_private_groups_present:

pki_private_groups_present
--------------------------

This list can be used to create system groups that otherwise could be not
present when the PKI realm is managed. For example another role creates custom
user/group that maintains its own service certificates, but in order to do
that, ``debops.pki`` is used to manage the PKI realm. but at the moment that
the ``debops.pki`` role is run by Ansible, custom group does not exist, so the
Ansible run stops. Therefore, you can create system groups beforehand using
this list.

You can define the system groups as simple items, or dictionary values with
parameters:

``name``
  The name of the group to create.

``system``
  Bool, by default ``True``. Specify if a given group is a system group.

``when``
  The value of this variable is checked as a bool (``True``/``False``) to
  determine if a given system group should be created or not. You can use this
  as a condition to, for example, create groups only on specific hosts.

Examples
~~~~~~~~

Ensure two system groups exist, one with a condition:

.. code-block:: yaml

   pki_private_groups_present:

     - 'group1'

     - name: 'group2'
       when: '{{ inventory_hostname in specific_inventory_group }}'

.. _pki_realms:

pki_realms
----------

The set of ``pki_realms`` lists can be used to define the configuration of PKI
realms located on remote hosts. Each realm keeps a set of private keys and
certificates which are signed by the various Certificate Authorities.

Each entry is a dictionary variable with specific parameters. Most of the
parameters are optional, and if they are not specified, the ``pki-realm``
script that manages the PKI realms should pick the correct options by itself.

List of parameters related to the entire PKI realm:

``name``
  Required. This is the name of the PKI realm, used as the name of the
  directory which contains the realm subdirectories, by default stored in
  ``/etc/pki/realms/`` directory.

  If the ``subject`` parameter is not specified, ``name`` parameter is checked
  to see if it might be a DNS domain (at least 1 dot present in the value). If
  yes, it will be used as a default domain for a given PKI realm.

  Example:

  .. code-block:: yaml

     pki_realms:

       # Default PKI realm
       - name: 'domain'

       # Custom PKI realm
       - name: 'example.org'

``acme``
  Optional, boolean. Enable or disable support for ACME Certificate Authority.
  Can be used to invert the global ``pki_acme`` setting per PKI realm if
  needed, but support for ACME needs to be present on the remote host for it to
  work (see ``pki_acme_install`` variable).

``internal``
  Optional, boolean. Enable or disable support for internal CA certificates in
  a given realm.

``library``
  Optional. Specify name of the crypto library used to generate private key and
  internal certificate requests in a given PKI realm. Either ``gnutls``
  (default) or ``openssl``.

``acme_library``
  Optional. Specify name of the crypto library used to generate ACME
  certificate requests in a given PKI realm. Either ``openssl`` (default) or
  ``gnutls``.

``private_dir_group``
  Optional. System group which will be set as the group of the ``private/``
  directory of a given PKI realm. By default, ``ssl-cert``. It needs to exist,
  and can be created using ``pki_private_groups_resent`` list.

``private_file_group``
  Optional. System group which will be set as the group of the private keys
  inside of the ``private/`` directory. It needs to exist, and can be created
  using ``pki_private_groups_present`` list.

``dhparam``
  Optional, boolean. Enable or disable support for adding the Diffie-Hellman
  parameters at the end of the certificate chain.

``dhparam_file``
  Optional. Path to the Diffie-Hellman parameters to include in the certificate
  chain. If not specified, DHE parameters managed by the ``debops.dhparam``
  role will be used automatically, if they're available.

``enabled``, ``when``
  Optional, boolean. Enable or disable management of a given realm. If
  disabled, Ansible will not execute commands related to that realm. The
  ``when`` parameter is meant for automated processing, and ``enabled`` should
  be used as an user option, exposed through the inventory.

These parameters are related to internal certificates and ACME certificates,
respectively:

``default_domain``
  Optional. Change the default domain used by a given PKI realm. If not
  specified, default domain is based on the ``name`` parameter if it has at
  least 1 dot, or it will be taken from ``pki_default_domain`` variable which
  is populated by ``ansible_domain`` variable.

``default_subdomains``, ``acme_default_subdomains``
  Optional. List of subdomains added to each domain configured in a given PKI
  realm. A special value ``_wildcard_`` can be used to indicate that a wildcard
  domain should be present in the certificate.

  If not specified, ``pki_default_subdomains`` (for internal CA) and
  ``pki_acme_default_subdomains`` (for ACME CA) will be used. The PKI
  parameters can be set to empty to override the default variables.

``subject``, ``acme_subject``
  Optional. The Distinguished Name of the certificate, specified as a list of
  DN elements. If not specified, a CommonName based on the default domain of
  the given PKI realm.

  Example:

  .. code-block:: yaml

     pki_realms:

       - name: 'domain'
         subject: [ 'o=Organization Name', 'ou=IT', 'cn=example.org' ]

``domains``, ``acme_domains``
  Optional. List of domains which should be included in a given certificate.
  Each domain will include a set of subdomains specified by the other
  parameters. This can be used to easily create certificates that use multiple
  domains with similar set of subdomains.

``subdomains``, ``acme_subdomains``
  Optional. List of subdomains which will be added to each domain specified by
  the above parameters. The special value ``_wildcard_`` indicates that
  a wildcard domain should be included in the certificate.

``subject_alt_names``, ``acme_alt_names``
  Optional. Specify a custom set of SubjectAltNames included in a certificate,
  as a list. Each element of a list needs to indicate its type in a special
  format. Currently supported types:

  - a DNS record: ``[ 'dns:example.org', 'DNS:example.com' ]``

  - an IP address: ``[ 'ip:192.0.2.1', 'IP:2001:db8::dead:beef' ]``

  - an URI path: ``[ 'uri:http://example.org/', 'URI:https://example.com/' ]``

  - an email address: ``[ 'email:root@example.org', 'EMAIL:staff@example.com' ]``

  If an element of the list does not specify its type, it will not be included
  in the certificate request. Different element types can be used in the same
  list.

  Example:

  .. code-block:: yaml

     pki_realms:

       - name: 'domain'
         subject_alt_names:
           - 'ip:{{ ansible_default_ipv4.address }}'
           - 'uri:https://{{ ansible_domain }}/'
           - 'dns:*.{{ ansible_domain }}'
           - 'dns:{{ ansible_domain }}'

