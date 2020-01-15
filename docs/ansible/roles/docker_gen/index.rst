.. _debops.docker_gen:

debops.docker_gen
=================

`docker-gen`_ generates configuration files for host services to make the
Dockerized services accessible to them.
For example this role can create the required configuation
for publishing a Dockerized web-service via the host's web-server.
The configuration is
based on available Docker container metadata.

This role creates a service and configuration to generate :program:`nginx` upstream
service definitions, which can be used by ``debops.nginx`` role to configure
Dockerized services, either local or remote, behind an :program:`nginx` reverse proxy.
Other services and templates might be provided in the future.

.. _docker-gen: https://github.com/jwilder/docker-gen

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   upgrade

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/docker_gen/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
