.. Copyright (C) 2013-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _pki__ref_acme_integration:

.. include:: ../../../includes/global.rst

ACME Integration
================

`Automated Certificate Management Environment` (ACME_) is a protocol that
allows automated certificate requests, retrieval of certificates and
certificate renewal. It was designed to enable easy deployment of X.509
certificates from `Let's Encrypt`_.

The ``debops.pki`` Ansible role provides support for the ACMEv2 protocol which
is used by default with the Let's Encrypt (there is a possibility to integrate
other similar services in the future). Interaction with the ACME Certificate
Authority is performed using the acme-tiny_ alternative client written in
Python.

Let's Encrypt rate limits
-------------------------

The Let's Encrypt ACME Certificate Authority has
`different rate limits <https://letsencrypt.org/docs/rate-limits/>`_
related to the number of certificate requests and the number of domains permitted per
certificate.

Certificate renewal
-------------------

The ``debops.pki`` role creates a :program:`cron` entry for the :program:`pki-realm` script
to be executed periodically for all realms. When a realm has the ACME
configuration active, it will check for validity of the certificate, and
about a month before the expiration date it will try to renew the certificate
automatically.

Example: Certificate for apex domain and subdomains
---------------------------------------------------

The `apex domain` is the "root" level of your domain.
In this example a X.509 certificate for the apex domain ``example.com`` is
going to be issued. ``example.com`` will be listed in the certificate
``Subject`` DN.
The certificate will also be valid for the subdomains ``www.example.com``,
``blog.example.com`` and ``mail.example.com`` which are included in the
certificate as `Subject Alternative Names`_.

.. code-block:: yaml

    pki_realms:
      - name: 'example.com'
        acme: True
        acme_subdomains: [ 'www', 'blog', 'mail' ]
        # acme_ca: 'le-staging-v2'

For testing it's strongly advised to uncomment ``acme_ca`` with
``le-staging-v2`` to use the staging environment of Let's Encrypt. It does not
create a trusted certificate and allows you to avoid problems with the rate
limits in the production environment. When you are sure that everything works
correctly, comment the staging environment out again to get yourself a valid
and trusted X.509 certificate.

Example: Certificate for subdomains excluding the apex domain
-------------------------------------------------------------

In the example we create a certificate for ``logs.example.com`` (certificate
``Subject``) and for ``mon.example.com`` (certificate `Subject Alternative
Names`_), which does not include the ``example.com`` apex (root) domain.

.. code-block:: yaml

    pki_realms:
      - name: 'logs.example.com'
        acme: True
        acme_default_subdomains: []
        # Can also include different domains like 'mail.example.org'
        # in the same realm.
        acme_domains: [ 'mon.example.com' ]
        # acme_ca: 'le-staging-v2'

Again, for testing it's strongly advised to uncomment
``acme_ca: le-staging-v2``. See above for details.


ACME configuration variables
----------------------------

The ``debops.pki`` role has several default variables which can be used to
control ACME support. The most important are:

:envvar:`pki_acme`
  Boolean. When ``True``, support for ACME Certificate Authority will be
  configured for all PKI realms unless disabled on the realm level. By default
  the role checks if a public IP address is available and a default domain is
  configured, otherwise the support is disabled automatically.

:envvar:`pki_acme_install`
  Boolean. Enable or disable installation of :program:`acme-tiny` and configuration of
  ACME support without enabling it for all realms. When this variable is set to
  ``True`` and :envvar:`pki_acme` is set to ``False``, ACME support can be enabled
  independently in each PKI realm. By default, it is set to the same value as
  :envvar:`pki_acme`.

:envvar:`pki_acme_ca`
  Name of the ACME Certificate Authority API endpoint to use. Dictionary with
  endpoints is defined in the :envvar:`pki_acme_ca_api_map` variable. By
  default, ``le-live-v2`` is used which points to the Let's Encrypt Live CA.
  For testing you can switch the default CA to ``le-staging-v2`` which points
  to Let's Encrypt Staging CA.

:envvar:`pki_acme_default_subdomains`
  List of subdomains which will be added to the default ACME domain and all
  other domains configured for ACME certificate by default, can be overridden by
  ``item.acme_subdomains`` parameter. By default, the ``www.`` subdomain will be
  added to each domain configured in the realm. Remember that all subdomains
  need to be correctly configured in the DNS for the Certificate Authority to
  sign the request.

Each PKI realm configured in the :envvar:`pki_realms` or ``pki_*_realms`` variables
can have several parameters related to the ACME certificates:

``item.name``
  Name of the PKI realm. If it has at least one dot, the realm name will be
  treated as the apex (root) domain to configure for this realm.

``item.acme``
  Boolean. Enable or disable ACME support per realm.

``item.acme_domains``
  List of additional apex (root) domains to add in ACME Certificate Signing
  Request. Each domain will have the default or custom subdomains added to it.

``item.acme_default_subdomains``
  List of subdomains that should be added to all of the ACME apex (root) domains.
  If you want to create an ACME certificate only with the apex domain, you
  might need to set this parameter to an empty list using ``[]`` to override
  :envvar:`pki_acme_default_subdomains`.

``item.acme_subdomains``
  List of subdomains added to each apex (root) domain configured in the ACME
  certificate. Overrides list of default ACME subdomains.

``item.acme_subject``
  List of Distinguished Name entries which define the ACME certificate Subject.
