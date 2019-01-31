Default variable details
========================

Some of ``debops.rsyslog`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _rsyslog__capabilities:

rsyslog__capabilities
---------------------

The default configuration provided in the ``debops.rsyslog`` role supports
a few different usage scenarios. To make it easier to enable them as needed,
a separate list of "capabilities" is checked by Ansible to see if specific
keywords are present; this allows for easy selection of different operation
modes.

With the empty list of capabilities, the ``debops.rsyslog`` role should
configure a local syslog server which stores the logs in a standard set of
files located in :file:`/var/log/` directory.

The different capabilities that can be enabled in the list:

``network``
  Enable support for receiving the logs over the network, via UDP or TCP
  connections. By default you also need to specify the CIDR subnets or IP
  addresses which are allowed through the firewall using :envvar:`rsyslog__allow`,
  :envvar:`rsyslog__group_allow` and/or :envvar:`rsyslog__host_allow` variables.

``remote-files``
  Enable storage of remote logs as files in :file:`/var/log/remote/` directory. If
  this is not enabled, by default remote logs will be discarded due to being
  directed to a separate ``remote`` ruleset.

``tls``
  Enable support for TLS connections to the ``rsyslog`` server, both as
  a forwarder and as a receiver. This option depends on availability of X.509
  certificates managed by :ref:`debops.pki` role.

``xconsole``
  Enable log output to :file:`/dev/xconsole`. The ``rsyslogd`` daemon needs to run
  in privileged mode, or additional steps need to be taken to allow access to
  the :file:`/dev/xconsole` by the ``rsyslogd`` unprivileged user.

``!mark``
  Disable the periodic ``-- MARK --`` messages in the logs, by default they
  will be emitted every hour.

``!news``
  Disable storage of the ``news.*`` logs to separate log files.

.. _rsyslog__forward:

rsyslog__forward
----------------

The :envvar:`rsyslog__forward`, :envvar:`rsyslog__group_forward` and
:envvar:`rsyslog__host_forward` variables are lists used to define forwarding rules
for ``rsyslog``. Because the daemon configuration is ordered, the forward
statements should be set in a specific place in the configuration. You can of
course define your own forwarding rules instead of using these specific
variables, if you wish.

You can check `the rsyslog remote forward documentation <http://www.rsyslog.com/sending-messages-to-a-remote-syslog-server/>`_ to see
how to forward logs to other hosts. Each configuration entry should be
specified in a separate YAML list element. Some examples:

Forward all logs over UDP to remote log server:

.. code-block:: yaml

   rsyslog__forward:
     - '*.* @logs.example.org'

Forward logs to different hosts over TCP:

.. code-block:: yaml

   rsyslog__forward:
     - 'mail.* @@mail-logs.example.org'
     - '*.*;mail.none @@no-mail-logs.example.org'

Forward logs over TCP with TLS encryption using default configuration:

.. code-block:: yaml

   # Enable TLS encryption
   rsyslog__capabilities: [ 'tls' ]

   # Forward logs over TLS
   rsyslog__forward: [ '*.* @@logs.example.org:6514' ]

.. _rsyslog__rules:

rsyslog__rules
--------------

The ``rsyslog`` configuration is defined in YAML dictionaries. The role uses
a simple set of keys and values to allow conditional activation or deactivation
of parts of the ``rsyslogd`` configuration. Each configuration section will be
defined in a separate file located in :file:`/etc/rsyslog.d/` directory. List of
known parameters:

``divert``
  Optional, boolean. If specified and ``True``, ``debops.rsyslog`` will use the
  :command:`dpkg-divert` command to move specified originaL configuration file out of
  the way before generating the configuration from a template. This parameter
  can be used to modify the ``rsyslogd`` configuration provided by the system
  packages. It should only be used with the ``filename`` parameter, otherwise
  there might be unforeseen consequences.

``divert_to``
  Optional. If the ``divert`` parameter is enabled, using this parameter you can
  specify the filename to divert the file to. The diversion will be confined to
  :file:`/etc/rsyslog.d/` directory. This can be used to change the order of the
  configuration files if needed.

``filename``
  Optional. Full name of the file in which to store the given configuration. If
  not specified, ``debops.rsyslog`` will generate a filename based on a set of
  alternative parameters.

``type``
  Optional. Specify the type of the configuration a given entry defines. This
  will be mapped to :envvar:`rsyslog__weight_map` variable to a "weight" number
  which will determine ordering of the configuration files in
  :file:`/etc/rsyslog.d/`.

``name``
  Optional. Specify custom name of the configuration file, appended to the
  "weight" number.

``suffix``
  A custom "extension" added after the dot to the generated filename; different
  suffixes are included in different parts of the configuration. If not
  specified, ``.conf`` will be used by default.

``sections``
  Optional. This is a list of YAML dictionaries with configuration definition
  which should be included in the given file. If this option is present, some
  of the known parameters on the main level are ignored, and only configuration
  in the ``sections`` list will be set in the configuration file.

The parameters below can be used in the main list or in the ``sections`` list:

``comment``
  Optional. A comment added at the beginning of the file.

``options``
  Required. YAML text block which contains the ``rsyslogd`` configuration

``state``
  Optional. Either ``present`` or ``absent``. If undefined or ``present``
  a given configuration file or configuration section will be present, if
  ``absent``, given configuration file or section will be removed. This
  parameter can be used to conditionally enable or disable parts of the
  configuration.

You can see many examples of the rules in :file:`defaults/main.yml` file of the
``debops.rsyslog`` role.

.. _rsyslog__conf_additional_templates:

rsyslog__conf_additional_templates
----------------------------------

This list defines additional rsyslog templates. 

Each additional template can have following parameters, some of them are
mandatory.

``name```
  Name of the template. Required.

``comment``
  Comment to the template, which you want to see on the top of the
  template file. Optional.

``options``
  Text block with value mapping specified in the template format, check
  rsyslog documentation or examples if not sure about syntax. Required.

``state``
  If this parameter is defined and ``absent``, template file will be removed
  from the rsyslog configuration. Optional.

Example of a template definition:

.. code-block:: yaml

   rsyslog__conf_additional_templates:
     - name: "RemoteServiceNewsLog"
       comment: "Very interesting news!"
       options: |
         type="string"
         string="/var/log/remote/services/news/news.log"
