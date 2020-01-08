Introduction
============

`Nginx <https://nginx.org/>`_ is a fast and light webserver with extensible
configuration.

The ``debops.nginx`` role can be used to install and manage `nginx` configuration
for multiple websites at the same time. The server is configured using
inventory variables. This role can also be used as a dependency of another role
to configure a webserver for that role using dependency variables.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.5``. To install it, run::

    ansible-galaxy install debops.nginx

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
