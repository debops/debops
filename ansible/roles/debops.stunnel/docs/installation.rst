Installation
============

This role requires at least Ansible ``v1.8.0``. To install it, run::

    ansible-galaxy install debops.stunnel

``debops.stunnel`` role does not manage the required certificates by itself. To
help with that, you can use a separate role, `debops.pki`_. Or, you can provide
your own certificates in a well-known location.

.. _debops.pki: https://github.com/debops/ansible-pki/

