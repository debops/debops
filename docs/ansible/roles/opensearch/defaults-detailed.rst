.. Copyright (C) 2022 CipherMail B.V. <https://www.ciphermail.com/>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of the ``debops.opensearch`` default variables have more extensive
configuration than simple strings or lists. Here you can find documentation and
examples for them.


.. _opensearch__configuration:

opensearch__configuration
-------------------------

The ``opensearch__*_configuration`` variables define the OpenSearch
configuration options that are set in the
:file:`/etc/opensearch/opensearch.yml` configuration file. For example:

.. code-block:: yaml

   opensearch__configuration:

     - name: 'cluster.name'
       value: 'example-cluster'

     - name: 'node.name'
       comment: 'My first node'
       value: 'node-1'

Each configuration entry is a list item containing a YAML dictionary. These
parameters are supported:

``name``
  String, mandatory. The name of the OpenSearch configuration entry.

``value``
  String, mandatory. The value of the OpenSearch configuration entry. Can be a
  string, an integer, a boolean or a list.

``comment``
  String or YAML text block, optional. A comment added to the configuration
  entry.

``state``
  String, optional. If not specified or ``present``, the entry will be included
  in the configuration file. If ``absent``, the entry will not be included.
