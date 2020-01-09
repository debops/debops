.. _slapd__ref_backup_restore:

Backup and restore procedures
=============================

Here you can find information about the backup procedure for the OpenLDAP
service configured by the :ref:`debops.slapd` Ansible role as well as tips
about restoring the backed-up data.


Backup snapshots
----------------

The :ref:`debops.slapd` role installs the :command:`slapd-snapshot` shell
script that can be used to create periodic LDIF snapshots of the databases used
by the OpenLDAP service.

By default, three :command:`cron` jobs will be configured by the role to create
daily (7 days), weekly (4-5 weeks) and monthly (12 months) snapshots of all
OpenLDAP databases found (ignoring the "frontend" database or any databases
with the ``olcReadOnly`` attribute present). This can be controlled using the
:envvar:`slapd__snapshot_deploy_state` and :envvar:`slapd__snapshot_cron_jobs`
default variables. Alternatively, the periodic :command:`cron` jobs can be
disabled, and the :command:`slapd-snapshot` script can be executed as ``root``
to create current snapshot of the OpenLDAP databases in LDIF format; previous
snapshots are automatically removed in this case with assumption that they have
been transferred to a remote storage by other means.

The :command:`slapd-snapshot` script will enable and disable read-only mode for
each database, with some caveats. The ``cn=config`` database is not backed-up
read-only, because read-only mode cannot be disabled without stopping the
service. The databases that have the ``olcReadOnly`` attribute defined (enabled
or disabled) are not backed up automatically.

The snapshots are stored in the :file:`/var/backups/slapd/` directory as
compressed tarballs. After finishing the snapshot, the
:command:`slapd-snapshot` script will change ownership of the created tarballs
to the ``backup:backup`` UNIX account and group. This account can then encrypt
the tarballs via its own set of scripts, using GnuPG assymetric encryption, to
prepare them to be sent to a remote location (this functionality is not
implemented by the :ref:`debops.slapd` role). The :command:`slapd-snapshot`
script will automatically remove periodic :file:`*.gz.asc` or :file:`*.gz.gpg`
files before creating new iterations to preserve disk space.


Restore procedure
-----------------

The LDAP server has crashed and burned, but you have the backup snapshots
available, how to restore them? The approach described here assumes that all
OpenLDAP server configuration was performed using the :ref:`debops.slapd` role
and is still available in the inventory; only the backup of the main LDAP
databass is needed.

.. note::
   This procedure can also be used to migrate LDAP directory between OpenLDAP
   installations.

tl;dr version
~~~~~~~~~~~~~

Set up a new OpenLDAP cluster, select one host as the restore point.

.. code-block:: console

   scp data.ldif slapd-host:
   ssh slapd-host
   sudo systemctl stop slapd.service
   sudo rm -rf /var/lib/ldap/*

   sudo slapadd -F /etc/ldap/slapd.d -n 1 -l data.ldif -w  # cluster
   sudo slapadd -F /etc/ldap/slapd.d -n 1 -l data.ldif     # standalone

   sudo chown openldap:openldap /var/lib/ldap/*
   sudo systemctl start slapd.service

After a while, data should be synchronized between all nodes in the cluster.

Detailed explanation
~~~~~~~~~~~~~~~~~~~~

1. Create a new OpenLDAP server and configure it using DebOps. If it's
   a cluster of servers, make sure that after applying the configuration the
   synchronization happens correctly, for example by adding and removing an
   OpenLDAP object on one host, and noticing it appearing and disappearing on
   the other(s).

2. Select one host as the backup importer. Copy the contents of the main LDAP
   database to it via :command:`scp` to have the data available on the host
   locally.

3. Stop the OpenLDAP service on the host:

   .. code-block:: console

      systemctl stop slapd.service

4. Remove the existing database files in the :file:`/var/lib/ldap/` directory
   and any other auxiliary directories, if you use multiple databases/DITs.

5. Import the backed up LDIF dataset to the OpenLDAP server using the
   :command:`slapadd` command. If you use multiple databases, make sure that
   you use the correct database number during import.

   .. warning::
      If you use a clustered OpenLDAP setup, use the ``-w`` flag to ensure that
      the imported LDAP objects have the correct attributes to override the
      synchronization data from other cluster nodes. Otherwise, the import node
      will have its data wiped after synchronizing with the other cluster
      nodes.

   Import of the main database in clustered setup:

   .. code-block:: console

      slapadd -F /etc/ldap/slapd.d -n 1 -l data.ldif -w

   Import of the main database in standalone setup:

   .. code-block:: console

      slapadd -F /etc/ldap/slapd.d -n 1 -l data.ldif

6. Set the correct UNIX account and UNIX group ownership of the OpenLDAP
   database(s), for example:

   .. code-block:: console

      chown openldap:openldap /var/lib/ldap/*

7. Start the OpenLDAP service:

   .. code-block:: console

      systemctl start slapd.service

  The OpenLDAP cluster should now synchronize new LDAP objects imported into
  the LDAP directory.
