.. Copyright (C) 2013-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2018 DebOps <https://debops.org/>
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

.. _apt__ref_conf:

apt__conf
---------

This list, along with ``apt__group_conf`` and ``apt__host_conf`` can be used
to manage APT configuration files through Ansible inventory. Each entry is a
YAML dictionary with keys and values the same as the ones used by the
`Ansible ansible.builtin.copy module`_. See its documentation for parameter
advanced usage and syntax.

Here are some more important parameters:

``item.dest`` or ``item.name`` or ``item.path``
  Required. Filename on the remote host. The role will automatically prefix it
  with ``item.priority`` and put it in the right directory.

``item.priority``
  Optional. Priority that prefix the filename to order the instruction with the
  different configuration files. If not specified, priority ``60`` is used by
  default.

``item.src``
  Path to the source file on the Ansible Controller. Alternatively you can use
  ``item.content`` to provide the file contents directly in the inventory.

``item.content``
  String or YAML text block with the file contents to put in the destination
  file. Alternatively you can use ``item.src`` to provide the path to the
  source file on Ansible Controller.

``item.state``
  Optional. If not specified, or if specified and ``present``, the file(s) will
  be created. If specified and ``absent``, file will be removed.

Examples
~~~~~~~~

Copy file from the Ansible Controller to all remote hosts:

.. code-block:: yaml

   apt__conf:
     - name: personal
       src: 'path/to/apt.conf.d/02personnal.conf'
       priority: '99'


Create a configuration file that calls script before/after DPKG in order to
set/unset extras options on some mount points :

.. code-block:: yaml

   apt__host_conf:
     - name: filesystem
       priority: '02'
       content: |
         # This file is managed remotely, all changes will be lost
         {% if (ansible_virtualization_type != 'lxc') %}
         Dpkg
         {
           Pre-Invoke { "/usr/local/bin/remountrw" };
           Post-Invoke { "/usr/local/bin/remountdefault" };
         };

.. _apt__ref_keys:

apt__keys
---------

This list, along with ``apt__group_keys`` and ``apt__host_keys``
and can be used to manage APT repository keys through Ansible inventory.  Each
entry is a YAML dictionary with parameters that correspond to the ``apt_key``
module parameters:

``data``
  Optional. GPG key contents provided directly.

``file``
  Optional. Path to the GPG key file on the remote host.

``id``
  Optional. GPG key identifier.

``keyring``
  Optional. Path to the keyring file in :file:`/etc/apt/trusted.gpg.d/` directory.

``keyserver``
  Optional. IP address or FQDN of the GPG keyserver to download the keys from.

``state``
  Optional. Either ``present`` for the key to be present (default), or
  ``absent`` for the key to be removed. The ``absent`` state might be ignored
  due to the issues with not enough information provided about the key to
  remove it. See also ``architecture``, ``distribution`` and
  ``distribution_release`` parameters.

``url``
  Optional. The URL of the GPG key to download and install on the host.

If you don't specify the ``state`` parameter directly, you can use additional
parameters that control how the specified key is managed:

``architecture``
  Optional. Name of the system architecture, for example ``amd64`` or ``i386``.
  If the current host has the specified architecture, the key will be
  installed. Only one architecture can be specified at a time, use the
  ``state`` parameter for more complex conditions.

``distribution``
  Optional. Name of the OS distribution. If the current host has the specified
  distribution, the key will be installed. Only one distribution can be
  specified at a time, use the ``state`` parameter for more complex conditions.

``distribution_release``
  Optional. Name of the OS release. If the current host has the specified
  distribution, the key will be installed. Only one release can be specified at
  a time, use the ``state`` parameter for more complex conditions.

You need to specify either an URL, path to the file or key contents for the
role to install a given GPG key.

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
       distribution: 'Debian'

Add an APT GPG key only on Ubuntu hosts that have been already configured once
(delayed key configuration):

.. code-block:: yaml

   apt__keys:
     - url: 'http://example.com/apt-key.asc'
       state: '{{ "present"
                  if (ansible_local | d() and ansible_local.apt | d() and
                      ansible_local.apt.configured | bool and
                      ansible_distribution == "Ubuntu")
                  else "absent" }}'


.. _apt__ref_repositories:

apt__repositories
-----------------

This list, along with ``apt__group_repositories`` and
``apt__host_repositories`` can be used to manage APT repositories through
Ansible inventory. Each entry is a YAML dictionary with parameters that
correspond to the ``apt_repository`` module parameters:

``repo``
  Required. The APT repository to configure, in the :man:`sources.list(5)` format.

``filename``
  Optional. Name of the source file in :file:`/etc/apt/sources.list.d/` directory.
  Ansible automatically adds ``.list`` suffix, therefore it's not needed..

``mode``
  Optional. The file mode in octal. Needs to be quoted to be interpreted
  correctly by Ansible.

``state``
  Optional. Either ``present`` for the repository to be present (default), or
  ``absent`` for the repository to be removed. See also ``architecture``,
  ``distribution`` and ``distribution_release`` parameters.

If you don't specify the ``state`` parameter directly, you can use additional
parameters that control how the specified repository is managed:

``architecture``
  Optional. Name of the system architecture, for example ``amd64`` or ``i386``.
  If the current host has the specified architecture, the repository will be
  configured. Only one architecture can be specified at a time, use the
  ``state`` parameter for more complex conditions.

``distribution``
  Optional. Name of the OS distribution. If the current host has the specified
  distribution, the repository will be configured. Only one distribution can be
  specified at a time, use the ``state`` parameter for more complex conditions.

``distribution_release``
  Optional. Name of the OS release. If the current host has the specified
  distribution, the repository will be configured. Only one release can be
  specified at a time, use the ``state`` parameter for more complex conditions.

Examples
~~~~~~~~

Add an APT repository on all hosts without any conditions:

.. code-block:: yaml

   apt__repositories:
     - repo: 'deb http://example.com/debian jessie main'

Add an APT repository only on hosts with Debian OS:

.. code-block:: yaml

   apt__repositories:
     - repo: 'deb http://example.com/debian jessie main'
       distribution: 'Debian'

Add an APT repository only on Ubuntu hosts that have been already configured
once (delayed repository configuration):

.. code-block:: yaml

   apt__repositories:
     - repo: 'deb http://example.com/ubuntu xenial main'
       state: '{{ "present"
                  if (ansible_local | d() and ansible_local.apt | d() and
                      ansible_local.apt.configured | bool and
                      ansible_distribution == "Ubuntu")
                  else "absent" }}'

Configure an Ubuntu PPA on Ubuntu hosts:

.. code-block:: yaml

   apt__repositories:
     - repo: 'ppa:nginx/stable'
       distribution: 'Ubuntu'


.. _apt__ref_deb822_repositories:

apt__deb822_repositories
------------------------

This list, along with ``apt__group_deb822_repositories`` and
``apt__host_deb822_repositories`` can be used to manage APT repositories through
Ansible inventory. Each entry is a YAML dictionary with parameters that
correspond to the `Ansible ansible.builtin.deb822_repository module`_. See its
documentation for parameter advanced usage and syntax.

``name``
  Required. Name of the repo. Specifically used for ``X-Repolib-Name`` and in
  naming the repository and signing key files.

``uris``
  Required. Must specify the base of the Debian distribution archive, from which
  APT finds the information it needs. Multiple URIs can be specified in a list.

``state``
  Optional. Either ``present`` for the repository to be present (default), or
  ``absent`` for the repository to be removed.

``architectures``
  Optional. Architectures to search within repository, for example ``amd64``
  (default) or ``i386``.

``components``
  Optional. Specify different sections of one distribution version present in
  Suite, such as ``main`` (default), ``contrib``, ``non-free-firmware``…

``mode``
  Optional. The octal mode for newly created files in
  :file:`/etc/apt/sources.list.d/` directory.

``suites``
  Optional. Can take the form of a distribution release name (default).

``signed_by``
  Optional. Either a URL to a GPG key, absolute path to a keyring file, one or
  more fingerprints of keys. Keys will be store in :file:`/etc/apt/keyrings/`
  directory (automatically created if absent).

``types``
  Optional. Which types of packages to look for from a given source; either
  binary ``deb`` (default) or source code ``deb-src``.

Examples
~~~~~~~~

Add an APT repository with several components on all hosts without any
conditions:

.. code-block:: yaml

   apt__deb822_repositories:
   - name: debian
     types: deb
     uris: http://deb.debian.org/debian
     suites: bookworm
     components:
     - main
     - contrib
     - non-free-firmware

Add third-party APT repository with GPG key URL:

.. code-block:: yaml

   apt__deb822_repositories:
     - name: 'my-repo'
       uris: 'http://example.com/debian'
       signed_by: 'http://example.com/debian/example.com.asc'


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

This list as well as other ``apt__*_sources`` lists are used to configure what
APT package sources are configure in the :file:`/etc/apt/sources.list` file.
This file defines the primary OS package sources and indirectly defines the OS
release that's present on the host. The configuration template will track what
sources are present and will comment out the duplicates if they show up in more
than one list.

Apart from the usual inventory lists for all hosts, group of hosts and specific
hosts, there are additional lists that are included in the finished config
file:

``apt__original_sources``
  This list defines the APT sources that are present in the original, diverted
  :file:`/etc/apt/sources.list` file. The security sources are automatically
  filtered out based on the contents of the ``apt__security_sources`` list.

``apt__default_sources``
  The role provides a set of default package sources for each known OS
  distribution. These sources are usually URLs to mirror redirectors, which
  will try to point to the closest available mirror. They are provided as
  a backup in case the host does not have any recognized package sources
  available.

``apt__security_sources``
  This is a list of APT sources that provide security updates. This list has
  a more specific entries than the normal lists since security repositories
  tend to have different naming scheme than the regular mirrored repositories.

``apt__combined_sources``
  This list combines all of the above list and is used in the configuration
  template. It defines the order in which the APT sources are specified in the
  configuration file.

Each list entry that defines an APT source can have different forms.

The simplest entry is a string. It does not have any conditions and it will be
added to the :file:`/etc/apt/sources.list` file unless it is a duplicate. The
string should only contain the URL of the APT mirror, the rest will be added
automatically according to detected OS distribution and release. Example:

.. code-block:: yaml

   apt__sources:
     - 'http://ftp.debian.org/debian'

A more advanced alternative is a YAML dictionary, which uses OS distribution
names as keys and mirror URLs as values. You can specify multiple distributions
in one entry, they will be filtered according to the current OS. Example:

.. code-block:: yaml

   apt__sources:
     - Debian: 'http://ftp.debian.org/debian'

The third version of an APT sources entry is similar to the `Ansible
ansible.builtin.apt_repository module`_, and should be defined as a YAML
dictionary with ``repo`` as the key and complete APT source specification as the
value. These entries are not filtered by the role, and they are not checked for
duplicates. Example:

.. code-block:: yaml

   apt__sources:
     - repo: 'deb http://ftp.debian.org/debian jessie main contrib non-free'

The last version is a YAML dictionary with multiple keys as parameters. These
parameters allow for fine control over when a particular APT source is present,
what source types are used, which components are enabled, etc. Known
parameters:

``uri`` or ``uris``
  Required. The URI or other method known by APT (see :man:`sources.list(5)`)
  for a given APT source. It is possible to specify multiple entries as a list,
  they will be treated as one.

``type`` or ``types``
  Optional. What type of the packages are used for this source. It can be
  either a string of 1 type, or a list of types. Known source types: ``deb``,
  ``deb-src``. If not set, role will use the ``apt__source_types`` value.

``option`` or ``options``
  Optional. String or list of strings of APT options. Settings are expected in
  the form ``setting=value``.  See :man:`sources.list(5)` for details.

``suite`` or ``suites``
  Optional. Name of the "suite" to use for this source. The suite is usually
  a release name like ``jessie``, ``xenal``, or a "release class" like
  ``stable``, ``oldstable``, ``testing``, or a directory path in case of simple
  repositories (which needs to end with a slash). It can also be a list of
  releases. If not specified, role will use the ``apt__distribution_suffixes``
  value to generate a list of default suites for a given OS release.

``component`` or ``components``
  Optional. Name of a repository component or section to enable, for example
  ``main``, ``contrib``, ``non-free``, ``universe``, ``restricted``,
  ``multiverse``. It can also be a list of components. If not specified, role
  will use the ``apt__distribution_components`` value.

``comment`` or ``comments``
  Optional. A string or a YAML text block with comments about the given APT
  source.

``state``
  Optional. Either ``present`` if a given APT source should be present in the
  generated config file, or ``absent`` if not.

``architecture``
  Optional. If ``state`` is not specified, you can specify a system
  architecture name on which a given APT source is active. Only one
  architecture can be specified, use the ``state`` parameter for more complex
  conditions.

``distribution``
  Optional. If ``state`` is not specified, you can specify an OS distribution
  name on which a given APT source is active. Only one distribution can be
  specified, use the ``state`` parameter for more complex conditions.

``distribution_release``
  Optional. If ``state`` is not specified, you can specify an OS release on
  which a given APT source is active. Only one release can be specified, use
  the ``state`` parameter for more complex conditions.

Examples
~~~~~~~~

Add an archive repository in :file:`/etc/apt/sources.list` configuration file:

.. code-block:: yaml

   apt__sources:
     - uri: 'http://archive.debian.org/debian'
       suite: 'sarge'
       components: [ 'main', 'contrib' ]

Enable repository with source packages:

.. code-block:: yaml

   apt__sources:
     - uri: 'http://ftp.debian.org/debian'
       types: [ 'deb', 'deb-src' ]

Enable Canonical Partner repositories, only on Ubuntu hosts:

.. code-block:: yaml

   apt__sources:
     - uri: 'http://archive.canonical.com/ubuntu'
       component: 'partner'
       distribution: 'Ubuntu'
