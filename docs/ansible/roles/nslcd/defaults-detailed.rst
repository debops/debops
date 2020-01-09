Default variable details
========================

Some of the ``debops.nslcd`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.


.. _nslcd__ref_configuration:

nslcd__configuration
--------------------

The ``nslcd__*_configuration`` variables define the contents of the
:file:`/etc/nslcd.conf` configuration file. The variables are merged in order
defined by the :envvar:`nslcd__combined_configuration` variable, which allows
modification of the default configuration through the Ansible inventory.  See
:man:`nslcd.conf(5)` for possible configuration parameters and their values.

Examples
~~~~~~~~

See :envvar:`nslcd__default_configuration` variable for an example of
existing configuration.

Limit UNIX accounts and groups that appear on the server based on the ``host``
attribute. The value can be:

- ``host.example.org`` or ``host`` (specific host)
- ``*.example.org`` (specific subdomain)
- ``*`` (all hosts)

.. code-block:: yaml

   nslcd__configuration:

     - name: 'filter_passwd_group'
       comment: 'Limit which UNIX accounts and groups are present on a host'
       raw: |
         filter passwd (&(objectClass=posixAccount)(|(host={{ ansible_fqdn }})(host=\2a.{{ ansible_domain }})(host={{ ansible_hostname }})(host=\2a)))
         filter group  (&(objectClass=posixGroupId)(|(host={{ ansible_fqdn }})(host=\2a.{{ ansible_domain }})(host={{ ansible_hostname }})(host=\2a)))
         filter shadow (&(objectClass=shadowAccount)(|(host={{ ansible_fqdn }})(host=\2a.{{ ansible_domain }})(host={{ ansible_hostname }})(host=\2a)))

Send debug logs to ``syslog`` to allow easier debugging:

.. code-block:: yaml

   nslcd__configuration:

     - name: 'log'
       value: 'syslog debug'


Syntax
~~~~~~

The variables contain a list of YAML dictionaries, each dictionary can have
specific parameters:

``name``
  Required. Name of the :man:`nslcd.conf(5)` configuration option. The
  configuration options with the same ``name`` parameter will be merged in
  order of appearance.

  If you want to specify multiple configuration options with the same name,
  make sure that the ``name`` parameter is unique and use the ``option``
  parameter to specify the "real" option name to use.

``value``
  Required. The value of a given configuration option. It can be either
  a string, or a YAML list (elements will be joined with spaces).

``option``
  Optional. When configuration options are specified multiple times, this
  parameter can be used to specify the option name instead of the ``name``
  parameter.

``map``
  Optional. Name of the "map" to configure, inserted between the option name,
  and its value. You can find more about map usage in the :man:`nslcd.conf(5)`
  documentation.

``raw``
  Optional. String or YAML text block which will be included in the
  configuration file "as is". If this parameter is specified, ``name``,
  ``option`` and ``map`` parameters are ignored - you need to specify the
  entire line(s) with configuration option names as well.

``state``
  Optional. If not defined or ``present``, a given configuration option will be
  included in the generated configuration file. If ``absent``, a given
  configuration option will be removed from the generated file. If ``comment``,
  the option will be included, but commented out and inactive. If ``ignore``,
  the role will not evaluate the configuration entry during template
  generation, this can be used for conditional activation of
  :man:`nslcd.conf(5)` configuration options.

``comment``
  Optional. String or YAML text block that contains comments about a given
  configuration option.

``separator``
  Optional, boolean. If ``True``, and additional empty line will be added
  before a given configuration option to separate it from the other options for
  readability.
