Changelog
=========

v0.1.3
------

*Released: 2016-08-06*

- Move the following variables from ``vars/main.yml`` to ``defaults/main.yml``:
  - reprepro_nginx_server_http
  - reprepro_nginx_server_https
  - reprepro_debian_previous
  - reprepro_debian_next
  - reprepro_debian_releases
  - reprepro_debian_suites
  - reprepro_debian_architectures
  [timitos]

- Expose ``ansible_domain`` and ``ansible_fqdn`` in default variables so they
  can be modified if necessary. [drybjed]

- Expose ``gnupg.tar`` filename and location in the ``secret/`` directory in
  role default variables, so that they can be changed if needed. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

- Reload ``systemd`` daemons when ``inotincoming`` init script is installed. [drybjed]

- Move the ``reprepro`` incoming directory to ``/var/spool/reprepro/incoming``
  to fix the issue of the ``www-data`` user not able to move the files into
  ``/var/lib/reprepro/`` subdirectory due to restricted permissions. [drybjed]

v0.1.2
------

*Released: 2015-10-26*

- All dictionary lookups in different lists are wrapped in ``d()`` default
  value to make sure that when a dictionary key does not exist, the list is
  still correctly templated and used in Ansible v2. [drybjed]

- Package installation task won't automatically upgrade the installed packages.
  [drybjed]

- Convert all Ansible tasks from ``sudo`` to ``become``. [drybjed]

v0.1.1
------

*Released: 2015-04-30*

- Backport repositories have been redesigned to support distribution upgrades.

  Role will set up repositories for Debian Backports for current release,
  previous release and next release, with corresponding symlinks. When a new
  release comes around, this should let existing repositories easily migrate
  from "stable" to "oldstable" and create new "stable" repository for new
  release. [drybjed]

- By default, Debian Backport repositories will support ARM architectures in
  addition to AMD64 and i386. [drybjed]

- ``reprepro_uploaders_local`` variable has been renamed to
  ``reprepro_uploaders_default_rules`` to allow split between "local"
  repositories and repositories for distribution backports. [drybjed]

- Export repositories when configuration of distributions managed on the server
  changes. [drybjed]

- Change the location of gnupg snapshots stored in the DebOps ``secret/``
  directory on Ansible Controller to not create clashes between different hosts
  using the same domain name. [drybjed]

- Add new mirror configuration for Debian GNU/Linux 8 (Jessie). [drybjed]

- Switch Debian mirror servers to new HTTP redirector address. [drybjed]

- Redesign "local" repositories to support distribution upgrades.

  Repository naming scheme has been changed, new naming scheme::

      <release>-<origin>         (production, direct upload denied)
      <release>-<origin>-staging (testing, direct upload allowed)

  Previous, current and next Debian Stable releases are configured when
  repository is enabled on Debian-based hosts. On Ubuntu hosts, only
  repositories for current Ubuntu LTS release are configured at the moment.
  [drybjed]

v0.1.0
------

*Released: 2015-04-26*

- First release. [drybjed]

