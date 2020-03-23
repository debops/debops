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
  the :file:`/etc/pki/realms/` directory. The ``name`` parameter is interpreted
  by the role in various ways:

    - the single string name, like "domain", "xxxxaaaayyyy" or similar strings.
      These PKI realm names can be thought of as "handles" and they don't have any
      impact on the domains stored in the X.509 certificates. The role will
      by default use the host's FQDN and DNS domain name to generate such realms,
      but it can be overridden. Users can create multiple such PKI realms for
      various purposes.

    - the DNS-based name, which contains dots, like "example.com",
      "host.example.com" and the like. These PKI realms base their X.509 certificates
      after the realm name by default. This is also the reason the default PKI realm
      is named "domain" and not "{{ ansible_domain }}" - users can create a new PKI
      realm for their default DNS domain on hosts that are reachable publicly and
      they will automatically get the Let's Encrypt certificates when possible, or
      can easily use external certificates grabbed from some other CA.

      Some DebOps roles like :ref:`debops.nginx` can check the list of available
      PKI realms via the local facts and use some other PKI realm rather than the
      default one automatically. For example, if an user creates an "example.com" PKI
      realm and then uses the "example.com" DNS domain, standalone or with a
      subdomain like "sub.example.com", the :ref:`debops.nginx` role will check if a
      PKI realm named after a given FQDN or DNS domain exists and will use it instead
      of the "domain" PKI realm used by default. It can be thought of as a shortcut
      to easily manage X.509 certificates for multiple websites, each one with its
      own FQDN domain name.

    - the mail-based name, like "user@example.org" - any PKI realm name which
      contains the '@' character qualifies as one. These PKI realms were meant to
      keep the client certificates used to authenticate to services, but this idea
      was not developed further, so far.

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

``acme_contacts``
  Optional, list of (mailto:) URLs that the ACME server can use to contact you
  for issues related to your account. For example, the server may wish to
  notify you about server-initiated revocation or certificate expiration. If
  not specified, the list defined in :envvar:`pki_acme_contacts` will be used.

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
  The default is ``True`` which will result in ``critical, permitted;DNS:${config_domain}``
  (the 'critical, ' part is omitted when ``item.name_constraints_critical`` is
  set to ``False``). It can be set to ``False`` to not include X.509 Name
  Constraints in certificates. Any other value (not matching :regexp:`^(?:[Tt]rue|[Ff]alse)$`)
  will be included as is as X.509 Name Constraint.

``name_constraints_critical``
  Boolean, for specifying whether to mark the default Name Constraints
  extension as critical or not. The default is ``True``. The CA/Browser forum
  recommends this to be enabled (REQUIRING X.509 libraries to support it or to
  return an error), but mentions that the extension may be disabled for
  compatibility reasons
  (ref: `Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates (v1.6.4) <https://cabforum.org/wp-content/uploads/CA-Browser-Forum-BR-1.6.4.pdf>`_).
