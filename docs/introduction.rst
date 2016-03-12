Introduction
============

The ``debops.etc_services`` role can be used to "reserve" or "register" a
service port in the ``/etc/services`` file. Service ports configured this way can
appear as named entries in many command outputs, such as ``iptables --list``
or ``netstat --listening --program``. You can also have convenient database
of reserved and free ports on a particular host, and reference ports by
their names in firewall configuration files.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run::

    ansible-galaxy install debops.etc_services

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
