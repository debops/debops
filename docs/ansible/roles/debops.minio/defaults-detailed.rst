Default variable details
========================

Some of ``debops.minio`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _minio__ref_instances:

minio__instances
----------------

The ``minio__*_instances`` variable define the MinIO service instances, managed
by :command:`systemd`. Each instance can be accessed over its TCP port,
additionally for each instance a corresponding :ref:`debops.nginx`
configuration is generated that allows access to the instance over HTTP via
a subdomain based on its name.

Examples
~~~~~~~~

By default the ``main`` MinIO instance uses shared set of credentials to allow
multiple hosts with the same "tenant". With the configuration below, each host
will have separate set of credentials, and therefore will be owned by
a separate "tenant":

.. code-block:: yaml

   minio__instances:
     - name: 'main'
       standalone: True

Set an environment variable for a given MinIO instance, for example to set the
instance region (variable names are converted to uppercase automatically):

.. code-block:: yaml

   minio__instances:
     - name: 'main'
       environment:
         minio_region: 'us-east-1'

Create additional instances for new tenants:

.. code-block:: yaml

   minio__instances:

     - name: 'tenant1'
       port: 9001

     - name: 'tenant2'
       port: 9002

Configure a MinIO instance as `a NAS gateway`__, with a custom volume mounted
from a remote storage server elsewhere:

.. __: https://docs.min.io/docs/minio-gateway-for-nas.html

.. code-block:: yaml

   minio__volumes:
     - '/shared/nasvol'

   minio__instances:
     - name: 'nas-gw'
       port: 9001
       type: 'gateway'
       minio_options: 'nas'
       volumes: [ '/shared/nasvol' ]

You can find more example configurations in the
:ref:`minio__ref_deployment_guide` documentation page.

Syntax
~~~~~~

The variables are a list, each instance is defined as a YAML dictionary with
specific parameters:

``name``
  Required. The name of a MinIO instance, used in various file paths. Should be
  a short, alphanumeric string without spaces. Configuration entries with the
  same ``name`` parameter are merged together in order of appearance.

  By default the ``name`` parameter is used as the subdomain of the DNS domain
  defined in the :envvar:`minio__domain` variable, on which a given MinIO
  instance can be reached over HTTP, configured in the :command:`nginx`
  service. This can be overridden using the ``fqdn`` parameter.

``port``
  Required. The TCP port on which a given MinIO instance listens for
  connections. Usually the port numbers start from ``9000`` up.

``state``
  Optional. If not defined or ``present``, a given MinIO instance and all
  related configuration will be created on a host. If ``absent``, a MinIO
  instance and related configuration will be removed from the host (data is
  left intact). If ``ignore``, a given configuration entry will not be
  evaluated during role execution.

``bind``
  Optional. A string that defines the IP address on which a given MinIO
  instance should listen for connections, for example ``localhost`` or
  ``192.0.2.1``. If not defined, MinIO will listen for connections on all
  available interfaces.

``allow``
  Optional. A list of IP addresses or CIDR subnets which are allowed to connect
  to a given MinIO instance over its TCP port, managed by the firewall. If not
  specified, connections from anywhere are allowed.

``fqdn``
  Optional. A Fully Qualified Domain Name on which a given MinIO instance can
  be reached, defined in the :command:`nginx` configuration. If not specified,
  a FQDN will be generated automatically, based on the instance ``name``
  parameter and the DNS domain defined in the :envvar:`minio__domain` variable.

``domain`` / ``domains``
  Optional. A string or a list with additional DNS domain for which a given
  MinIO instance supports using subdomains as "bucket" names. The
  :command:`nginx` service will be configured to pass requests on subdomains of
  these DNS domains to a given MinIO instance.

``comment``
  Optional. A string or YAML text block with comments for a given MinIO
  instance, included in the generated :file:`/etc/minio/<name>` configuration
  file.

``type``
  Optional. If not specified or ``server``, the MinIO instance is started in
  the "server" mode, normal operation. If ``gateway``, the MinIO instance is
  started in the "gateway" mode.

``standalone``
  Optional, boolean. If not specified or ``False``, the MinIO instance is
  configured in a "distributed" mode, with the access and secret keys shared
  between instances with the same name on different host nodes. When ``True``,
  a MinIO instance is configured in a "standalone" mode, with each instance
  with the same name using different access and secret keys on different host
  nodes.

``volumes``
  Optional. A string or a list with MinIO "volumes" that store the data. This
  can be either an absolute path to a local filesystem directory, or a
  ``https://`` URL to a MinIO instance with absolute path to a filesystem
  directory, for example ``https://disk.example.org:9000/srv/minio/disk``. See
  :ref:`minio__ref_deployment_guide` for more relevant examples.

  If not specified, a given MinIO instance will use a subdirectory based on its
  ``name`` parameter in the local filesystem :envvar:`minio__volumes_dir`
  directory, by default :file:`/srv/minio/`.

  If the value is set to ``False`` boolean, the ``$MINIO_VOLUMES`` environment
  variable is not set and the volumes are not defined on the command line. This
  might be needed in certain configuration scenarios.

``minio_options``
  Optional. A string with additional :command:`minio` binary options for
  a given MinIO instance. The ``--address`` option is generated automatically
  by the role and should not be specified here.

``access_key``
  Optional. A string which defines the MinIO instance access key, should be an
  alphanumeric string. If not specified, the role will generate a randomized
  access key and store it in the :file:`secret/minio/` directory on the Ansible
  Controller, exact location depending on the instance deployment type
  (distributed or standalone). See :ref:`debops.secret` for more details about
  the :file:`secret/` directory.

``secret_key``
  Optional. A string which defines the MinIO instance secret key, should be an
  randomized string. If not specified, the role will generate a randomized
  secret key and store it in the :file:`secret/minio/` directory on the Ansible
  Controller, exact location depending on the instance deployment type
  (distributed or standalone). See :ref:`debops.secret` for more details about
  the :file:`secret/` directory.

``browser``
  Optional, boolean. If not specified or ``True``, the MinIO web interface is
  enabled on a given MinIO instance. Setting this parameter to ``False``
  disables the web interface access.

``environment``
  Optional. YAML dictionary with key-value pairs that define additional
  environment variables for a given MinIO instance, stored in the
  :file:`/etc/minio/*` configuration files. Variable names are automatically
  converted to uppercase. Values can be either strings or YAML lists which will
  be concatenated using commas.
