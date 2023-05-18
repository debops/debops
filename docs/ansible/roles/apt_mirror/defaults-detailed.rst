.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.apt_mirror`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _apt_mirror__ref_configuration:

apt_mirror__configuration
-------------------------

The ``apt_mirror__*_configuration`` variables define "instances" of
:command:`apt-mirror` configurations. Each instance has its own set of APT
sources to mirror, its own configuration options and its own :command:`cron`
job with a separate frequency. Mirrored repositories are stored under the same
:file:`/var/spool/apt-mirror/mirror/` directory and care should be taken to
avoid conflicts.

Examples
~~~~~~~~

Enable APT mirror of Debian Stable repository in the default configuration
(make sure that the space requirements are met before enabling this).
See :envvar:`apt_mirror__default_configuration` variable for the initial options:

.. code-block:: yaml

   apt_mirror__configuration:

     - name: 'default'
       sources:

         - name: 'debian-stable'
           state: 'present'

Add an APT mirror for `InfluxData`__ and `Zabbix`__ APT repositories in the
default configuration:

.. __: https://www.influxdata.com/blog/package-repository-for-linux/
.. __: https://www.zabbix.com/download

.. code-block:: yaml

   apt_mirror__configuration:

     - name: 'default'
       sources:

         - name: 'influxdata'
           raw: 'deb https://repos.influxdata.com/debian stable main'

         - name: 'zabbix'
           type: 'deb'
           uri: 'https://repo.zabbix.com/zabbix/6.4/debian'
           suite: '{{ ansible_distribution_release }}'
           components: [ 'main', 'contrib', 'non-free' ]

         - name: 'influxdata-clean'
           type: 'clean'
           uri: 'https://repos.influxdata.com/debian'

         - name: 'zabbix-clean'
           type: 'clean'
           uri: 'https://repo.zabbix.com/zabbix/6.4/debian'

Create a new APT mirror instance with private APT repositories synchronized
hourly using :command:`cron` service:

.. code-block:: yaml

   apt_mirror__configuration:

     - name: 'internal'
       cron_time: '@hourly'
       sources:

         - name: 'apt-repo'
           type: 'deb'
           uri: 'https://username:password@apt.example.org/debian'
           suite: 'stable'
           components: [ 'main' ]

         - name: 'clean-apt-repo'
           type: 'clean'
           uri: 'https://apt.example.org/debian'

Syntax
~~~~~~

The variables are defined as a list of YAML dictionaires, parsed using
:ref:`universal_configuration` system. Each dictionary defines an "instance"
using specific parameters:

``name``
  Required. An identifier for a particular :command:`apt-mirror` instance. The
  value is used in the filesystem paths and should be a simple alphanumeric
  string. Configuration entries with the same ``name`` parameters are merged
  during role execution and can affect each other via
  :ref:`universal_configuration` principles.

``filename``
  Optional. Name of the :command:`apt-mirror` configuration file to use,
  located under the :file:`/etc/apt/` directory. If not specified, the
  configuration files are named in the format: :file:`mirror.<name>.list`.

``state``
  Optional. If not specified or ``present``, a given APT mirror instance will
  be configured on the host. If ``absent``, the mirror will not be configured
  and the configuration file will be removed. If ``ignore``, a given
  configuration entry will not be evaluated during role execution.

``cron_time``
  Optional. The string which defines a time period for a given APT mirror
  synchronization, in the :man:`crontab(5)` format. If not specified, the value
  of the :envvar:`apt_mirror__cron_time` will be used instead.

``cron_user``
  Optional. The UNIX account under which a :command:`cron` job will be executed
  for a particular APT mirror. If not specified, the value in the
  :envvar:`apt_mirror__user` will be used by default.

``cron_command``
  Optional. The :command:`cron` job which should be executed for a given APT
  mirror. If not specified, the configuration template will automatically
  generate a configuration suitable for sequential :command:`apt-mirror`
  operation (the script does not support parallel processing).

``options``
  Optional. List of YAML dictionaries which defines :command:`apt-mirror`
  configuration options stored in the mirror configuration file. The
  ``options`` parameters from configuration entries with the same ``name``
  parameter are merged together and can affect each other. A set of default
  options is taken from the :envvar:`apt_mirror__default_options` as a base,
  user options are merged on top of it.

  The configuration is defined as a list of YAML dictionaries, each dictionary
  key being the option name and its value being the option value. Alternatively
  you can use specific parameters to control each option:

  ``name``
    The name of the option.

  ``value``
    The value of the option, can be a number or a string.

  ``state``
    If not specified or ``present``, the option is included in the
    configuration file. If ``absent``, the option will be removed from the
    configuration file. If ``comment``, the option will be present but it will
    be commented out. If ``dynamic``, the value of a given option will be
    replaced with a value set at runtime in the configuration template
    (currently only the ``var_path`` option utilizes this functionality).

  ``comment``
    String or YAML text block with comments related to a given configuration
    option.

``sources``
  Required. A list of APT repositories which will be mirrored by the
  :command:`apt-mirror` script. THe ``sources`` parameters from configuration
  entries with the same ``name`` parameter are merged together and can affect
  each other.

  The list is defined using YAML dictionaries:

  ``name``
    An identifier of a given APT repository, used only internally by the role.
    Multiple sources with the same ``name`` are merged together and can affect
    each other.

  ``raw``
    String specifying an APT repository in the :man:`sources.list(5)`
    one-line-style format, included in the generated configuration file as-is.
    If this parameter is specified, it takes precedence over the parametrized
    configuration below.

  ``type``
    Specify the APT repository type (``deb``, ``deb-src``, ``deb-<arch>`` for
    additional architecture mirrors, or ``clean`` to generate a cleanup script
    for a given repository).

  ``uri``
    Specify the URL of the APT repository to mirror or clean.

  ``suite``
    Specify the repository suite which should be mirrored (this is usually
    named ``stable``, or a specific distribution release like ``bookworm`` or
    ``bullseye``).

  ``component`` / ``components``
    A string (first version) or a YAML list (second version) of repository
    components to mirror (this is usually ``main``, ``contrib``, ``non-free``
    in Debian case, Ubuntu usually uses ``main``, ``restricted``, ``universe``,
    ``multiverse`` components).

  ``state``
    If not specified or ``present``, a given source will be present in the
    generated configuration file. If ``absent``, a given source will be omitted
    from the generated configuration file. If ``ignore``, a given configuration
    entry will not be evaluated during role execution. If ``comment``, the
    source will be present but commented out.

  ``weight``
    A positive or negative integer which will affect the order of the sources in
    the generated configuration file. Positive weight pushes a given source
    down the list, negative weight lifts it up the list.

  ``comment``
    String or YAML text block with comments related to a given source.
