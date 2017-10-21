Getting started
===============

.. contents::
   :local:

``debops.ipxe`` is just a small part of a larger stack of services to be
useful. To make it work, you will also need to set up a DHCP server, TFTP
server, DNS server, optionally a webserver to serve Debian Preseed files. These
services can be configured separately by different Ansible roles included in
DebOps.

Example inventory
-----------------

To create iPXE configuration files on a given host you should add it in the
``[debops_ipxe]`` Ansible host group::

    [debops_ipxe]
    hostname


Example playbook
----------------

Here's an example playbook which uses ``debops.ipxe`` role::

    ---

    - name: Configure iPXE scripts
      hosts: debops_ipxe

      roles:
        - role: debops.ipxe
          tags: ipxe

