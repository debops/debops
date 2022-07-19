.. Copyright (C) 2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.gitlab`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _gitlab__ref_ssl_symlinks:

gitlab__ssl_symlinks
--------------------

GitLab Omnibus uses private keys and X.509 certificates provided in the
:file:`/etc/gitlab/ssl/` directory to configure encrypted connection support
inside of its environment. The ``gitlab__ssl_*_symlinks`` variables can be used
to create symlinks to the private keys and certificates stored elsewhere in the
filesystem; this is used to integrate GitLab Omnibus with the PKI
infrastructure managed by the :ref:`debops.pki` Ansible role.

Examples
~~~~~~~~

You can see the default set of private key and X.509 certificate symlinks
defined in the :envvar:`gitlab__ssl_default_symlinks` variable.

Syntax
~~~~~~

The variables are defined as a list of YAML dictionaries, with specific
parameters:

``link``
  Required. Name of the symlink in the :file:`/etc/gitlab/ssl/` directory which
  will point to a specific resource. GitLab Omnibus expects the :file:`*.key`
  and :file:`*.crt` files respectively, with names based on the DNS names used
  for different resources, for example the service addresses.

``src``
  Required. Absolute path to a file which will be symlinked to in the
  :file:`/etc/gitlab/ssl/` directory.

``state``
  Optional. If not specified or ``link``, a given symlink will be created or
  updated if necessary. If ``absent``, a given symlink will be removed.


.. _gitlab__ref_configuration:

gitlab__configuration
---------------------

The ``gitlab__*_configuration`` variables define the contents of the
:file:`/etc/gitlab/gitlab.rb` configuration file, used to configure GitLab
Omnibus installation. You can find an example configuration file with complete
contents in the :file:`/opt/gitlab/etc/gitlab.rb.template` file, which might be
useful as a reference. You can also use `online GitLab Omnibus documentation`__
to find more details about configuring GitLab Omnibus.

The role uses :ref:`universal_configuration` system to integrate the default
and inventory variables during configuration file generation.

.. __: https://docs.gitlab.com/omnibus/settings/

Examples
~~~~~~~~

You can see the default configuration defined in the role in
:envvar:`gitlab__default_configuration` variable to see examples of various
configuration options.

Syntax
~~~~~~

The variables are defined as lists of YAML dictionaries, each entry can
configure either a simple variable, a list or a "section" of configuration
options. Entries are defined using specific parameters:

``name``
  Required. Name of the variable to define in the configuration file, or
  a configuration section (for example ``gitlab_rails``) if the ``options``
  parameter is also included. Configuration entries with the same ``name``
  parameter are merged together and can affect each other.

``title``
  Optional. String or YAML text block with a short "title" comment which
  describes a given option.

``comment``
  Optional. String or YAML text block with a longer "description" comment.

``value``
  The value of a given configuration option. It can be a string, a number,
  a boolean variable or a YAML list (usually with strings).

``raw``
  If the ``raw`` parameter is specified, the ``name`` and ``value`` parameters
  are not included in the generated configuration file. The contents of the
  ``raw`` parameter (string or YAML text block) will be included in the
  generated configuration file as-is. You can use Jinja inside of the ``raw``
  parameter to augment generated configuration as needed. This is useful with
  more complex configuration options such as dictionaries or Ruby code.

``state``
  Optional. If not specified or ``present``, a given configuration option will
  be included in the generated file. If ``absent``, a given configuration
  option will not be included in the finished file. If ``comment``, the option
  will be included but commented out. If ``ignore``, a given configuration
  entry will not be evaluated during role execution.

``separator``
  Optional. Add an empty line before a given configuration option, for
  aesthetic purposes.

``options``
  Optional. A list of configuration options which belong to a given "section"
  (in Ruby terms, keys and values of a given dictionary). Each element of the
  list is a YAML dictionary with the same paraneters as the main configuration;
  the ``name`` parameter specifies the dictionary key and ``value`` or ``raw``
  parameters can be used to define it.
