.. Copyright (C) 2022 CipherMail B.V. <https://www.ciphermail.com/>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

`OpenSearch <https://www.opensearch.org/>`_ is a fork of the popular
distributed search engine and storage system Elasticsearch (see
:ref:`debops.elasticsearch`). Some software vendors, for example Graylog, have
switched to OpenSearch because of legal concerns regarding the Server Side
Public License under which Elasticsearch is nowadays released.

The ``debops.opensearch`` role only implements a subsection of the features
supported by :ref:`debops.elasticsearch`. The role is currently only suitable
for setting up a local OpenSearch instance without TLS support.
