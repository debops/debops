Introduction
============

.. include:: ../../../includes/global.rst

tinc_ is a Virtual Private Network daemon, it can be used to create encrypted
and tunneled connections to other hosts, forming a separate network, either
a centralized or a mesh one.

``debops.tinc`` Ansible role allows you to install and configure a mesh VPN
using ``tinc``, including automatic public key exchange between all hosts in
the Ansible inventory, connection to external hosts and secure configuration.


Installation
------------

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

    ansible-galaxy install debops.tinc

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
