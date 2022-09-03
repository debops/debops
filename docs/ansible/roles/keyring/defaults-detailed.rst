.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.keyring`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _keyring__ref_dependent_apt_auth_files:

keyring__dependent_apt_auth_files
---------------------------------

The :envvar:`keyring__dependent_apt_auth_files` list can be used to create and
manage :file:`/etc/apt/auth.conf.d/` configuration files which caontain
authentication credentials required by specific APT repositories. The format
and more details about these files can be found in :man:`apt_auth.conf(5)`
manual page. The ``debops.reprepro`` role can be used to create APT
repositories that require authentication.

This functionality is also available in the :ref:`debops.apt` role for use via
the Ansible inventory. See :ref:`apt__ref_auth_files` for more details.

Examples
~~~~~~~~

Provide credentials for a private APT repository, with password stored in the
:file:`secret/` directory managed by the :ref:`debops.secret` role. The APT
repository is managed by the ``debops.reprepro`` role which uses the
:ref:`debops.nginx` role to manage the authentication credentials.

.. code-block:: yaml

   keyring__dependent_apt_auth_files:

     - name: 'private_repo'
       machine: 'https://repo.example.org/debian'
       login: 'username'
       password: '{{ lookup("password", secret + "/credentials/repo"
                                               + "/nginx/htpasswd"
                                               + "/apt_access/username") }}'

Syntax
~~~~~~

THe variables are defined as a list of YAML dictionaries .Each configuration
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


.. _keyring__ref_dependent_apt_keys:

keyring__dependent_apt_keys
---------------------------

This variable defines a list of GPG keys which should be present (or absent) in
the host's `APT keyring`__, used to verify signatures of the Debian/Ubuntu
package lists. It is meant to be used by other Ansible roles via the
role-dependent variables.

.. __: https://wiki.debian.org/SecureApt

Examples
~~~~~~~~

Using the :ref:`debops.nginx` role, ensure that the `nginx.org`__ upstream APT
key is present in the APT keyring. If the key is not available in the local
key store, it will be downloaded from the keyserver specified in the
:envvar:`keyring__keyserver` variable:

.. __: https://nginx.org/en/linux_packages.html

.. code-block:: yaml

   # Role: debops.nginx/defaults/main.yml
   nginx__keyring__dependent_apt_keys:

     - '573B FD6B 3D8F BC64 1079  A6AB ABF5 BD82 7BD9 BF62'

.. code-block:: yaml

   # Playbook: nginx.yml
   - hosts: [ 'debops_service_nginx' ]
     roles:

       - role: debops.keyring
         keyring__dependent_apt_keys:
           - '{{ nginx__keyring__dependent_apt_keys }}'

       - role: debops.nginx

Using the :ref:`debops.nginx` role, ensure that the ``nginx.org`` upstream APT
key is present in the APT keyring, if support for upstream version of
:command:`nginx` is enabled. If the key is not available in the local key
store, it will be downloaded from the specified URL. Additionally, ensure that
the APT repository configuration is present and the cache is updated. The
playbook is the same as in the previous example:

.. code-block:: yaml

   # Role: debops.nginx/defaults/main.yml
   nginx__upstream: True
   nginx__keyring__dependent_apt_keys:

     - id: '573B FD6B 3D8F BC64 1079  A6AB ABF5 BD82 7BD9 BF62'
       url: 'https://nginx.org/keys/nginx_signing.key'
       repo: 'deb http://nginx.org/packages/debian {{ ansible_distribution_release }} nginx'
       state: '{{ "present" if nginx__upstream|bool else "absent" }}'

Also with the :ref:`debops.nginx` role, install the APT GPG key in a separate
keyring and tell APT to use this key only for Nginx official packages. The APT
repository configuration will be stored in the
:file:`/etc/apt/sources.list.d/nginx-upstream.list' configuration file (note
the ``>`` YAML block marker, which will fold the repository string to a single
line):

.. code-block:: yaml

   nginx__keyring__dependent_apt_keys:

     - id: '573B FD6B 3D8F BC64 1079  A6AB ABF5 BD82 7BD9 BF62'
       url: 'https://nginx.org/keys/nginx_signing.key'
       keyring: '/usr/share/keyring/nginx-archive-keyring.gpg'
       repo: >
         deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg]
             http://nginx.org/packages/debian {{ ansible_distribution_release }} nginx
       filename: 'nginx-upstream'
       state: '{{ "present" if nginx__upstream | bool else "absent" }}'

There are many more real-world examples available in various DebOps roles. To
find them, you can run the command in the DebOps monorepo root directory:

.. code-block:: console

   git grep '__keyring__dependent_apt_keys:' ansible/roles

Syntax
~~~~~~

The value of the :envvar:`keyring__dependent_apt_keys` variable is a YAML list.
Each list entry can be a string which represents the GPG key ID which will be
imported either from the local storage, or from the configured GPG keyserver.
Alternatively, list entry can be a YAML dictionary which allows a more
fine-grained control over the state of the GPG key and its source.

The YAML dictionaries are defined using specific parameters:

``id``
  The GPG key fingerprint which is defined by this entry. It can be specified
  with spaces, which will be automatically removed when necessary. This
  parameter is not required if the ``repo`` parameter is specified.

``data``
  Optional. The contents of the GPG key specified as a YAML text block (the key
  should be armored). If not specified, and the GPG key is found in the
  configured local key store, the role will try to lookup the key data from the
  file. If the key is not available in the local key store, the role will try
  to use the configured GPG keyserver to retrieve it, unless ``url`` or
  ``keybase`` parameters are specified.

``url``
  Optional. The URL where a given GPG key can be found. The ``id`` parameter
  still needs to be specified for the ``apt_key`` Ansible module to work as
  expected.

``keybase``
  Optional. The name of the `Keybase`__ profile which should be used to lookup
  the key using the `Keybase API`__. If the ``url`` parameter is specified, it
  will override the ``keybase`` parameter.

  .. __: https://keybase.io/
  .. __: https://keybase.io/docs/api/1.0/call/user/pgp_keys.asc

``keyring``
  Optional. Absolute path for the keyring where the GPG key should be stored.
  If omitted, the key will be stored in the system-wide keyring
  (:file:`/etc/apt/trusted.gpg`).

``keyserver``
  Optional. Override the default GPG keyserver URL specified in the
  :envvar:`keyring__keyserver` variable.

``state``
  Optional. If not specified or ``present``, the GPG key will be added to the
  APT keyring. If ``absent``, the key will be removed from the APT keyring. The
  same state will be applied to the APT repository, if the ``repo`` parameter
  is specified.

``repo``
  The :man:`sources.list(5)` entry which defines an APT repository. This
  parameter can be specified with the GPG key id of the APT repository, or as
  standalone, to more efficiently configure APT (for example if multiple GPG
  keys are configured at once).

``filename``
  Optional. The name of the configuration file in the
  :file:`/etc/sources.list.d/` directory which will be used to store the APT
  repository configuration.


.. _keyring__ref_dependent_gpg_keys:

keyring__dependent_gpg_keys
---------------------------

The :envvar:`keyring__dependent_gpg_keys` variable can be used to manage GPG
keys on the UNIX accounts. If an account is not defined, the ``root`` account
GPG keyring will be used by default. The GPG keys are useful to verify
signatures of the :command:`git` commits or tags, or other files downloaded
over the network with external GPG signatures.

Examples
~~~~~~~~

Using the :ref:`debops.yadm` Ansible role, prepare the GPG key of the
:command:`yadm` upstream author to verify his GPG signature on the specific
:command:`git` tag checked out from the repository, but only when the
installation from upstream is enabled. The GPG key will be added to the
``root`` UNIX account GPG keyring:

.. code-block:: yaml

   # Role: debops.yadm/defaults/main.yml
   yadm__upstream_enabled: True
   yadm__upstream_gpg_id: '31B9 62F7 CC57...'
   yadm__keyring__dependent_gpg_keys:
     - id: '{{ yadm__upstream_gpg_id }}'
       state: '{{ "present" if yadm__upstream_enabled|bool else "absent" }}'

.. code-block:: yaml

   # Playbook: yadm.yml
   - hosts: [ 'debops_service_yadm' ]
     roles:

       - role: debops.keyring
         keyring__dependent_gpg_keys:
           - '{{ yadm__keyring__dependent_gpg_keys }}'

       - role: debops.yadm

.. note:: The functionality below will be implemented at a later date.

Extract GPG key ids from the :ref:`debops.golang` configuration and install
them on the UNIX account used by the role to build the ``docker-registry`` Go
binary, which is then used by the :ref:`debops.docker_registry` role. The GPG
keys will be used to verify the :command:`git` tags of the downloaded
repositories:

.. code-block:: yaml

   # Role: debops.docker_registry/defaults/main.yml
   docker_registry__golang__dependent_packages:

     - name: 'docker-registry'
       apt_packages: [ 'docker-registry' ]
       upstream: True
       gpg: '8C7A 111C 2110 5794 B0E8  A27B F58C 5D0A 4405 ACDB'
       git:
         - repo: 'https://github.com/docker/distribution'
           version: 'v2.7.1'
           build_script: |
             make clean binaries
       binaries:
         - src: 'github.com/docker/distribution/bin/registry'
           dest: 'docker-registry'
           notify: [ 'Restart docker-registry' ]

.. code-block:: yaml

   # Role: debops.golang/defaults/main.yml
   golang__user: '_golang'
   golang__group: '_golang'
   golang__home: '/var/local/_golang'
   golang__combined_packages: '{{ golang__dependent_packages | d([]) }}'

   golang__keyring__dependent_gpg_user: '{{ golang__user }}'

   golang__keyring__dependent_gpg_keys:

     - user: '{{ golang__user }}'
       group: '{{ golang__group }}'
       home: '{{ golang__home }}'

     - '{{ golang__combined_packages | parse_kv_items
           | selectattr("gpg", "defined") | selectattr("state", "equalto", "present")
           | map(attribute="gpg") | list }}'

.. code-block:: yaml

   # Playbook: docker_registry.yml
   - hosts: [ 'debops_service_docker_registry' ]
     roles:

       - role: debops.keyring
         keyring__dependent_gpg_user: '{{ golang__keyring__dependent_gpg_user }}'
         keyring__dependent_gpg_keys:
           - '{{ golang__keyring__dependent_gpg_keys }}'

       - role: debops.golang
         golang__dependent_packages:
           - '{{ docker_registry__golang__dependent_packages }}'

       - role: debops.docker_registry

There are many more real-world examples available in various DebOps roles. To
find them, you can run the command in the DebOps monorepo root directory:

.. code-block:: console

   git grep '__keyring__dependent_gpg_keys:' ansible/roles

Syntax
~~~~~~

The value of the :envvar:`keyring__dependent_gpg_keys` variable is a YAML list.
Each list entry can be a string which represents the GPG key ID which will be
imported either from the local storage, or from the configured GPG keyserver.
Alternatively, list entry can be a YAML dictionary which allows a more
fine-grained control over the state of the GPG key and its source.

The YAML dictionaries are defined using specific parameters:

``id``
  The GPG key fingerprint which is defined by this entry. It can be specified
  with spaces, which will be automatically removed when necessary. This
  parameter is not required if the ``user`` parameter is specified.

``data``
  Optional. The contents of the GPG key specified as a YAML text block (the key
  should be armored). If not specified, and the GPG key is found in the
  configured local key store, the role will try to lookup the key data from the
  file. If the key is not available in the local key store, the role will try
  to use the configured GPG keyserver to retrieve it, unless ``url`` or
  ``keybase`` parameters are specified.

``url``
  Optional. The URL where a given GPG key can be found.

``keybase``
  Optional. The name of the `Keybase`__ profile which should be used to lookup
  the key using the `Keybase API`__. If the ``url`` parameter is specified, it
  will override the ``keybase`` parameter.

  .. __: https://keybase.io/
  .. __: https://keybase.io/docs/api/1.0/call/user/pgp_keys.asc

``keyserver``
  Optional. Override the default GPG keyserver URL specified in the
  :envvar:`keyring__keyserver` variable.

``state``
  Optional. If not specified or ``present``, the GPG key will be added to the
  GPG keyring of a specified UNIX account, or the ``root`` account. If
  ``absent``, the key will be removed from the GPG keyring. If ``ignore``,
  a given configuration entry will not be evaluated by the role.

``create_user``
  Optional, boolean. If not specified or ``True``, and the ``user`` parameter
  is present, the configured UNIX account will be created to allow GPG keyring
  management. If ``False``, the role will not try to create an UNIX account;
  this might be useful if the account is already created in non-local user
  database, like LDAP.

``user``
  A name of the UNIX account to create by the :ref:`debops.keyring` role, so
  that its GPG keyring can be correctly created and accessed. If this parameter
  is specified, you can omit the ``id`` parameter to only create the UNIX
  account.

``group``
  Optional. A name of the primary UNIX group of the created UNIX account. If
  not specified, the UNIX group will have the same name as the UNIX account.

``home``
  Optional. The absolute path of the home directory of the created UNIX
  account. If not specified, a home directory will be created in the
  :file:`/home/` directory by default.

``system``
  Optional, boolean. If not specified or ``True``, the created UNIX account and
  group will be "system" account and group, with UID/GID < 1000. If ``False``,
  the UNIX account and group will be "normal" account and group, with UID/GID
  > 1000.
