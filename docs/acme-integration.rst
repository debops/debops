.. _acme_integration:

ACME Integration
================

The `Automated Certificate Management Environment <https://en.wikipedia.org/wiki/Automated_Certificate_Management_Environment>`_
is a protocol that allows automated certificate requests, retrieval of signed
certificates and certificate renewal. It was designed to enable easy deployment
of TLS/SSL certificates by the `Let's Encrypt <https://letsencrypt.org/>`_
project.

The ``debops.pki`` Ansible role provides integrated support of the ACME
protocol, used by default with Let's Encrypt service (there is a possibility to
integrate other similar services in the future). Interaction with the ACME
Certificate Authority is performed using the `acme-tiny <https://github.com/diafygi/acme-tiny>`_
alternative client written in Python.

Prerequisites
-------------

To request and renew ACME certificates, a host needs to meet several
requirements enforced by the Ansible role:

- A webserver configured to handle ACME challenges needs to be installed on the
  host (currently role supports only "webroot" challenges). The
  ``debops.nginx`` role configures ACME support for all servers by default when
  other conditions are met.

- A publicly routable IPv4 or IPv6 address is required, so that the Certificate
  Authority can contact the webserver and check the challenge responses. The
  ``debops.pki`` role detects if a suitable IP address is present, and disables
  the ACME support otherwise. This can be overriden if necessary to for example
  allow ACME on an internal server which can handle challenges forwarded
  through the gateway.

- Each domain or subdomain requested in a particular certificate needs to be
  correctly configured in the DNS to point to the host that requests the
  certificate. This is currently not done automatically and requires
  intervention by the administrator. If any domain specified in the request is
  not authorized by the correct ACME challenge, certificate request won't be
  completed.

Due to above requirements, the default ``domain`` PKI realm configured by the
role does not request ACME certificates automatically. Other realms created by
the ``debops.pki`` role might have ACME support enabled, depending on presence
of a public IP address and configured ``nginx`` server.

Let's Encrypt rate limits
-------------------------

The Let's Encrypt ACME Certificate Authority has `different rate limits <https://community.letsencrypt.org/t/rate-limits-for-lets-encrypt/6769>`_
related to number of certificate requests and number of domains permitted per
certificate.

To avoid triggering the limits too quickly due to a mistake, ``debops.pki``
disables the requests when the ``acme/error.log`` file is present in the PKI
realm directory. You can check contents of this file to find out what might be
the issue, and after fixing it you need to remove the file to let the
``pki-realm`` script run the request again.

How ACME certificates are managed
---------------------------------

When a new PKI realm is created and support for ACME Certificate Authority is
enabled, a separate configuration for a Certificate Request will be created in
the ``acme/`` directory. This request does not use a wildcard certificate;
instead the default domain and a set of subdomains will be requested (see below
for configuration variables). The directory structure at this time looks like
this::

    /etc/pki/realms/
    └── example.com/
        ├── acme/
        │   ├── account_key.pem
        │   ├── openssl.conf
        │   └── request.pem
        ├── config/
        │   └── realm.conf
        ├── external/
        ├── internal/
        │   ├── gnutls.conf
        │   └── request.pem
        ├── private/
        │   ├── key.pem
        │   └── realm_key.pem
        ├── public/
        ├── CA.crt -> /etc/ssl/certs/ca-certificates.crt
        └── default.key -> private/key.pem

When the ``pki-realm`` detects the ``acme/request.pem`` file, it automatically
calls ``acme-tiny`` script using ``pki-acme`` unprivileged account to request
the certificate. When the request is completed successfully and an
``external/cert.pem`` certificate is not found, ACME certificate will be
activated in the ``public/`` directory. Script automatically downloads Let's
Encrypt intermediate certificate as well as links the Root CA certificate from
the system certificate store provided by ``ca-certificates`` package.

The realm directory after the process is complete::

    /etc/pki/realms/
    └── example.com/
        ├── acme/
        │   ├── account_key.pem
        │   ├── cert.pem
        │   ├── openssl.conf
        │   ├── intermediate.pem
        │   ├── request.pem
        │   └── root.pem -> /usr/share/ca-certificates/mozilla/DST_Root_CA_X3.crt
        ├── config/
        │   └── realm.conf
        ├── external/
        ├── internal/
        │   ├── cert.pem
        │   ├── gnutls.conf
        │   ├── intermediate.pem
        │   ├── request.pem
        │   └── root.pem
        ├── private/
        │   ├── key_chain.pem
        │   ├── key.pem
        │   └── realm_key.pem
        ├── public/
        │   ├── cert_intermediate.pem
        │   ├── cert.pem -> ../acme/cert.pem
        │   ├── cert.pem.sig
        │   ├── chain.pem -> cert_intermediate.pem
        │   ├── intermediate_root.pem
        │   ├── root.pem -> ../acme/root.pem
        │   └── trusted.pem -> intermediate_root.pem
        ├── CA.crt -> public/trusted.pem
        ├── default.crt -> public/chain.pem
        ├── default.key -> private/key.pem
        ├── default.pem -> private/key_chain.pem
        └── trusted.crt -> public/trusted.pem

If the request is not successful, you will find a ``acme/error.log`` file with
log of the ``acme-tiny`` session. Check and fix the issue, and remove the log
file to re-enable the process again. Otherwise, ``pki-realm`` will not request
the certificates to avoid rate limit issues explained above.

Certificate renewal
-------------------

The ``debops.pki`` role creates a ``cron`` entry for ``pki-realm`` script to be
executed periodically for all realms. When a realm has the ACME configuration
active, it will check validity of the signed certificate, and about a month
before the expiration date it will try to renew the certificate automatically.

ACME configuration variables
----------------------------

The ``debops.pki`` role has several default variables which can be used to
control ACME support. The most important are:

``pki_acme``
  Bool. When ``True``, support for ACME Certificate Authority will be
  configured for all PKI realms unless disabled on the realm level. By default
  role checks if a public IP address is available and a default domain is
  configured, otherwise the support is disabled automatically.

``pki_acme_install``
  Bool. Enable or disable installation of ``acme-tiny`` and configuration of
  ACME support without enabling it for all realms. When this variable is set to
  ``True`` and ``pki_acme`` is set to ``False``, ACME support can be enabled
  independently in each PKI realm. By default has the same value as
  ``pki_acme``.

``pki_acme_ca``
  Name of the ACME Certificate Authority API endpoint to use. Dictionary with
  endpoints is defined in the ``pki_acme_ca_api_map`` variable. By default,
  ``le-live`` is used which points to the Let's Encrypt Live CA. For testing
  you can switch the default CA to ``le-staging`` which points to Let's Encrypt
  Staging CA.

``pki_acme_default_subdomains``
  List of subdomains which will be added to the default ACME domain and all
  other domains configured for ACME certificate by default, can be overriden by
  ``item.acme_subdomains`` parameter. By default, ``www.`` subdomain will be
  added to each domain configured in the realm. Remember that all subdomains
  need to be correctly configured in the DNS for the Certificate Authority to
  sign the request.

Each PKI realm configured in the ``pki_realms`` or ``pki_*_realms`` variables
can have several parameters related to the ACME certificates:

``item.name``
  Name of the PKI realm. If it has at least one dot, the realm name will be
  treated as the apex (root) domain to configure for this realm.

``item.acme``
  Bool. Enable or disable ACME support per realm.

``item.acme_domains``
  List of additional apex (root) domains to add in ACME Certificate Signing
  Request. Each domain will have the default or custom subdomains added to it.

``item.acme_default_subdomains``
  List of subdomains that should be added to all of the ACME apex/root domains.
  If you want to create an ACME certificate only with the apex domain, you need
  to use this parameter with ``[]`` value to override
  ``pki_acme_default_subdomains``.

``item.acme_subdomains``
  List of subdomains added to each apex (root) domain configured in the ACME
  certificate. Overrides list of default ACME subdomains.

``item.acme_subject``
  List of Distinguished Name entries which define the ACME certificate Subject.

