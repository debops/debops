Description
===========

The ``debops.pki`` role provides a standardized management of the X.509
certificates on hosts controlled by Ansible. Other Ansible roles can utilize
the environment created by ``debops.pki`` to automatically enable TLS/SSL
encrypted connections.

Using this role, you can bootstrap a Public Key Infrastructure in your
environment using an internal Certificate Authority, easily switch the active
set of certificates between internal and external Certificate Authorities, or
use the ACME protocol to automatically obtain certificates from CA that
support it (for example `Let's Encrypt`__).

.. __: https://en.wikipedia.org/wiki/Let's_Encrypt
