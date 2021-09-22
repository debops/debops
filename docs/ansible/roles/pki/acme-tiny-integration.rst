.. Copyright (C) 2013-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _pki__ref_acme_tiny_integration:

.. include:: ../../../includes/global.rst

ACME Tiny Integration
=====================

Prerequisites
-------------

To request and renew ACME certificates with acme-tiny_, a host needs to meet
several requirements enforced by this Ansible role:

- A webserver configured to handle ACME challenges needs to be installed on the
  host (currently this role supports only ``http-01`` challenges). The
  debops.nginx_ role configures ACME support for all servers by default when
  other conditions are met.

- A publicly routable IPv4 or IPv6 address is required, so that the Certificate
  Authority can contact the webserver and check the challenge responses. The
  ``debops.pki`` role detects if a suitable IP address is present, and disables
  the ACME support otherwise. This can be overridden if necessary for example to
  allow ACME on an internal server which can handle challenges forwarded
  through the gateway.

- Each domain or subdomain requested in a particular certificate needs to be
  correctly configured in the DNS to point to the host that requests the
  certificate. This is currently not done automatically and requires
  intervention by the administrator. If any domain specified in the request is
  not authorized by the correct ACME challenge, the certificate request won't be
  successful.

To request and renew ACME certificates with ``certbot`` and a DNS challenge,
a host needs to meet several requirements enforced by this Ansible role:

- A registered domain name.

- API credentials that enable the DNS challenge to succeed.

Due to above requirements, the default ``domain`` PKI realm configured by the
role does not request ACME certificates automatically. Other realms created by
the ``debops.pki`` role might have ACME support enabled, depending on presence
of a public IP address and a configured :program:`nginx` server.

Let's Encrypt rate limits
-------------------------

When a certificate request fails, useful error output will be written to
:file:`acme/error.log`. This file will also prevent the :program:`pki-realm`
script from quickly retrying the request and potentially hitting a rate limit.
If this file exists and it was modified less than two days ago, the
:program:`pki-realm` script will not perform the request. If the file is older
than two days, it will move the file out of the way and perform the request as
usual. If you want to retry the request straightaway, you can just move
:file:`acme/error.log` out of the way yourself.

How ACME certificates are managed
---------------------------------

When a new PKI realm is created and support for ACME Certificate Authority is
enabled, a separate configuration for a Certificate Request will be created in
the :file:`acme/` directory. The `acme-tiny` request does not use a wildcard
certificate, instead the default domain and a set of subdomains will be 
requested (see below for configuration variables). The directory structure at
this time looks like this:

.. code-block:: none

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

When the :program:`pki-realm` detects the :file:`acme/request.pem` file, it
automatically calls the :program:`acme-tiny` script using the ``pki-acme``
unprivileged account to request the certificate. When the request has completed
successfully and an :file:`external/cert.pem` certificate is found, the
certificate will be activated in the :file:`public/` directory. The script
automatically downloads Let's Encrypt intermediate certificate as well as links
the Root CA certificate from the system certificate store provided by the
``ca-certificates`` package.

The realm directory after the process is complete:

.. code-block:: none

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
        │   ├── key_chain_dhparam.pem
        │   ├── key_chain.pem
        │   ├── key.pem
        │   └── realm_key.pem
        ├── public/
        │   ├── cert_intermediate_dhparam.pem
        │   ├── cert_intermediate.pem
        │   ├── cert.pem -> ../acme/cert.pem
        │   ├── cert.pem.sig
        │   ├── chain.pem -> cert_intermediate_dhparam.pem
        │   ├── intermediate_root.pem
        │   ├── root.pem -> ../acme/root.pem
        │   └── trusted.pem -> intermediate_root.pem
        ├── CA.crt -> public/trusted.pem
        ├── default.crt -> public/chain.pem
        ├── default.key -> private/key.pem
        ├── default.pem -> private/key_chain_dhparam.pem
        └── trusted.crt -> public/trusted.pem

If the request is not successful, you will find a :file:`acme/error.log` file with
log of the :program:`acme-tiny` session. Check and fix the issue, and remove the log
file to re-enable the process again. Otherwise, :program:`pki-realm` will not request
the certificates to avoid rate limit issues explained above.

