.. Copyright (C) 2022 CipherMail B.V. <https://www.ciphermail.com/>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:


When to use this role
---------------------

WARNING: this role can only manage local, unsecured OpenSearch installations.
This is useful when running it alongside dependent software like Graylog, which
switched from Elasticsearch to OpenSearch due to
`issues with the new Elasticsearch license <https://www.graylog.org/post/graylog-to-add-support-for-opensearch>`_.

If you are not encumbered by Elasticsearch's new license, then please consider
using the :ref:`debops.elasticsearch` role instead.

Installation
------------

This role installs OpenSearch from the release tarball. The PGP signature is
used to verify the tarball. Directories for configuration and logging are
created according to the
`Filesystem Hierarchy Standard <https://refspecs.linuxfoundation.org/fhs.shtml>`_.
The role is able to upgrade your installation automatically, and can configure
OpenSearch, the included JVM, and the systemd service.

Example inventory
-----------------

To deploy OpenSearch, you can add the host to the
``[debops_service_opensearch]`` Ansible inventory group:

.. code-block:: none

   [debops_service_opensearch]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.opensearch`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/opensearch.yml
   :language: yaml
   :lines: 1,5-
