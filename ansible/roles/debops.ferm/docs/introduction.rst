Introduction
============

`ferm`_ is a wrapper around the :command:`iptables` and the :command:`ip6tables` commands which lets
you manage host firewalls in an easy and Ansible-friendly way. This role can
be used to setup firewall rules directly from the inventory, or it can be used
as a dependency by other roles to setup firewall rules for other services.

.. _ferm: http://ferm.foo-projects.org/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.ferm

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
