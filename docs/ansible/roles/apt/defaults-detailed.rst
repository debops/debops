.. Copyright (C) 2013-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _apt__ref_defaults_detailed:

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.apt`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _apt__ref_configuration:

apt__configuration
------------------

The ``apt__*_configuration`` lists defined as the default variables can be used
to manage APT configuration files located in the :file:`/etc/apt/apt.conf.d/`
directory through Ansible inventory, using the :ref:`universal_configuration`
system.

Examples
~~~~~~~~

Create a configuration file that executes a script before/after the
:command:`dpkg` command in order to set/unset extras options on some mount
points:

.. code-block:: yaml

   apt__configuration:

     - name: 'filesystem'
       filename: '02filesystem.conf'
       comment: 'Remount filesystems for package changes'
       raw: |
         Dpkg
         {
           Pre-Invoke { "/usr/local/bin/remountrw" };
           Post-Invoke { "/usr/local/bin/remountdefault" };
         };
       state: '{{ "present"
                  if (ansible_virtualization_type != "lxc")
                  else "absent" }}'

You can see other examples in the :envvar:`apt__default_configuration` default
variable.

Syntax
~~~~~~

Each configuration entry is a YAML dictionary with specific parameters:

``name``
  Required. Name of the configuration entry, used as a part of the
  configuration file name. The role will automatically append the :file:`.conf`
  suffix if it's not specified (unless the ``filename`` parameter is used).

  Configuration entries with the same ``name`` parameter are merged in order of
  appearance and can affect each other.

``filename``
  Optional. Specify the full name of the configuration file which should be
  managed. This can be useful for diverting existing files which might have
  unusual names without the :file:`.conf` suffix.

``raw``
  Optional. String or YAML text block with :man:`apt.conf(5)` configuration
  options.

``comment``
  Optional. String or YAML text block with additional comments included with
  the configuration file.

``state``
  Optional. If not specified or ``present``, the configuration file will be
  created in the :file:`/etc/apt/apt.conf.d/` directory. If ``absent``,
  specified configuration file will be removed from the host. If ``divert``,
  specified configuration file will be diverted away to not be included in the
  configuration (this is useful for files included in :file:`.deb` packages).
  If ``ignore``, a given configuration entry will not be processed at runtime.


.. _apt__ref_keys:

apt__keys
---------

This list, along with ``apt__group_keys`` and ``apt__host_keys``
and can be used to manage APT repository keys through Ansible inventory, using
the :man:`apt-key(8)` command.

.. warning:: Support for the :command:`apt-key` command is deprecated in Debian
   and might be removed in future release. Consider using the
   :ref:`apt__ref_repositories` configuration to set up APT keys with their
   respective repositories.

Examples
~~~~~~~~

Add an APT GPG key on all hosts without any conditions:

.. code-block:: yaml

   apt__keys:

     - url: 'http://example.com/apt-key.asc'

Add an APT GPG key only on hosts with Debian OS:

.. code-block:: yaml

   apt__keys:

     - url: 'http://example.com/apt-key.asc'
       state: '{{ "present"
                  if (ansible_distribution == "Debian")
                  else "absent" }}'

Add an APT GPG key only on Ubuntu hosts that have been already configured once
(delayed key configuration):

.. code-block:: yaml

   apt__keys:

     - url: 'http://example.com/apt-key.asc'
       state: '{{ "present"
                  if ((ansible_local.apt.configured | d()) | bool and
                      ansible_distribution == "Ubuntu")
                  else "absent" }}'

Syntax
~~~~~~

Each entry is a YAML dictionary with parameters that correspond to the
``apt_key`` module parameters:

``data``
  Optional. GPG key contents provided directly.

``file``
  Optional. Path to the GPG key file on the remote host.

``id``
  Optional. GPG key identifier.

``url``
  Optional. The URL of the GPG key to download and install on the host.

``keyring``
  Optional. Path to the keyring file in :file:`/etc/apt/trusted.gpg.d/` directory.

``keyserver``
  Optional. IP address or FQDN of the GPG keyserver to download the keys from.

``state``
  Optional. Either ``present`` for the key to be present (default), or
  ``absent`` for the key to be removed. The ``absent`` state might be ignored
  due to the issues with not enough information provided about the key to
  remove it.

You need to specify either an URL, path to the file or key contents for the
role to install a given GPG key.


.. _apt__ref_repositories:

apt__repositories
-----------------

The ``apt__*_repositories`` variables can be used to manage APT sources in the
:file:`/etc/apt/sources.list.d/` directory. The role supports both one-line
:file:`*.list` configuration files, as well as Deb822-format :file:`*.sources`
configuration files (with support for GPG key management), depending on the
used parameters. Configuration is defined using the
:ref:`universal_configuration` principles.

Examples
~~~~~~~~

Add an APT repository on all hosts without any conditions, using the one-line
style syntax:

.. code-block:: yaml

   apt__repositories:

     - name: 'example-repo'
       filename: 'example-repo.list'
       repo: 'deb http://example.com/debian jessie main'

Add an APT repository only on hosts with Debian OS, using the one-line syntax:

.. code-block:: yaml

   apt__repositories:

     - name: 'example-repo'
       filename: 'example-repo.list'
       repo: 'deb http://example.com/debian jessie main'
       state: '{{ "present"
                  if (ansible_distribution == "Debian")
                  else "ignore" }}'

Add an APT repository only on Ubuntu hosts that have been already configured
once, using the one-line syntax (delayed repository configuration):

.. code-block:: yaml

   apt__repositories:
     - name: 'example-repo'
       filename: 'example-repo.list'
       repo: 'deb http://example.com/ubuntu xenial main'
       state: '{{ "present"
                  if ((ansible_local.apt.configured | d()) | bool and
                      ansible_distribution == "Ubuntu")
                  else "ignore" }}'

Configure an Ubuntu PPA on Ubuntu hosts:

.. code-block:: yaml

   apt__repositories:

     - name: 'nginx-ppa'
       filename: 'nginx-ppa.list'
       repo: 'ppa:nginx/stable'
       state: '{{ "present"
                  if (ansible_distribution == "Ubuntu")
                  else "ignore" }}'

Add an APT repository with several components on all hosts without any
conditions, using Deb822 format:

.. code-block:: yaml

   apt__repositories:

     - name: 'debian'
       filename: 'debian.sources'
       types: 'deb'
       uris: 'http://deb.debian.org/debian'
       suites: 'bookworm'
       components:
         - 'main'
         - 'non-free-firmware'
         - 'contrib'
         - 'non-free'

Add third-party APT repository with GPG key URL, using Deb822 format:

.. code-block:: yaml

   apt__repositories:

     - name: 'my-repo'
       filename: 'my-repo.sources'
       uris: 'http://example.com/debian'
       signed_by: 'http://example.com/debian/example.com.asc'

Switch `Proxmox VE`__ APT repositories from the default ones which require
subscription to community versions (this example is included in documentation
as a separate file for convenience):

.. __: https://pve.proxmox.com/wiki/Package_Repositories

.. literalinclude:: examples/proxmox-ve.yml
   :language: yaml
   :lines: 1,8-

Syntax
~~~~~~

The configuration entries are defined as YAML dictionaries with specific
parameters. You can check the documentation of the `apt_repository`__ and
`deb822_repository`__ Ansible modules for available options.

.. __: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_repository_module.html
.. __: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/deb822_repository_module.html

The parameters below are used for both one-line and Deb822 formats:

``name``
  Required. An identifier for a specific APT source configuration, not used
  otherwise. Entries with the same ``name`` parameter are merged together in
  order of appearance and can affect each other.

``filename``
  Required. Name of the configuration file stored in the
  :file:`/etc/apt/sources.list.d/` directory. The :file:`.list` and
  :file:`.sources` suffixes are automatically stripped from the specified
  filename and added as necessary.

  When the Deb822 format is used, this parameter is used in the
  ``X-Repolib-Name`` field, as well as the name of the keyring with the signing
  GPG key.

``mode``
  Optional. The file mode in octal. Needs to be quoted to be interpreted
  correctly by Ansible.

``state``
  Optional. If not specified or ``present``, a given APT source will be
  configured on the host. If ``ignore``, a given configuration entry will not
  be processed during role execution.

  If ``divert``, an existing configuration file with the specified ``filename``
  will be diverted to disable it without removing it (this is useful for APT
  sources included in packages). This only works if the ``repo`` and ``uris``
  parameters are not specified to avoid conflicts with Ansible modules that
  manage the APT repositories.

  If ``absent``, the specified APT source will be removed from the host. If the
  ``repo`` and ``uris`` are not specified, the role assumes that a diverted
  configuration is present and the diversion will be removed in this case.

The parameters below are used for one-line format APT sources (the
:file:`*.list` configuration files):

``repo``
  Required. The APT repository to configure, in the one-line format described
  in the :man:`sources.list(5)` manual page.

``codename``
  Optional. Override the distribution codename to use for PPA repositories.

The parameters below are used for Deb822 format APT sources (the
:file:`*.sources` configuration files):

``uris``
  Required. Must specify the base of the Debian distribution archive, from which
  APT finds the information it needs. Multiple URIs can be specified in a list.

``architectures``
  Optional. Architectures to search within repository, for example ``amd64``
  (default) or ``i386``.

``components``
  Optional. Specify different sections of one distribution version present in
  Suite, such as ``main`` (default), ``non-free-firmware``, ``contrib``,
  ``non-free``

``suites``
  Optional. Can take the form of a distribution release name (default).

``signed_by``
  Optional. Either:

  - a URL to a GPG key

  - absolute path to a keyring file stored in the filesystem

  - one or more fingerprints of keys stored in the :file:`/etc/apt/trusted.gpg`
    kerying or in one of the keyrings in the :file:`/etc/apt/trusted.gpg.d/`
    directory

  Keys downloaded via the URL will be stored in :file:`/etc/apt/keyrings/`
  directory (automatically created if absent), with filenames based on the
  ``filename`` parameter.

``types``
  Optional. Which types of packages to look for from a given source; either
  binary ``deb`` (default) or source code ``deb-src``.

The role supports most of the ``deb822_repository`` options, check its
documentation for in-depth explanation.


.. _apt__ref_auth_files:

apt__auth_files
---------------

The ``apt__*_auth_files`` lists can be used to create and manage
:file:`/etc/apt/auth.conf.d/` configuration files which caontain authentication
credentials required by specific APT repositories. The format and more details
about these files can be found in :man:`apt_auth.conf(5)` manual page. The
:ref:`debops.reprepro` role can be used to create APT repositories that require
authentication.

.. note:: Private APT repositories accessible over HTTPS might result in issues
   during host bootstrapping due to lack of trusted Root CA certificates on the
   host. You can avoid that by applying the :ref:`debops.pki` role before the
   actual bootstrap playbook, for example:

   .. code-block:: console

      $ debops run service/python_raw service/pki -l <host> -u root

   This command will prepare the host for use via Ansible and set up PKI
   environment, including custom Root CA certificates.

This functionality is also available in the :ref:`debops.keyring` role for use
by other Ansible roles via dependent role variables.
See :ref:`keyring__ref_dependent_apt_auth_files` for more details.

Examples
~~~~~~~~

Provide credentials for a private APT repository, with password stored in the
:file:`secret/` directory managed by the :ref:`debops.secret` role. The APT
repository is managed by the :ref:`debops.reprepro` role which uses the
:ref:`debops.nginx` role to manage the authentication credentials.

.. code-block:: yaml

   apt__auth_files:

     - name: 'private_repo'
       machine: 'https://repo.example.org/debian'
       login: 'username'
       password: '{{ lookup("password", secret + "/credentials/repo"
                                               + "/nginx/htpasswd"
                                               + "/apt_access/username") }}'

Syntax
~~~~~~

The variables are defined as a list of YAML dictionaries .Each configuration
entry defines a separate file in the :file:`/etc/apt/auth.conf.d/` directory.
The state and contents of the file are specified using specific parameters:

``name``
  Required. Name of the configuration file with authentication credentials, can
  contain :file:`.conf` suffix which will be stripped. Entries with the same
  ``name`` parameter are merged together using :ref:`universal_configuration`
  and can affect each other in order of appearance.

``machine``
  Required. The URL of the APT repository that requires the following
  credentials.

``login``
  Required. The username expected by the APT repository during HTTP Basic
  Authentication.

``password``
  Required. The password expected by the APT repository during HTTP Basic
  Authentication. It can be stored in the :file:`secret/` directory and
  retrieved from there if needed.

``state``
  Optional. If not defined or ``present``, a given configuration file will
  created on the host. If ``absent``, a given configuration file will be
  removed from the host. If ``ignore``, a given entry will not be evaluated
  during role execution.

``comment``
  Optional. String or YAML text block with additional comments included in the
  generated configuration file.


.. _apt__ref_sources:

apt__sources
------------

The ``apt__*_sources`` lists define the contents of the
:file:`/etc/apt/sources.list` configuration file. The default configuration is
composed from multiple entries at runtime; each entry conditionally updates the
configuration based on the host facts. For convenience, role defaults are split
into :ref:`multiple variables <apt__ref_sources_defaults>` based on the OS
distribution.

.. note:: The :file:`/etc/apt/sources.list` should be focused only on the
   official OS repositories. If you want to add third-party or external APT
   repositories to your hosts, consider using the :ref:`apt__ref_repositories`
   variables to put them in the :file:`/etc/apt/sources.list.d/` directory.

Examples
~~~~~~~~

Add an archive repository in :file:`/etc/apt/sources.list` configuration file:

.. code-block:: yaml

   apt__sources:

     - name: 'debian-archive'
       uri: 'http://archive.debian.org/debian'
       suite: 'sarge'
       components: [ 'main' ]

Add custom options to existing ``debian-release`` APT source configuration (see
:man:`sources.list(5)` manual page for details):

.. code-block:: yaml

   apt__sources:

     - name: 'debian-release'
       options:
         - arch: [ 'amd64', 'i386' ]
         - signed-by: '{{ "/usr/share/keyrings/debian-archive-"
                          + ansible_distribution_release
                          + "-stable.gpg" }}'

To see more examples, you can check the :envvar:`apt__debian_sources`,
:envvar:`apt__devuan_sources` and :envvar:`apt__ubuntu_sources` default
variables.

Syntax
~~~~~~

Configuration is defined using :ref:`universal_configuration` syntax. Each
entry is a YAML dictionary with specific parameters (singular spelling is for
strings, plural spelling is for YAML lists):

``name``
  Required. Repository identifier, not used otherwise. Entries with the same
  ``name`` parameter are merged together in order of appearance and can affect
  each other. This is used extensively in the default configuration of the
  role.

``raw``
  Optional. String or YAML text block with :man:`sources.list(5)` one-line
  repository format entries included in the configuration file as-is. If this
  parameter is specified, it takes precedence over other parameters.

``uri`` or ``uris``
  Optional. The URI or other method known by APT (see :man:`sources.list(5)`)
  for a given APT source. It is possible to specify multiple entries as a list,
  they will be treated as one. The ``uris`` lists from multiple entries with
  the same ``name`` parameter are combined together.

``type`` or ``types``
  Optional. What type of the packages are used for this source. It can be
  either a string of 1 type, or a list of types. Known source types: ``deb``,
  ``deb-src``. If not set, role will use the ``apt__source_types`` value. The
  ``types`` lists from multiple entries with the same ``name`` parameter are
  combined together.

``suite`` or ``suites``
  Optional. Name of the "suite" to use for this source. The suite is usually
  a release name like ``jessie``, ``xenal``, or a "release class" like
  ``stable``, ``oldstable``, ``testing``, or a directory path in case of simple
  repositories (which needs to end with a slash). It can also be a list of
  releases. The ``suites`` lists from multiple entries with the same ``name``
  parameter are combined together.

``component`` or ``components``
  Optional. Name of a repository component or section to enable, for example
  ``main``, ``contrib``, ``non-free``, ``universe``, ``restricted``,
  ``multiverse``. It can also be a list of components. The ``components`` lists
  from multiple entries with the same ``name`` parameter are combined together.

``options``
  Optional. List of YAML dictionaries which describe options for a given APT
  repository. Each dictionary key is an option name, and dictionary value is an
  option value. Values can be strings or YAML lists. The ``options`` lists in
  configuration entries with the same ``name`` parameter are combined together.

  Option names will be written in the configuration file as-is. You should use
  the short option names specified in brackets in the :man:`sources.list(5)`
  manual page to conform to the one-line format.

``state``
  Optional. If not specified or ``present``, a given APT source will be
  included in the generated :file:`/etc/apt/sources.list` configuration file.
  If ``absent``, a given APT source will not be included in the generated file.
  If ``comment``, the APT source will be included, but it will be commented
  out. If ``ignore``, a given entry will not be processed during role
  execution.

``comment``
  Optional. A string or a YAML text block with comments about the given APT
  source.

``separate``
  Optional, boolean. If ``True`` (default), a given APT source will be visually
  separated from the next one in the generated configuration file; if
  ``False``, no separation will be added.
