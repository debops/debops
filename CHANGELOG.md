ginas changelog
===============

## Changelog for 25-31 August 2014

### Changelog changes format

Previously changelog was written on a monthly basis, which resulted in very
long entries because of the pace that ginas is developed at. Because if that
I decided to instead write changelog entries on a weekly basis, which should
result in shorter and more manageable entries. In changelog you will also find
more general description of changes, to see every detail, I suggest running
`git log` from time to time. :-)

### ansible_managed variable is abolished

`ansible_managed` variable caused lots of problems with the playbook. Many
times Ansible rewrote the configuration files even though there were no
apparent changes, which caused restarts of various services and could prevent
access to them, which also caused subsequent playbook runs to be idempotent.

This variable has now been removed from all templates and replaced with
a static comment explaining that the file is managed using Ansible and all
changes made in the file will be lost.

### Other news

- in `mysql` role, firewall and tcpwrappers configuration has been moved from
  the main role to its dependencies (via dependency variables). Default
  variable which defines what hosts can connect to `mysqld` over the network
  has been renamed from `mysql_network_allow_list` to `mysql_mysqld_allow`.

***

## Changelog for August 2014

### New roles

- **rails_deploy**: [Nick Janetakis](https://github.com/nickjj) created a role
  which you can use to easily deploy custom Ruby on Rails applications. Other
  ginas roles like `nginx`, `postgresql`, and others will be used for the
  infrastructure. Look at the
  [README.md](https://github.com/ginas/ginas/blob/master/playbooks/roles/ginas.rails_deploy/README.md)
  of that role for more information.

- **redis**: [redis](http://redis.io/) is RAM-based key-value store. This role
  will let you install and configure redis as a separate service, or as
  a cluster composed of a master and slaves, monitored by `redis-sentinel`
  and automatically self-healing if necessary.

- **apt_preferences**: [APT
  preferences](https://wiki.debian.org/AptPreferences) can be used to
  influence the package selection process performed by APT during
  installation or upgrades.

- **monit**: [monit](http://mmonit.com/monit/) is a proactive service and
  system monitoring application, which can react to events, restart failed
  services and notify an administrator about errors.

### Ruby

`ruby` role has been rewritten to use `backporter` role on Debian Wheezy.
Instead of compilation of Ruby 2.1 from upstream sources, Ruby 2.1 packages
from Debian Jessie will be backported to Wheezy and automatically installed
(only base packages, use `gem` command to install Ruby gems). You can also use
local APT repository to distribute generated Ruby 2.1 .deb packages to other
hosts, drastically shortening the installation in the process.

Backported Ruby 2.1 packages should be compatible with Debian Jessie versions,
and upgrade process should proceed as normal (not tested).

If you don't want to use Ruby 2.1 on Debian Wheezy, or you use Ubuntu, you can
switch `ruby` role to use Ruby 1.9.1 (actually 1.9.3) and install packages from
official Wheezy or Ubuntu repositories.

### nginx

`nginx` role has been almost completely rewritten - syntax of most tasks has
been updated to use YAML parameters instead of inline parameters, default
server configuration template has been rewritten to be cleaner and easier to
use.

PHP5 support in nginx has been moved from the default server template to
a separate 'php5' template which extends the default. It has also been updated
to work better with some variables like PHP\_SELF or PATH\_INFO, but support
still is not 100% correct. Some websites might not work correctly (for example
Joomla CMS with SEO-friendly URLs). You will need to set `item.type: 'php5'` in
your site configuration to enable PHP5 support in nginx.

Nginx upstream configuration template has been extended to support Ansible
inventory groups (either using a host FQDN or all of its IP addresses).

`/etc/nginx/fastcgi_params` templated file is being dropped and original file
will be used instead. For now, `nginx` role will disable the diversion and
create temporary files to not do it again and have working nginx setup. They
will be removed in the future.

ginas will by default install `nginx` package from `wheezy-backports`
repository, which provides newer version of nginx (1.6.x), supporting [OCSP
Stapling](https://en.wikipedia.org/wiki/OCSP\_stapling) and [SPDY
protocol](https://en.wikipedia.org/wiki/SPDY). Problems with nginx not
correctly saving its PID on first start are prevented by restarting it on first
install by a task.

Variable `item.name` in nginx server template has changed type, from 'string'
to 'list'. You will need to update your roles/inventory configuration or
otherwise your nginx configuration might not work correctly.

You can now use `location_list` list variable to have more fine-grained control
over nginx server location sections, including nested locations and location
pattern defined by a separate variable.

Custom error pages for a server can be defined in `error_pages` hash variable.
They will be automatically protected from direct access using specific location
sections.

You can easily create a separate server configuration section with redirection
from specific domain names using `redirect_from` variable. If you enable it
using `True`, list of domains will be taken from `item.name` list (all but the
first one will be redirected to the first one), if you specify a list of
domains, this list will be used instead. This way you can easily create
redirection from `http://www.example.com/` to `http://example.com/` (or
`http://example.com/` to `http://www.example.com/` if the latter is defined as
the first element of `item.name` list).

### GitLab, GitLab CI, GitLab CI Runner

All GitLab roles have been modified to use `ruby` role as a dependency instead
of installing Ruby packages directly. This way, by default GitLab can use Ruby
2.1, which will be installed by default by `ruby` role.

`gitlab` role has been updated to support GitLab 7.0 and 7.1, including
seamless upgrade. GitLab 7.1 will be now installed by default, and your current
installation should be automatically upgraded during next playbook run. No new
configuration files have been added at this time, since changes are either in
the sections commented out by default, or at the moment irrelevant to ginas
environment (for example LDAP support, which currently is not present).

You can now change default Redis server used by GitLab using new
`gitlab_redis*` variables.

### OpenVZ

`openvz` role has new default container configuration script which uses disk
space and memory usage parameters calculated by Ansible (parameters used to
calculate proposed values can be tweaked using inventory variables). New
configuration file tries to split available resources according to number of
containers you plan to use on a Hardware Node (by default, 5).

Default container template has been changed to use official Debian 7.0 minimal
template.

There's new `vzbootstrap-ansible` script which helps with initial preparation
of OpenVZ clusters to be managed by Ansible. It will install Python support and
put users' OpenSSH public key inside the container for easy SSH access.

## users

Two varaibles have been renamed:

- ~~`users_dotfiles_enabled_default`~~ is now `users_default_dotfiles`, and is
  doing the same function (enable/disable dotfiles for all accounts
  globally);

- ~~`users_default_dotfile`~~ is renamed to `users_default_dotfiles_key` and
  specifies a default key from `users_dotfiles` hash to use to configure
  dotfiles;

### Other news

`postgresql` role will now set default password for `postgres` user and save it
in `secret` directory.

Many small changes in `backporter` role, which should be now more reliable and
can be correctly used to backport and install multiple packages at once.

`reprepro` role now supports `i386` architecture in addition to `amd64`.

Serial console is now disabled by default. This should prevent endless spamming
in syslog on hosts which don't have `/dev/ttyS0` configured (virtual machines
and containers, mostly). You can re-enable it by setting `console_serial: True`
in inventory.

`playbooks/` directory has been cleaned up, small separate playbooks have been
merged into a larger one, and a few no longer needed playbooks have been
removed.

`githost` role has been removed because we have `gitlab` role now.

Support for APT preferences has been removed from `apt` role and is now
a separate role, which can be used as a dependency by other roles.

`sks` role has been cleaned up and now automatically configures SKS cluster
based on a list of hosts in a specified group (`ginas_sks` by default).

`ansible` role can now detect Redis installed on Ansible Controller and
configure ansible to use host fact caching automatically.

`php5` role will now use timezone of the remote host instead of Ansible
Controller.

`interfaces` role will now use 2 second delay between bringing an interface
down and bringing it back up again, this should let different subsystems like
bridges, etc. "settle" and be ready for bringing the interface back up. This
should fix an error where NAT bridge interface could not be restarted properly.

`lxc` role should now correctly stop and start containers as needed on Ubuntu.

***

## Changelog for July 2014

### New roles

- **ruby**: [Ruby](https://www.ruby-lang.org/) programming language can be
  installed either from Debian packages (old 1.9.x versions) or from official
  sources (2.1.x versions). This role can be easily used as a dependency in
  other roles that require Ruby support.

- **smstools**: [smstools](http://smstools3.kekekasvi.com/) is a set of scripts
  which support communication with GSM modems under Linux. This role creates
  TCP to SMS and mail to SMS gateway using these scripts.

- **backporter**: this role is based on [Simple Backport Creation
  HOWTO](https://wiki.debian.org/SimpleBackportCreation) and can be used to
  make sure that packages with specific version are available using APT. If
  not, they can be built and installed automatically.

- **gitusers**: this role allows you to create user accounts with restricted
  privileges - these accounts will use
  [git-shell](http://git-scm.com/docs/git-shell.html) as default shell, and
  users will be able to manage their own git repositories (create, delete,
  etc.), and easily publish their own website content using `git`.

- **sftpusers**: using this role you can create restricted user accounts with
  access to chrooted home directory using
  [SFTPonly](https://en.wikibooks.org/wiki/OpenSSH/Cookbook/SFTP#Chrooted_SFTP_Accounts_Accessible_Only_from_Particular_Addresses).

### Removal of Jinja2 logic syntax from Ansible task lists

Recent security update to Ansible (1.6.7+) has disabled the option to use
Jinja2 if/else syntax in Ansible tasks (this does not affect templates).
Because of that some roles had to be modified to work correctly again (for
example `users` role will be split into three roles to support functionality
provided by only one role previously).

### LXC

LXC support on Ubuntu related to cgroups has been fixed, now cgroups are not
mounted on Ubuntu and systems other than Debian Wheezy, due to systemd being
the manager of cgroups.

New Debian containers (based on 'ginas' template script) will now be upgraded
using packages from `security.debian.org` repository during creation process.
This change affects the time needed to create new containers (from about 10
seconds to about a minute) but helps secure newly booted systems better. It's
an optional task that can be disabled using a variable.

Support for automatic build and installation of LXC 1.0 packages on Debian
Wheezy has been removed from 'lxc' role. It will be handled by
'ginas.backporter' role instead.

### users

Because of the security fix mentioned above, `users` role had to be modified to
work correctly again. Specifically, ability to create restricted accounts with
support for `sftponly` access or `git` repositories has been removed from
`users` role and will be introduced, after proper testing, using new roles and
new set of variables.

Support for [Monkeysphere](http://web.monkeysphere.info/) key management on
user accounts has been removed from `users` role and will be reintroduced at
a later date in a separate, non-common role (most likely merged into
`monkeysphere` role).

`users` role will now use `ansible_ssh_user` variable for configuration of
default user account with admin privileges.

### Other news

`postgresql` role has been modified to support more granular auth parameters in
`pg_hba.conf` configuration files, thanks to [Nick Janetakis](https://github.com/nickjj)
and welcome to the team!

`etc_services` role can now add custom service entries using lists in inventory
and dependency variables.

`contrib/bootstrap-ginas.py` script has been added which can help you install
ginas on your Debian/Ubuntu host and even generate an example inventory
directory.

`contrib/bootstrap-ansible.sh` script now can correctly install new and old
Ansible versions using different .deb package creation methods. Script checks
for existence of the packages in two ways and installs the correct one.

APT package management system will now support `https://` URLs of repositories
by default (these repositories will not be cached by `apt-cacher-ng` proxy).

`reprepro` role has been fixed and now supports multiple APT repositories. By
default, two repositories are created - `wheezy` for local packages managed
manually by administrator, and `wheezy-backports` for packages built
automatically by `ginas.backporter` role.

`auth` role got a long overdue update, now it should use the correct user
account by default and not create messy "$ENV(USER)" user accounts.

Added ducks.

***

## Changelog for June 2014

After some hiatus, time to go back to work!

### LXC

Huge Linux Containers rewrite, which brings LXC 1.0 support to Debian Wheezy.

Since verion 1.0 will probably not land in Wheezy itself, 'lxc' role will
automatically build and install LXC 1.0 Debian packages on Debian Wheezy (this
will not happen on other distributions or suites). Additionally, 'lxc' .deb
packages will be made available to the ginas cluster via "reprepro" repository
(built packages will be copied to special directory on Ansible Controller where
'reprepro' role expects .deb packages which then will be automatically
downloaded to local apt repository on next Ansible run). This way, you can
build LXC 1.0 packages on one spare host, and then have them available all the
time for all other hosts without any -dev packages required.

Because proper LXC support requires newer Linux kernel than the one available
in Debian Wheezy by default, 'lxc' role will install current Linux kernel from
`wheezy-backports` repository and will send an e-mail to administrator about
required server reboot. 'lxc' role will not configure and manage containers
without that reboot (idempotence is still maintained within the role).

Default container generation has been changed from `multistrap` to
`debootstrap`, which is used by modified `lxc-debian` script called `lxc-ginas`
- script will automatically install packages required by Ansible and configure
default administrator account with SSH key from Ansible Controller and
`sudo` access.

You can now manage Linux containers using a simple YAML list, with options to
start, stop or destroy containers, select different container templates, etc.
See `playbooks/roles/ginas.lxc/defaults/main.yml` file for more information.

### Postfix and Mailman

Mailman support in 'postfix' role has been removed. Instead, 'postfix' role
gained a set of new `postfix_dependent_*` variables which can be used to
configure parts of Postfix configuration (`/etc/postfix/main.cf` and
`/etc/postfix/master.cf` files) from other roles using dependency variables.
Those changes are idempotent and are saved in Ansible facts by 'postfix' role.

Examples of new functionality can be found in
`playbooks/roles/ginas.postfix/defaults/main.yml` file. Mailman role also is
now configured to use these variables, you can check new configuration in
`playbooks/roles/ginas.mailman/meta/main.yml` to see the details.

### Other news

`contrib/bootstrap-ansible.sh` script has been updated to work with new `make
deb` output. Ansible now requires `build-essential` and `devscripts` packages
to create .deb packages correctly.

After some changes to variables in 'apt' role, APT configuration was not able
to use `apt-cacher-ng` automatically. Now cache will be used correctly.

***

## Changelog for May 2014

A definition of "public API" has been added in CONTRIBUTING.md. Following that,
ginas will start using git tags for stable releases. This changelog will change
format from monthly to version-based on release of v0.0.0.

All ginas roles have been renamed from "rolename" to "ginas.rolename", with
updated dependencies, to make them similar to roles downloaded from Ansible
Galaxy. This should help you use ginas roles in your own environment and
playbooks, using `roles_path` variable in Ansible.

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

### GitLab

`gitlab` role has been updated with support for GitLab CE 6.9. This update is
very light, without additional set of config files, because changes made in
'6-9-stable' branch added only commented out code which means that older config
files should work fine.

`gitlab-shell` will no longer use a separate nginx server instance to
communicate with GitLab, instead it will talk to unicorn server directly.
Unicorn gained a port variable and is now registered as a separate service in
`/etc/services`.

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

***

## Changelog for April 2014

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

