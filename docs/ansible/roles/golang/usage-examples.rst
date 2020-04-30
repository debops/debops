.. Copyright (C) 2015      Nick Janetakis <nickjanetakis@gmail.com>
.. Copyright (C) 2016-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Usage examples
==============

These example configurations show how :ref:`debops.golang` role can be used
either via the Ansible inventory, or by other Ansible roles using role
dependent variables.


The ``docker-gen`` package
--------------------------

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
--------------------

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
---------------------

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
---------------------

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
