Getting started
===============

.. contents::
   :local:


.. _system_users__ref_libuser:

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


LDAP integration
----------------

The role checks if the LDAP support has been configured on a host, via the
:ref:`debops.ldap`. If LDAP support is enabled, local UNIX groups, local UNIX
accounts and their home directory names will have the ``_`` prefix prepended to
them, to avoid clashes with the LDAP-based groups and accounts. This is
controlled by the :envvar:`system_users__prefix` variable.

LDAP support also affects the default home directory paths. By default home
directories will be put in :file:`/home`; with LDAP support enabled that will
change to :file:`/var/local`, to avoid clashes with remote filesystems that
might be mounted at the :file:`/home` path, for example via NFS.


Example inventory
-----------------

The ``debops.system_users`` Ansible role is included by default in the
:file:`common.yml` DebOps playbook; you don't need to do anything to have it
executed. It's also included in the :file:`bootstrap.yml` and
:file:`bootstrap-ldap.yml` playbooks to create sysadmin accounts during host
bootstrapping.

If you don’t want to let ``debops.system_users`` manage user accounts, you can
disable it with the following setting in your inventory:

.. code-block:: yaml

   system_users__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.system_users`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/system_users.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Common role tags:

``role::system_users``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``skip::system_users``
  Main role tag, should be used in the playbook to skip all of the role tasks.

``skip::check``
  Used in specific tasks that might break in the Ansible ``--check`` mode on
  first run of the role on a host, but not subsequent runs. It can be used to
  skip these tasks in such case.

You can see full list of available role tags by executing the command:

.. code-block:: console

   debops service/system_users --list-tags
