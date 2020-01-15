.. _debops.unbound:

debops.unbound
==============

`Unbound <https://unbound.net/>`_ is a local DNS resolver. It supports
`DNSSEC <https://en.wikipedia.org/wiki/DNSSEC>`_ validation and can be used to
ensure that DNS queries protected by DNSSEC are signed by the correct DNS root
zone key, verified locally.

.. toctree::
   :maxdepth: 3

   getting-started
   defaults/main
   defaults-detailed
   defaults-server

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/unbound/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
