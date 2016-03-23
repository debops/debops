Changelog
=========


v0.1.0
------

*Released: 2016-03-22*

- Initial release. [ypid]

- Switch the default Debian mirror to new official redirector at
  http://httpredir.debian.org/. [ypid]

- Add support for proxying the :program:`apt-cacher-ng` server via :program:`nginx` on
  a subdomain. Direct access to the cache is still possible. [drybjed]

- Enable installation of backported ``apt-cacher-ng`` package on Debian Wheezy.
  [drybjed]

- Check boolean values in configuration template. [drybjed]

