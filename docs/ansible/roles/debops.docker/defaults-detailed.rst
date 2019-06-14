Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.docker`` default variables have more extensive configuration
than simple strings or lists. Here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _docker_ref_networks:

docker__*_networks
------------------

The ``docker__*_networks`` variables define the Docker networks which should be
managed by Ansible. These variables are lists of networks with parameters from
the `Ansible docker_network module`_.

Here are some of the more important parameters:

``item.name``
  Required. The name of the network.

``item.connected``
  Optional. List of container names or IDs to connect to the network.

``item.appends``
  Optional. Set to ``True`` to prevent the removal of a container from the
  network when the container name or ID is removed from the ``item.connected``
  list.

``item.state``
  Optional. If not specified or ``present``, the network will be configured on
  the Docker host. If ``absent``, the network will be removed.

Examples
~~~~~~~~

Create a network:

.. code-block:: yaml

   docker__networks:

     - name: 'debopsnet'
       connected:

         - 'debops1'
         - 'debops2'

Remove a network:

.. code-block:: yaml

   docker__networks:

     - name: 'debopsnet'
       state: 'absent'

.. _docker_ref_registry_accounts:

docker__*_registry_accounts
---------------------------

The ``docker__*_registry_accounts`` variables define the Docker registry
accounts which should be managed by Ansible. These variables are lists of
registry accounts with parameters from the `Ansible docker_login module`_.

Here are some of the more important parameters:

``item.username``
  Required. The username for the registry account.

``item.password``
  Required. The plaintext password for the registry account.

``item.email``
  Optional. The email address for the registry account.

``item.registry_url``
  Optional. The registry URL, defaults to the registry URL of Docker Hub.

``item.state``
  Optional. If not specified or ``present``, the registry account will be
  configured on the Docker host. If ``absent``, the account will be removed.

``item.reauthorize``
  Optional. If ``True``, refresh existing authentication found in the
  configuration file.

Examples
~~~~~~~~

Sign in to Docker Hub:

.. code-block:: yaml

   docker__registry_accounts:

     - username: 'myusername'
       password: 'mypassword'

Sign in to a private GitLab container registry:

.. code-block:: yaml

     docker__registry_accounts:

       - username: 'myusername'
         password: 'mypassword'
         registry_url: 'https://registry.gitlab.{{ ansible_domain }}/'

Sign out of Docker Hub:

.. code-block:: yaml

   docker__registry_accounts:

     - username: 'myusername'
       password: 'mypassword'
       state: 'absent'

.. _docker_ref_containers:

docker__*_containers
--------------------
The ``docker__*_containers`` variables define the Docker containers which
should be managed by Ansible. These variables are lists of registry accounts
with parameters from the `Ansible docker_container module`_.

Here are some of the more important parameters:

``item.name``
  Required. The name of the container.

``item.image``
  Optional. Repository path and tag used to create the container. If the image
  is not found locally or ``item.pull`` is ``True``, the image will be pulled
  from the registry. If no tag is included, 'latest' will be used.

``item.networks``
  Optional. List of networks the container belongs to. See
  `Ansible docker_container module`_ for details about the data structure.

``item.volumes``
  Optional. List of volumes to mount within the container. Use Docker CLI-style
  syntax: ``/host:/container[:mode]``

``item.env``
  Optional. Dictionary of key:value pairs for defining environment variables
  inside the container. Values which might be parsed as numbers, booleans or
  other types by the YAML parser must be quoted (e.g. ``"true"``) in order to
  avoid data loss.

``item.state``
  Optional. Ensure a container is ``absent``, ``present``, ``stopped`` or
  ``started`` (default).

Examples
~~~~~~~~

Spin up a WordPress server, quick and dirty:

.. code-block:: yaml

   docker__networks:

     - name: 'testpress'

   docker__containers:

     - name: 'testpress-db'
       image: 'mariadb:latest'
       networks:
         - name: 'testpress'
       volumes:
         - 'testpress-db:/var/lib/mysql'
       env:
         MYSQL_ROOT_PASSWORD: 'mydbpassword'

     - name: 'testpress'
       image: 'wordpress:latest'
       networks:
         - name: 'testpress'
       published_ports:
         - '80:80'
       volumes:
         - 'testpress:/var/www/html'
       env:
         WORDPRESS_DB_HOST: 'testpress-db'
         WORDPRESS_DB_PASSWORD: 'mydbpassword'
         WORDPRESS_DB_NAME: 'testpress'
