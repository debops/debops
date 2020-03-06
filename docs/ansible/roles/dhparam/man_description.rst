.. Copyright (C) 2015-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Diffie-Hellman Key Exchange`_ is a way to securely share encryption keys
publicly between two parties. It's used in TLS and SSL connections to provide
`Perfect Forward Secrecy`_. Unfortunately, the default DH parameters distributed
with applications are susceptible to a `downgrade attack`_.

The ``debops.dhparam`` Ansible role will generate a set of strong
Diffie-Hellman parameters on the Ansible Controller, which will be preseeded on
remote hosts, and will be ready to use by other applications. A separate script
can then be used on remote hosts in the background to generate new random DH
parameters, either once or in regular intervals.

.. _Diffie-Hellman Key Exchange: https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
.. _Perfect Forward Secrecy: https://en.wikipedia.org/wiki/Forward_secrecy
.. _downgrade attack: https://weakdh.org/
