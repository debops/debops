Default variable details
========================

Some of the ``debops.nscd`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.


.. _nscd__ref_configuration:

nscd__configuration
--------------------

The ``nscd__*_configuration`` variables define the contents of the
:file:`/etc/nscd.conf` configuration file. The variables are merged in order
defined by the :envvar:`nscd__combined_configuration` variable, which allows
modification of the default configuration through the Ansible inventory. See
:man:`nscd.conf(5)` for possible configuration parameters and their values.

Examples
~~~~~~~~

See :envvar:`nscd__default_configuration` variable for an example of
existing configuration.

Syntax
~~~~~~

The variables contain a list of YAML dictionaries, each dictionary can have
specific parameters:

``name``
  Required. Name of the NSS service to cache. If the ``name`` parameter is set
  to ``'global'``, and the ``options`` parameter is defined, this creates
  a special "global" section at the beginning of the configuration file.

  The ``name`` parameter is used as an anchor to merge multiple configuration
  entries with the same name together.

``state``
  Optional. If not specified or ``present``, a given configuration section will
  be included in the generated configuration file. If ``absent``, a given
  configuration section will be removed from the generated file. If
  ``comment``, the configuration section will be present, but commented out.

``comment``
  Optional. String or YAML text block with a comment added before a given
  configuration section.

``options``
  Optional. A list of configuration options which should be included in a given
  configuration section. This parameter only makes sense in the "global"
  section, and otherwise should not be present in configuration entries. See
  the :man:`nscd.conf(5)` manual page for the possible configuration options.

  Each list element is defined as a YAML dictionary with specific parameters:

  ``name``
    Required. The configuration option name.

  ``value``
    Required. The configuration option value. Can be defined as a string, an
    integer or a boolean.

  ``state``
    Optional. If not specified or ``present``, a given configuration option
    will be included in the generated configuration file. If ``absent``,
    a given configuration option will be removed from the generated file. If
    ``comment``, the configuration option will be present, but commented out.

The parameters described below are based on the configuration options defined
in the :man:`nscd.conf(5)` manual page. All of the parameters are usually
required for a given configuration section to work; different ``nscd`` flavors
will use different parameters.

``enable_cache``
  Boolean. Enable or disable cache for a given NSS service.

``positive_time_to_live``
  Number of seconds after which an existing entry is removed from cache.

``negative_time_to_live``
  Number of seconds after which a non-existent entry is removed from cache.

``suggested_size``
  Size of the hash that is used to store cached entries. Its value should be
  a prime number.

``check_files``
  Boolean. If ``True``, the service checks the contents of the
  :file:`/etc/passwd`, :file:`/etc/group` and :file:`/etc/hosts` files and
  invalidates the cached entries if the files changed.

``persistent``
  Boolean. If ``True``, cached entries of a given NSS service will be kept
  between :command:`nscd` daemon restarts.

``shared``
  Boolean. If ``True``, the memory mapped for cache is shared with the service
  clients directly instead of forcing them to talk to the daemon.

``max_db_size``
  Specify the maximum size of the cache for a given NSS service.

``auto_propagate``
  Boolean. When set to ``False`` for the ``passwd`` or ``group`` service, then
  the ``.byname`` requests are not added to ``passwd.byuid`` or ``group.bygid``
  cache. This may help for tables containing multiple records for the same
  ``id`` value.
