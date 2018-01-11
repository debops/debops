Getting started
===============

``debops.stunnel`` does not create any tunnels by default, they need to be
defined by the user. A natural place for them is usually a host group in
Ansible inventory.

Example inventory
-----------------

As an example, let's create an encrypted tunnel between two hosts, one of which
acts as a MySQL server, and other is a client which connects through the tunnel
to the server.

This is an example Ansible hosts file, located in ``inventory/hosts``. It
defines two host groups::

    [mysql_encrypted_tunnel]
    dbserver
    dbclient

    [debops_mysql]
    dbserver

    [debops_stunnel:children]
    mysql_encrypted_tunnel

in ``inventory/group_vars/mysql_encrypted_tunnel/stunnel.yml`` you should
define your MySQL tunnel connection::

    ---
    stunnel_services:
      - name: 'mysql-ssl-tunnel'

        server_accept:  '3307'
        server_connect: '3306'

        client_accept:  '3306'
        client_connect: 'dbserver:3307'

``debops.stunnel`` will try and select the correct host as a server/client
automatically, using a number of factors. By default all hosts are treated as
clients; if automatic detection of a server fails, you will be able to override
it.

This configuration sets up only ``stunnel4`` service, configuration of the
firewall and TCP wrappers can be performed using additional configuration
parameters. See :doc:`guides` for more details.

Example playbook
----------------

This is an example playbook which can be used to configure ``stunnel`` on all
hosts that use it - they should be present in ``[debops_stunnel]`` group,
either directly or indirectly via a child group::

    ---
    - name: Manage stunnel connections
      hosts: debops_stunnel

      roles:
        - role: debops.stunnel
          tags: stunnel

