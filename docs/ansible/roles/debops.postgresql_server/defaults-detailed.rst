Default variable details
========================

Some of ``debops.postgresql_server`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _postgresql_server__ref_preferred_version:

postgresql_server__preferred_version
------------------------------------

By default the role installs the PostgreSQL version preferred by the APT
package manager. This behaviour is influenced by how the PostgreSQL is packaged
in Debian - each version has its own set of packages with the version as
a suffix, and there's a set of metapackages which depend on the version
available in the distribution (by default only 1 version is available).

Multiple PostgreSQL versions become available after enabling the upstream APT
repository. To choose a different version than the default one, you need to set
two variables in the inventory:

:envvar:`postgresql_server__preferred_version`
  The value of this variable should be set as the version of the PostgreSQL you
  wish the role to manage (it does not influence the APT packages the role
  installs, but what version is used in different file/directory paths managed
  by the role, what features are enabled/disabled in the configuration, etc.).

:envvar:`postgresql_server__base_packages`
  This is a list of APT packages which will be used by the role to install
  PostgreSQL. By default, it contains the metapackages which install the
  highest available version of PostgreSQL packages. To select a different
  version, you need to change the list of packages.

For example, to install PostgreSQL 9.3 instead of the default available
version, in inventory you need to define:

.. code-block:: yaml

   postgresql_server__upstream: True
   postgresql_server__preferred_version: '9.3'
   postgresql_server__base_packages:
     - 'postgresql-9.3'
     - 'postgresql-client-9.3'
     - 'postgresql-contrib-9.3'

Remember that role does not support management of multiple PostgreSQL versions
at the same time. The above variables should be defined in the inventory at all
times, otherwise role might revert to the default PostgreSQL packages and
version, and break your installation. This also is true for server upgrades.
The preferred way to make an upgrade is to configure a new database server with
desired PostgreSQL version and move the database to it.

You might also need to set similar set of variables for the
:ref:`debops.postgresql` role to keep both of the roles in sync. Refer to its
documentation for details.

.. _postgresql_server__ref_hba:

postgresql_server__hba_*
------------------------

`Host-Based Authentication <http://www.postgresql.org/docs/9.4/static/auth-pg-hba-conf.html>`_
configuration in ``debops.postgresql_server`` Ansible role is specified in
a set of lists:

- :envvar:`postgresql_server__hba_system`: controls the local and remote access to the
  database administrator role ``postgres``.

- :envvar:`postgresql_server__hba_replication`: control access to ``replication`` role
  and database.

- :envvar:`postgresql_server__hba_public`: controls access for public connections to
  ``postgres`` database, to allow certain applications like ``phpPgAdmin`` to
  work correctly.

- :envvar:`postgresql_server__hba_trusted`: control access by local UNIX accounts to
  certain roles/databases without the requirement to specify a password.

- :envvar:`postgresql_server__hba_local`: controls access to the databases by local
  UNIX accounts.

- :envvar:`postgresql_server__hba_remote`: controls access to the database by remote
  clients.

Each PostgreSQL cluster by default uses all of the above lists in its
:file:`pg_hba.conf` configuration file. A cluster can disable any list by
specifying its abbreviated name as a parameter with ``False``. For example:

.. code-block:: yaml

   postgresql_server__cluster_main:
     name: 'main'
     port: '5432'
     hba_replication: False
     hba_public: False
     hba_trusted: False
     hba_local: False
     hba_remote: False

Above configuration will disable connections by trusted users (all users will
be required to specify a password) and from remote clients.

Additionally, each cluster can specify its own HBA entries using ``item.hba``
parameter which will be added at the end of the :file:`pg_hba.conf` file. By
disabling selected global lists and adding custom entries you can redefine the
HBA configuration file as needed. Example:

.. code-block:: yaml

   postgresql_server__cluster_main:
     name: 'main'
     port: '5432'
     hba_remote: False

     hba:
       - comment: 'Custom remote entries'
         type: 'hostssl'
         database: 'all'
         user: 'all'
         address: [ '192.0.2.0/24' ]
         method: 'md5'

Each entry in a HBA list is a YAML dictionary with parameters:

``comment``
  Optional. Comment added to a given entry in :file:`pg_hba.conf` file.

``type``
  Required. Specifies connection type to use for a given entry. Known types are:

  - ``local``: local connections by UNIX accounts

  - ``host``: remote TCP connections, either with or without SSL

  - ``hostssl``: remote TCP connections, SSL is required

  - ``hostnossl``: remote TCP connections, plaintext is required

``database``
  Required. String or a list of database names that are controlled by a given
  HBA entry. You can use special names:

  - ``all``: all databases in a cluster

  - ``sameuser``: database with the same name as the PostgreSQL role

  - ``samerole``: all databases accessible by a given PostgreSQL role

  - ``@name``: file with a list of database names, relative to a given
    cluster's configuration directory in :file:`/etc`

``user``
  Required. String or a list of PostgreSQL roles that are controlled by a given
  HBA entry. You can use special names:

  - ``all``: all roles in on the PostgreSQL cluster

  - ``+role``: a specified role and all roles that are included in it

  - ``@name``: file with a list of roles, relative to a given cluster's
    configuration directory in :file:`/etc`

  - ``*postgres*``: a custom ``debops.postgresql_server`` name, it will be
    replaced by the UNIX system account name that manages a given cluster,
    usually ``postgres``

``address``
  Required by all types other than ``local``. A string or list of IP addresses
  or CIDR networks (``debops.postgresql_server`` does not support ip/netmask
  notation). You can use special names:

  - ``all``: any network clients

  - ``samenet``: any IP address from a subnet the host is directly connected to

``method``
  Required. Authentication method used by this HBA entry. You most likely
  either want ``peer`` for local connections or ``md5`` for remote connections.
  There are also other methods available, see the PostgreSQL documentation for
  information about how to use them.

``options``
  Optional. List of additional options specific to a given authentication
  method.

You can find different examples of how to defined HBA lists in
:file:`defaults/main.yml` file of ``debops.postgresql_server`` role.

.. _postgresql_server__ref_ident:

postgresql_server__ident_*
--------------------------

`Ident maps
<http://www.postgresql.org/docs/9.4/static/auth-username-maps.html>`_ stored in
:file:`pg_ident.conf` configuration file is used to map local UNIX accounts to
PostgreSQL roles. This can be used to control what UNIX accounts can login to
the PostgreSQL server as a given role.

Ident maps should only be used by the local UNIX accounts with the ``peer``
authentication method. Using them for ``ident`` method with remote clients is
unreliable and discouraged - ``ident`` protocol is not meant to be used for
authentication or authorization.

By default, PostgreSQL clusters managed by the ``debops.postgresql_server``
role use global lists of ident maps:

- :envvar:`postgresql_server__ident_system`: a user mapping which specifies which
  system users can login as the ``postgres`` superuser role.

- :envvar:`postgresql_server__ident_trusted`: this user mapping can be used with the
  "trusted" HBA list to specify which local UNIX accounts can login without
  specifying a password. It's not set by default.

- :envvar:`postgresql_server__ident_local`: this user mapping can be used to define
  local UNIX accounts globally for all clusters. It's not set by default.

Above ident maps can be disabled in a given cluster by specifying their
abbreviated names in a parameter with ``False`` value. Example:

.. code-block:: yaml

   postgresql_server__cluster_main:
     name: 'main'
     port: '5432'
     ident_trusted: False
     ident_local: False

You can specify custom lists of ident maps in a PostgreSQL cluster configuration:

.. code-block:: yaml

   postgresql_server__cluster_main:
     name: 'main'
     port: '5432'
     ident_local: False

     ident:
       - map: 'main_local'
         user: [ 'user1', 'user2' ]
         role: 'role1'

Each ident map entry is a YAML dictionary with parameters:

``map``
  Required. Name of the user map, can be repeated in different entries.

``user``
  Required. String or list of UNIX user accounts to use in this map. You can
  use a regexp to specify accounts in various ways, see PostgreSQL
  documentation for more information.

  Special string ``*postgres*`` will be replaced by Ansible to the owner of the
  PostgreSQL cluster, usually ``postgres``.

``role``
  Optional. String or list of PostgreSQL roles to map to the UNIX accounts.

  If defined, specifies the PostgreSQL role to map to a given UNIX accounts.

  If not defined, each entry role name will be the same as the UNIX account
  name. Don't use this option with regexp user entries.

  Special string ``*postgres*`` will be replaced by Ansible to the owner of the
  PostgreSQL cluster, usually ``postgres``.

Examples can be found in the :file:`defaults/main.yml` file of the
``debops.postgresql_server`` Ansible role.

.. _postgresql_server__ref_clusters:

postgresql_server__clusters
---------------------------

On Debian and its derivatives, `PostgreSQL installation <https://wiki.debian.org/PostgreSql>`_
is based around "clusters", each cluster being run on a particular PostgreSQL
version and on a specific TCP port. ``debops.postgresql_server`` is designed
to be used within that system, and allows you to create separate PostgreSQL
clusters. A default ``<version>/main`` cluster will be created, based on
default PostgreSQL version installed on a given host.

You can create and manage separate PostgreSQL clusters using
:envvar:`postgresql_server__clusters` list. Each cluster is defined as a YAML dict
with at least two parameters - ``name`` and ``port``. You should take care to
always use separate port for each cluster you define. Role will create an entry
for each cluster in :file:`/etc/services` as well as maintain firewall
configuration as needed.

Some of the global variables defined in ``debops.postgresql_server`` concerning
clusters can be overridden on a cluster by cluster basis using their abbreviated
names (without ``postgresql_server__`` prefix) as cluster parameters. In
addition, **almost all of the PostgreSQL parameters found in the
:file:`postgresql.conf` configuration file can be specified as cluster parameters
as well, to change the defaults**.

Each cluster configuration directory contains the :file:`conf.d/` subdirectory
where you can put :file:`postgresql.conf` configuration snippets; file names
should end with ``.conf`` extension. These files will be included in the main
:file:`postgresql.conf` configuration file and can be used to override the
database configuration.

List of some of the parameters that you can specify in a cluster configuration
entry:

``name``
  Required. Name of the cluster, used to separate different clusters based on
  the same PostgreSQL version.

``port``
  Required. TCP port to use for a given cluster. Default PostgreSQL port is
  ``5432``, more clusters usually use the next port number available.

``version``
  Optional. PostgreSQL version to use for a given cluster. If it's not
  specified, default detected version will be used, which is usually what you
  want.

``environment``
  Optional. Dictionary which specifies environment variables and their values
  that should be set for a given PostgreSQL cluster. Example::

      postgresql_server__cluster_main:
        name: 'main'
        port: '5432'

        environment:
          HOME: '/var/lib/postgresql'
          SHELL: '/bin/bash'

``listen_addresses``
  List of network interfaces specified by their addresses a given cluster
  should bind to. If not set, global value of
  :envvar:`postgresql_server__listen_addresses` will be used instead.

``allow``
  List of IP addresses or CIDR subnets which should be allowed to connect to
  a given cluster.

``standby``
  Optional.
  Configure `standby replication <https://www.postgresql.org/docs/current/warm-standby.html>`_
  cluster parameters. This cluster will act as a streaming replication standby server. The
  replication master configuration can be done using standard :file:`postgresql.conf`
  configuration parameters. Standby configuration parameters:

  ``conninfo``
    Required. Connection info (as a PostgreSQL connection string) to connect to the
    master cluster.

  ``slot_name``
    Optional. Replication slot name to use.

  Example standby configuration:

  .. code-block:: yaml

     postgresql_server__cluster_main:
       name: 'main'
       port: '5432'

       hot_standby: 'on'
       standby:
         conninfo: 'host=postgresql-master user=replication password=XXXX'
         slot_name: 'my_hot_standby'

  Example master configuration:

  .. code-block:: yaml

     postgresql_server__cluster_main:
       name: 'main'
       port: '5432'

       max_replication_slots: 1
       # Set to 2 to allow for 1 "hanging" connection until it times out
       max_wal_senders: 2
       wal_level: 'replica'

     # Create replication user
     postgresql__roles:
       - name: 'replication'
         flags:
           - 'REPLICATION'
           - 'LOGIN'
