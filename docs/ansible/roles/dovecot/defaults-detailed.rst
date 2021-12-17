.. Copyright (C) 2015      Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2017-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variables: configuration
================================

Some of ``debops.dovecot`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.


.. _dovecot__ref_configuration:

dovecot__configuration
----------------------

The ``dovecot__*_configuration`` variables define the contents of the
:file:`/etc/dovecot/dovecot.conf` configuration file. The variables are merged
in the order defined by the :envvar:`dovecot__combined_configuration` variable,
which allows modification of the default configuration through the Ansible
inventory.

See the :command:`dovecot` `configuration documentation`__ for details on the
possible configuration parameters.

.. __: https://doc.dovecot.org/settings/


Examples
~~~~~~~~

See :envvar:`dovecot__default_configuration` variable for an example of
existing configuration.

Autosubscribe users to the ``Junk`` mailbox:

.. code-block:: yaml

  dovecot__group_configuration:
  
    - section: 'mailbox_namespaces'
      options:
  
        - name: 'namespace inbox'
          options:

            - name: 'mailbox Junk'
              options:

                - name: 'auto'
                  value: 'subscribe'

Rename the ``Junk`` mailbox to ``INBOX.Spam``:

.. code-block:: yaml

  dovecot__group_configuration:
  
    - section: 'mailbox_namespaces'
      options:
  
        - name: 'namespace inbox'
          options:

            - name: 'mailbox Junk'
              state: 'absent'

            - name: 'mailbox INBOX.Spam'
              options:

                - name: 'auto'
                  value: 'subscribe'

                - name: 'special_use'
                  value: '\Junk'


.. _dovecot__ref_configuration_syntax:

Syntax
~~~~~~

The variables contain a list of YAML dictionaries, each dictionary can have
the following parameters:

``section``
  Required. Name of the section to create in the
  :file:`/etc/dovecot/dovecot.conf` file. This parameter is used as an
  "anchor", configuration entries with the same ``section`` are combined
  together and affect each other in order of appearance.

``title``
  Optional. A short description of a given configuration ``section``.
  If not defined, the ``section`` name itself will be used.

``state``
  Optional. If not specified or ``present``, the configuration section will be
  generated. If ``hidden``, the section will be generated, but without a
  section header. If ``absent``, ``ignore`` or ``init``, the configuration
  section will not be generated. If ``comment``, the section will be generated
  but commented out.

``weight``
  Optional. A positive or negative number which can be used to affect the order
  of sections in the generated configuration file. Positive numbers add more
  "weight" to the section making it appear "lower" in the file; negative
  numbers substract the "weight" and therefore move the section upper in the
  file.

``comment``
  Optional. This parameter can be used to provide a short description
  which will be included in the generated configuration file.

``options``
  Required. A list of :command:`dovecot` configuration options for a given
  ``section``.

  Note that the ``options`` parameters can be used recursively to generate
  configuration blocks of arbitrary depth (as illustrated in the example
  above).

  The options can be specified with the following parameters:

  ``name``
    Required. The name of a given :command:`dovecot` configuration option
    for a given ``section``. Options with the same ``section`` and ``name``
    hierarchy will be merged in order of appearance.

  ``option``
    Optional. An alternative to ``name`` to be used as the key in the
    ``key = value`` pairs written to the configuration.

  ``value``
    Either ``value`` or ``options`` is required. This defines the value of a
    given configuration option. It can be either a string, a boolean, a number,
    or a YAML list (elements will be joined with commas).

  ``options``
    Either ``value`` or ``options`` is required. This parameters takes a list
    of configuration sub-options, thus allowing ``options`` to be used
    recursively to generate configuration blocks of arbitrary depth (as
    illustrated in the example above).

  ``raw``
    Optional. String or YAML text block which will be included in the
    configuration file "as is". If this parameter is specified, the ``name``
    and ``value`` parameters are ignored - you need to specify the
    entire line(s) with configuration option names as well.

  ``state``
    Optional. Same values as documented above.

  ``comment``
    Optional. String or YAML text block that contains comments about a given
    configuration option.
