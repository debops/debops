.. Copyright (C) 2015      Nick Janetakis <nickjanetakis@gmail.com>
.. Copyright (C) 2016-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _golang__ref_defaults_detailed:

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.golang`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _golang__ref_packages:

golang__packages
----------------

Each ``golang__*_packages`` variable contains a list of YAML dictionaries, each
dictionary defines a Go package installation using specific parameters:

``name``
  Required. A name of the Go package definition. Multiple configuration entries
  with the same ``name`` parameter are merged together in order of appearance.
  This parameter is not used for anything else.

``state``
  Optional. If not defined or ``present``, the Go application will be
  installed. When the parameter is set to ``absent`` or ``ignore``, the Go
  application will not be processed by Ansible; there's currently no support
  for uninstalling already installed Go applications.

  If the parameter is set to ``append``, a given configuration entry will be
  evaluated only if the entry with the same ``name`` was already defined
  earlier. This can be useful to modify role dependent configuration through
  the Ansible inventory.

``apt_packages``
  Optional. A string or a list of APT packages with the Go application to
  install. If the APT packages are not available, the role will automatically
  switch to an installation from upstream.

``apt_required_packages``
  Optional. List of APT packages which should be present on a host when Go
  application is downloaded directly from upstream. Some of the Go applications
  are distributed as tarballs; installing ``unzip`` APT packages might be
  requires to uncompress the ``.zip`` archives.

``apt_dev_packages``
  Optional. List of APT packages which should be present on a host when Go
  application is built from source. You can specify here additional packages
  that are required for building the binary; the
  :envvar:`golang__apt_dev_packages` variable contains the default set of APT
  packages which will be installed when a Go application is to be built from
  source.

``upstream``
  Optional, boolean. If defined and ``True``, install the Go application from
  upstream, even if APT packages are available. The ``False`` value will result
  in not installing the Go application at all if the APT packages are not
  available.

``upstream_type``
  Optional. Specify the type of upstream installation to perform, either
  ``git`` (default) to install the Go application from source, or ``url`` to
  download the Go application binaries directly. Either option needs to be
  configured as well for the preferred installation method to work.

``gpg``
  Optional. A string or a list of GPG key fingerprints to add to the
  :envvar:`golang__user` GPG keyring. The key management is performed by the
  :ref:`debops.keyring` Ansible role; you can use the
  :ref:`keyring__ref_dependent_gpg_keys` syntax to define the GPG keys to
  install or remove.

``url``
  Optional. A list of YAML dictionaries, each dictionary defines a remote
  resource which can be downloaded to the UNIX account defined in the
  :envvar:`golang__user` variable, optionally unpacked from an archive by the
  ``unarchive`` Ansible module and verified using GPG keys. With this
  parameter, Go applications can be downloaded directly from upstream.

  Each entry in the list is defined with specific parameters:

  ``src``
    Required. The URL of the file to download.

  ``dest``
    Required. Directory where the downloaded file will be stored, relative to
    the :envvar:`golang__gosrc` directory.

  ``checksum``
    Optional. Checksum (usually ``sha256``) of the downloaded file. This
    parameter is not strictly required, but should be used with bigger files
    because without the checksum available Ansible will download the specified
    file on each run to compare it with the downloaded file.

  ``unarchive``
    Optional, boolean. If defined and ``True``, a given file is presumed to be
    a tarball and its contents will be extracted with the ``unarchive`` Ansible
    module.

  ``unarchive_dest``
    Optional. Path where the contents of the specified file will be unarchived
    to, relative to the :envvar:`golang__gosrc` directory. If not specified,
    files will be extracted in the same directory where the archive was
    downloaded to.

  ``unarchive_creates``
    Optional. Specify a path relative to the :envvar:`golang__gosrc` directory.
    If that path is present on the host, the ``unarchive`` Ansible module will
    not try to extract the archive contents again on the next Ansible run,
    ensuring idempotency.

  ``gpg_verify``
    Optional, boolean. If defined and ``True``, the role will use the
    :command:`gpg --verify` command to check the valid signature of a file.

    it's best to first download the intended file, and then its detached GPG
    signature (usually with the ``.asc`` extension) which should have this
    parameter enabled; the :command:`gpg` command will automatically assume
    that the signed file is named after the signature file, without the
    ``.asc`` extension. The GPG keys need to be defined using the ``gpg``
    parameter to be correctly imported beforehand by the :ref:`debops.keyring`
    role.

``url_binaries``
  Optional. List of downloaded binaries which should be installed system-wide,
  by default in the :file:`/usr/local/bin/` directory.

  Each list entry can define a path to the binary, relative to the
  :envvar:`golang__gosrc` path. The specified binary will be copied to the
  default installation directory without renaming the binary.

  Alternatively, a given binary can be described using a YAML dictionary with
  specific parameters:

  ``src``
    Path to a given binary, relative to the :envvar:`golang__gosrc` directory.

  ``dest``
    Path where a given binary should be installed. You can specify just the
    name of the binary, in which case it will be installed in
    :file:`/usr/local/bin/` directory by default.

  ``mode``
    Specify the default file mode to use. If not specified, ``0755`` will be
    used by default.

  ``notify``
    A string or a YAML list of Ansible handlers to notify when a binary is
    first installed or updated. This parameter only makes sense when the
    :ref:`debops.golang` role is ued in a playbook as a dependent role, and the
    subsequent application role(s) define a handler to use. In such case, this
    functionality can be used to restart a service after the binary is
    upgraded.

``git``
  Optional. List of YAML dictionaries, each dictionary defines a :command:`git`
  repository which can be cloned to the UNIX account defined in the
  :envvar:`golang__user` variable and subsequently can be used to build the Go
  application binaries from source. The :command:`git` tag or commit signatures
  will be verified if the GPG keys are configured using the ``gpg`` parameter.

  Each :command:`git` repository is defined using specific parameters:

  ``repo``
    The URL of the :command:`git` repository to clone. Currently only
    ``https://`` scheme is supported.

  ``dest``
    The path to which the specified repository will be cloned, relative to the
    :envvar:`golang__gosrc` directory. If not specified, the ``dest`` directory
    will be based on the URL specified in the ``repo`` parameter.

  ``version`` / ``branch``
    The :command:`git` branch or tag to check out after cloning the repository.

  ``depth``
    If specified, only the specified number of revisions will be cloned instead
    of the whole repository. If not specified, the value of the
    :envvar:`golang__git_depth` variable will be used by default.

  ``build_script``
    A string or YAML text block with a shell script that specifies how the Go
    application should be built. It will be executed as a Bash script, with the
    :envvar:`golang__user` privileges, in the directory where the repository
    has been cloned.

``git_binaries``
  Optional. List of built binaries which should be installed system-wide, by
  default in the :file:`/usr/local/bin/` directory.

  Each list entry can define a path to the binary, relative to the
  :envvar:`golang__gosrc` path. The specified binary will be copied to the
  default installation directory without renaming the binary.

  Alternatively, a given binary can be described using a YAML dictionary with
  specific parameters:

  ``src``
    Path to a given binary, relative to the :envvar:`golang__gosrc` directory.

  ``dest``
    Path where a given binary should be installed. You can specify just the
    name of the binary, in which case it will be installed in
    :file:`/usr/local/bin/` directory by default.

  ``mode``
    Specify the default file mode to use. If not specified, ``0755`` will be
    used by default.

  ``notify``
    A string or a YAML list of Ansible handlers to notify when a binary is
    first installed or updated. This parameter only makes sense when the
    :ref:`debops.golang` role is ued in a playbook as a dependent role, and the
    subsequent application role(s) define a handler to use. In such case, this
    functionality can be used to restart a service after the binary is
    upgraded.
