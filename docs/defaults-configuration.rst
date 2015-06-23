Default variables: configuration
================================

some of ``debops.mariadb`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _mariadb_databases:

mariadb_databases
-----------------

List of databases that should be present or absent on a given MariaDB server.
Each database is defined as a YAML dict with following keys:

``database`` or ``name``
  Name of the database, required. Should be composed from alphanumeric
  characters and underscore (``_``) only. Max length: 16 for MySQL databases,
  80 for MariaDB databases.

``state``
  Optional. If value is ``present``, database will be created; if ``absent``,
  database will be removed.

``source``
  Optional. Path to a file with SQL dump on the Ansible Controller, which will
  be copied to the remote host at the ``target`` location, imported into
  database (only if it was recently created), and removed afterwards. Role does
  not check if the file exists before copying it, so make sure that it's
  present in the location that you specify beforehand.

``target``
  Optional. Path to a file on remote host which will be imported to the
  database after it has been created (only once). Role does not check if the
  file exists before trying to import it. You can use ``source`` parameter to
  specify a file on the Ansible Controller to copy to the ``target`` location
  before import.

``target_delete``
  Optional. If present and ``False``, it will prevent deletion of target file
  on remote host.

Examples
~~~~~~~~

Create databases, remove some of the existing ones::

    mysql_databases:

      - name: 'database1'

      - name: 'database2'

      - name: 'old_database'
        state: 'absent'

Create a database and import its contents from file already present on remote
host::

    mysql_databases:

      - name: 'fancy_db'
        target: '/tmp/dbcontents.sql.gz'

Create a database and import its contents from file on Ansible Controller::

    mysql_databases:

      - name: 'new_database'
        source: '/tmp/database-contents.sql.gz'
        target: '/tmp/dbcontents.sql.gz'

.. _mariadb_users:

mariadb_users
-------------

List of user accounts that should be present or absent on a given MariaDB
server. Each user account is defined as a dict with a set of keys and values.

User account parameters
~~~~~~~~~~~~~~~~~~~~~~~

``user`` or ``name``
  The "username" part of the user account on the MariaDB server, required. If
  ``name`` is specified, it will be used to determine the database name for
  setting default privileges, if ``database`` is not specified.

``host``
  Optional. The "hostname" part of the user account on the MariaDB server. If
  not specified, it will be generated automatically by the role (this is
  usually what you want). It specifies the hostname or IP address of the host
  that is allowed to connect to the database.

``password``
  Optional. If specified, the role will set it as the password for the MariaDB
  account. If not present, a random password will be generated automatically
  and stored in ``secret/`` directory on the Ansible Controller. See
  ``debops.secret`` role for more details.

``state``
  Optional. If ``present``, account will be created on the database server. If
  ``absent``, account will be removed from the database server.

Database privileges
~~~~~~~~~~~~~~~~~~~

``database``
  Optional. If present, it specifies the database name and / or database prefix
  that a given user account will be able to access using default privileges. If
  not present, ``name`` will be used instead.

``priv_default``
  Optional. By default, user accounts will get all privileges to databases with
  the same name. If this key is present and ``False``, users will not get
  default privileges.

``priv_aux``
  Optional. By default, user accounts will get all privileges to database
  prefixed with the name of user account. If this key is present and ``False``,
  users will not get default prefix privileges.

``priv``
  Optional. String or list of privileges to grant to a given user account. See
  ``mysql_user`` documentation for information about how to spefcify the
  privileges.

``append_privs``
  Optional. If present and ``True``, specified privileges will be appended to
  already existing privileges (default). If ``False``, specified privileges
  will replace all current privileges for a given user account.

User configuration file
~~~~~~~~~~~~~~~~~~~~~~~

``owner``
  Optional. It should specify a local UNIX account on the host managed by
  ``debops.mariadb`` role (not on the host with the database, unless it's
  a local installation). If specified, ``debops.mariadb`` role will create
  a local UNIX account if it doesn't exist with specified name and create
  a ``~/.my.cnf`` configuration file with MariaDB account credentials and
  configuration pointing to the MariaDB server.

``group``
  Optional. Main local UNIX group of the created account. If not specified,
  a group named after the account will be created instead.

``home``
  Required if ``item.owner`` is specified. Specifies the home directory of
  given local UNIX account.

``system``
  Optional. If specified and ``True``, created local UNIX group/user account
  will be a "system" account with UID/GID < 1000. If specified and ``False``,
  created local UNIX group/user account will be a "normal" account with UID/GID
  >= 1000. By default created groups and accounts are "system" accounts.

``mode``
  Optional. If specified, defines the attributes of ``~/.my.cnf`` configuration
  file. By default they are set to ``0640``.

Examples
~~~~~~~~

Create a MariaDB user account with all privileges to ``someuser.*`` and
``someuser\_%.*`` databases::

    mariadb_users:

      - name: 'someuser'

Creata a MariaDB user account with all privileges to ``somedatabase.*``
without auxiliary privileges::

    mariadb_users:

      - name: 'someuser'
        database: 'somedatabase'
        priv_aux: False

Create a MariaDB user account and set up local system account with
configuration file::

    mariadb_users:

      - name: 'someuser'
        owner: 'system-user'
        home: '/var/local/system-user'

Creata a MariaDB user account without default privileges::

    mariadb_users:

      - name: 'someuser'
        priv_default: False
        priv_aux: False

Create a MariaDB user account with custom additional privileges::

    mariadb_users:

      - name: 'someuser'
        priv: [ 'otherdb.*:ALL' ]

