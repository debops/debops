.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.reprepro`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _reprepro__ref_instances:

reprepro__instances
-------------------

The ``reprepro__*_instances`` variables define the "instances" of APT
repositories managed by :command:`reprepro`. Each "instance" consists of an APT
repository and corresponding :ref:`debops.nginx` configuration to provide
HTTP/HTTPS access for package retrieval and upload. The :ref:`debops.nginx`
configuration is optional and will be created only when specific configuration
parameters are present.

Examples
~~~~~~~~

Restrict allowed GPG keys for specific APT repositories
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

Modify the default configuration by adding a new set of uploaders for specific
APT repositories. The role configuration will be updated via the
:ref:`universal_configuration` system, so there's no need to copy the entire
contents of default variables to modify them through the inventory.

.. code-block:: yaml

   reprepro__instances:

     - name: 'main'
       uploaders:
         - name: 'ci-builders'
           raw: |
             allow * by key 5833EC7492A6E482D742F7FF729ABA78462947AA+
       distributions:

         - name: 'bookworm'
           Uploaders: 'uploaders/ci-builders'

         - name: 'bullseye'
           Uploaders: 'uploaders/ci-builders'

Mirrors of Debian and Ubuntu APT repositories
'''''''''''''''''''''''''''''''''''''''''''''

Create two mirrors of APT repositories for stable Debian and Ubuntu releases,
available under the same FQDN address. The repositories are available publicly
and new packages can be uploaded to them, but this configuration is only
provided as an example and more secure configuration should be used instead.

.. code-block:: yaml

   reprepro__instances:

     # Disable the default instance
     - name: 'main'
       state: 'absent'

     - name: 'mirror'
       fqdn: '{{ ansible_fqdn }}'

       upload_map:
         '/upload': ''
         '/upload-ubuntu': '/var/spool/reprepro/mirror-ubuntu/incoming'

       incoming:

         - name: 'incoming'
           Allow:
             - 'bullseye'
             - 'stable>bullseye'
           Options:
             - 'multiple_distributions'
           Cleanup:
             - 'on_deny'
             - 'on_error'

       distributions:

         - name: 'bullseye'
           Origin: '{{ reprepro__origin }}'
           Codename: 'bullseye'
           Suite: 'stable'
           Architectures: [ 'source', 'amd64', 'i386', 'ppc64el', 's390x',
                            'armel', 'armhf', 'arm64', 'mipsel', 'mips64el' ]
           Components: [ 'main', 'contrib', 'non-free' ]
           Update: 'bullseye'

       updates:

         - name: 'bullseye'
           Method: 'http://deb.debian.org/debian'
           Suite: 'bullseye'
           Components: [ 'main', 'contrib', 'non-free' ]
           Architectures: [ 'source', 'amd64', 'i386', 'ppc64el', 's390x',
                            'armel', 'armhf', 'arm64', 'mipsel', 'mips64el' ]
           VerifyRelease: 'blindtrust'

       uploaders:

         - name: 'anybody'
           raw: |
             allow * by any key

     - name: 'mirror-ubuntu'
       outdir: '{{ reprepro__public_root + "/sites/mirror/public/ubuntu" }}'
       incoming:

         - name: 'incoming'
           Allow:
             - 'focal'
             - 'lts>focal'
           Options:
             - 'multiple_distributions'
           Cleanup:
             - 'on_deny'
             - 'on_error'

       distributions:

         - name: 'focal'
           Origin: '{{ reprepro__origin }}'
           Suite: 'lts'
           Architectures: [ 'source', 'amd64', 'i386' ]
           Components: [ 'main', 'restricted', 'universe', 'multiverse' ]
           Update: 'focal'

       updates:

         - name: 'focal'
           Method: 'http://us.archive.ubuntu.com/ubuntu'
           Suite: 'focal'
           Components: [ 'main', 'restricted', 'universe', 'multiverse' ]
           Architectures: [ 'amd64', 'i386' ]
           VerifyRelease: 'blindtrust'

       uploaders:

         - name: 'anybody'
           raw: |
             allow * by any key

After the role has set up repositories, login to the ``reprepro`` account,
:command:`cd` into the repository directory and run :command:`reprepro update`
to download the archive.

Local APT repositories with restricted access
'''''''''''''''''''''''''''''''''''''''''''''

Create a set of two APT repository instances, each one with its own
authentication using HTTP Basic Auth passwords, which are stored in the
:file:`secret/` directory on Ansible Controller.

.. code-block:: yaml

   # Create access policies with HTTP Basic Auth
   nginx_access_policy_auth_basic_map:
     'repo_alpha_access': 'alpha_access'
     'repo_beta_access': 'beta_access'

   # Create password files with passwords for specified users
   nginx__htpasswd:

     - name: 'alpha_access'
       users: [ 'client1', 'client2', 'client3' ]

     - name: 'beta_access'
       users: [ 'client1', 'client2', 'client3' ]

   # Custom variable which holds the "conf/incoming" configuration
   incoming_sets:

     - name: 'incoming'
       Allow:
         - 'bullseye'
         - 'stable>bullseye'
       Options:
         - 'multiple_distributions'
       Cleanup:
         - 'on_deny'
         - 'on_error'

   # Custom variable which holds the "conf/distributions" configuration
   distributions_sets:

     - name: 'bullseye'
       Origin: '{{ reprepro__origin }}'
       Suite: 'stable'
       Architectures: [ 'source', 'amd64' ]
       Components: [ 'main' ]
       SignWith: 'default'
       DebIndices: [ 'Packages', 'Release', '.', '.gz', '.xz' ]
       DscIndices: [ 'Sources', 'Release', '.gz', '.xz' ]
       Uploaders: 'uploaders/anybody'
       Log: |
         packages.bullseye.log
         --type=dsc email-changes.sh

   # Custom variable which holds the "conf/uploaders" configuration
   uploaders_sets:

     - name: 'anybody'
       raw: |
         allow * by any key

   # List of GPG keys which are allowed to upload APT packages
   reprepro__gpg_uploaders_keys:

     # Automatic Signing Key <ci-builder@example.org>
     - '5833EC7492A6E482D742F7FF729ABA78462947AA'

   # Configuration of repository instances
   reprepro__instances:

     # Disable the default configuration provided by the role
     - name: 'main'
       state: 'absent'

     - name: 'alpha'
       fqdn: 'alpha.{{ ansible_domain }}'
       public: False
       access_policy: 'repo_alpha_access'
       incoming: '{{ incoming_sets }}'
       distributions: '{{ distributions_sets }}'
       uploaders: '{{ uploaders_sets }}'

     - name: 'beta'
       fqdn: 'beta.{{ ansible_domain }}'
       public: False
       access_policy: 'repo_beta_access'
       incoming: '{{ incoming_sets }}'
       distributions: '{{ distributions_sets }}'
       uploaders: '{{ uploaders_sets }}'

You can see more configuration examples in the
:envvar:`reprepro__default_instances` variable in the role defaults.

Syntax
~~~~~~

The variables are defined as a list of YAML dictionaires, each dictionary
defines an "instance" using specific parameters:

``name``
  Required. An identifier for a particular APT repository instance. The value
  is used in the filesystem paths and should be a simple alphanumeric string.
  Configuration entries with the same ``name`` parameters are merged during
  role execution and can affect each other via :ref:`universal_configuration`
  principles.

``state``
  Optional. If not specified or ``present``, a given APT repository instance
  will be configured on the host. If ``absent``, the repository will not be
  configured (some configuration like :command:`nginx` server configuration
  will be automatically removed). If ``ignore``, a given configuration entry
  will not be evaluated during role execution.

``fqdn``
  Optional. Fully Qualified Domain Name under which the APT repository will be
  served over HTTP/HTTPS using :command:`nginx` webserver, via the
  :ref:`debops.nginx` Ansible role. Presence of this parameter enables the
  :command:`nginx` configuration.

  This parameter shouldn't be used when the ``outdir`` parameter is specified,
  to not create a duplicate :command:`nginx` configuration which can interfere
  with the other APT repository instances.

``public``
  Optional, boolean. If not present or ``True``, the APT repository will be
  accessible over HTTP and HTTPS without any specific restrictions (subnet
  access can still affect this).

  If ``False``, HTTP access is disabled entirely. The ``access_policy``
  parameter can then specify the "access policy" configured in the
  :ref:`debops.nginx` role which can enforce password authentication for
  a given APT repository.

``allow``
  Optional. List of IP addresses or CIDR subnets which are allowed to access
  the APT repository over HTTP or HTTPS. If not specified, any host can connect
  to the repository.

``allow_upload``
  Optional. List of IP addresses or CIDR subnets which are allowed to upload
  content to the APT repository using WebDAV. If not specified, any host can
  upload content to the repository.

``access_policy``
  Optional. Name of the "access policy" defined in the :ref:`debops.nginx` role
  which should be used for a given APT repository to control access. This can
  be used to allow or deny access per client using login/password combination
  or X.509 client certificates (planned). See :man:`apt_auth.conf(5)` for
  details about configuring password-based access to the APT repository.

``auth_realm``
  Optional. The string presented to the HTTP clients during authentication. If
  not specified, the value of the :envvar:`reprepro__auth_realm` variable will
  be used by default.

``max_body_size``
  Optional. Specify the maximum size of the uploaded content, including the
  suffix. If not specified, the value of the :envvar:`reprepro__max_body_size`
  variable is used, ``50M`` by default.

``pki_realm``
  Optional. Name of the PKI realm managed by the :ref:`debops.pki` Ansible role
  to use for the HTTPS configuration in the :command:`nginx` configuration.
  Normally the :ref:`debops.nginx` role detects the PKI realm to use based on
  the FQDN and domain of the server; this parameter can be used to override
  that detection if needed.

``basedir``
  Optional. Override the base directory of the :command:`reprepro` repository,
  which contains the internal state database and repository configuration
  files. If not specified, the repository database will be locaed in the
  :envvar:`reprepro__data_root` variable location (by default
  :file:`/var/local/reprepro/repositories/` directory).

``outdir``
  Optional. Override the public directory where :command:`reprepro` manages the
  APT repository contents. This can be used to combine multiple APT repository
  "instances" under one FQDN to, for example, provide Debian and Ubuntu
  packages under one FQDN. If the parameter is not specified, the role will
  generate the path automatically based on the instance name and use
  :file:`/debian` as the suffix to indicate that the repository is for the
  Debian distribution.

  Repository instances that use the ``outdir`` parameter don't need separate
  :command:`nginx` configuration (no ``fqdn`` parameter), since that can
  interfere with the configuration of the "parent" instance.

``os``
  Optional. Specify the suffix of the autogenerated output dir, used if the
  ``outdir`` parameter is not set. If not specified, ``debian`` will be used by
  default.

``upload_map``
  Optional. By default the ``/upload`` subdirectory of the APT repository URL
  is used for uploading APT packages to be processed by :command:`reprepro`. In
  case of multiple repositories using the same FQDN with the ``outdir``
  parameter or if the default path should be different, the ``upload_map``
  parameter can define a YAML dictionary. Each key should be a subdirectory off
  of the APT repository URL, and the value should be an absolute path to the
  filesystem directory monitored for new uploads. An empty value (``''``) can
  be used to let the role generate the directory path automatically, based on
  the standardized directory structure maintained by the :ref:`debops.reprepro`
  role.

``mail_name``
  Optional. Specify the mail sender name used in e-mails generated by
  :command:`email-changes.sh` script executed by :command:`reprepro` on any
  repository modifications. If not specified, a sensible name will be generated
  automatically.

``mail_from``
  Optional. Specify the mail sender address used in e-mails generated by
  :command:`email-changes.sh` script executed by :command:`reprepro` on any
  repository modifications. If not specified, the value from the
  :envvar:`reprepro__mail_from` variable will be used by default.

``mail_to``
  Optional. Specify the mail recipient address used in e-mails generated by
  :command:`email-changes.sh` script executed by :command:`reprepro` on any
  repository modifications. If not specified, the value from the
  :envvar:`reprepro__mail_to` variable will be used by default.

``options``
  Optional. This parameter defines the contents of the :file:`conf/options`
  configuration file in the :command:`reprepro` repository. The ``options`` parameters
  from configuration entries with the same ``name`` parameter are merged
  together and can affect each other.

  The ``basedir``, ``outdir``, ``waitforlock`` and ``verbose`` options are
  defined by default but can be modified. See the :man:`reprepro(1)` manual
  page for possible options.

  The configuration is defined as a list of YAML dictionaries, each dictionary
  key being the option name and its value being the option value. Alternatively
  you can use specific parameters to control each option:

  ``name``
    The name of the option.

  ``value``
    The value of the option, can be a number or a string.

  ``state``
    If not specified or ``present``, the option is included in the
    configuration file. If ``absent``, the option will be removed from the
    configuration file.

``distributions``
  Optional. This parameter defines the contents of the
  :file:`conf/distributions` configuration file in the :command:`reprepro`
  repository. The ``distributions`` parameters from configuration entries with
  the same ``name`` parameter are merged together and can affect each other.
  See the :man:`reprepro(1)` manual page for possible options.

  The configuration is defined as a list of YAML dictionaries, each dictionary
  can define a single distribution. The ``name`` parameter is used to define
  a distribution but can be overridden by the ``Codename`` parameter. Other
  options should be specified as defined in the manual page and will be added
  to the configuration as-is. There are special parameters ignored by the
  configuration template, used to manage the configuration entry itself:

  ``name``
    The name of the distribution, can be overridden by the ``Codename``
    parameter.

  ``state``
    If not specified or ``present``, the distribution is included in the
    configuration file. If ``absent``, the distribution will be removed from
    the configuration file.

  ``comment``
    String or YAML text block with a comment added before the distribution.

  ``raw``
    YAML text block with configuration which will be included in the
    configuration file as-is. Other parameters of a given distribution will not
    be processed by the role.

``incoming``
  Optional. This parameter defines the contents of the
  :file:`conf/incoming` configuration file in the :command:`reprepro`
  repository. The ``incoming`` parameters from configuration entries with
  the same ``name`` parameter are merged together and can affect each other.
  See the :man:`reprepro(1)` manual page for possible options.

  The configuration is defined as a list of YAML dictionaries, each dictionary
  can define a single incoming ruleset. The ``name`` parameter is used to
  define the ruleset name. Other options should be specified as defined in the
  manual page and will be added to the configuration as-is. There are special
  parameters ignored by the configuration template, used to manage the
  configuration entry itself:

  ``name``
    The name of the ruleset, stored as ``Name`` in the configuration file.

  ``state``
    If not specified or ``present``, the ruleset is included in the
    configuration file. If ``absent``, the ruleset will be removed from the
    configuration file.

  ``comment``
    String or YAML text block with a comment added before the ruleset.

  ``raw``
    YAML text block with configuration which will be included in the
    configuration file as-is. Other parameters of a given ruleset will not be
    processed by the role.

``uploaders``
  Optional. This parameter defines the contents of the
  :file:`conf/uploaders/*` configuration file in the :command:`reprepro`
  repository. The ``uploaders`` parameters from configuration entries with
  the same ``name`` parameter are merged together and can affect each other.
  See the :man:`reprepro(1)` manual page for possible options.

  The configuration is defined as a list of YAML dictionaries, each dictionary
  can define a single configuration file in the :file:`conf/uploaders/`
  directory. The ``name`` parameter is used to define the file name. Other
  options should be specified as defined in the manual page using the ``raw``
  parameter and will be added to the configuration as-is. There are special
  parameters ignored by the configuration template, used to manage the
  configuration entry itself:

  ``name``
    The name of the ruleset file.

  ``state``
    If not specified or ``present``, the ruleset file is generated by the role.
    If ``absent``, the ruleset file won't be generated, existing files are not
    removed.

  ``comment``
    String or YAML text block with a comment added before the ruleset.

  ``raw``
    YAML text block with configuration which will be included in the
    configuration file as-is.

``updates``
  Optional. This parameter defines the contents of the
  :file:`conf/updates` configuration file in the :command:`reprepro`
  repository. The ``updates`` parameters from configuration entries with
  the same ``name`` parameter are merged together and can affect each other.
  See the :man:`reprepro(1)` manual page for possible options.

  The configuration is defined as a list of YAML dictionaries, each dictionary
  can define a single update ruleset. The ``name`` parameter is used to
  define the ruleset name. Other options should be specified as defined in the
  manual page and will be added to the configuration as-is. There are special
  parameters ignored by the configuration template, used to manage the
  configuration entry itself:

  ``name``
    The name of the ruleset, stored as ``Name`` in the configuration file.

  ``state``
    If not specified or ``present``, the ruleset is included in the
    configuration file. If ``absent``, the ruleset will be removed from the
    configuration file.

  ``comment``
    String or YAML text block with a comment added before the ruleset.

  ``raw``
    YAML text block with configuration which will be included in the
    configuration file as-is. Other parameters of a given ruleset will not be
    processed by the role.

``pulls``
  Optional. This parameter defines the contents of the
  :file:`conf/pulls` configuration file in the :command:`reprepro`
  repository. The ``pulls`` parameters from configuration entries with
  the same ``name`` parameter are merged together and can affect each other.
  See the :man:`reprepro(1)` manual page for possible options.

  The configuration is defined as a list of YAML dictionaries, each dictionary
  can define a single pull ruleset. The ``name`` parameter is used to
  define the ruleset name. Other options should be specified as defined in the
  manual page and will be added to the configuration as-is. There are special
  parameters ignored by the configuration template, used to manage the
  configuration entry itself:

  ``name``
    The name of the ruleset, stored as ``Name`` in the configuration file.

  ``state``
    If not specified or ``present``, the ruleset is included in the
    configuration file. If ``absent``, the ruleset will be removed from the
    configuration file.

  ``comment``
    String or YAML text block with a comment added before the ruleset.

  ``raw``
    YAML text block with configuration which will be included in the
    configuration file as-is. Other parameters of a given ruleset will not be
    processed by the role.
