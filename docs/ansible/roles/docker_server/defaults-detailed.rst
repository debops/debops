.. Copyright (C) 2015-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Imre Jonk <mail@imrejonk.nl>
.. Copyright (C) 2015-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.docker_server`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation
and examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _docker_server__ref_configuration:

docker_server__configuration
----------------------------

The ``docker_server__*_configuration`` variables contain the contents of the
:file:`/etc/docker/daemon.json` configuration file in the form of YAML
dictionary entries in a list. These entries are merged into a complete JSON
file during configuration file generation. The :ref:`universal_configuration`
system is used to manage the file contents and can be used to easily set up all
needed Docker configuration options.

Users can read the `Docker documentation`__ about the
:file:`/etc/docker/daemon.json` configuration file to learn more details about
it and what can be set using this file.

.. __: https://docs.docker.com/config/daemon/

Examples
~~~~~~~~

Change the default data directory of the Docker daemon (directory must be
created separately, for example with the :ref:`debops.resources` role):

.. code-block:: yaml

   docker_server__configuration:

     - name: 'rootdir'
       config:
         'data-root': '/srv/data/docker'
       state: 'present'

Set custom `object labels`__ on the Docker daemon:

.. code-block:: yaml

   docker_server__configuration:

     - name: 'custom-labels'
       config:
         'labels':
           - 'com.example.environment=production'
           - 'com.example.storage=extfs'
       state: 'present'

Users can check the :envvar:`docker_server__default_configuration` for the
default configuration options included in the role.

.. __: https://docs.docker.com/config/labels-custom-metadata/

Syntax
~~~~~~

Configuration entries are defined as YAML dictionaries with specific syntax:

``name``
  Required. An identifier for a particular section of the configuration, not
  used otherwise. Entries with the same ``name`` parameter are merged together
  and can affect each other in order of appearance.

``config``
  Required. YAML dictionary with Docker configuration options, which will be
  merged recursively during generation of the :file:`/etc/docker/daemon.json`
  configuration file.

``state``
  Optional. If not specified or ``present``, a given configuration will be
  included in the generated configuration file. If ``absent``, a given
  configuration will not be included in the generated file (this cannot be used
  to remove existing configuration entries if they are specified in an entry
  with a different ``name``). If ``ignore``, a given configuration entry will
  not be evaluated during role execution.
