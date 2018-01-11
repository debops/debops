.. _unbound__ref_server:

Default variable details: unbound__server
=========================================


The ``unbound__*_server`` variables are used to define the contents of the
:file:`/etc/unbound/unbound.conf.d/ansible.conf` configuration file. The
variables are YAML lists, concatenated together into
:envvar:`unbound__combined_server` variable, which is passed to the
configuration template. Only the ``server`` section of the configuration is
managed by these variables.

Each list entry is a YAML dictionary, which can be written in a simple or
complex form. Entries that control Unbound parameters of the same name will be
combined together in order of appearance. Since most of the Unbound
configuration options use dashes in their names, you might want to quote the
YAML dictionary keys to avoid issues with Jinja templating.

.. contents::
   :local:
   :depth: 1


Simple form of the configuration parameters
-------------------------------------------

Simple form of the Unbound configuration uses the dictionary key as a option
name, and its value as that option's parameters:

.. code-block:: yaml

   unbound__server:

     # Option with boolean value
     - 'extended-statistics': True

     # Option with integer value
     - verbosity: 1

     # Option with string value
     - 'private-domain': 'example.org'

     # Option with multiple values in a list
     - 'domain-insecure': [ 'example.org', 'example.com' ]

The result of the above configuration in :file:`/etc/unbound/unbound.conf.d/ansible.conf`:

.. code-block:: none

   server:
       extended-statistics:           yes
       verbosity:                     1
       private-domain:                "example.org"
       domain-insecure:               "example.org"
       domain-insecure:               "example.com"

The parameters in the configuration file will be present in the order they were
first defined in the variables.


Complex form of the configuration parameters
--------------------------------------------

Complex form of the Unbound configuration is detected when a dictionary key
contains a ``name`` parameter. In that case, the role will interpret the entry
using specific parameters:

``name``
  The name of the configuration option to manage. This parameter is used as an
  identifier during the variable parsing.

``value``
  Required. A value which should be set for a given option. Values can be YAML
  strings, integers, booleans and lists (not dictionaries). Lists can contain
  simple strings, numbers, or YAML dictionaries that describe each value in
  greater detail. See :ref:`unbound__ref_server_values` for more details.

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

  If ``append``, the given entry will be evaluated only if an entry with the
  same name already exists. The current state will not be changed.

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

   unbound__server:

     - name: 'extended-statistics'
       comment: 'Enable extended server statistics'
       value: True

     - name: 'verbosity'
       value: 1

     - name: 'private-domain'
       value: 'example.org'

     - name: 'domain-insecure'
       value: [ 'example.org', 'example.com' ]

Unbound supports more complex parameters with arguments. You can define them
using extended syntax as well:

.. code-block:: yaml

   unbound__server:

     - 'define-tag': 'tag1 tag2 tag3'

     - name: 'access-control'
       value:

         - name: '127.0.0.0/8'
           args: 'allow_snoop'

         - name: '::1/128'
           args: 'allow_snoop'

         - name: '192.0.2.0/24'
           args: 'allow'

     - name: 'access-control-tag'
       value:
         - name: '192.0.2.0/24'
           args: '"tag1 tag2"'

The result of the above configuration in
:file:`/etc/unbound/unbound.conf.d/ansible.conf`:

.. code-block:: none

   server:

       # Enable extended server statistics
       extended-statistics:           yes
       verbosity:                     1
       private-domain:                "example.org"
       domain-insecure:               "example.org"
       domain-insecure:               "example.com"
       define-tag:                    "tag1 tag2 tag3"
       access-control:                127.0.0.0/8 allow_snoop
       access-control:                192.0.2.0/24 allow
       access-control:                ::1/128 allow_snoop
       access-control-tag:            192.0.2.0/24 "tag1 tag2"

The parameters in the configuration file will be present in the order they were
first defined in the variables, unless the ``weight`` parameter is added, which
will change the order.


.. _unbound__ref_server_values:

Configuration values and their interactions
-------------------------------------------

The `Unbound configuration file <https://unbound.net/documentation/unbound.conf.html>`_
uses key-value format, with values being either strings, numbers, booleans or
lists. The first three types are handled by the ``debops.unbound`` role as
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

``args``
  Optional. Some Unbound values can have additional arguments. They should be
  added using this parameter which will be appended to a given value "as-is".
  Any quotes needed by Unbound (for example, tags) need to be included inside
  the quoted string itself.


Example list
~~~~~~~~~~~~

Define a list with conditional values:

.. code-block:: yaml

   unbound__server:

     - name: 'domain-insecure'
       value:

         - 'example.com'

         - name: 'example.org'
           state: '{{ "present"
                      if (ansible_domain.split(".")|count > 1)
                      else "ignore" }}'

         - name: 'example.net'
           weight: 100


Base value replacement
~~~~~~~~~~~~~~~~~~~~~~

Repeating the string, number or boolean option will result in the latter entry
replacing the former entry:

.. code-block:: yaml

   unbound__server:

     # Old value
     - verbosity: 1

     # New, active value
     - verbosity: 2

The result of the above configuration in
:file:`/etc/unbound/unbound.conf.d/ansible.conf`:

.. code-block:: none

   verbosity:          2


Lists are merged together
~~~~~~~~~~~~~~~~~~~~~~~~~

The list parameters behave differently. Specifying the same option multiple
times, if the preceding option was a list, will add the specified parameters to
the list:

.. code-block:: yaml

   unbound__server:

     - 'domain-insecure': [ 'example.com', 'example.org' ]

     - 'domain-insecure': [ 'example.net' ]

The result of the above configuration in
:file:`/etc/unbound/unbound.conf.d/ansible.conf`:

.. code-block:: none

   domain-insecure:     "example.org"
   domain-insecure:     "example.net"
   domain-insecure:     "example.com"


How to reset a list
~~~~~~~~~~~~~~~~~~~

If the option was a list, and subsequent option specified a boolean, string or
a number, the value will replace the previous one, instead of adding to a list.
This can be used to reset the list instead of appending to it.

.. code-block:: yaml

   unbound__server:

     - 'domain-insecure': [ 'example.com', 'example.org' ]

     - 'domain-insecure': 'example.net'

The result of the above configuration in
:file:`/etc/unbound/unbound.conf.d/ansible.conf`:

.. code-block:: none

   domain-insecure:     "example.net"


Lists don't add duplicates
~~~~~~~~~~~~~~~~~~~~~~~~~~

The role checks if a given list element is already present, and it won't add
a duplicate value to the list:

.. code-block:: yaml

   unbound__server:

     - 'domain-insecure': [ 'example.org', 'example.com' ]

     - 'domain-insecure': [ 'example.org' ]

The result of the above configuration in
:file:`/etc/unbound/unbound.conf.d/ansible.conf`:

.. code-block:: none

   domain-insecure:       "example.org"
   domain-insecure:       "example.com"
