ginas changelog
===============

## May 2014

- added new, simplier Vagrant setup with only one server and easy way to select
  which application should be installed (GitLab, ownCloud or phpIPAM).


## April 2014

### New roles

- **dhcpd**: [ISC DHCP Server](https://www.isc.org/downloads/dhcp/) with
  extensive configuration template that accounts for multiple networks, and
  nesting. Non-authoritative by default, requires configuration by the admin.

- **mailman**: [GNU Mailing List Manager](http://www.list.org/), integrated
  with Postfix. Role allows you to create or remove multiple mailing lists,
  other configuration is done using web interface.

- **ntp**: [OpenNTPd](http://www.openntpd.org/), previously installed by `apt`
  role, has been moved to it's own role, with separate configuration. It will be
  installed on all hosts, excluding OpenVZ/LXC containers.

- **openvz**: [OpenVZ](http://openvz.org/Main_Page) support is based on
  packages from Debian Wheezy and custom kernel from `openvz.org` repository.
  Role will automatically configure container migration over SSH when multiple
  OpenVZ Hardware Nodes are configured, either as one big cluster, or multiple
  separate clusters.

### GitLab

In a span of a month, `gitlab` role gained support for two new releases
(6.7 and 6.8) and lost support for 6.5 and 6.6 releases due to [removal
of modernizr gem](https://github.com/gitlabhq/gitlabhq/issues/6687) which
prevents automated installation of older GitLab releases. Since GitLab 6.8 has
been officially released, upgrade from older release is unaffected by the
change and can still be tested.

GitLab role gained support for PostgreSQL database (both installation and
upgrades). Currently `postgresql` role in ginas is not very secure and does
not support creation of roles and databases using dependency variables
(similar to MySQL). Fixes are planned in the future. For now, production
GitLab instances should use MySQL database.

### nginx

You can install nginx package with support for SPDY and OCSP stapling from
Debian Backports (it is enabled by default via APT pinning in `apt` role).
Currently nginx package from Jessie seems to have problems with pid file which
is not created correctly on first install and system cannot stop or restart
`nginx` daemon. Killing the daemon manually and restarting `nginx` fixes the
problem.

nginx role gained support for Diffie-Hellman parameter generation (by default
done once a day via a cron script). Because of that, `openssl` command is now
a requirement, which forced `pki` role to be run almost at the beginning of
'common.yml' playbook.

Lists of available SSL cipher suites have been updated, and now you can also
see the source for a particular list (as a comment). 'nginx' role allows you
to select a particular ECDH curve, either globally for a host, or for a server
instance.

You can now define a list of allowed referer hosts which can hotlink
a particular location. This function was added to block access to Mailman web
interface from domains other than the allowed ones, which should prevent
subscribe backscatter spam via forms hosted on external servers.

### Other news

I've added `CONTRIBUTING.md` text file with information about project, mailing
list and IRC channel.

`CHANGELOG.md` file has been added which will describe significant changes in
ginas on a monthly basis.

