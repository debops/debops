Getting started
===============

.. contents::
   :local:


.. _users__ref_libuser:

Support for ``libuser`` library
-------------------------------

The role uses the ``libuser`` library, supported by the ``group`` and ``user``
Ansible modules, to manage the UNIX groups and accounts present on the hosts.
The library is used to ensure that the groups and accounts created locally on
the host that uses the LDAP directory as the user/group database have UID/GID
values in the correct ranges, thus avoiding collisions with the LDAP directory
UID/GID ranges. Without the ``libuser`` these local groups and accounts would
be created in the LDAP UID/GID ranges, since the normal UNIX user management
tools pick the next UID/GID based on the contents of the ``getent`` output, and
not from the local user and group databases.

This behaviour can be controlled using the ``item.local`` parameter, which by
default is enabled and shouldn't be specified directly unless you want to
override the use of the ``libuser`` library for some reason. Due to issues with
the Ansible modules, additional UNIX groups are managed using normal UNIX tools
instead of their ``libuser`` equivalents.
