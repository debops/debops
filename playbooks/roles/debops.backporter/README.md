## debops.backporter

[![Platforms](http://img.shields.io/badge/platforms-debian%20|%20ubuntu-lightgrey.svg)](#)

This is a helper [Ansible](https://github.com/ansible/ansible.git) role which
allows you to ensure that Debian packages with certain versions are available
on your hosts. If requested version is not available in currently configured
APT repositories (for example `wheezy` and `wheezy-backports` from official
Debian archives), `backporter`, if properly configured, will try to build and
install required version from `testing` repository.

If successful, newly built backported packages will be uploaded to Ansible
Controller host which then can make these packages available to the rest of the
Ansible cluster using `debops.reprepro` role to create and maintain local APT
repository.

`backporter` role is based on instructions from [Simple Backport Creation
HOWTO](https://wiki.debian.org/SimpleBackportCreation). `rmadison` utility from
`devscripts` package is used to check available Debian packages, and depends on
availability of [Debian QA Madison service](https://qa.debian.org/madison.php).

### Installation

To install `debops.backporter` using Ansible Galaxy, run:

    ansible-galaxy install debops.backporter

### Role dependencies

- `debops.secret`



### Role variables

List of default variables available in the inventory:

    ---
    
    # ---- Required configuration variables ----
    
    # Name of a package to build
    backporter_package: ""
    
    # What package version should be available in APT repositories?
    backporter_version: ""
    
    
    # ---- Common configuration variables ----
    
    # If a package to backport is not present in current APT repositoriesA, version
    # comparsion with required package will fail. In that case you can fake
    # non-existent version number to force backport of the package (keep it much
    # lower than existing packages to be compatible with future releases).
    backporter_fake_version: ""
    
    # Name of a source package to build from (usually the same as the package)
    backporter_source_package: '{{ backporter_package }}'
    
    # List of required packages to install before build
    backporter_prerequisites: []
    
    # Fallback version number of source package to use in case rmadison service is
    # inaccessible
    backporter_source_version: ""
    
    # Regexp to use to find orig tarball in build directory (by default Debian uses
    # .tar.xz format but it might be different)
    backporter_source_orig: '.orig.tar.xz'
    
    # Which Debian component to look in for a package source
    backporter_component: 'main'
    
    # What comparsion to use to check for available package version? By default
    # check if package available is older than the package you are requesting
    backporter_comparsion: '<'
    
    # List of regexps used to find created .deb packages which will be installed on
    # build host
    backporter_install_packages: [ '{{ backporter_package }}_*.deb' ]
    
    # List of regexps used to find created .deb packages which will be uploaded to
    # Ansible Controller host (in 'secret' directory) to include in local reprepro
    # repositories
    backporter_upload_packages: '{{ backporter_install_packages }}'
    
    # Send mail reminder to administrator about uploaded packages? If yes, specify
    # list of mail recipients
    backporter_mail_to: [ '{{ backporter_email }}' ]
    
    # Specify a temporary directory where backported packages will be stored for
    # later installation. Without 'backporter_package' set, specify directory where
    # packages to install are stored.
    backporter_cache: ""
    
    # Delete cache directory after installation?
    backporter_cache_clean: True
    
    
    # ---- Backport configuration variables ----
    
    # Maintainer name
    backporter_maintainer: 'Automated Package Maintainer'
    
    # Maintainer mail address (will receive information about new uploaded packages)
    backporter_email: 'root@{{ ansible_domain }}'
    
    # Base string to append to backported package version (will be used in
    # changelog and name of .orig.tar.xz file)
    backporter_new_version: '~bpo{{ ansible_distribution_version | replace(".","") }}'
    
    # Full string to append to backported package version (will be used in
    # changelog and finished .deb package names)
    backporter_changelog_version: '{{ backporter_new_version }}+'
    
    # Message included in changelog
    backporter_changelog_message: 'Package rebuilt automatically by Ansible for local {{ backporter_release }}-backports repository.'
    
    
    # ---- Backporter role internal variables ----
    
    # Linux distribution and release which will trigger backport requirement tests
    backporter_distribution: 'Debian'
    backporter_release: 'wheezy'
    
    # Should package be backported regardless of wether it's currently available in
    # APT repository?
    backporter_force: False
    
    # Address to a Debian mirror which will be used to download source packages
    backporter_build_mirror: 'http://cdn.debian.net/debian'
    
    # Name of next distribution release which will be used to check available
    # package version (don't use suite names here, because backports make sense
    # only for specific releases)
    backporter_build_codename: '{{ backporter_next[backporter_release] }}'
    
    # Length of the slice of source package name used to create path to source
    # package (from the start of the string). If you are backporting a library, set
    # this to 4 to use path like '.../main/liba/libansible/libansible_...'
    backporter_source_package_slice: 1
    
    # Part of URI to a source package (last part will be added during runtime after
    # check for available versions)
    backporter_source_path: '{{ backporter_build_mirror }}/pool/{{ backporter_component }}/{{ backporter_source_package[0:backporter_source_package_slice] }}/{{ backporter_source_package }}/{{ backporter_source_package }}'
    
    # Path to directory on remote host where backported packages will be built
    backporter_build_path: '/usr/local/src'
    
    # Command used to download .dsc package sources. If you have problems with GPG
    # key verification, set this to 'dget -u'
    backporter_command_dget: 'dget'
    
    # If a package that is backported does not exist in current Debian release, its
    # build dependencies might not exist too and 'apt-get build-dep' step will fail.
    # Instead enable this variable and provide all required dependencies in
    # 'backporter_prerequisites' variable.
    backporter_skip_builddep: False
    
    # Should .deb packages that are created be automatically installed on build
    # host?
    backporter_install: True
    
    # Should .deb packages that are created be automatically uploaded to Ansible
    # Controller in a directory accessible by 'reprepro' role?
    backporter_upload: True
    
    # Path to a directory on Ansible Controller used by 'reprepro' role to download
    # packages to local APT repository
    backporter_upload_storage: '{{ secret + "/reprepro/includedeb/" + backporter_release + "-backports" }}'
    
    # List of required Debian SDK packages to install on a host before backporting
    backporter_sdk_packages: [ 'devscripts', 'build-essential', 'debian-keyring',
                               'liburi-perl', 'libdistro-info-perl', 'python-httplib2',
                               'curl', 'debhelper' ]
    
    # List of source repositories to enable on a host
    backporter_repositories:
      - 'deb-src {{ backporter_build_mirror }} {{ ansible_distribution_release }} main contrib'



List of internal variables used by the role:

    backporter_register_package_dpkg_version
    backporter_register_build_source_dir
    backporter_register_package_version
    backporter_build_root
    backporter_register_dsc_version


### Detailed usage guide

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
      - role: debops.backporter
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

#### Local package cache and multiple package installation

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

#### Sharing backported packages using reprepro

By default, `backporter` role will try to upload created `.deb` packages to
Ansible Controller host, to a specific directory within the `secret` directory
tree. This way packages can be used on other hosts within the Ansible cluster
using `debops.reprepro` role.

To enable this, you need to specify a FQDN hostname of a host within Ansible
cluster (or a group within that cluster) which will act as an APT cache and
local APT repository. To do that, in your `inventory/all.yml` (or other part of
the inventory, per group or per host), set variable:

    ---
    apt: 'host.example.com`

This variable will tell `debops.apt` role to configure `apt-cacher-ng` APT cache
and `reprepro` repository on specified host, automatically enabling use of
these services on other hosts within cluster/group. `debops.reprepro` role will
download packages from `secret` directory of Ansible Controller and include
them in local APT repository, which then can be accessed by other hosts within
the cluster.

You can easily exploit this feature by, for example, creating temporary LXC
containers using `debops.lxc` role, building backported `.deb` packages that
you need (by configuring specific Ansible roles in these temporary containers)
and distributing them among your other hosts using local APT repository.
Temporary containers can then be removed to reclaim space/IP addresses, etc.


### Authors and license

`debops.backporter` role was written by:

- Maciej Delmanowski - [e-mail](mailto:drybjed@gmail.com) | [Twitter](https://twitter.com/drybjed) | [GitHub](https://github.com/drybjed)


License: [GNU General Public License v3](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3))


***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).

