.. _debops.tinc:

debops.tinc
===========

`tinc`__ is a Virtual Private Network daemon, it can be used to create encrypted
and tunneled connections to other hosts, forming a separate network, either
a centralized or a mesh one.

``debops.tinc`` Ansible role allows you to install and configure a mesh VPN
using ``tinc``, including automatic public key exchange between all hosts in
the Ansible inventory, connection to external hosts and secure configuration.

.. __: https://tinc-vpn.org/

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed
   examples
   upgrade

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/tinc/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
