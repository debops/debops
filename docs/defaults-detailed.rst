Default variable details
========================

.. include:: includes/all.rst

Some of ``debops.elasticsearch`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _elasticsearch__ref_plugins:

elasticsearch_plugins
---------------------

List of Elasticsearch plugins to install or delete. Each list element is a YAML
configuration dictionary with the following parameters:

``name``
  Required. Plugin name. E.g. ``com.sksamuel.elasticsearch/elasticsearch-river-redis/1.1.0``

``url``
  Optional. URL pointing to a plugin archive.

``delete``
  Optional. Deletes the plugin.

``config``
  Optional. Plugin configuration snippet.

Example
~~~~~~~

Plugin definition with configuration:

.. code-block:: yaml

    elasticsearch_plugins:
      - name: elasticsearch/elasticsearch-cloud-aws/2.3.0
        config: |
          # cloud-aws configuration
          cloud:
            aws:
              access_key: <your access key>
              secret_key: <your secret key>
            discovery:
              type: ec2
            repositories:
              bucket: <the bucket created in s3>

.. _elasticsearch__ref_libs:

elasticsearch_libs
------------------

List of additional Java libraries to install or delete. Each list element is a
YAML dictionary with the following keys:

``url``
  Required. URL pointing to a Java archive (jar).

``file``
  Optional. Target file name.

``user``
  Optional. User name for HTTP basic authentication.

``pass``
  Optional. Password for HTTP basic authentication

``delete``
  Optional. Deletes the library.
