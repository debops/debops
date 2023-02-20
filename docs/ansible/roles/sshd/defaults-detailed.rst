.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.sshd`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _sshd__ref_configuration:

sshd__configuration
-------------------

The ``sshd__*_configuration`` default variables define the contents of the
:file:`/etc/ssh/sshd_config` configuration file. The role uses
:ref:`universal_configuration` to generate this configuration file. You can
read the :man:`sshd_config(5)` manual page for details about SSH daemon
configuration options.

Examples
~~~~~~~~

Enable debug logs in the SSH service to diagnose connection issues:

.. code-block:: yaml

   sshd__configuration:

     - LogLevel: 'DEBUG'

Define a list of UNIX groups allowed to access the SSH service:

.. code-block:: yaml

   sshd__configuration:

     - AllowGroups: [ 'admins', 'sshusers', 'sftponly' ]

This is an example of the "simple syntax" definition. Note that the PAM
configuration used in the role is much more flexible than the ``AllowGroups``
option.

Configure SSH service to accept plaintext password authentication on the
``root`` UNIX account (you shouldn't do this in production environments!):

.. code-block:: yaml

   sshd__configuration:

     - name: 'PermitRootLogin'
       value: True

Configure SSH daemon to listen on additional TCP ports for network connections:

.. code-block:: yaml

   sshd__configuration:

     - name: 'Port'  # default
       state: 'present'

     - name: 'Port_2222'
       option: 'Port'
       value: 2222
       copy_id_from: 'Port'

     - name: 'Port_3322'
       option: 'Port'
       value: 3322
       copy_id_from: 'Port'

Alternatively, you can specify a list of TCP ports using the
:envvar:`sshd__ports` variable which will generate the corresponding
configuration options.

You can check the :envvar:`sshd__original_configuration` variable to see an
example configuration that comes with the ``openssh-server`` Debian package.
The changes added by DebOps are set in the
:envvar:`sshd__default_configuration` variable which is also a good source of
examples.

Syntax
~~~~~~

Each configuration entry in the list is a YAML dictionary. The simple form of
the configuration uses the dictionary keys as the parameter names, and
dictionary values as the parameter values. Remember that the parameter names
need to be specified in the exact case they are used in the documentation (e.g.
``PermitRootLogin``, ``ClientAliveCountMax``), otherwise they will be
duplicated in the generated configuration file. It's best to use a single YAML
dictionary per configuration option.

If the YAML dictionary contains the ``name`` key, the configuration switches to
the complex definition mode, with configuration options defined by specific
parameters:

``name``
  Required. Specify the name of the SSH daemon configuration parameter. The
  case is important and should be the same as specified in the configuration
  file or the :man:`sshd_config(5)` manual page, otherwise the configuration
  entries will be duplicated.

  Multiple configuration entries with the same ``name`` parameter are merged
  together in order of appearance. This can be used to modify parameters
  conditionally.

``option``
  Optional. If a given :man:`sshd_config(5)` configuration option needs to be
  specified more than once (for example ``Port``, ``ListenAddress`` or
  ``Match``), you need to use unique ``name`` parameters in each case. The
  ``option`` parameter can be used to specify the actual option name in such
  case.

``raw``
  Optional. String or YAML text block with :man:`sshd_config(5)` configuration
  options which will be included as-is in the generated configuration file.
  When the ``raw`` parameter is specified, ``name`` and ``value`` options are
  not included so they need to be present explicitly. Jinja statements can be
  used to further augment the generated output.

``value``
  Required. The value of a given configuration option. It can be a string,
  number, ``True``/``False`` boolean or a YAML list. List entries will be
  joined with the space character

  Lists can use simple strings and numbers, or can be defined using YAML
  dictionary with specific parameters:

  ``name``
    The value of a given list element (string, number).

  ``weight``
    Positive or negative number, by default ``0``. Weight can be used to affect
    the order of list elements, with negative weight resulting in a given
    element being moved "up" towards the start of the list, and positive number
    resulting in an element being moved "down" towards the end of the list.

``state``
  Optional. If not specified or ``present``, a given configuration parameter
  will be present in the generated configuration file. If ``absent``, a given
  parameter will be removed from the configuration file. If ``comment``, the
  parameter will be present but commented out.

  If the state is ``init``, the parameter will be "primed" in the configuration
  pipeline, but it will be commented out in the generated configuration file.
  Any subsequent configuration entry with the same ``name`` will switch the
  state to ``present`` - this is used to define the default parameters in the
  role which can be changed via the Ansible inventory.

  If the state is ``ignore``, a given configuration entry will not be evaluated
  during role execution. This can be used to activate configuration entries
  conditionally.

``config``
  Optional. String or YAML text block with :man:`sshd_config(5)` configuration
  options specified as-is (boolean variables should be specified as ``yes`` or
  ``no``, not the Jinja/YAML equivalents). The contents will be included
  indented after a given configuration option. This parameter is meant to be
  used with the ``Match`` configuration option to specify ``Match`` options
  used by the SSH service.

``comment``
  Optional. String or YAML text block with additional comments for a specific
  configuration option.

``separator``
  Optional, boolean. If specified and ``True``, a given configuration option
  will be separated by an empty line from previous options. Used for cosmetic
  purposes to better match the original :file:`/etc/ssh/sshd_config`
  configuration file.

``weight``
  Optional. Positive or negative number, by default ``0``. Weight can be used
  to affect the order of configuration options (important, first option sets
  the configuration in the SSH daemon), with negative weight resulting in
  a given configuration being moved "up" in the generated config file, and
  positive number resulting in an option being moved "down" in the generated
  config file.

``copy_id_from``
  Optional. Name of a configuration entry (``name`` parameter), which should be
  used as an "anchor" for a given entry. This parameter can be used to group
  related configuration options together - for example multiple ``Port``
  options (see the examples section above). The ``weight`` parameter can be
  used to fine-tune the order of options in the generated configuration file.
