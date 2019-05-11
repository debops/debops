Getting started
===============

.. contents::
   :local:


LDAP integration
----------------

The role checks if the LDAP support has been configured on a host, via the
:ref:`debops.ldap`. If LDAP support is enabled, local UNIX groups, local UNIX
accounts and their home directory names will have the ``_`` prefix prepended to
them, to avoid clashes with the LDAP-based groups and accounts. This is
controlled by the :envvar:`users__prefix` variable.

LDAP support also affects the default home directory paths. By default home
directories will be put in :file:`/home`; with LDAP support enabled that will
change to :file:`/var/local`, to avoid clashes with remote filesystems that
might be mounted at the :file:`/home` path, for example via NFS.


Example inventory
-----------------

The ``debops.users`` Ansible role is included by default in the
:file:`common.yml` DebOps playbook; you don't need to do anything to have it
executed.

If you don’t want to let ``debops.users`` manage user accounts, you can disable
it with the following setting in your inventory:

.. code-block:: yaml

   users__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.users`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/users.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::users``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
