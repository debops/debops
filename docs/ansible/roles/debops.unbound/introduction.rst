Introduction
============

`Unbound <https://unbound.net/>`_ is a local DNS resolver. It supports
`DNSSEC <https://en.wikipedia.org/wiki/DNSSEC>`_ validation and can be used to
ensure that DNS queries protected by DNSSEC are signed by the correct DNS root
zone key, verified locally.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.unbound

The role uses the ``ipaddr`` Ansible filter plugin to generate revDNS zone
names. For this to work, the ``netaddr`` Python library is required on the
Ansible Controller. On Debian/Ubuntu distributions, you can install the
``python-netaddr`` APT package; otherwise you can install the required
``netaddr`` Python library from PyPI.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
