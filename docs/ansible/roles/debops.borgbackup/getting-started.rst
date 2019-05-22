Getting started
===============

.. contents::
   :local:


Role design
-----------

``debops.borgbackup`` is designed to configure cluster-wide backup for hosts
to dedicated backup servers.

The role itself only handles installation and configuration of borgbackup and
borgmatic. Other integration into the environment is proposed to be done using
dedicated DebOps roles and the following example inventory configuration. The
example configuration presented here takes the principle of least privilege to
heart in that each host/component only has the access it needs.

The setup of the backup server does not need it’s own role and is documented
here: :ref:`borgbackup__ref_backup_server`.

Setup order
-----------

1. Backup controllers (optional).
2. Backup servers.
3. Backup clients (hosts to backup).
4. If you have never run DebOps against your backup clients before, you will
   need to rerun the :ref:`debops.resources` role against your backup
   controllers (optional).

Example inventory
-----------------

Hosts which should be backed up need to be added to the
``[debops_service_borgbackup]`` group in Ansible’s inventory. Fortuermore, the
example below assumes that the host is also assigned to a site/location group:

.. code-block:: none

   [debops_service_borgbackup]
   db.example.net

   [site_a]
   db.example.net


Configure the defaults for your environment like retention time. Also, we need
to distribute the SSH host key of the backup server:

.. literalinclude:: inventory/group_vars/all/default.yml
   :language: yaml

For each site, you can then configure the backup server to use like this in
:file:`inventory/group_vars/site_a.yml`:

.. literalinclude:: inventory/group_vars/site_a.yml
   :language: yaml

Backup trigger via cron
-----------------------

The simplest backup trigger is a cron job on each host causing it to make a
backup of itself.

.. literalinclude:: inventory/host_vars/backup.example.net/default.yml
   :language: yaml

Backup trigger via centralized cron
-----------------------------------

In case you configure multiple hosts to backup to one backup server, you might
want to run the backups one after each other for example when the WAN bandwidth
is your limiting factor or when the backup server should not be overloaded.
This is an alternative to the previously shown triggering via cron.
For this you will need a controller server from which the backups are
triggered. The backup server could also act as the controller server but for
security reasons a dedicated controller server is recommended.

Hosts which should act as "controllers" need to be added to the
``[controller_server]`` group in Ansible’s inventory:

.. code-block:: none

   [controller_server]
   controller.example.net

You will need to distribute the SSH host key of the backup server to the backup
clients as well as distribute the SSH host keys of the backup clients to the
controller server. You will also need to create users. ``backup-mgt`` is
configured on the backup clients. When the controller connects via SSH as this
user, the backup will be triggered. ``backup-controller`` is configured on the
controller for running a script which triggers the backups sequentially:

.. literalinclude:: inventory/group_vars/all/default_controller.yml
   :language: yaml

``backup-mgt`` needs the priviliate to run borgmatic as root to backup the
whole system. For this sudo needs to be configured like this in
:file:`inventory/group_vars/debops_service_borgbackup.yml`.

.. literalinclude:: inventory/group_vars/debops_service_borgbackup.yml
   :language: yaml

Finally we configure a cron job to run the backup script:

.. literalinclude:: inventory/host_vars/controller.example.net/default.yml
   :language: yaml

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.borgbackup`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/borgbackup.yml
   :language: yaml
