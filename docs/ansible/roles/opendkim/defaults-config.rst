.. _opendkim__ref_config:

Default variable details: opendkim__config
==========================================


The ``opendkim__*_config`` variables are used to define the contents of the
:file:`/etc/opendkim.conf` configuration file. The variables are YAML lists,
concatenated together into :envvar:`opendkim__combined_config` variable, which
is passed to the configuration template.

Each list entry is a YAML dictionary, which can be written in a simple or
complex form. Entries that control OpenDKIM parameters of the same name will be
combined together in order of appearance.

.. contents::
   :local:
   :depth: 1


Simple form of the configuration parameters
-------------------------------------------

Simple form of the OpenDKIM configuration uses the dictionary key as a option
name, and its value as that option's parameters:

.. code-block:: yaml

   opendkim__config:

     # Option with boolean value
     - Syslog: True

     # Option with integer value
     - AutoRestartCount: 0

     # Option with string value
     - Domain: 'example.com'

     # Option with multiple values in a list
     - OversignHeaders: [ 'Header1', 'Header2' ]

The result of the above configuration in :file:`/etc/opendkim.conf`:

.. code-block:: none

   Syslog              yes
   AutoRestartCount    0
   Domain              example.com
   OversignHeaders     Header1,Header2

The parameters in the configuration file will be present in the order they were
first defined in the variables.


Complex form of the configuration parameters
--------------------------------------------

Complex form of the OpenDKIM configuration is detected when a dictionary key
contains a ``name`` parameter. In that case, the role will interpret the entry
using specific parameters:

``name``
  The name of the configuration option to manage. This parameter is used as an
  identifier during the variable parsing.

``value``
  Required. A value which should be set for a given option. Values can be YAML
  strings, integers, booleans and lists (not dictionaries). Lists can contain
  simple strings, numbers, or YAML dictionaries that describe each value in
  greater detail. See :ref:`opendkim__ref_config_values` for more details.

``option``
  Optional. If specified, the option will use this string as the "name" instead
  of the ``name`` value. This is useful to create examples in the configuration
  file that have the same name as existing configuration options.

``comment``
  Optional. String or a YAML dictionary with additional comments for a given
  configuration option.

``separator``
  Optional, boolean. if ``True``, an empty line will be added above a given
  option, useful for readability.

``state``
  Optional. If not specified or ``present``, the option will be present in the
  finished configuration file.

  If ``absent``, the option will not be included in the configuration file.

  If ``ignore``, the given entry will not be evaluated by the role, and no
  changes will be done to the preceding parameters with the same name. This can
  be used to conditionally activate entries with different configuration.

  If ``hidden``, the option will not be displayed in the configuration file,
  but any comments will be present. This can be used to add free-form comments
  in the Postfix configuration file.

  If ``comment``, the option will be present, but it will be commented out.
  This can be used to add examples in the configuration file.

``weight``
  Optional. A positive or negative number which affects the position of a given
  option in the configuration file. The higher the number, the more a given
  option "weighs" and the lower it will be placed in the finished configuration
  file. Negative numbers make the option "lighter" and it will be placed
  higher.

``copy_id_from``
  Optional. This is an internal role parameter which can be used to change the
  relative position of a given option in the configuration file. If you specify
  a name of an option, it's internal "id" number (used for sorting) will be
  copied to the current option. This can be used to move options around to
  different configuration file sections.


Examples
~~~~~~~~

Define the previous example using complex form:

.. code-block:: yaml

   opendkim__config:

     - name: 'Syslog'
       comment: 'Log to syslog'
       value: True

     - name: 'AutoRestartCount'
       value: 0

     - name: 'Domain'
       value: 'example.com'

     - name: 'OversignHeaders'
       value: [ 'Header1', 'Header2' ]

The result of the above configuration in :file:`/etc/postfix/main.cf`:

.. code-block:: none

   # Log to syslog
   Syslog              yes

   AutoRestartCount    0
   Domain              example.com
   OversignHeaders     Header1,Header2

The parameters in the configuration file will be present in the order they were
first defined in the variables, unless the ``weight`` parameter is added, which
will change the order.


.. _opendkim__ref_config_values:

Configuration values and their interactions
-------------------------------------------

The `OpenDKIM configuration file <http://opendkim.org/opendkim.conf.5.html>`_
uses key-value format, with values being either strings, numbers, booleans or
lists. The first three types are handled by the ``debops.opendkim`` role as
normal.

List values are by default concatenated to allow easy extension of existing
values. The values in a list are either YAML strings, numbers, or can be
defined as YAML dictionaries with specific parameters:

``name`` or ``param``
  Required. The value itself, usually a string.

``state``
  Optional. If not defined or ``present``, the value will be included in the
  list.

  If ``absent``, the value will be removed from the list.

  If ``ignore``, the given entry will not be evaluated by the role, and will
  not change the state of the value. This can be used to enable or disable
  values conditionally.

``weight``
  Optional. A positive or negative number which affects the position of a given
  value in the list. The higher the number, the more a given value "weighs" and
  the lower it will be placed in the finished list. Negative numbers make the
  value "lighter" and it will be placed higher.


Example list
~~~~~~~~~~~~

Define a list with conditional values:

.. code-block:: yaml

   opendkim__config:

     - name: 'OversignHeaders'
       value:

         - 'From'

         - name: 'To'
           state: '{{ "present"
                      if (ansible_domain.split(".")|count > 1)
                      else "ignore" }}'

         - name: 'Subject'
           weight: 100


Base value replacement
~~~~~~~~~~~~~~~~~~~~~~

Repeating the string, number or boolean option will result in the latter entry
replacing the former entry:

.. code-block:: yaml

   opendkim__config:

     # Old value
     - Domain: 'example.com'

     # New, active value
     - Domain: 'example.org'

The result of the above configuration in :file:`/etc/opendkim.conf`:

.. code-block:: none

   Domain          example.org


Lists are merged together
~~~~~~~~~~~~~~~~~~~~~~~~~

The list parameters behave differently. Specifying the same option multiple
times, if the preceding option was a list, will add the specified parameters to
the list:

.. code-block:: yaml

   opendkim__config:

     - InternalHosts: [ '127.0.0.1', 'localhost' ]

     - InternalHosts: [ '192.0.2.1' ]

The result of the above configuration in :file:`/etc/opendkim.conf`:

.. code-block:: none

   InternalHosts          127.0.0.1,localhost,192.0.2.1


How to reset a list
~~~~~~~~~~~~~~~~~~~

If the option was a list, and subsequent option specified a boolean, string or
a number, the value will replace the previous one, instead of adding to a list.
This can be used to reset the list instead of appending to it.

.. code-block:: yaml

   opendkim__config:

     - InternalHosts: [ '127.0.0.1', '::1' ]

     - Internalhosts: 'localhost'

The result of the above configuration in :file:`/etc/opendkim.conf`:

.. code-block:: none

   InternalHosts          localhost


Lists don't add duplicates
~~~~~~~~~~~~~~~~~~~~~~~~~~

The role checks if a given list element is already present, and it won't add
a duplicate value to the list:

.. code-block:: yaml

   opendkim__config:

     - Domain: [ 'example.org', 'localhost' ]

     - Domain: [ 'example.org' ]

The result of the above configuration in :file:`/etc/opendkim.conf`:

.. code-block:: none

   Domain           example.org,localhost
