.. _unbound__ref_defaults_detailed:

Default variable details
========================

some of ``debops.unbound`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


unbound__server
---------------

Configuration of the ``unbound__*_server`` variables is described in a separate
document, :ref:`unbound__ref_server`.


.. _unbound__ref_zones:

unbound__zones
--------------

The ``unbound__*_zones`` lists are used to configure forward or stub DNS zones
published by Unbound service. Each DNS zone delegation is configured in its own
:file:`/etc/unbound/unbound.conf.d/zone_<name>.conf` configuration file.

Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. Name of the DNS zone, used in the filename. This parameter is used
  as an identifier during the variable parsing.

``zone``
  Optional. If specified, this string will be used as the DNS zone name. With
  this parameter specified, ``name`` can be used as a general identifier of
  a particular delegation.

``type``
  Optional. The zone type to use, either ``forward`` (default if not
  specified), ``local`` or ``stub``. See the :man:`unbound.conf(5)` for details
  about stub and forward zones.

``local_zone_type``
  Optional. If the ``type`` parameter is set to ``local``, this parameter can
  be used to define the type of the local zone (``static`` (default),
  ``transparent``, etc. See :man:`unbound.conf(5)` manual page, ``local-zone:``
  keyword for the details about local zone types.

``local_zone_data``
  Optional. If the ``type`` parameter is set to ``local``, this parameter can
  be used to define the data of a given local zone. This is a YAML list of
  entries, each entry can specify a DNS Resource Record as a string. See the
  examples section for an example local zone configuration.

``nameserver``, ``nameservers``
  Optional. IP address or list of IP addresses of the DNS nameservers of
  a particular zone. You can specify the port using the @ character, for
  example ``192.0.2.1@5353``.

``revdns``
  Optional. Specify a CIDR subnet or multiple subnets for a given DNS zone. If
  specified, a revDNS zones will be included in the generated zone file; each
  revDNS zone will use the same nameserver IP addresses and other options
  specified for the main DNS zone. Currently only IPv4 C-class subnets (``/16``
  to ``/24``) are supported best.

  If specified subnet is in a RFC 1918 private network range, the main DNS zone
  and revDNS zones will be set as local, insecure zones to avoid issues with
  DNSSEC. This can be overridden by setting the ``private_domain``,
  ``domain_insecure`` and/or ``local_zone`` parameters to ``False``.

``state``
  Optional. If not specified or ``present``, the zone file will be generated.

  If ``absent``, the configuration file will be removed.

  If ``ignore``, the given entry will not be evaluated by the role, and no
  changes will be done to the preceding parameters with the same name. This can
  be used to conditionally activate entries with different configuration.

  If ``append``, the given entry will be evaluated only if an entry with the
  same name already exists. The current state will not be changed.

``comment``
  Optional. String or a YAML dictionary with additional comments for a given
  DNS zone.

``options``
  Optional. List of configuration options for a particular zone. The format is
  the same as :ref:`unbound__ref_server` configuration options. For a list of
  supported options, see the stub zone and forward zone sections of the
  :man:`unbound.conf(5)` manual page.

``server_options``
  Optional. List of ``server:`` configuration options associated with
  a particular zone. The format is the same as :ref:`unbound__ref_server`
  configuration options.

Examples
~~~~~~~~

Forward all queries to external Google DNS servers:

.. literalinclude:: examples/forward-all-to-google.yml
   :language: yaml

Create custom forward zone for internal network:

.. code-block:: yaml

   unbound__zones:

     - name: 'internal-net'
       zone: 'nat.example.org'
       revdns: '192.0.2.0/24'
       nameserver: '192.0.2.1'
       options:
         - 'forward-first': True

Define a local DNS entry ``example.test.`` with a few resource records:

.. code-block:: yaml

   unbound__zones:

     - name: 'example.test'
       zone: 'example.test.'
       type: 'local'
       local_zone_type: 'static'
       local_zone_data:
         - 'NS localhost.'
         - 'SOA localhost. nobody.invalid. 1 3600 1200 604800 10800'
         - 'PTR localhost.'
         - 'A 192.0.2.1'
         - 'AAAA 2001:db8::1'
