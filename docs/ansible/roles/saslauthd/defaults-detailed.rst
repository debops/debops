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

``notify``
  Optional. String or a list which contains names of the Ansible handlers to
  notify when a configuration changes. This parameter makes sense only in
  dependent configuration, because the handlers need to be present in a given
  Ansible playbook.

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

``ldap_profile``
  Optional. Name of the :ref:`LDAP profile <saslauthd__ref_ldap_profiles>` to
  use for a given :command:`saslauthd` instance. If not specified, the
  ``global`` profile located in the :file:`/etc/saslauthd.conf` configuration
  file will be used by default. This parameter is only valid with the ``ldap``
  authentication mechanism enabled.

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

.. _saslauthd__ref_ldap_profiles:

saslauthd__ldap_profiles
------------------------

The ``saslauthd__ldap_*_profiles`` variables define a list of "LDAP profiles",
:file:`/etc/saslauthd-*.conf` configuration files which configure the ``ldap``
SASL authentication mechanism. The :command:`saslauthd` service instances can
select a LDAP profile to use, or if not defined, will fall back to the
:file:`/etc/saslauthd.conf` configuration file which is defined in the
``global`` LDAP profile.

Examples
~~~~~~~~

Check the :envvar:`saslauthd__ldap_default_profiles` variable for a set of
default LDAP profiles defined in the role.

The manual for the :file:`/etc/saslauthd.conf` configuration file is not
available in Debian directly. You can find it in the ``cyrus-sasl2-doc`` APT
package, in the :file:`/usr/share/doc/cyrus-sasl2-doc/LDAP_SASLAUTHD.gz` file.

Syntax
~~~~~~

Each LDAP profile definition is a YAML dictionary with specific parameters:

``name``
  Required. The name of the LDAP profile, used in the filename. You can select
  a given LDAP profile in the SASL instance configuration by specifying this
  name in the ``ldap_profile`` parameter.

  Multiple configuration entries with the same ``name`` parameter are merged
  together and can affect each other.

``state``
  Optional. If not specified or ``present``, a given LDAP profile configuration
  file is created on the host. If ``absent``, a given LDAP profile will be
  removed from the host. If ``ignore``, this configuration entry will not be
  evaluated by the role during execution.

``owner``
  Optional. The UNIX account which will be the owner of the generated
  configuration file. If not specified, ``root`` is used by default.

``group``
  Optional. The UNIX group of the generated configuration file. If not
  specified, ``sasl`` is used by default.

``mode``
  Optional. The mode of the generated configuration file. If not specified,
  ``0640`` is used by default.

``raw``
  Optional. String or YAML text block with contents of the
  :file:`/etc/saslauthd.conf` configuration, inserted in the configuration file
  as-is.

``options``
  Optional. If the ``raw`` configuration parameter is not specified, this
  parameter can be used to define the contents of the configuration file.
  The ``options`` parameters from multiple configuration entries with the same
  ``name`` parameter are merged together, and can affect each other.

  The configuration is defined as a list of YAML dictionaries with specific
  parameters:

  ``name``
    The name of the configuration option.

  ``value``
    The value of the configuration option, defined as a string or a YAML list
    which list elements joined by spaces.

  ``state``
    If not specified or ``present``, a given configuration option will be
    present in the generated file. If ``absent``, a given configuration option
    will be removed from the generated file.
