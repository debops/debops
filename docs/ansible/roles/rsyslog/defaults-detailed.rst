.. Copyright (C) 2015-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.rsyslog`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _rsyslog__ref_forward:

rsyslog__forward
----------------

The :envvar:`rsyslog__default_forward`, :envvar:`rsyslog__forward`,
:envvar:`rsyslog__group_forward` and :envvar:`rsyslog__host_forward` variables
are lists used to define forwarding rules for :command:`rsyslog`. Because the
daemon configuration is ordered, the forward statements should be set in
a specific place in the configuration. You can of course define your own
forwarding rules instead of using these specific variables, if you wish.

You can check `the rsyslog remote forward documentation <https://www.rsyslog.com/sending-messages-to-a-remote-syslog-server/>`_ to see
how to forward logs to other hosts. Each configuration entry should be
specified in a separate YAML list element. The entries can be simple FQDN
hostnames which will be configured to use TCP connections over TLS and port
``6514``; alternatively you can define more detailed configuration using
specific parameters:

``selector``
  What type of logs to forward to another server, by default ``*.*`` (all
  facilities, all priorities).

``target``
  The FQDN of the syslog server where logs will be forwarded.

``port``
  The port to which ``rsyslog`` will connect, by default ``6514``.

``protocol``
  The protocol which should be used for connections, by default ``tcp``.

``resume_retry_count``
  Number of times ``rsyslog`` should try to reconnect to the syslog server when
  connection is lost, by default ``100``.

``queue_type``
  The type of the internal queue to use for this server, by default ``linkedList``.

``queue_size``
  The size of the message queue, by default ``10000``.


.. _rsyslog__ref_configuration:

rsyslog__configuration
----------------------

The ``rsyslog__*_configuration`` variables define the contents of the
:file:`/etc/rsyslog.conf` configuration file. This is the main
:command:`rsyslog` configuration, additional config snippets can be found in
the :file:`/etc/rsyslog.d/` directory, which can be managed using the
:ref:`rsyslog__ref_rules` variables.

Examples
~~~~~~~~

Enable kernel log input module in :command:`rsyslog` service:

.. code-block:: yaml

   rsyslog__configuration:

     - name: 'module_imklog'
       raw: |
         module(load="imklog")

Other examples can be found in the :envvar:`rsyslog__original_configuration`
default variable. The :envvar:`rsyslog__default_configuration` contains changes
to the original options applied by the role.

Syntax
~~~~~~

The variables are lists of YAML dictionaries with specific parameters:

``name``
  Required. An identification of the configuration entry, not used otherwise.
  Multiple configuration entries with the same ``name`` parameter are merged
  together; this can be used to modify already defined entries.

``state``
  Optional. If not defined or ``present``, a given configuration entry will be
  present in the generated config file. If ``absent``, the entry will not be
  included in the configuration file. If ``comment``, the entry will be
  present, but commented out. If ``ignore``, a given configuration entry will
  not be evaluated during role execution.

``comment``
  Optional. String or a YAML text block with additional comments about a given
  configuration entry, included in the generated file.

``raw``
  Optional. String or YAML text block with the :manpage:`rsyslog.conf(5)`
  configuration options or `RainerScript definitions`__, included in the
  generated file as-is.

  .. __: https://www.rsyslog.com/doc/v8-stable/rainerscript/index.html

``section``
  Optional. Specify the configuration section in which a given entry should be
  included. The sections are defined using the
  :ref:`rsyslog__ref_configuration_sections` variables; the default sections
  available are: ``modules``, ``global``, ``templates``, ``output``, ``rules``
  and ``unknown``. If the section is not defined, the entry will be added to
  the ``unknown`` section.


.. _rsyslog__ref_configuration_sections:

rsyslog__configuration_sections
-------------------------------

The ``rsyslog__*_configuration_sections`` variables define what sections are
present in the :file:`/etc/rsyslog.conf` configuration file. Sections will be
included in the file in the order they appear in the configuration variables.

The default set of configuration sections, defined in the
:envvar:`rsyslog__default_configuration_sections` variable, is based on the
recommendations from the :manpage:`rsyslog.conf(5)` manual page.

Examples
~~~~~~~~

Define a section with a custom title:

.. code-block:: yaml

   rsyslog__configuration_sections:

     - name: 'custom_section'
       title: 'Example configuration'

Syntax
~~~~~~

Each configuration entry is a YAML dictionary with specific parameters:

``name``
  Required. The name of the section, used in the ``section`` parameter of the
  :file:`/etc/rsyslog.conf` configuration. Multiple entries with the same
  ``name`` parameter are merged together.

``title``
  Optional. This parameter can be used to override the section name which is
  used in the generated configuration file.

``state``
  Optional. If not specified or ``present``, a given section will be included
  in the generated configuration file. If ``absent``, the section will not be
  included in the file. If ``ignore``, a given configuration entry will not be
  evaluated during role execution. If ``hidden``, the section's title comment
  will be hidden in the generated configuration file.

``weight``
  Optional. A positive or negative number which can be used to affect the order
  of sections in the generated configuration file. Positive numbers add more
  "weight" to the section making it appear "lower" in the file; negative
  numbers substract the "weight" and therefore move the section upper in the
  file.


.. _rsyslog__ref_rules:

rsyslog__rules
--------------

The ``rsyslog__*_rules`` variables define the configuration stored in the
:file:`/etc/rsyslog.d/` directory. Configuration files in the directory can be
named with different "extensions", each one imported at different point in the
:file:`/etc/rsyslog.conf` configuration file. The supported extensions are:
``.module``, ``.template``, ``.conf``, ``.output``, ``.ruleset``, ``.remote``.

Examples
~~~~~~~~

See the :envvar:`rsyslog__default_rules` variable for example configurations.

Syntax
~~~~~~

Each configuration file is described using YAML dictionaries with specific parameters:

``name``
  Required. Name of the configuration file in the :file:`/etc/rsyslog.d/`
  directory. Multiple configuration entries with the same ``name`` parameter
  will be merged together.

``divert``
  Optional, boolean. If specified and ``True``, the :ref:`debops.rsyslog` role
  will use the :command:`dpkg-divert` command to move specified originaL
  configuration file out of the way before generating the configuration from
  a template. This parameter can be used to modify the ``rsyslogd``
  configuration provided by the system packages.

``divert_to``
  Optional. If the ``divert`` parameter is enabled, using this parameter you can
  specify the filename to divert the file to. The diversion will be confined to
  :file:`/etc/rsyslog.d/` directory. This can be used to change the order of the
  packaged configuration files if needed.

``comment``
  Optional. A comment added at the beginning of the file.

``raw``
  A string or YAML text block with the :man:`rsyslog.conf(5)` configuration,
  included in the generated config files as-is.

``state``
  Optional. Either ``present`` or ``absent``. If undefined or ``present``
  a given configuration file present, if ``absent``, given configuration file
  will be removed. If ``ignore``, a given configuration entry will not be
  evaluated during execution. This parameter can be used to conditionally
  enable or disable parts of the configuration.

``options``
  Optional. This is a list of YAML dictionaries with configuration definition
  which should be included in the given file. If the ``raw`` parameter is
  present on the file level, the ``options`` list is ignored.

  Each configuration entry in the ``options`` list needs to be defined as
  a YAML dictionary with parameters:

  ``name``
    Required. An identifier for a particular section of the configuration file,
    not used otherwise. The options with the same ``name`` parameter from
    different configuration file entries are merged together.

  ``comment``
    Optional. A comment added at the beginning of a given section.

  ``raw``
    A string or YAML text block with the :man:`rsyslog.conf(5)` configuration,
    included in the generated config file section as-is.

  ``state``
    Optional. Either ``present`` or ``absent``. If undefined or ``present``
    a given configuration file or configuration section will be present, if
    ``absent``, given configuration file or section will be removed. This
    parameter can be used to conditionally enable or disable parts of the
    configuration.
