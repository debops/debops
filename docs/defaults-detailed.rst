.. _apt__ref_defaults_detailed:

Default variable details
========================

.. include:: includes/all.rst

Some of ``debops.apt`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1

.. _apt__ref_keys:

apt__keys
---------

This list, along with :envvar:`apt__group_keys` and :envvar:`apt__host_keys`
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
                  if (ansible_local|d() and ansible_local.apt|d() and
                      ansible_local.apt.configured|bool and
                      ansible_distribution == "Ubuntu")
                  else "absent" }}'


.. _apt__ref_repositories:

apt__repositories
-----------------

This list, along with :envvar:`apt__group_repositories` and
:envvar:`apt__host_repositories` can be used to manage APT repositories through
Ansible inventory. Each entry is a YAML dictionary with parameters that
correspond to the ``apt_repository`` module parameters:

``repo``
  Required. The APT repository to configure, in the :manpage:`sources.list(5)` format.

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
                  if (ansible_local|d() and ansible_local.apt|d() and
                      ansible_local.apt.configured|bool and
                      ansible_distribution == "Ubuntu")
                  else "absent" }}'

Configure an Ubuntu PPA on Ubuntu hosts:

.. code-block:: yaml

   apt__repositories:
     - repo: 'ppa:nginx/stable'
       distribution: 'Ubuntu'


.. _apt__ref_sources:

apt__sources
------------

This list as well as other ``apt__*_sources`` lists are used to configure what
APT package sources are configure in the :file:`/etc/apt/sources.list` file. This
file defines the primary OS package sources and indirectly defines the OS
release that's present on the host. The configuration template will track what
sources are present and will comment out the duplicates if they show up in more
than one list.

Apart from the usual inventory lists for all hosts, group of hosts and specific
hosts, there are additional lists that are included in the finished config
file:

:envvar:`apt__original_sources`
  This list defines the APT sources that are present in the original, diverted
  :file:`/etc/apt/sources.list` file. The security sources are automatically
  filtered out based on the contents of the :envvar:`apt__security_sources` list.

:envvar:`apt__default_sources`
  The role provides a set of default package sources for each known OS
  distribution. These sources are usually URLs to mirror redirectors, which
  will try to point to the closest available mirror. They are provided as
  a backup in case the host does not have any recognized package sources
  available.

:envvar:`apt__security_sources`
  This is a list of APT sources that provide security updates. This list has
  a more specific entries than the normal lists since security repositories
  tend to have different naming scheme than the regular mirrored repositories.

:envvar:`apt__combined_sources`
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
apt_repository module`_, and should be defined as an YAML dictionary with
``repo`` as the key and complete APT source specification as the value. These
entries are not filtered by the role, and they are not checked for duplicates.
Example:

.. code-block:: yaml

   apt__sources:
     - repo: 'deb http://ftp.debian.org/debian jessie main contrib non-free'

The last version is a YAML dictionary with multiple keys as parameters. These
parameters allow for fine control over when a particular APT source is present,
what source types are used, which components are enabled, etc. Known
parameters:

``uri`` or ``uris``
  Required. The URI or other method known by APT (see :manpage:`sources.list(5)`) for
  a given APT source. It is possible to specify multiple entries as a list,
  they will be treated as one.

``type`` or ``types``
  Optional. What type of the packages are used for this source. It can be
  either a string of 1 type, or a list of types. Known source types: ``deb``,
  ``deb-src``. If not set, role will use the :envvar:`apt__source_types` value.

``option`` or ``options``
  Optional. String or list of strings of APT options. Settings are expected in
  the form ``setting=value``.  See :manpage:`sources.list(5)` for details.

``suite`` or ``suites``
  Optional. Name of the "suite" to use for this source. The suite is usually
  a release name like ``jessie``, ``xenal``, or a "release class" like
  ``stable``, ``oldstable``, ``testing``, or a directory path in case of simple
  repositories (which needs to end with a slash). It can also be a list of
  releases. If not specified, role will use the :envvar:`apt__distribution_suffixes`
  value to generate a list of default suites for a given OS release.

``component`` or ``components``
  Optional. Name of a repository component or section to enable, for example
  ``main``, ``contrib``, ``non-free``, ``universe``, ``restricted``,
  ``multiverse``. It can also be a list of components. If not specified, role
  will use the :envvar:`apt__distribution_components` value.

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
