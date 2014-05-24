ginas changelog
===============

## May 2014

### New roles

- **nodejs**: [NodeJS](http://nodejs.org/) is a platform built on Chrome's
  JavaScript runtime for easily building fast, scalable network applications.

- **etherpad**: [Etherpad Lite](http://etherpad.org/) is a collaborative web
  text editor written using NodeJS.

- **gitlab_ci** and **gitlab_ci_runner**: [GitLab CI](https://www.gitlab.com/gitlab-ci/)
  is a Continuous Integration server which integrates with
  [GitLab](https://www.gitlab.com/). It is divided into two components - GitLab
  CI itself which coordinates work between GitLab and its runners, and GitLab
  CI Runner which executes provided scripts.

### secrets

Support for "secret" directory on Ansible Controller has been rewritten (third
time, hopefully the last). Previously 'secret' variable usage was optional and
it needed to be defined manually by the user; now it will be required (with
time, tasks that depend on it will not check if 'secret' variable is defined,
to simplify the code) and will be automatically defined relative to currently
selected inventory. There are several variables that can be used to influence
this behaviour. More information and explanation of the concept can be found in
[README.md](https://github.com/ginas/ginas/blob/master/playbooks/roles/secret/README.md)
file of the 'secret' role.

To further redesign the 'secret' concept, automatic encryption of the directory
using `encfs` has been disabled. If you currently have encrypted secret
directory and want to keep the contents, you should decrypt it and move the
contents to the new, unencrypted, secret directory. To protect the data
I suggest using an encrypted filesystem, like eCryptfs or LUKS.

There are currently no plans to enable encryption for secret directory, but it
might happen in the future. At the moment users should secure the data by
themselves. Any suggestions how to bring back encryption in a reliable and easy
way are welcome.

### nginx

nginx installation from Debian Backports has been temporarily disabled due to
problems with first daemon startup on install - when nginx from backports is
installed, an empty pidfile is created on first startup and system init script
does not have control over nginx daemon, which results in an error when nginx
needs to be restarted. When this error is resolved, change will be reverted.

You can now tell nginx role to use IP-based SSL certificates (instead of
FQDN-based), useful for hosts without DNS domain name, like Vagrant virtual
machines.

You can disable 'favicon.ico' filtering in nginx server configuration and let
your application handle the icon (used by Etherpad role).

### Other news

Default Vagrant setup has been simplified to use only one server with
a selection of web applications to install (either GitLab, ownCloud or phpIPAM,
selectable via Vagrant inventory).

If you use Debian Preseed server, you can define short hostnames in DNS and use
them instead of long hostname to point installer to a correct preseed file
- for example instead of using `url=destroy.debian.nat.example.org`, you can
use `url=destroy.debian`. You can also change the domain that is configured for
Debian Preseed server, when for example your datacenter uses long hostnames for
its servers.

`interfaces` role has been modified to use separate variable for interface list
defined via dependency. This will allow interfaces to be configured in
subsequent plays instead of just the common one (needed for example by `nat`
role to configure separate bridge interface).

Abusive Hosts Blocking List has been removed from Postfix DNSBL list because of
[impending end of the service](http://ahbl.org/content/changes-ahbl).

Travis CI build has been modified to test idempotence of the playbook - it is
run a second time to check if there are any changes.

`gitlab` role has been updated with support for GitLab CE 6.9. This update is
very light, without additional set of config files, because changes made in
'6-9-stable' branch added only commented out code which means that older config
files should work fine.


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

