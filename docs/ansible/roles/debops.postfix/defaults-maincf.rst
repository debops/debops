.. _postfix__ref_maincf:

Default variable details: postfix__maincf
=========================================


The ``postfix__*_maincf`` variables are used to define the contents of the
:file:`/etc/postfix/main.cf` configuration file. The variables are YAML lists,
concatenated together into :envvar:`postfix__combined_maincf` variable, which
is passed to the configuration template.

Each list entry is a YAML dictionary, which can be written in a simple or
complex form. Entries that control Postfix parameters of the same name will be
combined together in order of appearance.

.. contents::
   :local:
   :depth: 1


Simple form of the configuration parameters
-------------------------------------------

Simple form of the Postfix :file:`main.cf` configuration uses the dictionary
key as a option name, and its value as that option's parameters:

.. code-block:: yaml

   postfix__maincf:

     # Option with boolean value
     - append_dot_mydomain: False

     # Option with integer value
     - mailbox_size_limit: 0

     # Option with string value
     - myorigin: '/etc/mailname'

     # Option with multiple values in a list
     - mydestination: [ 'example.org', 'localhost' ]

     # Option with an empty value
     - relayhost: ''

     # Option with multiline value
     - debugger_command: |
         PATH=/bin:/usr/bin:/usr/local/bin:/usr/X11R6/bin
         ddd $daemon_directory/$process_name $process_id & sleep 5

The result of the above configuration in :file:`/etc/postfix/main.cf`:

.. code-block:: none

   append_dot_mydomain = no
   mailbox_size_limit = 0
   myorigin = /etc/mailname
   mydestination = example.org, localhost
   relayhost =
   debugger_command =
       PATH=/bin:/usr/bin:/usr/local/bin:/usr/X11R6/bin
       ddd $daemon_directory/$process_name $process_id & sleep 5

The parameters in the configuration file will be present in the order they were
first defined in the variables.


Complex form of the configuration parameters
--------------------------------------------

Complex form of the Postfix :file:`main.cf` configuration is detected when
a dictionary key contains a ``name`` parameter. In that case, the role will
interpret the entry using specific parameters:

``name``
  The name of the configuration option to manage. This parameter is used as an
  identifier during the variable parsing.

``value``
  Required. A value which should be set for a given option. Values can be YAML
  strings, text blocks, integers, booleans and lists (not dictionaries). Lists
  can contain simple strings, numbers, or YAML dictionaries that describe each
  value in greater detail. See :ref:`postfix__ref_maincf_values` for more
  details.

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

``section``
  Optional. Name of the section of the :file:`/etc/postfix/main.cf`
  configuration file in which a given option should be placed. If it's no
  specified, ``unknown`` section is used.
  See :ref:`postfix__ref_maincf_sections` for more details.

``weight``
  Optional. A positive or negative number which affects the position of a given
  option in the configuration file, within the selected section. The higher the
  number, the more a given option "weighs" and the lower it will be placed in
  the finished configuration file. Negative numbers make the option "lighter"
  and it will be placed higher.

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

   postfix__maincf:

     - name: 'append_dot_mydomain'
       comment: 'appending .domain is the MUA's job.'
       value: False
       state: 'comment'

     - name: 'mailbox_size_limit'
       value: 0

     - name: 'myorigin'
       value: '/etc/mailname'

     - name: 'mydestination'
       value: [ 'example.org', 'localhost' ]
       weight: 100

     - name: 'relayhost'
       value: ''

     - name: 'debugger_command'
       value: |
         PATH=/bin:/usr/bin:/usr/local/bin:/usr/X11R6/bin
         ddd $daemon_directory/$process_name $process_id & sleep 5

The result of the above configuration in :file:`/etc/postfix/main.cf`:

.. code-block:: none

   # appending .domain is the MUA's job.
   #append_dot_mydomain = no

   mailbox_size_limit = 0
   myorigin = /etc/mailname
   relayhost =
   debugger_command =
       PATH=/bin:/usr/bin:/usr/local/bin:/usr/X11R6/bin
       ddd $daemon_directory/$process_name $process_id & sleep 5

   mydestination = example.org, localhost

The parameters in the configuration file will be present in the order they were
first defined in the variables, unless the ``weight`` parameter is added, which
will change the order.


.. _postfix__ref_maincf_values:

Configuration values and their interactions
-------------------------------------------

The `Postfix main.cf configuration <http://www.postfix.org/postconf.5.html>`_
uses key-value format, with values being either strings, numbers, booleans or
lists. The first three types are handled by the ``debops.postfix`` role as
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

   postfix__maincf:

     - name: 'mydestination'
       value:

         - '{{ ansible_fqdn }}'

         - name: '{{ ansible_domain }}'
           state: '{{ "present"
                      if (ansible_domain.split(".")|count > 1)
                      else "ignore" }}'

         - name: 'localhost'
           weight: 100


Base value replacement
~~~~~~~~~~~~~~~~~~~~~~

Repeating the string, number or boolean option will result in the latter entry
replacing the former entry:

.. code-block:: yaml

   postfix__maincf:

     # Old value
     - myorigin: '/dev/null'

     # New, active value
     - myorigin: '/etc/mailname'

The result of the above configuration in :file:`/etc/postfix/main.cf`:

.. code-block:: none

   myorigin = /etc/mailname


Lists are merged together
~~~~~~~~~~~~~~~~~~~~~~~~~

The list parameters behave differently. Specifying the same option multiple
times, if the preceding option was a list, will add the specified parameters to
the list:

.. code-block:: yaml

   postfix__maincf:

     - mydestination: [ 'example.org', 'localhost' ]

     - mydestination: [ 'example.com' ]

The result of the above configuration in :file:`/etc/postfix/main.cf`:

.. code-block:: none

   mydestination = example.org, localhost, example.com


How to reset a list
~~~~~~~~~~~~~~~~~~~

If the option was a list, and subsequent option specified a boolean, string or
a number, the value will replace the previous one, instead of adding to a list.
This can be used to reset the list instead of appending to it.

.. code-block:: yaml

   postfix__maincf:

     - inet_interfaces: [ '127.0.0.1', '::1' ]

     - inet_interfaces: 'all'

The result of the above configuration in :file:`/etc/postfix/main.cf`:

.. code-block:: none

   inet_interfaces = all


Lists don't add duplicates
~~~~~~~~~~~~~~~~~~~~~~~~~~

The role checks if a given list element is already present, and it won't add
a duplicate value to the list:

.. code-block:: yaml

   postfix__maincf:

     - mydestination: [ 'example.org', 'localhost' ]

     - mydestination: [ 'example.org' ]

The result of the above configuration in :file:`/etc/postfix/main.cf`:

.. code-block:: none

   mydestination = example.org, localhost
