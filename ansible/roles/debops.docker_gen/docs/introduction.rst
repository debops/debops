Introduction
============

`docker-gen`_ can be used to generate configuration files for other services
based on available Docker container metadata.

This role creates a service and configuration to generate :program:`nginx` upstream
service definitions, which can be used by ``debops.nginx`` role to configure
Dockerized services, either local or remote, behind an :program:`nginx` reverse proxy.
Other services and templates might be provided in the future.

.. _docker-gen: https://github.com/jwilder/docker-gen

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.9.0``. To install it, run:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.docker_gen

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
