.. Copyright (C) 2021-2021 Julien Lecomte <julien@lecomte.at>
.. Copyright (C) 2021-2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _pki__ref_acme_certbot_integration:

.. include:: ../../../includes/global.rst

ACME Certbot Integration
========================

The `Certbot`__ application, developed by `Electronic Frontier Foundation`__ is
an ACME client that gives users the ability to request and renew X.509
certificates from `Let's Encrypt`__ or another provider that supports the ACME
protocol. The :ref:`debops.pki` role includes support for :command:`certbot` to
allow the X.509 certificates obtained via the service to be used by Ansible
roles and other applications integrated with DebOps PKI infrastructure.

The :command:`certbot` integration with the role is focused specifically on
supporting the `DNS-01`__ ACME challenge, which allows users to request
wildcard X.509 certificates and doesn't require a standalone webserver to
operate. If you plan to use the HTTP-01 challenge instead, you should refer to
the :ref:`pki__ref_acme_tiny_integration` documentation.

.. __: https://certbot.eff.org/about/
.. __: https://www.eff.org/
.. __: https://letsencrypt.org/
.. __: https://letsencrypt.org/docs/challenge-types/#dns-01-challenge


Prerequisites
-------------

To request and renew ACME certificates with :command:`certbot`, certain
requirements must be met. You need to have a registered DNS domain which is
served by one of supported `DNS providers`__. Each DNS plugin requires a set of
API credentials, either a token or an user/password combination - refer to the
specific plugin documentation for details about obtaining them.

Due to the requirements above, the default ``domain`` PKI realm does not
include support for ACME certificates. You will have create a separate
:ref:`PKI realm <pki_realms_structure>` with name based either on the domain
you plan to use or the host's FQDN, which will then hold the private key and
X.509 certificate. Other DebOps roles can then use such PKI realm, either
automatically or when configured.

.. __: https://certbot.eff.org/docs/using.html#dns-plugins


Example ACME certificates with CloudFlare
-----------------------------------------

This is an example :ref:`debops.pki` configuration which enables the
:command:`certbot` integration and uses `CloudFlare`__ to manage the DNS
domain. We will be using the `CloudFlare DNS plugin`__ to manage the DNS
entries.

.. __: https://www.cloudflare.com/
.. __: https://certbot-dns-cloudflare.readthedocs.io/en/stable/

The role will request a X.509 certificate for the ``example.org`` DNS domain as
well as the ``*.example.org`` wildcard to cover any potential subdomains. The
configuration will be applied only on specific hosts in the cluster, included
in the ``[pki_acme_cloudflare]`` Ansible inventory group, that way DebOps can
configure multiple hosts with the X.509 certificates later on. There's no need
to get ACME certificates on backend hosts, the cluster can use the DebOps
Internal CA for encrypted communication between nodes. The PKI realm will be
named ``example.org``, based on the DNS domain.

The example Ansible inventory looks like this:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [pki_acme_cloudflare]
   hostname

You will need to obtain the API access token from CloudFlare web interface. The
role expects the credentials in specific files, named after the
:command:`certbot` DNS plugins. On the remote hosts the files should be located
in the :file:`/etc/pki/realms/<realm>/private/dns-*-credentials.key` file. To
ensure that the credentials file will be put there by the role, you should
place it on the Ansible Controller host in the path (relative to the project
directory):

.. code-block:: none

   ansible/secret/pki/realms/by-group/<inventory_group>/<realm_name>/private/dns-<dns_plugin>-credentials.key

So, in our case, that would be:

.. code-block:: none

   ansible/secret/pki/realms/by-group/pki_acme_cloudflare/example.org/private/dns-cloudflare-credentials.key

In the CloudFlare's case, the actual credentials file will look like:

.. code-block:: ini

   dns_cloudflare_api_token = <token>

On older OS releases where the :command:`certbot` version is not recent enough,
you might need to use the CloudFlare global API key instead. In such case, the
credentials file will look like:

.. code-block:: ini

   dns_cloudflare_email = <cloudflare account email>
   dns_cloudflare_api_key = <secret key>

The last bit is the inventory configuration. The variables will be set on the
group level, in the
:file:`ansible/inventory/group_vars/pki_acme_cloudflare/pki.yml` file:

.. code-block:: yaml

   ---
   # ansible/inventory/group_vars/pki_acme_cloudflare/pki.yml

   # Use CloudFlare as the DNS provider for ACME. Changing this variable
   # implicitly enables 'certbot' support.
   pki_acme_type: 'dns-cloudflare'

   # Certbot requires a working e-mail account (it will be validated), you
   # might need to specify it if the role uses a non-existent e-mail address.
   pki_acme_contacts: [ 'admin@example.org' ]

   # If you want to try the staging Let's Encrypt CA to test if the
   # certificates are obtained correctly, uncomment this variable.
   #pki_acme_ca: 'le-staging-v2'

   # Tell the 'pki' role to manage X.509 certificates for these Ansible
   # inventory groups.
   pki_inventory_groups: [ 'debops_service_pki', 'pki_acme_cloudflare' ]

   # Here we define the actual PKI realm, which will be created on each host in
   # this inventory group.
   pki_group_realms:

     - name: 'example.org'
       acme: True

       # You can define your preferred certificate subject here, the 'CN='
       # attribute is ignored in certificate verification, only SANs are
       # important.
       subject: [ 'CN=example.org' ]

       # This is a list of domains which should be signed by Let's Encrypt CA.
       # Here we get the base domain as well as the wildcard for subdomains.
       domains: [ 'example.org', '*.example.org' ]

       # These parameters are required right now to override the defaults used
       # by the 'pki' role, otherwise you might get a wrong set of domains in the
       # certificate request.
       subdomains: [ '' ]
       default_subdomains: [ '' ]

After the inventory is set up, you can apply the configuration on the host
using the :ref:`debops.pki` role, by executing the command:

.. code-block:: console

   debops service/pki -l hostname --diff

After it finishes, the :command:`certbot` aplication should be installed, and symlinks to the :file:`/etc/letsencrypt/` directory should be present in the configured PKI realm. You can see an example realm directory structure below:

.. code-block:: none

   /etc/pki/realms/
   └── example.org
       ├── acme
       │   ├── account_key.pem
       │   ├── cert.pem -> /etc/letsencrypt/live/example.org/cert.pem
       │   ├── intermediate.pem -> /etc/letsencrypt/live/example.org/chain.pem
       │   ├── openssl.conf
       │   └── request.pem
       ├── CA.crt -> /etc/ssl/certs/ca-certificates.crt
       ├── config
       │   └── realm.conf
       ├── default.crt -> public/chain.pem
       ├── default.key -> private/key.pem
       ├── default.pem -> private/key_chain_dhparam.pem
       ├── external
       ├── internal
       │   ├── cert.pem
       │   ├── gnutls.conf
       │   ├── intermediate.pem
       │   ├── request.pem
       │   └── root.pem
       ├── private
       │   ├── dns-cloudflare-credentials.key
       │   ├── key_chain_dhparam.pem
       │   ├── key_chain.pem
       │   ├── key.pem -> /etc/letsencrypt/live/example.org/privkey.pem
       │   └── realm_key.pem
       └── public
           ├── cert_intermediate_dhparam.pem
           ├── cert_intermediate.pem
           ├── cert.pem -> ../acme/cert.pem
           ├── cert.pem.sig
           ├── chain.pem -> cert_intermediate_dhparam.pem
           └── intermediate.pem -> ../acme/intermediate.pem

If there are any issues, :command:`certbot` command will log everything in the
:file:`/var/log/letsencrypt/letsencrypt.log` log file. you should review it to
find what caused the problem and fix it. After that you need to re-initialize
the PKI realm by removing its directory (:file:`/etc/pki/realms/example.org/`)
from the remote host and re-running the :ref:`debops.pki` role again. The
certificates will be safely stored in the :file:`/etc/letsencrypt/` directory
so this shouldn't case issues with `Let's Encrypt rate limits`__ if the
certificates themselves were registered successfully, but take care otherwise.
To avoid rate limiting, you might want to consider enabling the staging CA for
testing purposes.

.. __: https://letsencrypt.org/docs/rate-limits/
