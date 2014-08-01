## backporter

This is a helper [Ansible](https://github.com/ansible/ansible.git) role which
allows you to ensure that Debian packages with certain versions are available
on your hosts. If requested version is not available in currently configured
APT repositories (for example `wheezy` and `wheezy-backports` from official
Debian archives), `backporter`, if properly configured, will try to build and
install required version from `testing` repository.

If successful, newly built backported packages will be uploaded to Ansible
Controller host which then can make these packages available to the rest of the
Ansible cluster using `ginas.reprepro` role to create and maintain local APT
repository.

`backporter` role is based on instructions from [Simple Backport Creation
HOWTO](https://wiki.debian.org/SimpleBackportCreation). `rmadison` utility from
`devscripts` package is used to check available Debian packages, and depends on
availability of [Debian QA Madison service](https://qa.debian.org/madison.php).

### Usage overview

`backporter` role is designed to be used as a dependency of another role
(multiple instances are supported). Thanks to this design, primary goal of the
role is to ensure that a specified version of the package is already available
in the configured repositories. If this is true, `backporter` skips all other
steps and primary role continues as usual, installing the package by itself
from APT repositories.

By defaut version and availability checks are performed on specific
distribution, [Debian Wheezy](https://www.debian.org/releases/stable/) (current
Stable Debian distribution) and should not interfere on other distributions
(Debian Jessie, Ubuntu). If needed, backport of a package can be enforced by
a variable.

To use `backporter` with your own role, create `meta/main.yml` file and add
information about role dependencies:

    ---
    dependencies:
      - role: ginas.backporter
        backporter_package: 'foo'
        backporter_version: '1.0'

This configuration will ensure that package `foo` is available in APT
repository in at least version `1.0` (different version formats are handled
internally by Ansible). If it's not available, `backporter` will try to
download a `.dsc` source package `foo` from Debian Testing repositories and
build it for Debian Wheezy (without using packages from Testing).

Different packages might require different configuration (for example name of
source package is different, additional packages need to be installed for the
build to be successful, and so on). Read `defaults/main.yml` file of
`backporter` role to see different configuration variables you can use in
dependency definition. To make configuration easier, it's best to try and build
the packages from `.dsc` sources manually using commands specified in [Simple
Backport Creation HOWTO](https://wiki.debian.org/SimpleBackportCreation) to
easily find out issues with build process, list of required packages, and so
on.

If Debian QA Madison service is not available, `backporter` will try to use
a static version number (if it is set in dependency variable) to look for
source packages. If static version number is not set, playbook execution will
stop and user will be asked to provide one, which can be found on
[https://packages.debian.org/](https://packages.debian.org/) webpage.

### Local package cache and multiple package installation

Some packages might require dependent packages of versions different than the
ones available in your APT repositories. In this case, you can use `backporter`
role as a dependency multiple times, to backport different packages in order.

To avoid problems with multiple package interdependencies during installation
which cannot be solved using APT because packages are not yet present in local
APT repository, you can use local cache directory, specified using
`backporter_cache` variable, for example `backporter_cache:
'/tmp/package-cache'`. Backported packages will be put there and stored for
later use (you might also need to disable automatic installation of generated
packages with `backporter_install: False` variable).

After all needed packages have been backported, use `backporter` role again
without specified package to backport, but specifying cache directory and list
of packages to install. After installation is finished, cache directory will be
automatically removed to prevent subseqent reinstalls (you can block that with
`backporter_cache_clean: False` variable).

### Sharing backported packages using reprepro

By default, `backporter` role will try to upload created `.deb` packages to
Ansible Controller host, to a specific directory within the `secret` directory
tree. This way packages can be used on other hosts within the Ansible cluster
using `ginas.reprepro` role.

To enable this, you need to specify a FQDN hostname of a host within Ansible
cluster (or a group within that cluster) which will act as an APT cache and
local APT repository. To do that, in your `inventory/all.yml` (or other part of
the inventory, per group or per host), set variable:

    ---
    apt: 'host.example.com`

This variable will tell `ginas.apt` role to configure `apt-cacher-ng` APT cache
and `reprepro` repository on specified host, automatically enabling use of
these services on other hosts within cluster/group. `ginas.reprepro` role will
download packages from `secret` directory of Ansible Controller and include
them in local APT repository, which then can be accessed by other hosts within
the cluster.

You can easily exploit this feature by, for example, creating temporary LXC
containers using `ginas.lxc` role, building backported `.deb` packages that
you need (by configuring specific Ansible roles in these temporary containers)
and distributing them among your other hosts using local APT repository.
Temporary containers can then be removed to reclaim space/IP addresses, etc.

