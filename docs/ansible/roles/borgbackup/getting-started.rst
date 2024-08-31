.. Copyright (C) 2019-2023 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2023 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2019-2023 DebOps https://debops.org/
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Setup order
-----------

1. Run the :file:`common.yml` playbook on all controllers/servers/clients.
2. Configure controllers (optional).
3. Configure server(s).
4. Configure client(s), i.e. hosts to backup.


Setting up backup server(s)
---------------------------

To setup a backup server, add it to the ``[debops_service_borgbackup]`` and
``[debops_service_borgbackup_server]`` groups. You also need to add all
clients to the ``[debops_service_borgbackup]`` and
``[debops_service_borgbackup_client]`` groups:

.. code-block:: none

   [debops_all_hosts]
   ...

   [debops_service_borgbackup]
   backup.example.net
   client1.example.net
   client2.example.net

   [debops_service_borgbackup_server]
   backup.example.net

   [debops_service_borgbackup_client]
   client1.example.net
   client2.example.net

Then make sure that the backup server to use is defined in
:file:`inventory/group_vars/debops_service_borgbackup/servers.yml`:

.. code-block:: yaml

   borgbackup__servers: [ 'backup.example.net' ]

   # This should be uncommented if using a controller
   #borgbackup__controller: 'controller.example.net'

Note that if you use aliases or short names in your inventory, the above
variables will have to use the alias or short name instead so that the
role can find the server in the Ansible inventory:

On each backup server, per-client accounts will be created, each with their
own BorgBackup repository.

With this, the backup server should be ready after you run the
``debops.borgbackup`` playbook against it.


Setting up backup client(s)
---------------------------

Look at the :envvar:`borgbackup__original_configuration` and
:envvar:`borgbackup__default_configuration` variables, and then make
changes to suit your environment via the :envvar:`borgbackup__configuration`,
:envvar:`borgbackup__group_configuration` and
:envvar:`borgbackup__host_configuration` variables in the Ansible inventory.

You will probably also want to fine-tune the
:envvar:`borgbackup__default_source_directories` and
:envvar:`borgbackup__default_exclude_patterns` variables via the
via the corresponding variables (``borgbackup__host_*``,
``borgbackup__group_*``, etc).

After running the role against a given client, the ``root`` account on that
client will be able to connect to the backup server(s) via SSH and run the
:command:`borg serve` command. The SSH key of the ``root`` account is managed
by the :ref:`debops.root_account` role (which is executed as part of the
:file:`common.yml` playbook).

The per-client encryption keys will be backed up to the Ansible controller
and a :man:`systemd.timer(5)` unit or a :man:`cron(8)` script will be installed
which will trigger regular backups. By default, the backups will be triggered
at a random (per-client specific) time between midnight and 6AM.


Backup trigger via centralized control
--------------------------------------

In case you configure multiple hosts to backup to one backup server, you might
want to run the backups one after each other for example when the WAN bandwidth
is your limiting factor.

This is an alternative to the previously shown client-triggered backups.
For this you will need a controller server from which the backups are
triggered. The backup server could also act as the controller server but for
security reasons a dedicated controller server is recommended.

The clients need to be added to the
``[debops_service_borgbackup_controlled_client]`` group instead of the
``[debops_service_borgbackup_client]`` group and the the host which should act
as a controller need to be added to the ``[debops_service_borgbackup]`` and
``[debops_service_borgbackup_controller]`` groups:

.. code-block:: none

   [debops_all_hosts]
   ...

   [debops_service_borgbackup]
   controller.example.net
   backup.example.net
   client1.example.net
   client2.example.net

   [debops_service_borgbackup_controller]
   controller.example.net

   [debops_service_borgbackup_server]
   backup.example.net

   [debops_service_borgbackup_controlled_client]
   client1.example.net
   client2.example.net

Also make sure that the :envvar:`borgbackup__controller` variable from the
example provided in the server section above is uncommented before executing
the role playbook against the controller.

The role will create the user ``backup-contoller`` on the controller and each
client. Using a :man:`systemd.timer(5)` unit or a :man:`cron(8)` script, the
controller user will connect periodically to the clients (sequentially) via SSH
and trigger backup jobs via :command:`sudo`. This ensures that only one client
will be performing a backup job at any given time.


Multiple sites
--------------

The above examples assume that you are running a single "site" or cluster with
a controller (optional), server(s) and client(s). If you instead want to
configure separate logical clusters, each with their own controller and
server(s), you need to create separate inventory groups for each cluster:

.. code-block:: none

   [debops_all_hosts]
   ...

   [debops_service_borgbackup_site_a]
   controller.a.example.net
   backup.a.example.net
   client1.a.example.net
   client2.a.example.net

   [debops_service_borgbackup_site_b]
   controller.b.example.net
   backup.b.example.net
   client1.b.example.net
   client2.b.example.net

   [debops_service_borgbackup_controller]
   controller.a.example.net
   controller.b.example.net

   [debops_service_borgbackup_server]
   backup.a.example.net
   backup.b.example.net

   [debops_service_borgbackup_controlled_client]
   client1.a.example.net
   client2.b.example.net
   client1.a.example.net
   client2.b.example.net

Then make sure that the :envvar:`borgbackup__controller` and
:envvar:`borgbackup__servers` variables are correctly defined for each
inventory group, e.g. in
:file:`inventory/group_vars/debops_service_borgbackup_site_a/servers.yml`:

.. code-block:: yaml

   borgbackup__servers: [ 'backup.a.example.net' ]

   borgbackup__controller: 'controller.a.example.net'

And in
:file:`inventory/group_vars/debops_service_borgbackup_site_b/servers.yml`:

.. code-block:: yaml

   borgbackup__servers: [ 'backup.b.example.net' ]

   borgbackup__controller: 'controller.b.example.net'


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.borgbackup`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/borgbackup.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::borgbackup``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::borgbackup:config``
  Performs tasks related to creating/updating various configuration files.

``role::borgbackup:install``
  Performs tasks related to software installation.
