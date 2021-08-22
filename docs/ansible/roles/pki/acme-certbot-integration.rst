.. Copyright (C) 2021-2021 Julien Lecomte <julien@lecomte.at>
.. Copyright (C) 2021-2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _pki__ref_acme_certbot_integration:

.. include:: ../../../includes/global.rst

ACME Certbot Integration
========================

Prerequisites
-------------

To request and renew ACME certificates with `certbot`, certain requirements
must be met:

- A registered domain name such as `example.com`.

- API credentials to programmatically edit the DNS records of that domain.

Due to above requirements, the default ``domain`` PKI realm configured by the
role does not request ACME certificates automatically.

