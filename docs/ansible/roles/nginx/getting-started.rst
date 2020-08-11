.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@drybjed.net>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Security defaults
-----------------

Following `Mozilla intermediate level recommendations`_, this role
configures nginx with only TLSv1.2 and TLSv1.3 enabled. All modern
browsers are supported with the default cipher suite. If you need
support for older clients, see ``nginx_default_ssl_ciphers`` and
``nginx_default_tls_protocols``. To follow modern level
recommendation, enable only TLSv1.3 in
``nginx_default_tls_protocols``. Note that there is still limited
client support for TLSv1.3.

Only one curve (ECC) is enabled by default: ``secp256r1``. While
`NCSC-NL`_ recommends three other curves, these are not supported by
openssl (in Debian Buster, as checked on 2020-08-06).

If TLSv1.3 is the only protocol in use, clients are allowed to choose
ciphers, because they know best if they have support for
hardware-accelerated AES. If TLSv1.2 or lower is used, server ciphers
are preferred, because those protocols allow downgrade attacks.

No dhparam is set if the only protocol is TLSv1.3, because that
protocol uses `Ephemeral Diffie-Hellman key exchange`_, which employs
one-time keys for the current network session. Omitting the option is
purely cosmetic, resulting in a cleaner configuration file.

If `HTTP Strict Transport Security`_ is enabled, the default age is 2
years.

.. _Mozilla intermediate level recommendations: https://ssl-config.mozilla.org/#server=nginx&version=1.17.7&config=intermediate&openssl=1.1.1d&guideline=5.6
.. _NCSC-NL: https://english.ncsc.nl/publications/publications/2019/juni/01/it-security-guidelines-for-transport-layer-security-tls
.. _Ephemeral Diffie-Hellman key exchange: https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
.. _HTTP Strict Transport Security: https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Strict_Transport_Security_Cheat_Sheet.html

Example inventory
-----------------

To manage Nginx on a given host or set of hosts, they need to be added
to the ``[debops_service_nginx]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_nginx]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nginx`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/nginx.yml
   :language: yaml
   :lines: 1,6-

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::nginx``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``type::dependency``
  This tag specifies which tasks are defined in role dependencies. You can use
  this to omit them using ``--skip-tags`` parameter.

``depend-of::nginx``
  Execute all ``debops.nginx`` role dependencies in its context.

``depend::secret:nginx``
  Run :ref:`debops.secret` dependent role in ``debops.nginx`` context.

``depend::apt_preferences:nginx``
  Run :ref:`debops.apt_preferences` dependent role in ``debops.nginx`` context.

``depend::ferm:nginx``
  Run :ref:`debops.ferm` dependent role in ``debops.nginx`` context.

``role::nginx:servers``
  Configure nginx servers configuration as configured by the ``nginx_servers``
  variable.
