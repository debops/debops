Default variable details
========================

Some of ``debops.docker_registry`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _docker_registry__ref_config:

docker_registry__config
-----------------------

The ``docker_registry__*_config`` variables contain configuration for the
Docker Registry service. The Docker Registry uses a YAML configuration file
with multiple level of configuration keys. To allow for better control over the
configuration file contents, the role uses a list of YAML dictionaries with
named entries which are recursively merged during configuration file
generation.

Examples
~~~~~~~~

Switch the Docker Registry to an Amazon Simple Storage Service (S3) backend,
based on the `example configuration`__:

.. __: https://docs.docker.com/registry/storage-drivers/s3/

.. code-block:: yaml

   docker_registry__config:

     # Disable default local filesystem storage
     - name: 'default-storage'
       state: 'absent'

     - name: 'storage-s3'
       config:
         storage:
           s3:
             region: 'us-east-1'
             bucket: 'registry.example.org'
         middleware:
           storage:
             - name: 'cloudfront'
               options:
                 baseurl: 'https://example.cloudfront.net/'
                 privatekey: '/etc/docker/cloudfront/pk-example.pem'
                 keypairid: 'example'

You should also see the :envvar:`docker_registry__original_config` and
:envvar:`docker_registry__default_config` variables for useful configuration
examples.

Syntax
~~~~~~

Each entry in the list is a YAML dictionary with specific parameters:

``name``
  Required. An identifier of this configuration entry, not used otherwise.
  Configuration entries with the same identifier are merged together, entries
  later on the list can affect the earlier ones.

``config``
  Required. An YAML dictionary with Docker Registry configuration options. Each
  ``config`` dictionary will be merged recursively in the final configuration
  file. You have to specify the entire dictionary structure fron the "base" of
  the configuration file. Refer to the `Docker Registry documentation`__ for
  details about supported parameters and their values.

  .. __: https://docs.docker.com/registry/configuration/

``state``
  Optional. If not specified or ``present``, a given configuration entry will
  be included in the final configuration file. If ``absent``, the entry will
  not be included in the final configuration file - this can be used to disable
  configuration entries with specific identifiers. If ``ignore``, a given
  configuration entry will not be evaluated by the role.
