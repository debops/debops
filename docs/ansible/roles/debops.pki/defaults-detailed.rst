Default variable details
========================

Some of ``debops.pki`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1

.. _pki__ref_private_groups_present:

pki_private_groups_present
--------------------------

This list can be used to create system groups that otherwise could be not
present when the PKI realm is managed. For example another role creates custom
user/group that maintains its own service certificates, but in order to do
that, ``debops.pki`` is used to manage the PKI realm but at the moment that
the ``debops.pki`` role is run by Ansible, custom group does not exist, so the
Ansible run stops. Therefore, you can create system groups beforehand using
this list.

You can define the system groups as simple items, or dictionary values with
parameters:

``name``
  The name of the group to create.

``system``
  Boolean, by default ``True``. Specify if a given group is a system group.

``when``
  The value of this variable is checked as a boolean (``True``/``False``) to
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

.. _pki__ref_realms:

pki_realms
----------

The set of :envvar:`pki_realms` lists can be used to define the configuration of PKI
realms located on remote hosts. Each realm keeps a set of private keys and
certificates which are signed by the various Certificate Authorities.

Each entry is a dictionary variable with specific parameters. Most of the
parameters are optional, and if they are not specified, the :program:`pki-realm`
script that manages the PKI realms should pick the correct options by itself.

List of parameters related to the entire PKI realm:

``name``
  Required. This is the name of the PKI realm, used as the name of the
  directory which contains the realm subdirectories, by default stored in
  the :file:`/etc/pki/realms/` directory.

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

``authority``
  Specify name of the internal Certificate Authority to send the internal
  certificate requests to instead of the default one configured in
  :envvar:`pki_default_authority` variable. This should be the "normal" name of the
  authority, not its subdomain name.

``acme``
  Optional, boolean. Enable or disable support for ACME Certificate Authority.
  Can be used to invert the global :envvar:`pki_acme` setting per PKI realm if
  needed, but support for ACME needs to be present on the remote host for it to
  work (see :envvar:`pki_acme_install` variable).

``internal``
  Optional, boolean. Enable or disable support for internal CA certificates in
  a given realm. If you disable internal CA support, an alternative,
  self-signed certificate will be created and enabled automatically.

``authority_preference``
  Optional. List of directory names (``external``, ``acme``, ``internal``,
  ``selfsigned``) which determines the order in which the PKI realm looks for
  valid certificates. The first found valid certificate is enabled. If not
  specified, the order configured in :envvar:`pki_authority_preference` will be used.

``library``
  Optional. Specify name of the crypto library used to generate private key and
  internal certificate requests in a given PKI realm. Either :command:`gnutls`
  (default) or :command:`openssl`.

``acme_library``
  Optional. Specify name of the crypto library used to generate ACME
  certificate requests in a given PKI realm. Either :command:`openssl` (default) or
  :command:`gnutls`.

``private_dir_group``
  Optional. System group which will be set as the group of the :file:`private/`
  directory of a given PKI realm. By default, ``ssl-cert``. It needs to exist,
  and can be created using :envvar:`pki_private_groups_present` list.

``private_file_group``
  Optional. System group which will be set as the group of the private keys
  inside of the :file:`private/` directory. It needs to exist, and can be created
  using :envvar:`pki_private_groups_present` list.

``private_dir_acl_groups``
  Optional. List of groups which should be allowed execute (``X``) permission to
  the :file:`private/` realm directory. The access will be granted using filesystem
  ACL table. If not specified, the list defined in
  :envvar:`pki_private_dir_acl_groups` will be applied.

``private_file_acl_groups``
  Optional. List of groups which should be allowed read (``r``) permission to
  the files in the :file:`private/` realm directory. The access will be granted
  using filesystem ACL table. If not specified, the list defined in
  :envvar:`pki_private_file_acl_groups` will be applied.

``dhparam``
  Optional, boolean. Enable or disable support for adding the Diffie-Hellman
  parameters at the end of the certificate chain.

``dhparam_file``
  Optional. Path to the Diffie-Hellman parameters to include in the certificate
  chain. If not specified, DHE parameters managed by the :ref:`debops.dhparam`
  role will be used automatically, if they're available.

``selfsigned_sign_days``
  Optional. Number of days a selfsigned certificate will be valid for.
  The default is ``365`` days.

``enabled``, ``when``
  Optional, boolean. Enable or disable management of a given realm. If
  disabled, Ansible will not execute commands related to that realm. The
  ``when`` parameter is meant for automated processing, and ``enabled`` should
  be used as an user option, exposed through the inventory.

These parameters are related to internal certificates and ACME certificates,
respectively:

``default_domain``
  Optional. Change the default domain used by a given PKI realm. If not
  specified, the default domain is based on the ``name`` parameter if it has at
  least 1 dot, or it will be taken from :envvar:`pki_default_domain` variable
  which is populated by the ``ansible_domain`` variable.

``default_subdomains``, ``acme_default_subdomains``
  Optional. List of subdomains added to each domain configured in a given PKI
  realm. A special value ``_wildcard_`` can be used to indicate that a wildcard
  domain should be present in the certificate.

  If not specified, :envvar:`pki_default_subdomains` (for internal CA) and
  :envvar:`pki_acme_default_subdomains` (for ACME CA) will be used. The PKI
  parameters can be set to empty to override the default variables.

``subject``, ``acme_subject``
  Optional. The Distinguished Name of the certificate, specified as a list of
  DN elements. If not specified, a CommonName based on the default domain of
  the given PKI realm will be used.
  Empty string elements of the list will be ignored.

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

.. _pki__ref_authorities:

pki_authorities
---------------

The set of :envvar:`pki_authorities` lists can be used to define internal
Certificate Authorities managed on an Ansible Controller.

List of supported parameters (incomplete):

``crl``
  The CRL URL to include in certificates which can be used for certificate
  status checking. The default is ``True`` which will result in ``http://\$name.\$domain_suffix/crl/``.
  It can be set to ``False`` to not include a CRL URL in certificates.
  Any other value (not matching :regexp:`^(?:[Tt]rue|[Ff]alse)$`) will be included as is as CRL URL.

``ocsp``
  The OCSP URL to include in certificates which can be used for certificate
  status checking. The default is ``True`` which will result in ``http://\$name.\$domain_suffix/ocsp/``.
  It can be set to ``False`` to not include a OCSP URL in certificates.
  Any other value (not matching :regexp:`^(?:[Tt]rue|[Ff]alse)$`) will be included as is as OCSP URL.

``name_constraints``
  The X.509 Name Constraints certificate extension to include in certificates
  which will be used during certificate verification to ensure that the CA is
  authorized to issue a certificate for the name in question.
  The extension is set to critical which REQUIRES X.509 libraries to support it or to return an error.
  This is done following common recommendations
  (ref: `Which properties of a X.509 certificate should be critical and which not? <https://security.stackexchange.com/questions/30974/which-properties-of-a-x-509-certificate-should-be-critical-and-which-not>`_).
  The default is ``True`` which will result in ``critical, permitted;DNS:${config_domain}``.
  It can be set to ``False`` to not include X.509 Name Constraints in certificates.
  Any other value (not matching :regexp:`^(?:[Tt]rue|[Ff]alse)$`) will be included as is as X.509 Name Constraint.
