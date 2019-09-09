Usage examples
--------------

These example configurations show how :ref:`debops.golang` role can be used
either via the Ansible inventory, or by other Ansible roles using role
dependent variables.


The ``docker-gen`` package
~~~~~~~~~~~~~~~~~~~~~~~~~~

The `docker-gen`__ application can be used to generate configuration files or
scripts based on templates with `Docker`__ metadata as a configuration source.
The :ref:`debops.docker_gen` role can be used to install and configure it as
a system service.

.. __: https://github.com/jwilder/docker-gen
.. __: https://docker.com/

To build the :command:`docker-gen` Go binary, ``gocolorize`` and ``glock`` Go
packages are required as build dependencies (they don't need to be installed
system-wide, only in the build environment). The ``gocolorize`` Go package is
packaged in Debian, but ``glock`` is not. All three source repositories do not
provide GPG-signed tags or commits, ``glock`` does not even have a tagged
release (old software tends to be like that).

This is an example install configuration for the :ref:`debops.golang` role:

.. code-block:: yaml

   golang__packages:

     - name: 'gocolorize'
       apt_packages: 'golang-github-agtorre-gocolorize-dev'
       git:
         - repo: 'https://github.com/agtorre/gocolorize'
           version: 'v1.0.0'

     - name: 'glock'
       git:
         - repo: 'https://github.com/robfig/glock'
           #version: 'master'
           build_script: |
             go get -u golang.org/x/tools/go/buildutil
             go build && go install

     - name: 'docker-gen'
       apt_dev_packages: [ 'gcc', 'libc6-dev' ]
       git:
         - repo: 'https://github.com/jwilder/docker-gen'
           version: '0.7.4'
           build_script: |
             glock sync -n < GLOCKFILE
             make docker-gen
       git_binaries:
         - 'github.com/jwilder/docker-gen/docker-gen'

The :ref:`debops.golang` role will install the ``gocolorize`` dev package from
Debian if it's available, otherwise it will be built and installed in the Go
build environment from its source repository.

The ``glock`` Go package is not included in Debian, therefore it will be built
and installed from its source repository. Note that the repository does not
have a release, therefore the ``master`` branch is checked out by default; an
additional ``go-buildutil`` Go package is also installed using the :command:`go
get` command. ``glock`` is only a build dependency, and is not installed
system-wide.

The ``docker-gen`` Go package is cloned from its source repository on
a specific :command:`git` tag. Additional APT packages required for building
the binary are installed from the Debian repository. The built binary is
installed to :file:`/usr/local/bin/` directory and registered in the Go package
database maintained by the role.


The ``etcd`` package
~~~~~~~~~~~~~~~~~~~~

The `etcd`__ application is a distributed key-value store written in Go, with
a server and client binaries. :command:`etcd` is included in Debian Buster, but
can also be installed from upstream.

.. __: https://etcd.io/

This is an example install configuration for the :ref:`debops.golang` role:

.. code-block:: yaml

   golang__packages:

     - name: 'etcd'
       apt_packages: [ 'etcd-server', 'etcd-client' ]
       gpg: 'B48D 29DE 85DD 570F 8873  8A0E B1C2 6A6D 6FF2 2270'
       git:
         - repo: 'https://github.com/etcd-io/etcd'
           version: 'v3.3.13'
           build_script: |
             make clean build
       git_binaries:
         - 'github.com/etcd-io/etcd/bin/etcd'
         - 'github.com/etcd-io/etcd/bin/etcdctl'

The :ref:`debops.golang` Ansible role will check if the specified APT packages
are available; if not, the specified version will be cloned from the sources
repository and the :command:`git` tag will be verified using the specified GPG
key. When the build is finished, the pecified binaries will be installed in the
:file:`/usr/local/bin/` directory.


The ``nomad`` package
~~~~~~~~~~~~~~~~~~~~~

`Hashicorp Nomad`__ is a job orchestrator which, combined with Consul and Vault
services, can be used to manage containerized and non-containerized
applications in a cluster.

.. __: https://www.nomadproject.io/

Nomad is currently (as of 2019) not packaged in Debian Stable. Hashicorp
provides its own download server for their applications, we can use that to
download the Nomad binary directly.

.. code-block:: yaml

   golang__packages:

     - name: 'nomad'
       apt_packages: 'nomad'
       apt_required_packages: 'unzip'
       upstream_type: 'url'
       url:
         - src: 'https://releases.hashicorp.com/nomad/0.9.5/nomad_0.9.5_linux_amd64.zip'
           dest: 'releases/linux-amd64/hashicorp/nomad/0.9.5/nomad_0.9.5_linux_amd64.zip'
           checksum: 'sha256:9a137abad26959b6c5f8169121f1c7082dff7b11b11c7fe5a728deac7d4bd33f'
           unarchive: True
           unarchive_creates: 'releases/linux-amd64/hashicorp/nomad/0.9.5/nomad'
       url_binaries:
         - src: 'releases/linux-amd64/hashicorp/nomad/0.9.5/nomad'
           dest: 'nomad'

The :ref:`debops.golang` role will check if the ``nomad`` APT package is
available. If not, it will make sure that the ``unzip`` APT package is present
on the host, download the specified tarball from the Hashicorp release server,
extract its contents and copy the specified :command:`nomad` binary to the
:file:`/usr/local/bin/` directory.


The ``minio`` package
~~~~~~~~~~~~~~~~~~~~~

`MinIO`__ is an Amazon Simple Storage Service (S3) compatible object storage
server written in Go. It's currently not included in Debian, but upstream
provides GPG-signed binary releases regularly, and it's also possible to build
one locally.

.. __: https://minio.io/

.. code-block:: yaml

   golang__packages:

     - name: 'minio'
       upstream_type: 'url'
       gpg: '4405 F3F0 DDBA 1B9E 68A3  1D25 12C7 4390 F9AA C728'
       url:

         - src: 'https://dl.min.io/server/minio/release/linux-amd64/archive/minio.RELEASE.2019-08-21T19-40-07Z'
           dest: 'releases/linux-amd64/minio/minio.RELEASE.2019-08-21T19-40-07Z'
           checksum: 'sha256:89b313a892455f7cdeae1c9d037d9d88d60032913c530b0f5968211264e667b7'

         - src: 'https://dl.min.io/server/minio/release/linux-amd64/archive/minio.RELEASE.2019-08-21T19-40-07Z.asc'
           dest: 'releases/linux-amd64/minio/minio.RELEASE.2019-08-21T19-40-07Z.asc'
           checksum: 'sha256:16f492ef21d26874360f7423c221e57c73a93f682e6737f7590eb94313e23615'
           gpg_verify: True

       url_binaries:
         - src: 'releases/linux-amd64/minio/minio.RELEASE.2019-08-21T19-40-07Z'
           dest: 'minio'
           notify: [ 'Restart minio' ]
       git:
         - repo: 'https://github.com/minio/minio'
           version: 'RELEASE.2019-08-21T19-40-07Z'
           build_script: |
             make clean build
       git_binaries:
         - src: 'github.com/minio/minio/minio'
           dest: 'minio'
           notify: [ 'Restart minio' ]

Because there's no ``apt_packages`` parameter, the role will install the
upstream version by default. The ``upstream_type`` parameter is sed to ``url``,
which means that :ref:`debops.golang` will download the specified binary and
its ``.asc`` GPG signature, verify the GPG signature against the GPG key
installed by the role and install the specified binary in the
:file:`/usr/local/bin/` directory.

Alternatively, the user can request installation using the :command:`git`
sources, which can be done by adding in the inventory:

.. code-block:: yaml

   golang__packages:

     - name: 'minio'
       state: 'append'
       upstream_type: 'git'

This will tell the :ref:`debops.golang` role to download the :command:`minio`
source code and compile it locally. The compiled binary will be installed in
the :file:`/usr/local/bin/` directory.

In both cases, if the :command:`minio` binary is changed, the ``"Restart
minio"`` Ansible handler will be notified. This is useful in cases where Go
packages are installed for other Ansible roles via role dependent variables,
where the handler can be defined in the application role. Usage of the
``handler`` parameter should be avoided in Go packages defined via the Ansible
inventory.


Configuration syntax
--------------------

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


Default variables
-----------------
