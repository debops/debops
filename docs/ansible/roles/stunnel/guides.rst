Guides and examples
===================

.. contents::
   :local:

Example MySQL tunnel
--------------------

This is an extended example of the MySQL tunnel defined in the Getting Started
section. In addition to the ``stunnel4`` configuration, ``debops.stunnel`` will
also configure firewall and TCP wrappers to allow connections from a specified
network

``inventory/hosts``::

    [mysql_encrypted_tunnel]
    dbserver
    dbclient

    [debops_mysql]
    dbserver

    [debops_stunnel:children]
    mysql_encrypted_tunnel

``inventory/group_vars/mysql_encrypted_tunnel/stunnel.yml``::

    ---
    inventory_mysql_tunnel_network: [ '2002:db8::/48', '192.0.2.0/24' ]
    inventory_mysql_hosts: [ 'dbserver' ]

    stunnel_services:
      - name: 'mysql-ssl-tunnel'

        # Register this client port in /etc/services
        port: '3307'

        # stunnel configuration
        server_accept:  ':::mysql-ssl-tunnel'
        server_connect: 'mysql'

        client_accept:  'mysql'
        client_connect: '{{ inventory_mysql_hosts }}'

        # Firewall configuration
        type: 'dport_accept'
        dport: [ 'mysql-ssl-tunnel' ]
        saddr: '{{ inventory_mysql_tunnel_network }}'

        # TCP wrappers configuration
        daemon: 'mysql-ssl-tunnel'
        client: '{{ inventory_mysql_tunnel_network }}'

        # Configure firewall and TCP wrappers only on
        # the server side of the tunnel
        enabled: '{{ inventory_mysql_hosts | intersect(stunnel_server_addresses) }}'

Multiple tunnels at once
------------------------

You can have multiple ``stunnel`` tunnels at the same time, by configuring them
in separate dict variables and adding them in the main list::

    stunnel_tunnel1:
      name: 'tunnel1'

    stunnel_tunnel2:
      name: 'tunnel2'

    stunnel_services:
      - '{{ stunnel_tunnel1 }}'
      - '{{ stunnel_tunnel2 }}'

Configure tunnels separately on each host
-----------------------------------------

If you don't want to, or can't use ``group_vars/`` to configure tunnels on
multiple hosts at once, you can still do this one host at a time::

    # on host1:
    stunnel_services:
      - name: 'tunnel'
        client_accept: '3306'
        client_connect: 'host2:3307'

    # on host2:
    stunnel_services:
      - name: 'tunnel'
        server_accept: ':::3307'
        server_connect: '3306'

        # Firewall
        type: 'dport_accept'
        dport: [ '3307' ]

        # TCP wrappers
        daemon: 'tunnel'

        # Accept connections from anywhere
        accept_any: True

