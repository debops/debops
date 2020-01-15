Default variable details
========================

Some of ``debops.nsswitch`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _nsswitch__ref_services:

nsswitch__services
------------------

The ``nsswitch__*_services`` variables define a list of NSS services which
should be defined on a host. Each element of this list will be checked against
the configuration stored in the :envvar:`nsswitch__combined_database_map` and
services that are present will be enabled in the finished configuration file.

To see a list of possible services, consult the :man:`nsswitch.conf(5)`
manual page. You can also check what NSS libraries are installed on the system
by running the command:

.. code-block:: console

   dpkg -l | grep -E '(libnss|libsss)'


NSS service configuration in Ansible inventory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :envvar:`nsswitch__services`, :envvar:`nsswitch__group_services` and
:envvar:`nsswitch__host_services` variables can be used in respective levels of
the Ansible inventory to configure the NSS services on different hosts. For
example, to make sure that a given host use LDAP lookups, add in the
:file:`ansible/inventory/host_vars/<hostname>/nsswitch.yml` file:

.. code-block:: yaml

   nsswitch__host_services: [ 'ldap' ]

This configuration should enable ``ldap`` NSS service for specific lookup
databases, according to the configuration defined in the
:ref:`nsswitch__ref_database_map` variables.

To remove a specific NSS service from the configuration file, you can add in
inventory:

.. code-block:: yaml

   nsswitch__remove_services: [ 'sss' ]


NSS service configuration by another role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``debops.nsswitch`` Ansible role supports activation of NSS services from
other roles via the :envvar:`nsswitch__dependent_services` variable. The
configuration will persist as long as the service activated by another role via
dependent variables is one of the services known by the ``debops.nsswitch``
roles and is included in the :ref:`nsswitch__ref_database_map` configuration.

In an application role, define a variable that can be passed to the
``debops.nsswitch`` role with list of NSS services to activate:

.. code-block:: yaml

   application__nsswitch__dependent_services: [ 'sss', 'ldap' ]

After that, you can use this variable in a playbook as a dependent variable:

.. literalinclude:: examples/dependent-nsswitch.yml
   :language: yaml

Make sure that the ``debops.nsswitch`` role is used after your application
role, or the one that configures a specific NSS service, that way it can
automatically detect any changes in the :file:`/etc/nsswitch.conf`
configuration file made by the OS packages.


.. _nsswitch__ref_database_map:

nsswitch__database_map
----------------------

The ``nsswitch__*_database_map`` variables are YAML dictionaries which define
the order of the NSS services for specific NSS databases. Each YAML dictionary
key is a name of the NSS database, and its value is a YAML list (only lists are
supported) of NSS services, which can contain different elements.


NSS services defined as strings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each element of a YAML service list can be a string, which is a name of the NSS
service which should be enabled for a given database. This service will be
enabled when a corresponding string is found in the
:envvar:`nsswitch__combined_services` variable. For example, the configuration
below will only enable file-based user and group lookups:

.. code-block:: yaml

   nsswitch__services: [ 'files' ]

   nsswitch__database_map:
     'passwd': [ 'files', 'sss', 'ldap' ]
     'group':  [ 'files', 'sss', 'ldap' ]
     'shadow': [ 'files', 'sss', 'ldap' ]


NSS services defined as YAML lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Another element type in a YAML service list is a YAML list. This format can be
used to include custom actions described in the :man:`nsswitch.conf(5)` for
a given NSS service. The role checks the first element of the list for the NSS
service name, if it should be enabled, the whole list will be included in the
generated configuration file. Remember to write the actions with square
brackets (see the example below). The following example will enable the ``nis``
database lookups for services, with a custom service action:

.. code-block:: yaml

   nsswitch__services: [ 'files', 'nis' ]

   nsswitch__database_map:
     'services':
       - [ 'nis', '[NOTFOUND=return]' ]
       - 'files'


NSS services defined as YAML dictionaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The last version of an element in a YAML service list is a YAML dictionary,
with specific parameters:

``service``
  Required. name of the NSS service to include in the service list.

``action``
  Optional. NSS service action to add after a given service in the service
  list. You need to include the square brackets in this string.

``replace``
  Optional. By default the role uses the ``service`` parameter to look up
  existing NSS services in the :file:`/etc/nsswitch.conf` configuration file
  and decide to include them. If the ``replace`` parameter is specified, the
  role will instead look for the service name specified in it and if found,
  replace it with the ``service`` string.

``require``
  Optional, boolean. If not present, or ``True``, this NSS service will always
  be added if a given NSS service type is present in the
  :envvar:`nsswitch__combined_services` list.

  If ``False``, role will not check if a given NSS service is present in the
  enabled services, but only of a given NSS service type is already present in
  the configuration file.

  This parameter can be used to ensure that a given NSS service state is
  preserved without enforcing its presence in the generated
  :file:`/etc/nsswitch.conf` config file.

``state``
  Optional. If not specified or ``present``, the given NSS service will be
  considered for inclusion in the service list, depending on its presence in
  :envvar:`nsswitch__combined_services` variable. if ``absent``, the given NSS
  service will be skipped during template generation. This can be used to
  enable or disable different NSS service entries conditionally.

An example configuration which will enable a ``ldap`` NSS lookup for user and
group accounts on Ubuntu-based hosts:

.. code-block:: yaml

   nsswitch__services: [ 'files', 'ldap' ]

   nsswitch__database_map:

     'passwd':

       - 'files'

       - service: 'ldap'
         state: '{{ "present"
                    if ansible_distribution == "Ubuntu"
                    else "absent" }}'

     'group':

       - 'files'

       - service: 'ldap'
         state: '{{ "present"
                    if ansible_distribution == "Ubuntu"
                    else "absent" }}'

     'shadow':

       - 'files'

       - service: 'ldap'
         state: '{{ "present"
                    if ansible_distribution == "Ubuntu"
                    else "absent" }}'

The example below will make sure that :command:`sudo` LDAP lookups will be
enabled if ``sudo-ldap`` package is enabled, but they won't be considered
otherwise:

.. code-block:: yaml

   nsswitch__services: [ 'files', 'ldap' ]

   nsswitch__database_map:
     'sudoers':

       - service: 'files'
         require: False

       - service: 'ldap'
         require: False


NSS service order
~~~~~~~~~~~~~~~~~

The order of elements in the NSS service lists is significant, and defines the
order in which the system uses various services to lookup the information. If
needed, the system administrator can change the order of services for
a particular NSS database, using the additional ``nsswitch__*_database_map``
variables. Order cannot be changed from another role due to idempotency
constraints, and because this property is related to the particular environment
as a whole, rather than to a specific application/service.

For example, the default (simplified) configuration for hostname lookups could
be defined as:

.. code-block:: yaml

   nsswitch__default_database_map:
     'hosts': [ 'files', 'dns' ]

In this configuration, the system resolver while looking for a hostname or an
IP address, will first check the local :file:`/etc/hosts` file, and if hostname
is not found there, the system will ask the DNS database of a hostname.

If you want to change this order and look in the DNS database first, you can
define a variable in Ansible inventory like this:

.. code-block:: yaml

   nsswitch__database_map:
     'hosts': [ 'dns', 'files' ]

With this configuration in place, system should ask the DNS database before
looking in local :file:`/etc/hosts` file. If you plan to change a database
service lookup order, make sure that you include all of the relevant services
in your customized variable, since it will mask the default database list as
a whole.
