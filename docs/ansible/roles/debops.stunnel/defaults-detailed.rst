Default variables: configuration
================================

some of ``debops.stunnel`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 2

.. _stunnel_services:

stunnel_services
----------------

This is a list of ``stunnel`` tunnel connections, each one defined as a YAML
dict. Each "service" can define either one end of a connection, or both ends at
once, when used in an Ansible group. Additional parameters can also be
specified for other roles, such as firewall configuration, TCP wrappers
configuration and registering a service in ``/etc/services`` database.

stunnel parameters
~~~~~~~~~~~~~~~~~~

These parameters are related to ``stunnel`` itself.

``name``
  String, required. Defines a name of the tunnel, which is used as the name of
  the configuration file and service name in ``/etc/services`` as well as
  daemon name in TCP wrappers.

  You should use only letters, numbers and a dash (``-``) character. You should
  pick an unique name for each service, preferably unique across your entire
  infrastructure. Check ``getent services`` database to avoid collisions with
  existing names.

``client_accept``
  String, optional. This parameter defines on what interface(s) and port this
  service will listen to for server connections. You should specify either
  a service port name or port number, which optional IP address on which to
  listen to.

  By default, ``stunnel`` binds to IPv4 connections only, to listen to IPv6
  connections as well, specify the port as ``:::<port>``.

  You need to define either ``client_accept`` or ``client_port`` in a service
  definition for ``stunnel`` to be configured correctly.

``client_connect``
  String or dict or list, optional. This key defines where a ``stunnel`` client
  will connect to. It can have 3 forms:

  - string: ``'<hostname>:<port>'`` or ``'<ip address>:<port>'`` or ``'<port>'``

  - dict: ``{ '<hostname>': '<port>', '<ip address>': '<port>' }``

  - list: ``[ '<hostname>', '<ip address>' ]``

  You can can use the string format if you have only one host you want to
  connect, or you want to connect to a local port.

  Dict format can be used to connect to multiple hosts with different ports.

  List format is useful when you need to connect to multiple hosts on the same
  port. The port is taken automatically either from ``server_accept`` key or
  ``server_port`` key, if present.

``client_port``
  String, optional. This key defines the port name or port number of the
  ``stunnel`` client. It can be used by the ``server_connect`` key (as a list)
  in case that ``client_accept`` is not specified, to specify the port number
  to which the ``stunnel`` server should connect.

  You need to define either ``client_port`` or ``client_accept`` in a service
  definition for ``stunnel`` to be configured correctly.

``client_options``
  Text block, optional. Add other options on the client side of the ``stunnel``
  configuration, in the form of a YAML text block.

``server_accept``
  String, optional. This parameter defines on what interface(s) and port this
  service will listen to for client connections. You should specify either
  a service port name or port number, which optional IP address on which to
  listen to.

  By default, ``stunnel`` binds to IPv4 connections only, to listen to IPv6
  connections as well, specify the port as ``:::<port>``.

  You need to define either ``server_accept`` or ``server_port`` in a service
  definition for ``stunnel`` to be configured correctly.

``server_connect``
  String or dict or list, optional. This key defines where a ``stunnel`` server
  will connect to. It can have 3 forms:

  - string: ``'<hostname>:<port>'`` or ``'<ip address>:<port>'`` or ``'<port>'``

  - dict: ``{ '<hostname>': '<port>', '<ip address>': '<port>' }``

  - list: ``[ '<hostname>', '<ip address>' ]``

  You can can use the string format if you have only one host you want to
  connect, or you want to connect to a local port.

  Dict format can be used to connect to multiple hosts with different ports.

  List format is useful when you need to connect to multiple hosts on the same
  port. The port is taken automatically either from ``client_accept`` key or
  ``client_port`` key, if present.

``server_port``
  String, optional. This key defines the port name or port number of the
  ``stunnel`` server. It can be used by the ``client_connect`` key (as a list)
  in case that ``server_accept`` is not specified, to specify the port number
  to which the ``stunnel`` client should connect.

  You need to define either ``server_port`` or ``server_accept`` in a service
  definition for ``stunnel`` to be configured correctly.

``server_options``
  Text block, optional. Add other options on the server side of the ``stunnel``
  configuration, in the form of a YAML text block.

``ssl_opts``
  List, optional. SSL options for ``stunnel`` configuration. Will override the
  defaults.

/etc/services parameters
~~~~~~~~~~~~~~~~~~~~~~~~

If you want to, you can assign a user-friendly name to a client port number
(server port number is probably already present, for example ``3306``
= ``mysql``). To do that, you can use :ref:`debops.etc_services` Ansible role,
which manages ``/etc/services`` database.

In the future the services database might be converted from the local files to
a central LDAP database. Because of that it's suggested that you use unique
port numbers and service names across your entire infrastructure.

.. _debops.etc_services: https://github.com/debops/ansible-etc_services/

``port``
  String, optional. This parameter is the port number which you want to reserve
  for the particular tunnel connection. Service name will be taken from the
  ``name`` parameter. Both TCP as well as UDP service name will be reserved.

  When you specify this parameter, the ``/etc/services`` support is activated
  using role dependencies. After that, you can use the service name in place of
  all client ports, in ``server_accept``, ``server_port`` and
  ``client_connect`` parameters, as well as the firewall configuration
  (``dport`` parameter).

``comment``
  String, optional. A comment with short description will be added in the
  ``/etc/services`` database, as well as in the TCP wrappers
  ``/etc/hosts.allow`` file.

ferm (iptables/ip6tables) parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, ``debops.stunnel`` role does not configure the firewall to enable
access to the server port from the outside. To do that, you can add the
parameters below to the tunnel definition. :ref:`debops.ferm` role will be used to
configure the ``iptables``/``ip6tables`` firewall using ``ferm``.

Firewall configuration will be performed on all hosts by default. To only
configure firewall on the server hosts (``stunnel`` clients do not require it),
look below for the ``enabled`` parameter.

.. _debops.ferm: https://github.com/debops/ansible-ferm/

``type``
  String, optional. Enables the firewall configuration support and specifies
  the rule type to use. See the ``debops.ferm`` role for available rule types.
  Usually, ``dport_accept`` is the correct choice.

  The type of the firewall rule to use will affect the keys used, so choose the
  rule carefully to avoid unintended effects.

``dport``
  List, optional. Specify port numbers or service names to configure in the
  firewall. You can use the service name if ``/etc/services`` support has been
  enabled (see above).

``saddr``
  List, optional. Specify list of hostnames, IP addresses or CIDR networks
  which are allowed to connect to specified ports. If it's not specified, no
  connections are allowed, unless ``accept_any`` parameter is enabled (see
  below).

  This list is similar to ``client`` list, but they are not fully compatible.

TCP wrappers parameters
~~~~~~~~~~~~~~~~~~~~~~~

``stunnel`` uses TCP wrappers on Debian to secure connections from remote
hosts. By default, ``debops.stunnel`` role does not configure TCP wrapper
entries in ``/etc/hosts.allow``, but you can do that by adding the parameters
below. :ref:`debops.tcpwrappers` role will be used to configure
``/etc/hosts.allow`` entries.

TCP wrappers configuration will be performed on all hosts by default. To only
configure host access on the server hosts (``stunnel`` clients do not require
it), look below for the ``enabled`` parameter.

.. _debops.tcpwrappers: https://github.com/debops/ansible-tcpwrappers/

``daemon``
  String, optional. Enables configuration of TCP wrappers. Name of the "daemon"
  that TCP wrappers will allow/deny connections to. Should be the same as
  ``name`` parameter.

``client``
  List, optional. Specify list of IP addresses, CIDR networks or domain names
  of hosts which are allowed to connect to the ``stunnel`` server. If no hosts
  are specified, TCP wrappers will deny remote connections from anywhere unless
  ``accept_any`` parameter is enabled (see below).

  This list is similar to ``saddr`` list, but they are not fully compatible.

Shared firewall & TCP wrappers parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some of the parameters are shared between firewall (``debops.ferm``) and TCP
wrappers (``debops.tcpwrappers``) roles.

``accept_any``
  Boolean, optional. Enable or disable access to the ``stunnel`` server from
  any host or network. Useful if you have a separate firewall in front of your
  servers or want to allow connections from anywhere to a particular service.

``enabled``
  List, optional. By default TCP wrappers and firewall are configured on all
  hosts - clients and servers alike, it's how Ansible works.

  To only configure firewall and TCP wrappers on the server side of ``stunnel``
  connections, you can use the ``enabled`` parameter as a list. Specify a list
  of ``stunnel`` servers, either hostnames or FQDN names, and intersect it with
  ``stunnel_server_addresses`` list. For example::

      tunnel_servers: [ 'hostname' ]
      stunnel_services:
        - name: 'tunnel'
          enabled: '{{ tunnel_servers | intersect(stunnel_server_addresses) }}'

  Relevant roles will still generate the necessary configuration files, but on
  the client hosts, the resulting list will be empty, disabling the firewall
  and TCP wrappers configuration. On server hosts, it will be not empty, and
  configuration will be enabled.

Other parameters
~~~~~~~~~~~~~~~~

``filename``
  String, optional. Will influence the filename of generated configuration
  files in all roles, which by default is based on the ``name`` parameter.

``weight``
  String, optional. This is a 2-digit number added at the beginning of the
  filename in some roles, which helps in ordering of the configuration files.

``other parameters``
  You can add other parameters from default variables by dropping the
  ``stunnel_`` prefix from the variable name. For example::

      stunnel_services:
        - name: 'tunnel'
          pki_realm: 'domain'

