Default variable details
========================

Some of ``debops.netbase`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _netbase__ref_hosts:

netbase__hosts
--------------

The ``netbase__*_hosts`` variables are used to define the host records in the
:file:`/etc/hosts` database. Each variable is a list of YAML dictionaries, the
entries with the same ``name`` parameter or the dictionary key are combined
together; this allows modification of the earlier entries by the later ones.
See :man:`hosts(5)` for more details.

Examples
~~~~~~~~

Add a Fully Qualified Domain Name host entry with IPv4 and IPv6 addresses:

.. code-block:: yaml

   netbase__hosts:

     - '192.0.2.1':   [ 'host.example.org', 'host' ]
     - '2001:db8::1': [ 'host.example.org', 'host' ]

     - '192.0.2.2':   'other.example.org'

Add a host entry with IP address specified by a variable:

.. code-block:: yaml

   host_address: '192.0.2.1'
   host_fqdn_hostname: [ 'host.example.org', 'host' ]

   netbase__hosts:

     - name: '{{ host_address }}'
       value: '{{ host_fqdn_hostname }}'

Remove a host record from the :file:`/etc/hosts` database:

.. code-block:: yaml

   netbase__hosts:

     - '127.0.1.1': ''

     # Alternative syntax
     - '127.0.1.1': []

Syntax
~~~~~~

Each element in the list variables is a YAML dictionary. If the dictionary
contains the ``name`` parameter, it will be evaluated as the "expanded" form
with specific parameters:

``name``
  Required. The IP address of a given host entry. In this form it can be
  a variable. The entries with the same ``name`` parameter (or the dictionary
  key in the simple form) are merged together, this allows to change the
  specific entries in the inventory without the need to copy the entire list.

  If the ``name`` is empty, the host record will not be added to the database.

``value``
  Required. A string or a YAML list with host addresses to define for a given
  host record. If the list is used, lists from multiple entries are combined
  together. To reset a list, specify an entry with an empty string as the
  value.

  If the value is empty, the host record will be removed from the database.

``separator``
  Optional, boolean. If set and ``True``, the generated template will contain an
  empty line before a given entry, to allow for better readability. This
  parameter is ignored when the ``lineinfile`` mode is used to manage the
  database.

If the YAML dictionary does not contain a ``name`` entry, the entire dictionary
is interpreted using the following simplified format: keys are the IP addresses
of the host records, and values are strings or YAML lists with the hostnames or
FQDN domains. It's best to use only 1 dictionary key for each host record, and
not combine multiple entries together in one list element.
