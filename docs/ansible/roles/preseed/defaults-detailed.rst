.. Copyright (C) 2015-2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.preseed`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _preseed__ref_definitions:

preseed__definitions
--------------------

The ``preseed__*_definitions`` variables are used to define what Debian Preseed
configuration files and :file:`postinst.sh` scripts will be available on the
Preseed server. Each combination consists of a preseed "flavor" which is used
to provide different combination of configuration options at boot time, and
a "release" which defines the Debian releases that will be able to use a given
"flavor"[#]_.

Examples
~~~~~~~~

Create a new Preseed definition with modifications to the default configuration
which will configure the host as being located in Germany with German UI by
default. The ``debian-de.seed.example.org`` DNS record needs to point to the
Preseed server for this to work as expected. Ensure that a few Debian releases
can be used if needed.

.. note:: This is just an example; locale configuration is set by default based
   on the facts of the :ref:`debops.locales` role applied on the Preseed server
   host. You shouldn't have to set these preferences in most cases.

.. code-block:: yaml

   # Variable which holds Preseed modifications used in multiple definitions
   preseed_options_german_locale:

     - name: 'debian-installer/locale'
       value: 'de_DE.UTF-8'
       state: 'present'

     - name: 'keyboard-configuration/xkb-keymap'
       value: 'de'
       state: 'present'

   preseed__definitions:

     - name: 'debian-stretch-de'
       flavor: 'debian-de'
       release: 'stretch'
       options: '{{ preseed_options_german_locale }}'

     - name: 'debian-buster-de'
       flavor: 'debian-de'
       release: 'buster'
       options: '{{ preseed_options_german_locale }}'

     - name: 'debian-bullseye-de'
       flavor: 'debian-de'
       release: 'bullseye'
       options: '{{ preseed_options_german_locale }}'

You can find a list of the default Preseed definitions in the
:envvar:`preseed__default_definitions` variable.

Syntax
~~~~~~

The Preseed definitions use the :ref:`universal_configuration` system to define
configuration entries. The variables are combined using
:envvar:`preseed__combined_definitions` variable which defines the general
order of merging the entries.

Each definition is created using a specific set of parameters:

``name``
  Required. An indentifier of a given Preseed definition, not used otherwise.
  Must be unique across all definitions. Entries with the same ``name`` are
  merged in order of appearance and can affect each other.

``flavor``
  Required. Name of the "flavor" of a particular Debian Preseed. Multiple
  definitions can have the same flavor (this is mandatory if you want to
  support more than one Debian release at a time). Flavors need to be
  configured in the DNS so that hosts can reach the Preseed server while
  booting.

``release``
  Required. Name of a Debian release (``bullseye``, ``buster``, etc.) which can
  use a particular Debian Preseed definition. Multiple definitions can have the
  same release as long as they use different flavors.

``state``
  Optional. If not defined or ``present``, a given Preseed definition will be
  created on the host. If ``absent``, a given definition will be removed from
  the host (the ``<release>/`` directory itself will be removed).

``options``
  Optional. A list of :file:`preseed.cfg` configuration options defined using
  the :ref:`preseed__ref_configuration` format. Because there are usually
  multiple definitions for a given "flavor", it's easier to put options you
  want to change in a separate variable which can be referenced in the
  inventory using Jinja expansion.

  The role uses the "configuration template" defined by the main
  :ref:`preseed__ref_configuration` variables as the base for each Preseed
  definition. The options specified here will override the ones defined
  elsewhere. Since many options are commented out by default, it's good
  practice to always specify the state ``present`` as needed to be sure that
  the option is in the correct state.

``root_sshkeys``
  Optional. YAML list of SSH public keys which should be added to the UNIX
  ``root`` account on the provisioned host using a :file:`postinst.sh` script.
  The SSH keys specified here will be combined with the ones specified in the
  :envvar:`preseed__root_sshkeys` list.

``admin_username``
  Optional. Name of the UNIX administrative account which should be configured
  for full :command:`sudo` access and provisioned with administrator SSH public
  keys. The UNIX account will not be created by the :file:`postinst.sh` script;
  you need to use the relevant Debian Preseed options to either create it
  automatically or allow the manual creation during provisioning.

``admin_sshkeys``
  Optional. YAML list of SSH public keys which should be added to the UNIX
  administrative account on the provisioned host using a :file:`postinst.sh`
  script. The SSH keys specified here will be combined with the ones specified
  in the :envvar:`preseed__admin_sshkeys` list.

``postinst_commands``
  Optional. YAML text block with :man:`bash(1)` commands which will be executed
  at the end of the provisioning process by the :file:`postinst.sh` script
  using ``eval``. The commands are executed one by one so you should use simple
  expressions without loops or conditional statements. Commands specified here
  will be executed after the ones specified in the
  :envvar:`preseed__debian_postinst_commands` variable.


.. _preseed__ref_configuration:

preseed__configuration
----------------------

The ``preseed__*_configuration`` variables define the default contents of the
:file:`preseed.cfg` configuration files. They can be thought of as a "template"
for Preseed configurations which can be further augmented in separate "flavors"
or OS releases using the ``options`` parameters.

Examples
~~~~~~~~

Enable network console in Debian Installer on all Preseed flavors and releases.
A file with SSH public keys should be published on a reachable host.

.. code-block:: yaml

   preseed__configuration:

     - name: 'anna/choose_modules'
       value: 'network-console'
       state: 'present'

     - name: 'network-console/authorized_keys_url'
       value: 'http://192.0.2.1/openssh-key'
       state: 'present'

The original Preseed configuration, based on the `Example Debian Stable preseed
file`__ can be found in the :envvar:`preseed__original_configuration` variable.
Customizations to the original options included by default in the role can be
found in the :envvar:`preseed__default_configuration` variable.

.. __: https://www.debian.org/releases/stable/example-preseed.txt

Syntax
~~~~~~

The Preseed configuration is based on the :ref:`universal_configuration`
system. The separate variables are merged in the
:envvar:`preseed__combined_configuration` variable which defines the merge
order of configuration entries. Configuration is defined using a list of YAML
dictionaries with specific parameters:

``name``
  Required. Name of the Preseed configuration option. Entries with the same
  ``name`` parameter are merged in order of appearance and can affect each
  other.

``option``
  Optional. If a configuration option has multiple "versions", each needs to be
  defined using an unique ``name`` parameter to avoid overwriting. In this case
  the ``option`` parameter can be used to specify the actual name of the
  Preseed configuration option stored in the config file.

``comment``
  Optional. A string or YAML text block with additional comments added to an
  option. The strings ``${flavor}`` and ``${release}`` inside comments will be
  replace with the current definition's "flavor" and "release" values.

``state``
  Optional. If not specified or ``present``, the configuration option will be
  included in the generated configuration file. If ``absent``, a given option
  will not be included in the generated file. If ``comment``, the option will
  be included but commented out (inactive). If ``hidden``, a configuration
  option will not be added but its comments will (this is useful to add
  separate comment sections). If ``ignore``, a given entry will not be
  evaluated during role execution.

  It's suggested to use ``present`` explicitly if any options are defined in
  the inventory to ensure that the customized options are uncommented, since
  most of the existing options are commented out by default.

``owner``
  Optional. Each Preseed option has an "owner" package, usually ``d-i`` as in
  Debian-Installer which will be used as default if this parameter is not
  specified. Some options have different owners.

``type``
  Optional. Specify the type of a given Preseed option, either a ``string``,
  ``boolean``, ``select``, ``multiselect`` or ``password``. If not specified,
  the role will try to guess the correct type based on the defined value
  - strings and booleans are recognized automatically. The role will default to
  ``string`` if the correct type cannot be determined.

``seen``
  Optional, boolean. If present and ``False``, the role will mark a given
  option as "not seen" by the Debian-Installer. This is supposed to allow
  manual confirmation of a given option, but this hasn't been observed in
  practice - further testing is needed.

``value``
  The value of a given option. This can be either a string, a YAML list which
  will be concatenated into a string separated by spaces, a boolean
  ``True``/``False`` or a YAML text block with multiline value. Empty strings
  are permitted.

  If a YAML list is used, multiple entries with the same ``name`` parameter
  will merge the lists together. To reset an existing list, use an empty string
  in a separate entry.

.. rubric:: Footnotes

.. [#] The "release" mechanism is explicitly required by Debian-Installer which
   will use the URL in the form ``https://<host>/d-i/<release>/./preseed.cfg``
   to retrieve the configuration file automatically.
