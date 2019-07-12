.. _debops.nslcd:

debops.nslcd
============

The :command:`nslcd` daemon, part of the `nss-pam-ldapd`__ software package, is
used to look up user, group or other information stored in LDAP that is related
to UNIX accounts or groups. It is needed if you want to use the
``posixAccount`` and ``posixGroup`` LDAP objects to authenticate to the
UNIX-like hosts.

.. __: https://arthurdejong.org/nss-pam-ldapd/

The ``debops.nslcd`` Ansible role can be used to configure the :command:`nslcd`
service on a host and, via :ref:`debops.ldap` role, create a bind account in
the LDAP directory used by :command:`nslcd` to perform LDAP lookups.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   ldap-dit

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.nslcd/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
