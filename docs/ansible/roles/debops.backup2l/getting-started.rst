Getting started
===============

.. contents::
   :local:

Default configuration
---------------------

By default the backups are maintained in the :file:`/var/backups/backup2l/`
subdirectory, which will be automatically excluded from the archive.

The role configures the :command:`backup2l` script to read the list of paths to
backup from an external file, by default stored in
:file:`/usr/local/etc/backup/include`. This file is maintained using the
``lineinfile`` Ansible module, therefore other Ansible roles or the system
administrators can add their own paths to it without breaking idempotency. This
functionality can be disabled using the :envvar:`backup2l__srclist_from_file`
variable.

The :command:`backup2l` script will execute pre-hooks and post-hooks from
specific directories, by default:

- pre-hooks: :file:`/usr/local/etc/backup/pre-hook.d/`
- post-hooks: :file:`/usr/local/etc/backup/post-hook.d/`

These directories can contain scripts which execute certain actions before or
after a backup is performed. This can be used to for example, send new archives
to a remote file using the :command:`rsync` command. You can use the
:ref:`debops.resources` Ansible role to provide custom pre/post hooks.

The pre/post hook integration is designed to be "agnostic", and it's best not
to rely on a specific backup solution, ie. :command:`backup2l` in this case, to
execute actions. You can maintain your own directories and files in the
:file:`/var/backups/` directory, which will be subsequently included in the
:command:`backup2l` archive.


Ansible local facts
-------------------

The ``debops.backup2l`` role provides a set of Ansible local facts available in
the ``ansible_local.backup2l.*`` hierarchy. Other Ansible roles can use these
facts to include additional configuration using pre/post hook scripts, or add
their own paths to the list of paths archived by the script.


Example inventory
-----------------

To enable :command:`backup2l` script on a given host, it needs to be included
in the ``[debops_service_backup2l]`` Ansible inventory group:

.. code-block:: none

   [debops_service_backup2l]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.backup2l`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/backup2l.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::backup2l``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
