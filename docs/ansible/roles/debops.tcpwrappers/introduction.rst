Introduction
============

The ``debops.tcpwrappers`` Ansible role can be used to manage entries in
``/etc/hosts.allow`` and ``/etc/hosts.deny`` which are used by TCP Wrappers to
limit connections to daemons that utilize the ``libwrap`` library.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.tcpwrappers

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
