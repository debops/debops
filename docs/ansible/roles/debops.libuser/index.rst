.. _debops.libuser:

debops.libuser
==============

The `libuser`__ library and its corresponding package provides a set of
commands and an API which can be used by tools like Ansible to manage UNIX
account and group configuration in different NSS databases (local
:file:`/etc/passwd` and :file:`/etc/group` databases, LDAP, NIS, etc.). This
allows to abstract away user and group management and make it independent from
the underlying database.

.. __: https://pagure.io/libuser/

The ``debops.libuser`` role installs and configures the ``libuser`` package on
Debian or Ubuntu hosts. The library is used by some other DebOps roles like
:ref:`debops.users`, :ref:`debops.system_users` to manage local UNIX accounts
and groups when the hosts are joined to an LDAP environment. The default
configuration set up by the role ensures that Ansible ``user`` and ``group``
modules, when instructed, can correctly create local account and group entries
in the ``passwd`` and ``group`` databases.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.libuser/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:

