Introduction
============

This `Ansible`_ role manages a NFS server. It can automatically configure
``iptables`` firewall using `debops.ferm`_ role and reserve ports for services
required by NFS using `debops.etc_services`_ role. You can also modify default
list of exported directories and use host Access Control Lists using Ansible
inventory. Clients which connect to NFS are configured separately.

.. _Ansible: http://ansible.com/
.. _debops.ferm: https://github.com/debops/ansible-ferm/
.. _debops.etc_services: https://github.com/debops/ansible-etc_services/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
