Default variables: configuration
================================

Some of ``debops.librenms`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _librenms__ref_snmp_credentials:

librenms__snmp_credentials
--------------------------

LibreNMS can use multiple SNMPv3 credentials at once, each one defined in
a YAML dict. Default set of credentials managed by ``debops.snmpd`` which will
use it for all DebOps-based hosts in the cluster will be used automatically by
``debops.librenms``. You can add more entries in ``librenms__snmp_credentials``
list as needed.

Parameters which define SNMP credentials:

``authname``
  SNMP v3 username.

``authpass``
  SNMP v3 authentication password.

``cryptopass``
  SNMP v3 encryption password.

``authlevel``
  Authentication and privacy level required by connection, you most likely want
  to use ``authPriv`` to request encrypted authentication and encrypted
  privacy.

``authalgo``
  Authentication encryption algorithm used for this credentials, either ``SHA``
  or ``MD5``.

``cryptoalgo``
  Privacy encryption algorithm used for this credentials, either ``AES`` or
  ``DES``.

For an example of SNMP v3 credentials, check out
``librenms__snmp_credentials_default`` variable in ``defaults/main.yml``.

.. _librenms__ref_configuration_maps:

librenms__configuration_maps
----------------------------

LibreNMS configuration is stored as PHP ``$config`` dictionary in
``config.php`` in main project directory. To make it easier to manage using
Ansible, a Jinja template is used to recursively convert a list of dictionaries
in YAML format to PHP format. Configuration is split into multiple
dictionaries, so that separate sections can be modified easier without the need
to copy everything to Ansible inventory.

Basic YAML syntax mirrors PHP syntax for dictionaries. Specifying your
configuration in a YAML dict like:

.. code-block:: yaml

   librenms__configuration_maps:
     - '{{ librenms__configuration }}'

   librenms__configuration:
     comment: 'Example configuration'
     'dict_string': 'string'
     'dict_bool': True
     'dict_int': 10

Will result in PHP configuration:

.. code-block:: php

   ### Example configuration
   $config['dict_string'] = "string";
   $config['dict_bool'] = TRUE;
   $config['dict_int'] = 10;

Special key ``comment`` is reserved for comments in the configuration.

You can use YAML lists as well:

.. code-block:: yaml

   librenms__configuration_maps:
     - '{{ librenms__configuration }}'

   librenms__configuration:
     'dict_list': [ 'first', 'second', 'third' ]

This will result in dict-like list which appends entries to already existing
ones from defaults:

.. code-block:: php

   $config['dict_list'][] = "first";
   $config['dict_list'][] = "second";
   $config['dict_list'][] = "third";

You can also define a specific list without appending to existing list using
``array`` dict key:

.. code-block:: yaml

   librenms__configuration_maps:
     - '{{ librenms__configuration }}'

   librenms__configuration:
     'dict_array': { array: [ 'one', 'two', 'three' ] }

This will result in PHP configuration:

.. code-block:: php

   $config['dict_array'] = array("one", "two", "three");

Dictionaries and list can be nested as well:

.. code-block:: yaml

   librenms__configuration_maps:
     - '{{ librenms__configuration }}'

   librenms__configuration:
     'dict_nested':
       'second_level':
         'third_list': [ 'abc', 'def' ]
         'third_string': 'example string'

This will result in PHP configuration:

.. code-block:: php

   $config['dict_nested']['second_level']['third_list'][] = "abc";
   $config['dict_nested']['second_level']['third_list'][] = "def";
   $config['dict_nested']['second_level']['third_string'] = "example string";

You can use lists of dictionaries as well. They will be automatically
enumerated at the correct level. This YAML configuration:

.. code-block:: yaml

   librenms__configuration_maps:
     - '{{ librenms__configuration }}'

   librenms__configuration:
     'dicts':

       - key0: 'value0'
         key1: 'value1'

       - key0: 'value2'
         key1: 'value3'

will result in PHP configuration:

.. code-block:: php

   $config['dicts'][0]['key0'] = "value0";
   $config['dicts'][0]['key1'] = "value1";
   $config['dicts'][1]['key0'] = "value2";
   $config['dicts'][1]['key1'] = "value3";

Template conversion might be incomplete, however at the moment it's enough to
generate correct ``config.php`` file for LibreNMS.
