.. _debops.apt_proxy:

debops.apt_proxy
================

This role manages the HTTP/HTTPS/FTP proxy configuration for APT. You can
define what proxy to use, what hosts should be connected to directly, as well
as set additional APT configuration options related to proxies as needed.

The role also features proxy online detection support to silently
skip/ignore temporally offline proxies which can make sense for
workstations and home servers.

.. toctree::
   :maxdepth: 2

   getting-started

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/apt_proxy/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
