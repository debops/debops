.. _debops.pam_access:

debops.pam_access
=================

The `Linux Pluggable Authentication Modules`__ provide dynamic authentication
support to services on Linux hosts. The ``debops.pam_access`` role can be used
to manage one aspect of PAM - access control rules that can be used to grant or
revoke access to services based on users, groups and origins.

.. __: https://en.wikipedia.org/wiki/Linux_PAM

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.pam_access/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
