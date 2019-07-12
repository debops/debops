.. _debops.users:

debops.users
============

The ``debops.users`` Ansible role can be used to manage local user accounts and
groups. The role allows for certain operations inside of the home directories,
like configuration of the mail forwarding, SSH public keys or automatic
deployment of user configuration files (dotfiles).

This role is designed to manage regular user accounts and application accounts.
In a LDAP-enabled environment, it might be better to configure these using LDAP
directory, and manage local system administrator accounts using the
:ref:`debops.system_users` Ansible role.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.users/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
