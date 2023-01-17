.. Copyright (C) 2015      Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2017-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variables: configuration
================================

Some of ``debops.dovecot`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.


.. _dovecot__ref_features:

dovecot__features
-----------------

Currently supported features for :envvar:`dovecot__features` are:

``imap``
    ``IMAP4rev2`` (:rfc:`9051`) with explicit ``TLS`` support via ``STARTTLS``,
    typically using port 143.
``imaps``
    ``IMAP4rev2`` with implicit ``TLS`` support, typically using port 993.
``pop3``
    ``POP3`` (:rfc:`1939`, extensions from :rfc:`2449` and authentication
    from :rfc:`1734`) with explicit ``TLS`` support via ``STARTTLS``, typically
    using port 110.
``pop3s``
    ``POP3`` with implicit ``TLS`` support, typically using port 995.
``sieve``
    Support for mail filtering/sorting using ``Sieve`` (:rfc:`5228`) scripts
    and the ``ManageSieve`` protocol (:rfc:`5804`, both with various extensions
    from other RFCs), the latter typically using port 4190. See `Dovecot's
    ManageSieve Documentation`__ for further details.
``quota``
    Support for per-user mail ``quotas``. See
    `Dovecot's Quota Plugin Documentation`__ for further details.
``dsync``
    Support for two-directional/pairwise ``dsync`` synchronization between two
    :command:`dovecot` servers using :command:`dovecot`'s own ``dsync``
    protocol, typically using port 12345. See
    `Dovecot's Replication Documentation`__ for further details.

Note that ``imaps`` and ``pop3s`` (implicit TLS) are recommended
over ``imap`` and ``pop3`` (explicit TLS) by :rfc:`8314`. Furthermore,
LMTP is recommended over LDA by the Dovecot project.

.. __: https://doc.dovecot.org/admin_manual/pigeonhole_managesieve_server/
.. __: https://doc.dovecot.org/configuration_manual/quota_plugin/
.. __: https://doc.dovecot.org/configuration_manual/replication/


.. _dovecot__ref_dsync:

DSync Replication
-----------------

Dovecot supports master/master replication using ``dsync``.  The replication is
done asynchronously, so high latency between the replicas isn't a problem.  The
replication is done by looking at Dovecot index files (not what exists in the
filesystem), so no mails get lost due to filesystem corruption or an accidental
deletion, they will simply be replicated back.

Replication works only between server pairs. Currently dsync is only supported
together with a virtual email user since dsync would need root access
otherwise.

The most important configuration variable is :envvar:`dovecot__dsync_host`,
which needs to be set to point to the other server for each server in a sync
pair. Assuming that you have two servers, named ``mail1.example.com`` and
``mail2.example.com``, setting something like this in your Ansible inventory
should be sufficient:

.. code-block:: yaml

   dovecot__dsync_host: '{{ "mail1.example.com"
                            if ansible_fqdn == "mail2.example.com"
                            else "mail2.example.com" }}'

Other variables are :envvar:`dovecot__dsync_port`,
:envvar:`dovecot__dsync_replica`, :envvar:`dovecot__dsync_password_path` and
:envvar:`dovecot__dsync_password`, but these should all have sensible defaults
for most installations.

For more information, see the Dovecot `Replication
<https://wiki.dovecot.org/Replication>`_ wiki page.


.. _dovecot__ref_user_accounts:

dovecot__user_accounts
----------------------

Currently supported mechanisms for :envvar:`dovecot__user_accounts` are:

``deny``
    Deny access for a statically defined list of users (see
    :envvar:`dovecot__deny_users`).

``system``
    Mail users are Linux system users.

``mysql``
    Mail users are stored in a MySQL/MariaDB database (see
    :ref:`dovecot__ref_sql` below).

``pgsql``
    Mail users are stored in a PostgreSQL database (see
    :ref:`dovecot__ref_sql` below).

``sqlite``
    Mail users are stored in a SQLite database (see
    :ref:`dovecot__ref_sql` below).

``ldap``
    Mail users are stored in the LDAP directory.

``passwdfile``
    Users and passwords are stored in a file.

``checkpassword``
    Users and passwords are stored in an external program.


.. _dovecot__ref_sql:

SQL User Databases
------------------

Users can be stored in an external ``SQL`` database (see
:ref:`dovecot__ref_user_accounts` above). In order to do so, a database-driver
specific connection string needs to be defined in
:envvar:`dovecot__sql_connect`. The parameters are generally provided as a
space-delimited string of ``parameter=value`` pairs (which means that it is not
possible to use spaces in parameters), with the possible parameters defined by
the used database type:

``pgsql``

    ``host``
        The host on which the database server is running.

    ``port``
        The port on which the database server is listening.

    ``user``
        The username to use when connecting to the database.

    ``password``
        The password to use when connecting to the database.

    ``dbname``
        The name of the database to use.

    ``maxconns``
        The number of connections to create to the database (default 5).

``mysql``

    The basic options (``host``, ``port``, ``user``, ``password``, ``dbname``)
    are the same as for ``pgsql``, additional settings include:

    ``client_flags``
        See the MySQL manual.

    ``ssl_ca, ssl_ca_path``
        Set either one or both to enable SSL.

    ``ssl_cert, ssl_key``
        For sending client-side certificates to the server.

    ``ssl_cipher``
        Sets the minimum allowed cipher security (default: HIGH).

    ``ssl_verify_server_cert``
        Verifies that the name in the server SSL certificate matches the host
        (default: no).

    ``option_file``
        Read options from the given file instead of the default :file:`my.cnf`
        location.

    ``option_group``
        Read options from the given group (default: client).

   You can connect to UNIX sockets by using ``host=/var/run/mysql.sock``.

``sqlite``
    Only one parameter is supported - the path to the database file (which
    is defined without the ``parameter=value`` format).

Examples:

.. code-block:: yaml

   # pgsql
   dovecot__sql_connect: 'host=192.168.1.1 dbname=users'
   # mysql
   dovecot__sql_connect: 'host=sql.example.com dbname=virtual user=virtual password=blarg'
   # sqlite
   dovecot__sql_connect: '/etc/dovecot/authdb.sqlite'

The database should have a structure like this:

::

   CREATE TABLE `users` (
     `userid` varchar(128) NOT NULL,
     `domain` varchar(128) NOT NULL,
     `password` varchar(128) NOT NULL,
     `home` varchar(255) NOT NULL,
     `uid` int(11) NOT NULL,
     `gid` int(11) NOT NULL,
     `active` char(1) NOT NULL DEFAULT 'Y',
     `maildir` varchar(255) NOT NULL
   );

Other configuration parameters of interest are
:envvar:`dovecot__sql_default_pass_scheme`,
:envvar:`dovecot__sql_password_query`, :envvar:`dovecot__sql_user_query`, and
:envvar:`dovecot__sql_iterate_query`.


.. _dovecot__ref_configuration:

dovecot__configuration
----------------------

The ``dovecot__*_configuration`` variables define the contents of the
:file:`/etc/dovecot/dovecot.conf` configuration file. The variables are merged
in the order defined by the :envvar:`dovecot__combined_configuration` variable,
which allows modification of the default configuration through the Ansible
inventory.

See the :command:`dovecot` `configuration documentation`__ for details on the
possible configuration parameters.

.. __: https://doc.dovecot.org/settings/


Examples
~~~~~~~~

See :envvar:`dovecot__default_configuration` variable for an example of
existing configuration.

Autosubscribe users to the ``Junk`` mailbox:

.. code-block:: yaml

  dovecot__group_configuration:

    - section: 'mailbox_namespaces'
      options:

        - name: 'namespace inbox'
          options:

            - name: 'mailbox Junk'
              options:

                - name: 'auto'
                  value: 'subscribe'

Rename the ``Junk`` mailbox to ``INBOX.Spam``:

.. code-block:: yaml

  dovecot__group_configuration:

    - section: 'mailbox_namespaces'
      options:

        - name: 'namespace inbox'
          options:

            - name: 'mailbox Junk'
              state: 'absent'

            - name: 'mailbox INBOX.Spam'
              options:

                - name: 'auto'
                  value: 'subscribe'

                - name: 'special_use'
                  value: '\Junk'


.. _dovecot__ref_configuration_syntax:

Syntax
~~~~~~

The variables contain a list of YAML dictionaries, each dictionary can have
the following parameters:

``section``
  Required. Name of the section to create in the
  :file:`/etc/dovecot/dovecot.conf` file. This parameter is used as an
  "anchor", configuration entries with the same ``section`` are combined
  together and affect each other in order of appearance.

``title``
  Optional. A short description of a given configuration ``section``.
  If not defined, the ``section`` name itself will be used.

``state``
  Optional. If not specified or ``present``, the configuration section will be
  generated. If ``hidden``, the section will be generated, but without a
  section header. If ``absent``, ``ignore`` or ``init``, the configuration
  section will not be generated. If ``comment``, the section will be generated
  but commented out.

``weight``
  Optional. A positive or negative number which can be used to affect the order
  of sections in the generated configuration file. Positive numbers add more
  "weight" to the section making it appear "lower" in the file; negative
  numbers subtract the "weight" and therefore move the section upper in the
  file.

``comment``
  Optional. This parameter can be used to provide a short description
  which will be included in the generated configuration file.

``options``
  Required. A list of :command:`dovecot` configuration options for a given
  ``section``.

  Note that the ``options`` parameters can be used recursively to generate
  configuration blocks of arbitrary depth (as illustrated in the example
  above).

  The options can be specified with the following parameters:

  ``name``
    Required. The name of a given :command:`dovecot` configuration option
    for a given ``section``. Options with the same ``section`` and ``name``
    hierarchy will be merged in order of appearance.

  ``option``
    Optional. An alternative to ``name`` to be used as the key in the
    ``key = value`` pairs written to the configuration.

  ``value``
    Either ``value`` or ``options`` is required. This defines the value of a
    given configuration option. It can be either a string, a boolean, a number,
    or a YAML list (elements will be joined with commas).

  ``options``
    Either ``value`` or ``options`` is required. This parameters takes a list
    of configuration sub-options, thus allowing ``options`` to be used
    recursively to generate configuration blocks of arbitrary depth (as
    illustrated in the example above).

  ``raw``
    Optional. String or YAML text block which will be included in the
    configuration file "as is". If this parameter is specified, the ``name``
    and ``value`` parameters are ignored - you need to specify the
    entire line(s) with configuration option names as well.

  ``state``
    Optional. Same values as documented above.

  ``comment``
    Optional. String or YAML text block that contains comments about a given
    configuration option.
