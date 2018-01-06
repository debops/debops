Introduction
============

`iPXE`_ is a network boot loader which allows you to boot host operating
systems in different ways, including over HTTP, from local NFS or ISCSI server,
etc.

This Ansible role configures iPXE configuration files on a specified host
which can be served to the other hosts on the network using TFTP or HTTP
server. You can use :ref:`debops.dnsmasq` or
:ref:`debops.dhcpd` + :ref:`debops.tftpd` Ansible roles to serve these
configuration files to your hosts.

.. _iPXE: http://ipxe.org/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
