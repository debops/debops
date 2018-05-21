Default variable details
========================

Some of ``debops.lxc`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1


.. _lxc__ref_configuration:

lxc__configuration
------------------

The ``lxc__*_configuration`` variables define the contents of the configuration
files in the :file:`/etc/lxc/` directory. Each variable is a list of YAML
dictionaries, each dictionary can contain specific parameters:

``name``
  Required. Name of the configuration file, saved as
  :file:`/etc/lxc/<name>.conf`. This parameter is also used as a key while
  merging multiple configuration entries.

  Please note that the ``lxc`` package creates the
  :file:`/etc/lxc/default.conf` configuration file. This file is not managed by
  the :ref:`debops.lxc` role and it's best not to overwrite it so that package
  upgrades don't have issues. In other words, don't use the ``default`` as the
  name of the configuration file.

``filename``
  Optional. Custom filename of the specified configuration. You need to include
  the ``.conf`` prefix in the filename.

``state``
  Optional. Specify desired state of a given configuration file. Possible
  states:

  - ``present`` or not specified: the file will be generated.

  - ``absent``: the file will be removed if it exists, otherwise it won't be
    generated.

  - ``ignore``: A given configuration entry will be ignored by the role.

``comment``
  Optional. A string or YAML text block with a comment added at the top of the
  configuration file.

``raw``
  Optional. A string or YAML text block with LXC configuration, which will be
  added as-is at the end of the configuration file.

``options``
  Optional. A YAML list of LXC configuration options defined as YAML
  dictionaries. Each dictionary key is an ``lxc.*`` configuration key, and the
  dictionary is the configuration value, defined as a string. The ``options``
  lists from multiple configuration entries with the same ``name`` will be
  merged together.

  If the dictionary has ``name`` and ``value`` keys, a given dictionary is
  interpreted with specific parameters:

  ``name``
    The LXC configuration option. It's used as a key to merge configuration
    options. If your configuration uses the same configuration options multiple
    times, you need to differentiate each one, for example with a prefix or
    suffix.

  ``alias``
    Optional. An alternative option name which will be used in the
    configuration file. This can be used to allow multiple LXC options with the
    same name.

  ``value``
    The value of an LXC configuration option, a string.

  ``comment``
    Option. a string or a YAML text block with a comment added to a given LXC
    configuration option.

  ``separator``
    Optional, boolean. If ``True``, a blank line will be added before the
    option. It can be used to separate configuration into sections for better
    readability.

  ``state``
    Optional. Set a custom state for a given LXC configuration option. Known
    states:

    - ``present`` or not specified: the option will be present in the generated
      configuration file.

    - ``absent``: the option will not be present in the generated configuration
      file.

    - ``comment``: the option will be present, but commented out.

    - ``ignore``: a given entry will be ignored during configuration file
      generation.

Examples
~~~~~~~~

Change the default LXC configuration file used to generate LXC containers to
unprivileged:

.. code-block:: yaml

   lxc__configuration:

     - name: 'lxc'
       options:

         - name: 'lxc.default_config'
           value: '/etc/lxc/unprivileged.conf'

The same change, written as a simple YAML dictionary

.. code-block:: yaml

   lxc__configuration:

     - name: 'lxc'
       options:
         - 'lxc.default_config': '/etc/lxc/unprivileged.conf'
