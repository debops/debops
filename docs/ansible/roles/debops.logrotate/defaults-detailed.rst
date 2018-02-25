Default variable details
========================

Some of ``debops.logrotate`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _logrotate__config:

logrotate__config
-----------------

This is a list of YAML dictionaries, each dictionary defines a file with one or
more sections that configure the ``logrotate`` service. The same syntax can be
used to configure log files in :file:`/etc/logrotate.conf` as well as separate
configuration files in :file:`/etc/logrotate.d/`. The configuration uses the
following keys:

``filename``
  Name of the configuration file located in :file:`/etc/logrotate.d/`. This
  parameter is ignored in the main configuration file.

``divert``
  Boolean, optional. When specified and ``True``, the original configuration
  file will be diverted using :man:`dpkg-divert(8)`. If a configuration file is
  due to be removed, the original file will be reverted back into place.

``sections``
  Optional. List of YAML dictionaries that define the multiple log
  configuration sections in a single configuration file.

The following configuration parameters can be specified either in the main YAML
dictionary or in separate sections.

``state``
  Optional. If specified and ``absent``, role will remove the specified
  configuration file, and if diversion is enabled with above boolean, the
  original configuration file will be reverted back into place.

  This parameter can also be used to disable or enable individual configuration
  sections when multiple sections are used in one configuration file.

``log`` or ``logs``
  Optional. String or a list of strings that define log filenames or shell glob
  patterns which specify what logs should be rotated. If it's not specified,
  options will be added as common options for all subsequent entries.

``options``
  YAML text block with ``logrotate`` options to include in a particular
  configuration section which override default log rotation options.

``firstaction``, ``prerotate``, ``postrotate``, ``lastaction``, ``preremove``
  Optional. A set of YAML text blocks which allow you to specify the respective
  scripts separately from the ``item.options`` configuration. You don't need to
  add the ``endscript`` command at the end of the scripts, the role will do
  that automatically.

Examples
~~~~~~~~

Add custom common options for all logs:

.. code-block:: yaml

   logrotate__config:

     - filename: '00archive-by-mail'
       comment: 'Send deleted logs to archive'
       options: |
         mail log-archive@example.org

Configure log rotation for a custom log file:

.. code-block:: yaml

   logrotate__config:

     - filename: 'custom-log'
       log: '/var/log/custom.log'
       state: 'present'
       options: |
         rotate 12
         monthly
         compress
         missingok
         notifempty

Change options of stock :command:`apt` log rotation configuration, with original
configuration diverted to a different file:

.. code-block:: yaml

   logrotate__config:

     - filename: 'apt'
       divert: True
       sections:

         - logs: [ '/var/log/apt/term.log' ]
           options: |
             rotate 24
             monthly
             compress
             missingok
             notifempty
           postrotate: |
             apt-get update

         - logs: [ '/var/log/apt/history.log' ]
           options: |
             rotate 24
             monthly
             compress
             missingok
             notifempty
