Getting started
===============

.. contents::
   :local:


Subordinate UID/GID range for root
----------------------------------

`Linux user namespaces <https://en.wikipedia.org/wiki/Linux_namespaces#User_ID_(user)>`__
can be used to create unprivileged LXC or Docker containers which don't use
normal UID/GID ranges of the host system. These "subordinate" UID/GID ranges
are configured in the :file:`/etc/subuid` and :file:`/etc/subgid` databases
respectively.

Unfortunately, Debian by default does not reserve a subordinate UID/GID range
for the ``root`` account. In conjunction with the system automatically creating
subUID/subGID ranges for new user accounts created on a host this might cause
creation of the ``root`` subUID/subGID ranges difficult. To avoid this issue,
the ``debops.root_account`` Ansible role will reserve a defined set of UID/GID
ranges for the ``root`` account which can then be used to, for example, create
unprivileged LXC containers.


Example inventory
-----------------

The ``debops.root_account`` role is included by default in the
:file:`common.yml` DebOps playbook; you don't need to do anything to have it
executed.

If you don’t want to let ``debops.root_account`` manage the root account, you
can do this with the following setting in your inventory:

.. code-block:: yaml

   root_account__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.root_account`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/root_account.yml
   :language: yaml
