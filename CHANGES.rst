Changelog
=========

v0.2.0
------

*Released: 2015-09-03*

- Use a static, configurable filename for ``nginx`` configuration. This helps
  when wiki domain is changed on an existing installation.

  This change will generate a new nginx configuration file. Depending on your
  server layout you might need to remove at least the symlink to the old
  DokuWiki configuration file to prevent ``nginx`` server from failing to
  restart properly. [drybjed]

- Change the ``dokuwiki`` system user home directory to be the same as website
  directory, based on ``ansible_local.nginx.www`` local Ansible fact. [drybjed]

- Add missing ``{% endif %}`` to the ``preload.php.j2`` template, required by
  Jinja engine to correctly generate the file. [drybjed]

v0.1.0
------

*Released: 2015-03-26*

- Initial release [drybjed]

