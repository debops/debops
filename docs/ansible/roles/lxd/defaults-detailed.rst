.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.lxd`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _lxd__ref_preseed:

lxd__preseed
------------

The ``lxd__*_preseed`` variables define a set of LXD "preseed" configuration
entries which are merged into one YAML document and passed to the :command:`lxd
init --preseed` command via stdin on first installation. These configuration
entries can be used to configure various aspects of the LXD environment, like
network interfaces, storage pools, clustered operation, profiles, and so on.

You can read the `Non-interactive configuration via preseed YAML`__ LXD
documentation page for more details about the preseeding process.

.. __: https://lxd.readthedocs.io/en/latest/preseed/

Examples
~~~~~~~~

See the :envvar:`lxd__default_preseed` for the default configuration entries
used to initialize the LXD service.

To see the current LXD configuration on a host, you can run the command:

.. code-block:: console

   lxd init --dump

This will print out the configuration in a YAML format which can then be split
into separate configuration entires and put under the ``seed`` parameters.

To re-apply the preseed configuration via Ansible you can execute the command:

.. code-block:: console

   debops service/lxd -l <host> -t role::lxd:init -e 'lxd__init_preseed=true'

This will re-run the command and apply the current preseed configuration again.

Syntax
~~~~~~

The preseed is defined using lists of YAML dictionaries, each dictionary
defines a configuration entry using specific paraneters:

``name``
  Required. A string that identifies a configuration entry, not used otherwise.
  Multiple configuration entries with the same ``name`` parameter are merged
  together, overriding the ``seed`` parameter each time - this can be used to
  replace specific configuration entry in the Ansible inventory.

``seed``
  Required. YAML dictionary with the contents of the preseed configuration.
  After the final list of configuration entries is generated, contents of the
  ``seed`` parameters are combined recursively using the Ansible ``combine()``
  filter. This can be used to override specific YAML keys in the preseed via
  different configuration entries.

``state``
  Optional. If not specified or ``present``, a given configuration entry will
  be included in the final preseed document. If ``absent``, a given
  configuration entry will not be included in the YAML document. If ``ignore``,
  a given configuration entry will not be evaluated by the role during
  execution.
