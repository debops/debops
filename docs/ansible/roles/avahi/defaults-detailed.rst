Default variable details
========================

Some of ``debops.avahi`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _avahi__ref_daemon_conf:

avahi__daemon_conf
------------------

The ``avahi__daemon_conf_*`` variables are used to specify what parameters
should be present in the :file:`/etc/avahi/avahi-daemon.conf` configuration
file. Each pair of variables manages one section of the INI file. The "default"
variable is combined with the custom variable therefore it's possible to change
the value of a parameter without the need to copy the entire variable over to
the Ansible inventory.

Each variable is a YAML dictionary with keys representing the available
parameters and values representing the parameter values. You can use boolean
YAML values (``True``, ``False``) to specify ``yes`` or ``no`` values, as well
as strings and numbers. if a value is an empty string, the corresponding
parameter will be commented out in the finished configuration file.

See the :man:`avahi-daemon.conf(5)` manual page for information about
recognized parameters and their meaning.


.. _avahi__ref_services:

avahi__services
---------------

The ``avahi__*_services`` variables define the services published by Avahi on
its ``.local`` domain. The variables are either YAML dictionaries or YAML lists
of dictionaries that are combined together in the
:envvar:`avahi__combined_services` in the order they appear in the
:file:`defaults/main.yml` file.

Each entry in the ``avahi__*_services`` variables is a YAML dictionary with
specific parameters:

``filename``
  Name of the configuration file that holds the service details. The name will
  be used in the file path in the format:

  .. code-block:: none

     /etc/avahi/services/<filename>.service

  If the filename is not specified and the main variable uses the YAML
  dictionary format, the dictionary key will be used as the filename.
  The examples below are equivalent:

  .. code-block:: yaml

     avahi__services:
       'example-service':
         name: 'Example service on %h'
         type: '_example._tcp'
         port: '1234'

     avahi__host_services:
       - filename: 'example-service'
         name: 'Example service on %h'
         type: '_example._tcp'
         port: '1234'

``services``
  Optional. A YAML list of services defined by this entry and encloses in
  a service group. Each list item is a YAML dictionary that specifies given
  service parameters. If the ``services`` parameter is not specified, role will
  automatically generate one based on parameters defined in the main entry.
  This parameter is only useful in applications that define multiple services,
  which can be defined together in a service group, otherwise you can use the
  simpler syntax.

``type``
  A string similar to a `SRV record <https://en.wikipedia.org/wiki/SRV_record>`_
  that defines the service type and protocol (it's similar in a way that only
  the service name and protocol are relevant, other parts of the SRV record
  shouldn't be used). Example service types are ``_ssh._tcp``, ``_http._tcp``.
  The list of possible service names can be found in the `Service Name and Transport Protocol Port Number Registry <https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xml>`_ maintained by `IANA <https://www.iana.org/>`_.

  If the type is not specified and a given entry has no separate ``services``
  list defined, the service will not be published. This can be used to define
  host CNAME entries without associated service (see below).

``subtype``
  Optional. Either a string, or a YAML list of additional subtypes to publish
  for this service. Example subtype definition: ``_custom._sub._example._tcp``.

``port``
  Optional. Specify the port number on which a given service listens for new
  connections. If it's not specified, the port number for this service will be
  set to ``0``.

``name``
  Optional. Custom description of a service, displayed in compatible Avahi
  clients. If not specified, the host's hostname will be used instead.

``replace_wildcards``
  Optional, boolean. If not defined or ``True``, Avahi will replace the ``%h``
  wildcard in the service description with the host's hostname. Setting this
  parameter to ``False`` will turn off the replacement.

``protocol``
  Optional. Specify which network to publish the service on, either IPv4, IPv6
  or both (default). Possible values: ``ipv4``, ``ipv6``, ``any``.

``domain`` or ``domain_name``
  Optional. Publish the service on a different domain than the default
  ``.local`` domain used by Avahi.

``fqdn`` or ``hostname`` or ``host_name``
  Optional. Specify a different FQDN for a given service. This can be used to
  publish services on behalf of other hosts on the network that do not support
  Avahi themselves. You also need to register the host A/AAAA record separately
  for the Avahi to correctly publish the service record.
  See :envvar:`avahi__hosts` for more details.

``txt`` or ``txt_record``
  Optional. String or YAML list of custom TXT records which should be published
  for this service. These records are used to provide additional information
  about the service, configuration options, etc.

The parameters below are additional and related to the role itself, rather than
to the Avahi services:

``comment``
  Optional. String or YAML text block with additional comments included in the
  service configuration file.

``state``
  Optional. If not specified or ``present``, the Avahi service will be
  configured. If ``absent``, the configuration of a given Avahi service will be
  removed.

``cname``
  Optional. Specify a custom CNAME record which will be used to register a host
  alias using the :command:`avahi-alias` script. The CNAME record will point to
  the originating host. See :ref:`avahi__ref_alias_support` for more details.
  You can define ``avahi__*_services`` entries that only publish CNAME records
  by not specifying a type, for example:

  .. code-block:: yaml

     avahi__services:
       - filename: 'custom-cname-of-host'
         cname: 'custom'

     avahi__host_services:
       'other-example':
         cname: 'other.local'

``cname_state``
  Optional. If the ``cname`` parameter is specified, you can use this parameter
  to control the state of the CNAME record separately from the main ``state``
  parameter. If not specified or ``present``, the CNAME record will be
  published. If ``absent``, the CNAME record will be removed.
