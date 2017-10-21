Introduction
============

`iPXE`_ is a network boot loader which allows you to boot host operating
systems in different ways, including over HTTP, from local NFS or ISCSI server,
etc.

This Ansible role configures iPXE configuration files on a specified host
which can be served to the other hosts on the network using TFTP or HTTP
server. You can use `debops.dnsmasq`_ or `debops.dhcpd`_ + `debops.tftpd`_
Ansible roles to serve these configuration files to your hosts.

.. _iPXE: http://ipxe.org/
.. _debops.dnsmasq: https://github.com/debops/ansible-dnsmasq/
.. _debops.dhcpd: https://github.com/debops/ansible-dhcpd/
.. _debops.tftpd: https://github.com/debops/ansible-tftpd/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
