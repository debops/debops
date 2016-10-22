Changelog
=========

.. include:: includes/all.rst


v0.2.0
------

*Unreleased*

- | Renamed ``apt_cacher_ng__nginx_upstream`` to :envvar:`apt_cacher_ng__nginx__upstream`.
  | Renamed ``apt_cacher_ng__nginx_upstream_servers`` to :envvar:`apt_cacher_ng__upstream_servers`. [ypid]

- Added :envvar:`apt_cacher_ng__connect_protocol` to allow to specify which IP
  version to prefer when contacting upstream mirrors. [ypid]

* Added :envvar:`apt_cacher_ng__interfaces` for restricting access to
  connections through that interface by the firewall. [ypid]

Changed
~~~~~~~

- Don’t update :envvar:`apt_cacher_ng__base_packages` on subsequent role runs. [ypid]



v0.1.0
------

*Released: 2016-03-22*

- Initial release. [ypid]

- Switch the default Debian mirror to new official redirector at
  http://httpredir.debian.org/. [ypid]

- Add support for proxying the Apt-Cacher NG server via :program:`nginx` on
  a subdomain. Direct access to the cache is still possible. [drybjed]

- Enable installation of backported ``apt-cacher-ng`` package on Debian Wheezy.
  [drybjed]

- Check boolean values in configuration template. [drybjed]
