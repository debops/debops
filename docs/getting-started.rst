Getting started
===============

.. contents:: Sections
   :local:

Security considerations
-----------------------

The ``debops.authorized_keys`` role is designed to manage files in
``/etc/ssh/authorized_keys/`` directory which contain SSH public keys for user
accounts.

By default, role modifies the ownership and permissions of these files after
the Ansible ``authorized_key`` changes them, so that the owner of these files
is ``root`` account, and the file group, either named after the specified
username, set as an ``item.group`` parameter or ``root`` if the previous
entries don't result in an existing group present on a given system. This
assumes that each user account has a primary group of the same name as their
account, and they are the only members of that group.

The file attributes will be set as ``640`` to allow read only access to the SSH
public key files. This should ensure that user accounts can be logged into the
specific SSH public keys, but they cannot be modified by their respective
users.

Unfortunately, it seems that the Ansible ``authorized_key`` module
`enforces the "600" file permissions <https://github.com/ansible/ansible-modules-core/blob/devel/system/authorized_key.py#L231-L235>`_
on any file change, therefore there exists a window of opportunity between the
given user file being updated by the ``authorized_key`` module and permissions
being enforced again by the ``file`` Ansible module. At the moment there's no
good solution to this issue, perhaps in the future the ``authorized_key``
module will be updated to allow for setting custom file ownership and
permissions similarly to the ``file`` module. However, if there are no updates
to the user files, the permissions are not changed.


SSH service configuration
-------------------------

The ``debops.authorized_keys`` role does not manage the ``sshd`` service
configuration by itself. Instead, you are expected to configure the ``sshd``
daemon to use the authorized keys from its directory, either by hand or by an
Ansible role.

.. note::

   The ``debops.sshd`` role enables use of the SSH public keys managed by the
   ``debops.authorized_keys`` automatically.

To enable the ``sshd`` service to use the configured public keys, you should
change the configuration in the ``/etc/ssh/sshd_config`` file to something like
this:

.. code-block:: bash

   # /etc/ssh/sshd_config
   AuthorizedKeysFile /etc/ssh/authorized_keys/%u %h/.ssh/authorized_keys

The above configuration will enable use of the configured keys by all
subsequent SSH connections.

You can use the ``Match`` keyword to restrict the use of the authorized keys to
a particular hosts, users, groups or IP addresses/subnets as needed. For
example, if you want to check these authorized keys only for users in
a specific subnet, you can do it like this:

.. code-block:: bash

   # /etc/ssh/sshd_config
   Match Address 192.0.2.0/24
         AuthorizedKeysFile /etc/ssh/authorized_keys/%u %h/.ssh/authorized_keys

Alternatively, you can use different conditions to restrict the SSH public keys
checked by the ``sshd`` daemon to only the authorized keys maintained by this
role. For example, to restrict a particular system group to only use these
authorized keys for authentication, you can do it like this:

.. code-block:: bash

   # /etc/ssh/sshd_config
   Match Group sftponly
         AuthorizedKeysFile /etc/ssh/authorized_keys/%u


Example inventory
-----------------

This role is included by default in the ``common.yml`` DebOps playbook, so you
don't need to do anything to enable it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.authorized_keys`` role:

.. literalinclude:: playbooks/authorized_keys.yml
   :language: yaml
