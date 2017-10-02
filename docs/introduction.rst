Introduction
============

This role manages the HTTP/HTTPS/FTP proxy configuration for APT. You can
define what proxy to use, what hosts should be connected to directly, as well
as set additional APT configuration options related to proxies as needed.

The role also features proxy online detection support to silently
skip/ignore temporally offline proxies which can make sense for
workstations and home servers.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.apt_proxy

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
