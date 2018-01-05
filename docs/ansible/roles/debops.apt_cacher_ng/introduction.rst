Introduction
============

Ansible role to install and manage Apt-Cacher NG.
Apt-Cacher NG is a caching HTTP proxy for downloading software packages.  This
role sets up the Apt-Cacher NG server in your network and allows clients to use
the proxy.  Only the proxy server is setup by this role.

The following options are available to get clients to use the Apt-Cacher NG server:

* Advanced Package Tool: :ref:`debops.apt_proxy`

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run::

    ansible-galaxy install debops.apt_cacher_ng

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
