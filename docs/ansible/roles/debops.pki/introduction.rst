Introduction
============

.. include:: ../../../includes/global.rst

The ``debops.pki`` role provides a standardized management of the X.509
certificates on hosts controlled by Ansible. Other Ansible roles can utilize
the environment created by ``debops.pki`` to automatically enable TLS/SSL
encrypted connections.

Using this role, you can bootstrap a Public Key Infrastructure in your
environment using an internal Certificate Authority, easily switch the active
set of certificates between internal and external Certificate Authorities, or
use the ACME protocol to automatically obtain certificates from CA that
support it (for example `Let's Encrypt`_).

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.pki

Ansible Controller requirements
-------------------------------

Some operations performed by the ``debops.pki`` role are done on the Ansible
Controller. However, DebOps roles are not designed to manage the Ansible Controller
host directly, so they cannot automatically install the required software.

Software packages required by the role on the Ansible Controller::

    bash >= 4.3.0
    openssl >= 1.0.1

.. Note that the role asserts that required dependencies are met. In case you
   change the required versions here, remember to update them in
   `../tasks/main.yml` as well.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
