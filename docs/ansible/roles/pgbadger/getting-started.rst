.. Copyright (C) 2025 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2025 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:
      :depth: 2

Default configuration
---------------------

The role will create the ``pgbadger`` UNIX account on the "main" host, as well
as ``pgbadger`` UNIX account on each remote host included in the
``[debops_service_postgresql_server]`` Ansible inventory group - all of these
configurable using role variables. The main account will have a SSH key which
will be added to the remote accounts, which should permit access to the remote
accounts without the need for a password. The accounts will be included in the
``adm`` and ``sshusers`` UNIX groups to permit access to log files and remote
SSH access. The default DebOps SSH configuration should permit access to the
UNIX account of the same name across the cluster; see :ref:`debops.sshd` and
:ref:`debops.pam_access` role documentation for details.

If pgBadger is managed on the same host as a PostgreSQL server, the role will
create a simple :file:`local` Bash script which will parse local PostgreSQL log
files via the ``adm`` UNIX group access.

By default, the generated Bash scripts are executed periodically using the
:command:`cron` service. The period can be changed, or entire :command:`cron`
job can be disabled to allow fine-grained control using the :ref:`debops.cron`
Ansible role.

Generated output files will be published using the :ref:`debops.nginx` role at
the domain specified in the :envvar:`pgbadger__fqdn` variable. The
:command:`nginx` configuration can be extended to permit multiple FQDNs or
subdirectories, as needed.


Example inventory
-----------------

To enable pgBadger support on a host, it needs to be included in a specific
Ansible inventory group:

.. code-block:: none

   [debops_service_pgbadger]
   hostname   ansible_host=hostname.example.org

By default, the role will use the ``debops_service_postgresql_server``
inventory group to configure remote SSH access to other hosts (if the pgBadger
host is included in it, SSH configuration will be skipped).


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the :ref:`debops.pgbadger` role:

.. literalinclude:: ../../../../ansible/playbooks/service/pgbadger.yml
   :language: yaml
   :lines: 1,15-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::pgbadger``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``skip::pgbadger``
  Main role tag, should be used in the playbook to skip all of the role tasks.

Other resources
---------------

List of other useful resources related to the :ref:`debops.pgbadger` Ansible role:

- Manual pages: :man:`pgbadger(1p)`
