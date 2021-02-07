.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.extrepo`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _extrepo__ref_configuration:

extrepo__configuration
----------------------

These variables define the contents of the :file:`/etc/extrepo/config.yaml`
configuration file. The original file is diverted to preserve its contents and
avoid configuration changes during package upgrades.

Examples
~~~~~~~~

Override the selection of the repository components via Ansibl inventory (the
default is based on the :ref:`debops.apt` local facts):

.. code-block:: yaml

   extrepo__configuration:

     - name: 'policies'
       config:
         enabled_policies: [ 'main', 'contrib', 'non-free' ]

Syntax
~~~~~~

The variables are defined as lists of YAML dictionaries. Each dictionary
defines a part of the final configuration file; configuration entries are
merged together and rendered as a YAML document. Each configuration entry is
defined using specific parameters:

``name``
  Required. An identifier for a particular configuration entry, not used in the
  configuration file itself. Entries with the same ``name`` parameter can be
  overriden by subsequent entries.

``config``
  Required. YAML dictionary with the :command:`extrepo` configuration options.

``state``
  Optional. If not specified or ``present``, a given configuration entry will
  be included in the generated configuration file. If ``absent``, the
  configuration entry will be removed from the generated configuration file. If
  ``ignore``, a given configuration entry will not be considered during
  template generation. This can be used to conditionally enable or disable
  configuration options.


.. _extrepo__ref_sources:

extrepo__sources
----------------

These lists define the names of the external APT sources available using the
:command:`extrepo` command, which should be configured on a host or a group of
hosts. You can see the list of available APT sources by running the
:command:`extrepo search` command on the remote host after the ``extrepo``
package is installed.

Examples
~~~~~~~~

Configure access to the `Debian FastTrack`__ repositories (the official Debian
Backports repository might also be needed, see :ref:`debops.apt` role for
details). In this example we use a simple syntax to specify a list of APT
sources.

.. __: https://fasttrack.debian.net/

.. code-block:: yaml

   extrepo__sources:

     - 'fasttrack'
     - 'fasttrack_backports'

Enable the Elastic APT repository to get access to Elasticsearch, Kibana,
Filebeat and other packages.

.. code-block:: yaml

   extrepo__sources:

     - 'elastic'

Make sure that the upstream Docker APT repository is disabled and enable the
upstream Kubernetes repository.

.. code-block:: yaml

   extrepo__sources:

     - name: 'kubernetes'
       state: 'present'

     - name: 'docker-ce'
       state: 'absent'

Syntax
~~~~~~

You can specify a list of strings which define the names of the APT sources
available via :command:`extrepo`. To see the available APT sources, you can run
the :command:`extrepo search` command.

Alternatively, each list entry can be a YAML dictionary with specific
parameters:

``name``
  Required. Name of the APT source to manage.

``state``
  Optional. If not specified or ``present``, the specified APT source will be
  enabled via the :command:`extrepo` command. If ``absent``, the source file
  located in :file:`/etc/apt/sources.list.d/extrepo_{name}.sources` will be
  removed.
