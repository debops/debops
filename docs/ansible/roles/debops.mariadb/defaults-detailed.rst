Default variable details
========================

Some of ``debops.mariadb`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _mariadb__databases:

mariadb__databases
------------------

List of databases that should be present or absent on a given MariaDB server.
Each database is defined as a YAML dict with the following keys:

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
  database (only if it was recently created), and removed afterwards. The role does
  not check if the file exists before copying it, so make sure that it's
  present in the location that you specify beforehand.

``target``
  Optional. Path to a file on the remote host which will be imported to the
  database after it has been created (only once). The role does not check if the
  file exists before trying to import it. You can use the ``source`` parameter to
  specify a file on the Ansible Controller to copy to the ``target`` location
  before import.

``target_delete``
  Optional. If present and ``False``, it will prevent deletion of target file
  on remote host.

``encoding``
  Optional. Encoding mode to use, examples include ``utf8`` or ``latin1_swedish_ci``.

``collation``
  Optional. Collation mode (sorting). This only applies to new table/databases
  and does not update existing ones, this is a limitation of MySQL.

Examples
~~~~~~~~

Create databases, remove some of the existing ones:

.. code-block:: yaml

   mariadb__databases:

     - name: 'database1'

     - name: 'database2'

     - name: 'old_database'
       state: 'absent'

Create a database and import its contents from a file already present on remote
host:

.. code-block:: yaml

   mariadb__databases:

     - name: 'fancy_db'
       target: '/tmp/dbcontents.sql.gz'

Create a database and import its contents from a file on the Ansible Controller:

.. code-block:: yaml

   mariadb__databases:

     - name: 'new_database'
       source: '/tmp/database-contents.sql.gz'
       target: '/tmp/dbcontents.sql.gz'

.. _mariadb__users:

mariadb__users
--------------

List of user accounts that should be present or absent on a given MariaDB
server. Each user account is defined as a dict with a set of keys and values.

User account parameters
~~~~~~~~~~~~~~~~~~~~~~~

``user`` or ``name``
  Required. The "username" part of the user account on the MariaDB server. If
  ``name`` is specified, it will be used to determine the database name for
  granting default privileges, if ``database`` is not specified.

``host``
  Optional. The "hostname" part of the user account on the MariaDB server. If
  not specified, it will be generated automatically by the role (this is
  usually what you want). It specifies the hostname or IP address of the host
  that is allowed to connect to the database.

``password``
  Optional. If specified, the role will set it as the password for the MariaDB
  account. If not present, a random password will be generated automatically
  and stored in the ``secret/`` directory on the Ansible Controller. Refer to the
  :ref:`debops.secret` role for more details.

``state``
  Optional. If ``present``, the account will be created on the database server. If
  ``absent``, account will be removed from the database server.

Database privileges
~~~~~~~~~~~~~~~~~~~

``database``
  Optional. If present, it specifies the database name and/or database prefix
  that a given user account will be able to access using default privileges. If
  not present, ``name`` will be used instead.

``priv_default``
  Optional. By default, the user accounts will get all privileges to databases with
  the same name. If this key is present and ``False``, the users will not get
  default privileges.

``priv_aux``
  Optional. By default, the user accounts will get all privileges to the database
  prefixed with the name of the user account. If this key is present and ``False``,
  the users will not get default prefix privileges.

``priv``
  Optional. String or list of privileges to grant to a given user account. See
  ``mysql_user`` documentation for information about how to specify the
  privileges.

``append_privs``
  Optional. If present and ``True``, specified privileges will be appended to
  already existing privileges (default). If ``False``, specified privileges
  will replace all current privileges for a given user account.

User configuration file
~~~~~~~~~~~~~~~~~~~~~~~

``owner``
  Optional. It should specify a local UNIX account on the host managed by
  the ``debops.mariadb`` role (not on the host with the database, unless it's
  a local installation). If specified, the ``debops.mariadb`` role will create
  a local UNIX account if it doesn't exist with the specified name and create
  a ``~/.my.cnf`` configuration file with the MariaDB account credentials and
  configuration pointing to the MariaDB server.

``group``
  Optional. Main local UNIX group of the created account. If not specified,
  a group named after the account will be created instead.

``home``
  Required if ``item.owner`` is specified. Specifies the home directory of
  given local UNIX account.

``system``
  Optional. If specified and ``True``, the local UNIX group/user account which is going to be created
  will be a "system" account with UID/GID < 1000. If specified and ``False``,
  local UNIX group/user account will be a "normal" account with UID/GID
  >= 1000. By default groups and accounts will be created as "system" accounts.

``mode``
  Optional. If specified, defines the permissions of the ``~/.my.cnf`` configuration
  file. By default they are set to ``0640``.

``creds_path``
  Optional, string. Allows you to change the file path for the credentials file
  which defaults to ``~/.my.cnf``.


Examples
~~~~~~~~

Create a MariaDB user account with all privileges granted to the ``someuser.*`` and
``someuser\_%.*`` databases:

.. code-block:: yaml

   mariadb__users:

     - name: 'someuser'

Create a MariaDB user account with all privileges to ``somedatabase.*``
without auxiliary privileges:

.. code-block:: yaml

   mariadb__users:

     - name: 'someuser'
       database: 'somedatabase'
       priv_aux: False

Create a MariaDB user account and set up a local system account configured to
use MariaDB:

.. code-block:: yaml

   mariadb__users:

     - name: 'someuser'
       owner: 'system-user'
       home: '/var/local/system-user'

Create a MariaDB user account without default privileges:

.. code-block:: yaml

   mariadb__users:

     - name: 'someuser'
       priv_default: False
       priv_aux: False

Create a MariaDB user account with custom additional privileges:

.. code-block:: yaml

   mariadb__users:

     - name: 'someuser'
       priv: [ 'otherdb.*:ALL' ]

.. _mariadb__ref_options:

mariadb__options
----------------

The role uses :file:`/etc/mysql/conf.d/client.cnf` configuration file to manage the
MariaDB/MySQL system-wide client configuration. This configuration file is
generated by a template that uses the :envvar:`mariadb__client_options` variable
to get the configuration data. The configuration itself is split among several
variables located in :file:`defaults/main.yml` file.

A minimal configuration is stored as a YAML dictionary. Keys of the dictionary
as MariaDB configuration option names, and values of the dictionary are the
configuration values. All values are automatically quoted in the generated
configuration file.

Example configuration section:

.. code-block:: yaml

   mariadb__options:
     'query_cache_type': '0'
     'key_buffer': '16M'
     'skip_name_resolve':

The dictionary keys without values will be written in the configuration file
with correct notation.

Alternative configuration notation is to use a YAML list, each element of
a list being a YAML dictionary in the above format. An example:

.. code-block:: yaml

   mariadb__options:

     - 'query_cache_type': '0'
       'key_buffer': '16M'

     - 'skip_name_resolve':

Yet another alternative format can be used if you use certain keys in the YAML
dictionary. The template checks for presence of the ``name`` or ``section``
keys, and if found, changes to a different format that uses YAML dictionary
keys:

``name``
  Required for the main options. Name of the option to add.

``section``
  Required for the definition of a configuration section. Create new section of
  the configuration file, written in square brackets.

``state``
  Optional. Either ``present`` or ``absent``. If not specified or ``present``,
  a given section or option will be added in the configuration file; if
  ``absent``, option or section won't be added.

``comment``
  Optional. Add a comment to a given option or section.

``value``
  Optional for main options. If specified, set a value of a given option.

``options``
  Optional. A YAML dictionary or list of YAML dictionaries with options to
  include in a given section, or multiple options specified together as
  a group. If it's specified, values of ``name`` and ``value`` are ignored.

Examples:

.. code-block:: yaml

   mariadb__options:

     - section: 'client'
       comment: 'Global MariaDB client options'
       options:

         - name: 'skip_name_resolve'

         - name: 'key_buffer'
           value: '16M'

         - name: 'query_cache_type'
           value: '0'
           state: 'present'
