Default variable details
========================

Some of ``debops.radvd`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _radvd__ref_interfaces:

radvd__interfaces
-----------------

The ``radvd__*_interfaces`` variables contain the :command:`radvd` interface
configuration. Each entry represents one interface in the form of a YAML
dictionary with specific parameters:

``name``
  Required. The name of the network interface to configure. This parameter is
  used to merge multiple interface configurations with the same name together.

``comment``
  Optional. String or a YAML text block with comments about a particular
  interface.

``state``
  Optional. If not specified or ``present``, the interface configuration will
  ge included in the :file:`/etc/radvd.conf` configuration file. If ``absent``,
  the configuration will be removed from the configuration file.

  If ``init``, a given entry will be prepared but not actually included in the
  finished configuration, this can be used to prepare interface configuration
  and activate it conditionally.

  If ``ignore``, a given entry will not be taken into account during
  configuration file generation.

``options``
  Optional. List with :man:`radvd.conf(5)` interface specific options. Each
  list entry is a YAML dictionary. You can use a simple form, where
  a dictionary key is an option name, and the dictionary value is its value
  (use YAML booleans as ``on``/``off`` values):

  .. code-block:: yaml

     radvd__interfaces:
       - name: 'eth1'
         options:

           - 'AdvSendAdvert': True
           - 'IgnoreIfMissing': True

  You can also use an extended form of configuration options with parameters:

  ``name``
    The name of a given option.

  ``value``
    The value of a given option.

  ``state``
    If not specified or ``present``, the option will be included in the
    configuration file; if ``absent``, the option will be removed from the
    configuration file.

  Example:

  .. code-block:: yaml

     radvd__interfaces:
       - name: 'eth1'
         options:

           - name: 'AdvSendAdvert'
             value: True

           - name: 'IgnoreIfMissing'
             value: True

  The ``options`` parameters from multiple configuration entries with the same
  name are merged together.

``prefix`` or ``prefixes``
  Optional. List of IPv6 subnets to advertise on this interface. You can
  specify either a simple string, or a YAML dictionary with specific options:

  ``name``
    The prefix to manage on this network interface.

  ``state``
    If not specified or ``present``, the prefix will be included in the
    configuration. If ``absent``, prefix will be removed from the
    configuration.

  ``options``
    Custom :file:`radvd.conf` options for a given prefix. The format is the
    same as the ``options`` parameter of the interface configuration.

  Example:

  .. code-block:: yaml

     radvd__interfaces:
       - name: 'eth1'
         prefixes:

           - '2001:db8:aaa::/64'

           - name: '2001:db8:bbb::/64'
             options:
               - 'AdvOnLink': True
               - 'AdvAutonomous': True

  The ``prefix`` or ``prefixes`` parameters from multiple configuration entries
  with the same name are NOT merged together.

``client`` or ``clients``
  Optional. List of client IPv6 link-local addresses which will be sent
  advertisements (if not specified, advertisements are sent to all hosts on the
  local network). You can specify either strings of IPv6 addresses, or use YAML
  dictionary with specific parameters:

  ``name``
    The IPv6 link-local address of the client.

  ``state``
    If not specified or ``present``, the client will be included in the
    configuration. If ``absent``, the client will be removed from the
    configuration.

  Example:

  .. code-block:: yaml

     radvd__interfaces:
       - name: 'eth1'
         clients:

           - 'fe80::21f:16ff:fe06:3aab'

           - name: 'fe80::21d:72ff:fe96:aaff'
             state: 'present'

  The ``client`` or ``clients`` parameters from multiple configuration entries
  with the same name are NOT merged together.

``route`` or ``routes``
  Optional. List of IPv6 routes to advertise on this interface. You can specify
  either a simple string, or a YAML dictionary with specific options:

  ``name``
    The route to manage on this network interface.

  ``state``
    If not specified or ``present``, the route will be included in the
    configuration. If ``absent``, route will be removed from the
    configuration.

  ``options``
    Custom :file:`radvd.conf` options for a given route. The format is the
    same as the ``options`` parameter of the interface configuration.

  Example:

  .. code-block:: yaml

     radvd__interfaces:
       - name: 'eth1'
         routes:

           - '2001:db8:ccc::/64'

           - name: '2001:db8:ddd::/64'
             options:
               - 'AdvRoutePreference': 'low'
               - 'RemoveRoute': True

  The ``route`` or ``routes`` parameters from multiple configuration entries
  with the same name are NOT merged together.

``rdnss``
  Optional. List of IPv6 nameservers to advertise to the clients. You can
  specify the addresses as simple strings or use a YAML dictionary with
  specific parameters:

  ``name``
    The IPv6 address of the nameserver.

  ``state``
    If not specified or ``present``, the nameserver will be included in the
    configuration. If ``absent``, nameserver will be removed from the
    configuration.

  Example:

  .. code-block:: yaml

     radvd__interfaces:
       - name: 'eth1'
         rdnss:

           - '2001:db8::53'

           - name: '2001:db8::5353'
             state: 'present'

  The ``rdnss`` parameters from multiple configuration entries with the same
  name are NOT merged together.

``rdnss_options``
  Optional. Specify custom RDNSS options. The format is the same as the
  ``options`` parameter of the interface configuration. The ``rdnss_options``
  parameters from multiple configuration entries with the same name are NOT
  merged together.

``dnssl``
  Optional. List of DNS search domains to advertise to the clients. You can
  specify the search domains as simple strings or use a YAML dictionary with
  specific parameters:

  ``name``
    The DNS search domain to manage.

  ``state``
    If not specified or ``present``, the search domain will be included in the
    configuration. If ``absent``, search domain will be removed from the
    configuration.

  Example:

  .. code-block:: yaml

     radvd__interfaces:
       - name: 'eth1'
         dnssl:

           - 'example.org'

           - name: 'other.example.org'
             state: 'present'

  The ``dnssl`` parameters from multiple configuration entries with the same
  name are NOT merged together.

``dnssl_options``
  Optional. Specify custom DNSSL options. The format is the same as the
  ``options`` parameter of the interface configuration. The ``dnssl_options``
  parameters from multiple configuration entries with the same name are NOT
  merged together.

``abro``
  Optional. List of Authoritative Border Router Option definitions. You can
  specify either a simple string, or a YAML dictionary with specific options:

  ``name``
    The IPv6 address of the router to manage.

  ``state``
    If not specified or ``present``, the given ABRO options will be included in
    the configuration. If ``absent``, the ABRO options will be removed from the
    configuration.

  ``options``
    Custom :file:`radvd.conf` options for a given ABRO configuration. The
    format is the same as the ``options`` parameter of the interface
    configuration.

  Example:

  .. code-block:: yaml

     radvd__interfaces:
       - name: 'eth1'
         abro:

           - 'fe80::a200:0:0:1'

           - name: 'fe80::a200:0:0:2'
             options:
               - 'AdvVersionLow': '10'
               - 'AdvVersionHigh': '2'
               - 'AdvValidLifetime': '2'

  The ``abro`` parameters from multiple configuration entries with the same
  name are NOT merged together.
