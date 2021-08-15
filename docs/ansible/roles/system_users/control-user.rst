.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _system_users__ref_control_user:

Centralized "control user" UNIX account
=======================================

.. only:: html

   .. contents::
      :local:

By default the :ref:`debops.system_users` role will create an administrator
UNIX account based on the local UNIX account of the person executing Ansible at
the time, for example ``username``. This allows the use of the :command:`ssh`
commands to connect to the host without specifying a separate user account and
is useful in a single-admin environment. In the :ref:`debops.system_users`
role, such an account configuration is called a "self account", since it
belongs to the user that is currently executing Ansible.

When multiple administrators are involved and share the same DebOps project
directory, this behaviour will result in each administrator using their own
"self" UNIX account to connect to the remote host. These accounts might need to
be created on the remote hosts by the existing administrator. They can be
defined using the :ref:`system_users__ref_accounts` variables.

Unfortunately there's a caveat - the remote and local "self" UNIX account of
each administrator needs to be the same. It's not a problem in a single-admin
environment, but in multi-admin environment there's no way to override a remote
UNIX account for a specific administrator outside of the DebOps project
directory, for example via environment variables. Since the project directory
is shared by multiple people, overriding the UNIX account will affect all of
them.

An alternative approach for remote host management might be the use of
a central "control user" UNIX account by all administrators, described below.
In such case, the account is defined in the ``ansible_user`` variable in the
Ansible inventory and is shared by all people with administrator access.


How to enable the "control user" account
----------------------------------------

To enable the shared "control user" account, you need to define two variables
in the Ansible inventory, ``ansible_user`` and
:envvar:`system_users__self_name`, with the same value. Remember to not
reference the ``ansible_user`` variable directly, because that will create
a `bootstrap paradox`__.

.. __: https://en.wikipedia.org/wiki/Causal_loop

In the examples below we will use ``ansible`` as the shared account name. An
example inventory host definition:

.. code-block:: none

   # ansible/inventory/hosts

   [debops_all_hosts]
   hostname    ansible_host=hostname.example.org   ansible_user=ansible
   hostname    system_users__self_name=ansible

This will tell the :ref:`debops.system_users` role to not use the local UNIX
account name and instead use the ``ansible`` as the account name to create.

Many VPS providers and OS image creators include default unprivileged UNIX
accounts in the virtual machine or OS images used for provisioning. For
example, on Debian-based VMs such account can be called ``debian``, on
Ubuntu-based VMs it might be ``ubuntu``, on Raspberry Pi system images the
account is usually called ``pi``, Vagrant boxes use the ``vagrant`` account,
and so on. In such case, you might want to use the account name already present
to avoid creating a separate administrator account.

The remote UNIX account definition can be further augmented using the
:ref:`system_users__ref_accounts` list. For example, to specify a list of
multiple SSH keys which can be used to connect to a given account, you can
define in the inventory variables:

.. code-block:: yaml

   ---
   # ansible/inventory/group_vars/all/system_users.yml

   system_users__accounts:

     - name: 'ansible'
       sshkeys:
         - 'ssh-rsa ...'
         - 'ssh-rsa ...'
         - 'ssh-rsa ...'

If the SSH keys are not specified, the role will import the SSH key(s) of the
local UNIX account that executes Ansible. If you specify a custom list,
remember to include your own SSH key as well.

You can also use the :ref:`debops.authorized_keys` role to further control what
SSH keys are present for the "control user" account, with expiration date,
forced command and other such options.


Host bootstrapping with "control user" account
----------------------------------------------

Definition of ``ansible_user`` variable in the Ansible inventory might cause
issues during bootstrapping when the ``root`` UNIX account might have to be
used. Ansible will insist on using the UNIX account specified in the
``ansible_user`` inventory variable to connect to the host. To override that,
you can use the command below to bootstrap a host via the ``root`` account:

.. code-block:: console

   debops bootstrap -l hostname -e 'ansible_user=root'

After the account is created, the use of a separate ``--extra-vars`` definition
shouldn't be required.

Take care to not bootstrap hosts with and without "control user" at the same
time, because ``ansible_user`` variable will be set on both during Ansible
execution and this might change the desired result. Bootstrapping multiple
hosts with "control user" accounts at the same time is fine.


Centralized "control user" and LDAP integration
-----------------------------------------------

When LDAP support is enabled using the :ref:`debops.ldap` role, the
:ref:`debops.system_users` role creates UNIX accounts with a prefix, by default
``_`` to distinguish them from the accounts defined in LDAP directory. When the
"control user" is enabled by defining the ``ansible_user`` variable, the prefix
will not be added automatically. If you want to prefix the account, you can
specify the ``_`` character manually in all locations, for example:

.. code-block:: none

   # ansible/inventory/hosts

   [debops_all_hosts]
   hostname    ansible_host=hostname.example.org   ansible_user=_ansible
   hostname    system_users__self_name=_ansible

.. code-block:: yaml

   ---
   # ansible/inventory/group_vars/all/system_users.yml

   system_users__accounts:

     - name: '_ansible'
       sshkeys:
         - 'ssh-rsa ...'
         - 'ssh-rsa ...'
         - 'ssh-rsa ...'


User authentication, access control and accounting
--------------------------------------------------

One issue to solve with a shared "control user" account might be user
accounting. In recent OpenSSH versions, the fingerprint of the SSH key used to
connect to an account is included in the :command:`sshd` service logs, usually
stored in :file:`/var/log/auth.log` logfile. This can be used to audit who
connected to a given account at a particular time.
