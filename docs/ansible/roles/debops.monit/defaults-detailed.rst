Default variable details
========================

Some of ``debops.monit`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _monit__ref_config:

monit__config
-------------

The ``monit__*_config`` variables contain the Monit configuration which will be
generated in the :file:`/etc/monit/conf.d/` directory. The configuration stored
in this directory will override configuration defined in the main Monit config
file.

Each entry is a YAML dictionary that defines one configuration file with
specific parameters:

``name``
  Required. Name of the configuration file. This parameter is used as the key
  in the internal configuration dictionary and can be used to override
  configuration entries in the inventory.

``content``
  A string or YAML text block with the contents of the generated configuration
  file. See the :man:`monit(1)` for the Monit configuration syntax that can
  be used here. This parameter can use Jinja template statements for
  conditional configuration.

``weight``
  Optional. If specified, this number will be prepended to the configuration
  file name to aid with order of the configuration files.

``state``
  Optional. If not specified or ``present``, the configuration will be
  generated. If ``absent``, existing configuration will be removed. If
  ``init``, the configuration will be defined, but it won't be generated - this
  can be used to conditionally enable Monit configuration without the need to
  define it entirely. If ``ignore``, a given configuration entry will not be
  processed by the role.

``mode``
  Optional. Set the attributes of the generated configuration file (they are
  set to ``0600`` by default). If the mode ``0600`` is set explicitly, the
  configuration file generation will not be logged by Ansible and diff of the
  file will not be shown, this is useful for files with sensitive data like
  passwords.

``comment``
  Optional. String or YAML text block with additional comments about the
  configuration.

Examples
~~~~~~~~

Check some of the system parameters using Monit:

.. code-block:: yaml

   monit__config:

     - name: 'check_system'
       content: |
         check system example.org
         if loadavg (1min) > 4 for 5 cycles then alert
         if memory usage > 75% for 5 cycles then alert
       weight: 50
