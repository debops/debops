.. _saslauthd__ref_defaults_detailed:

Default variable details
========================

some of ``debops.saslauthd`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _saslauthd__ref_instances:

saslauthd__instances
--------------------

The ``saslauthd__*_instances`` variables are used to configure separate
instances of the :command:`saslauthd` daemon for different services. The
variables are merged together in the order defined by the
:envvar:`saslauthd__combined_instances` variable, therefore it's possible to
modify existing instances defined by the role through Ansible inventory.

Each variable is defined as a list of YAML dictionaries with specific
parameters:

``name``
  Required. Name of a given :command:`saslauthd` instance. Used as a suffix of
  the :file:`/etc/default/saslauthd-*` configuration files.

``config_path``
  Required. Absolute path where SASL configuration file will be created.

``socket_path``
  Required. Absolute path to a directory where :command:`saslauthd` UNIX domain
  socket will be placed.

``state``
  Optional. If not specified or ``present``, a given instance will be
  configured. If ``absent``, a given instance will be removed. If ``ignore``,
  a given instance will not be managed by the role.

``group``
  Optional. Ensure that the specified UNIX group is present on the host. This
  might be needed if directories or files should use non-default UNIX groups.
  Only one group can be specified at once.

``system``
  Optional, boolean. If not specified or ``True``, the created UNIX group will
  be a system group with GID < 1000. If ``False``, it will be a normal group
  with GID >= 1000.

The parameters specified next are used and related to the :command:`saslauthd`
daemon configuration files located in :file:`/etc/default/saslauthd-*`:

``start``
  Optional, boolean. If not specified or ``True``, a given instance will be
  automatically started at system boot. if ``False``, it won't be started
  automatically.

``desc``, ``description``
  Optional. A string that describes a given :command:`saslauthd` daemon
  instance in the configuration file.

``mech``, ``mechanism``, ``mechanisms``
  Optional. Specify the authentication mechanism to use by a given
  :command:`saslauthd` instance. If not specified, ``pam`` is used by default.

``mech_options``
  Optional. Custom options defined for a given authorization mechanism.

``threads``
  Optional. Number of process threads to start for a given :command:`saslauthd`
  instance. If not specified, the number of threads will be equal to the number
  of VCPU cores of a given host.

``daemon_options``
  Optional. Additional :command:`saslauthd` daemon options for a given
  instance. If not specified, ``-c`` is added by default.

The following parameters are related to the SASL configuration file generated
for a given instance:

``config_dir_owner``
  Optional. The owner of the directory with the configuration file. If not
  specified, ``root`` is used by default.

``config_dir_group``
  Optional. The primary group of the directory with the configuration file. If
  not specified, ``root`` is used by default.

``config_dir_mode``
  Optional. The permissions of the directory with the configuration file. If
  not specified, ``0755`` is set by default.

``config_owner``
  Optional. The UNIX account which will be the owner of the configuration file.
  If not specified, ``root`` will be the owner.

``config_group``
  Optional. The UNIX group which will be the primary group of the configuration
  file. If not specified, ``sasl`` will be used by default.

``config_mode``
  Optional. The permissions set for the configuration file. If not specified,
  ``0640`` permissions will be set by default.

``config_raw``
  Optional. a string or YAML text block with the SASL configuration which will
  be placed in the configuration file as-is.

These parameters are related to the UNIX socket of a given :command:`saslauthd`
instance:

``socket_owner``
  Optional. The UNIX account which will be set as the owner of the directory
  where the :command:`saslauthd` UNIX socket is located. If not specified,
  ``root`` will be used by default.

``socket_group``
  Optional. The UNIX group which will be set as the primary group of the
  directory with the :command:`saslauthd` UNIX socket. If not specified,
  ``sasl`` will be used by default.

``socket_mode``
  Optional. The permissions of the directory with the :command:`saslauthd` UNIX
  socket. If not specified, ``0710`` will be used by default.

Examples
~~~~~~~~

Modify existing Postfix configuration to connect to a PostgreSQL database:

.. code-block:: yaml

   saslauthd__instances:

     - name: 'smtpd'
       config_raw: |
         pwcheck_method: auxprop
         auxprop_plugin: sql
         mech_list: plain login cram-md5 digest-md5
         sql_engine: pgsql
         sql_hostnames: 127.0.0.1
         sql_user: postfix
         sql_passwd: password
         sql_database: mail
         sql_select: select password from mailboxes where name='%u' and domain='%r' and smtp_enabled=1
