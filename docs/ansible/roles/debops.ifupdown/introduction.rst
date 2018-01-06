Introduction
============

.. include:: ../../../includes/global.rst

``ifupdown`` is a set of high-level scripts in Debian/Ubuntu Linux
distributions which can be used to configure network interfaces, bridges, VLAN
interfaces, bonding, and so on. You can find example configuration and usage
guides on the `NetworkConfiguration`_ page of the `Debian Wiki`_.

``debops.ifupdown`` is an Ansible role which wraps ``ifupdown`` in an easy to
use, and Ansible-friendly interface. It aims to be a safe and reliable way to
let you configure network interfaces on hosts managed using Ansible. It can be
used either as a standalone role configured using role/inventory variables, or
as a dependency of another role, to provide network configuration as needed.

.. _NetworkConfiguration: https://wiki.debian.org/NetworkConfiguration


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.2.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.ifupdown

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
