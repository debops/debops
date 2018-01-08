Introduction
============

The `radvd <https://en.wikipedia.org/wiki/Radvd>`_, Router Advertisement
Daemon, is used to publish IPv6 subnets, routes, DNS configuration to other
hosts on the local network. It's required for the hosts to use SLAAC
autoconfiguration.

The ``debops.radvd`` Ansible role can be used to install and configure the
:command:`radvd` service. It will detect and automatically configure any
network bridges with IPv6 networking enabled.


Installation
------------

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

    ansible-galaxy install debops.radvd

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
