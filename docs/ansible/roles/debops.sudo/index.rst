.. _debops.sudo:

debops.sudo
===========

The ``debops.sudo`` role can be used to ensure that :command:`sudo` is
supported on a host. The role will automatically install ``sudo-ldap`` APT
package if LDAP support is detected on a host, otherwise a normal ``sudo`` APT
package will be installed.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   ldap-dit

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.sudo/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
