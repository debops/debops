DebOps playbooks Changelog
==========================


This is a Changelog related to DebOps_ playbooks and roles. You can also read
`DebOps Changelog`_ to see changes to the DebOps project itself.

.. _DebOps Changelog: https://github.com/debops/debops/blob/master/CHANGELOG.md


v0.1.0 (release pending)
------------------------

2015-01-28
^^^^^^^^^^

Role updates
************

`debops.reprepro`_ role is no longer a dependency of `debops.apt`_. Instead
it's configured like any other service, by adding a host to
``[debops_reprepro]`` host group. This allows you to create separate hosts with
different repositories if needed.

Default configuration of `debops.reprepro`_ role has 3 repositories:

- a backport repository configured for your installed release (for example on
  Debian Wheezy it will manage packages for ``wheezy-backports``). You can
  upload to this repository directly;

- a "staging" repository for your organization, ``<release>-<domain>-staging``.
  You can upload to this repository directly;

- a "production" repository for your organization, ``<release>-<domain>-prod``,
  this repository is currently managed manually from the ``reprepro`` user
  account. You can promote packages to it from ``-staging`` repository using
  ``reprepro pull`` command;

You can also enable mirrors of selected distributions as needed, which allows
you to use local APT mirror as a buffer between official repositories and your
servers, if you need it. To upload packages to repositories you can use
``dput`` command to upload ``*.changes`` files over HTTPS.

`debops.reprepro`_ role automatically manages its GnuPG repository keys and
makes snapshots of current keyring state which are then uploaded to Ansible
Controller's ``secret/`` directory. In case of a reinstall, role will reuse
already existing GnuPG keys if they are found on Ansible Controller.

There are many more configuration options prepared in `debops.reprepro`_,
I suggest that you read its ``defaults/main.yml`` file to see what's available.

Because of above changes, you need to separately add your local repositories in
`debops.apt`_ configuration variables. To make it easier, there is now
a separate list variable for APT key definitions (``apt_keys``, as well as
a way to add APT keys and repositories in a "delayed" way - instead of
configuring your own repository immediately on first install, which could
result in an error if repository is not yet set up, you can add configuration
in separate set of ``apt_{keys,sources}_delayed`` variables which will be used
only after `debops.apt`_ role had configured a host once.

Another small change in `debops.apt`_ is modification of conditional package
installations - instead of separate ``apt`` module calls, packages are enabled
dynamically during Ansible run using ``set_fact`` module. `debops.apt`_ will
now also correctly distinguish Debian and Ubuntu firmware packages which are
named differently between those two distributions.

.. _debops.reprepro: https://github.com/debops/ansible-reprepro/
.. _debops.apt: https://github.com/debops/ansible-apt/


2015-01-21
^^^^^^^^^^

Role updates
************

Webserver status page has been enabled by default in `debops.nginx`_, it's
accessible on ``/nginx_status`` location, initially only from localhost
addresses (from the webserver itself). You can add additional IP addresses or
CIDR ranges using separate list, ``nginx_status``.

Fix for `CVE-2013-4547`_ has been removed from the server template, since the
issue has already been mitigated in Debian.

.. _debops.nginx: https://github.com/debops/ansible-nginx/
.. _CVE-2013-4547: https://security-tracker.debian.org/tracker/CVE-2013-4547


2015-01-20
^^^^^^^^^^

Role updates
************

`debops.gitlab_ci`_ role has been updated to support `GitLab CI`_ 5.4, with
GitLab 7.7 providing authorization based on OAuth. Due to the changes in GitLab
CI itself, some configuration variables have been changed - check the role
defaults for new ones (mainly, you can define only 1 GitLab instance to connect
to).

`debops.users`_ role has been slightly clenaed up and ``root``-proofed - it
shouldn't make an error if you are connecting to your hosts directly as
``root`` account anymore. Role uses ``default(omit)`` filter in its tasks,
which means that DebOps now requires Ansible >= 1.8 for correct operation.

.. _debops.gitlab_ci: https://github.com/debops/ansible-gitlab_ci/
.. _GitLab CI: https://about.gitlab.com/gitlab-ci/
.. _debops.users: https://github.com/debops/ansible-users/

New playbook plugins
********************

`Hartmut Goebel`_ created a small lookup plugin, ``with_lists``, which alows
you to use lists of items as "items" themselves, see an example in the
`with_lists plugin`_. Thanks!

.. _Hartmut Goebel: https://github.com/htgoebel
.. _with_lists plugin: https://github.com/debops/debops-playbooks/blob/master/playbooks/lookup_plugins/lists.py


2015-01-18
^^^^^^^^^^

Role updates
************

`debops.gitlab`_ role has been finally rewritten. Lots of important changes:

- support for `GitLab`_ 7.7 out of the box, even before official release ;)

- new home directory, ``/var/local/git/``, you might want to reinstall your
  GitLab instance from scratch or take care with moving your old instance files
  to new location;

- role does not depend on configuration file hashes anymore, updates should be
  much easier to perform and support for new versions should be included in
  a more timely manner;

- ``debops.gitlab`` will configure a daily backup of the application data to
  ``/var/backups/gitlab/``, backup files older than a week should be
  automatically cleaned up;

- new GitLab install uses a random password stored in the DebOps ``secret/``
  directory instead of the official password. Default admin account will have
  an email address in your domain instead of ``admin@example.com``, so random
  bounced mails shouldn't be a problem anymore;

.. _debops.gitlab: https://github.com/debops/ansible-gitlab/
.. _GitLab: https://about.gitlab.com/

Playbook updates
****************

``bootstrap.yml`` playbook gained new tasks which can be used to set hostname
and domain on a given host. You can define ``bootstrap_hostname`` or
``bootstrap_domain`` variables in inventory and Ansible will try to enforce
these settings on a given host as well as in ``/etc/hosts``. This functionality
makes the ``tools/fqdn.yml`` playbook redundant, so it's removed.

2015-01-13
^^^^^^^^^^

Happy New Year 2015!

PKI rewrite
***********

I've worked on `debops.pki`_ role since December, holiday season delayed it
slightly, but finally it is here. :-)

New PKI infrastructure in DebOps is designed around creating and managing
Certificate Authorities on the Ansible Controller, inside ``secret/`` directory
managed by `debops.secret`_, signing Certificate Requests generated by remote
hosts and sending back certificates. There's 1 Root CA certificate you need to
import into your browser or host certificate store and after that, all other
servers should show up in your browser as accepted automatically.

You can also very easily copy your own certificates signed by an external CA,
with private keys if needed, to your servers using a set of directories in the
``secret/`` directory.

Several roles which depended on the old `debops.pki`_ role have been now
updated as well and take advantage of functionality present in the new PKI
infrastructure. These roles are:

- `debops.nginx`_
- `debops.postfix`_
- `debops.postgresql`_
- `debops.boxbackup`_

If you use any of these roles in your infrastructure, take care to make sure
that your certificates are moved into new directory structure and configuration
is updated as needed.

If there are any questions regarding new PKI and how to use it, feel free to
ask them on the IRC channel or on the mailing list.

.. _debops.pki: https://github.com/debops/ansible-pki/
.. _debops.secret: https://github.com/debops/ansible-secret/
.. _debops.nginx: https://github.com/debops/ansible-nginx/
.. _debops.postfix: https://github.com/debops/ansible-postfix/
.. _debops.postgresql: https://github.com/debops/ansible-postgresql/
.. _debops.boxbackup: https://github.com/debops/ansible-boxbackup/


2014-12-23
^^^^^^^^^^

Role updates
************

`debops.users`_ role can now set or update user passwords (by default no
passwords are set).

`debops.ntp`_ role has gained support for ``ntpd`` daemon, thanks to
`RedRampage`_. Because of the issues with role dependency variables and Jinja,
access to NTP service through firewall is now controlled by a separate
variable, ``ntp_firewall_access``. By default, remote access is disabled.

.. _debops.users: https://github.com/debops/ansible-users/
.. _debops.ntp: https://github.com/debops/ansible-ntp/
.. _RedRampage: https://github.com/redrampage/


2014-12-05
^^^^^^^^^^

New roles
*********

- `debops.salt`_ role allows you to install and configure `Salt`_ Master
  service. You can use this to create Salt control host to which other hosts
  (Salt Minions) can connect to. At the moment configuration is very basic,
  Salt master will automatically listen to IPv6 connections and firewall will
  be configured to accept connections on default ports.

.. _debops.salt: https://github.com/debops/ansible-salt/
.. _Salt: http://saltstack.com/

Role updates
************

Salt Minion preseeding has been added in `debops.apt`_ (current Debian Preseed
configuration is there, will be moved in the future to separate role),
`debops.lxc`_ and `debops.openvz`_ roles. Automatic minion installation is
disabled by default and can be enabled separately for each "mode" - Debian
Preseed postinst script in case of physical hosts or KVM virtual machines, LXC
template script for LXC containers, OpenVZ bootstrap script for OpenVZ
containers. After installation, ``salt-minion`` will try to connect to ``salt``
host, so make sure that it's present in your DNS configuration for best
results.

.. _debops.apt: https://github.com/debops/ansible-apt/
.. _debops.lxc: https://github.com/debops/ansible-lxc/
.. _debops.openvz: https://github.com/debops/ansible-openvz/

2014-12-03
^^^^^^^^^^

Role updates
************

Continuing the `GitLab`_ revamp, `debops.gitlab_ci_runner`_ role has also been
refactored and is unfortunately not compatible with the previous version,
reinstall of the nost is recommended.

Runner home directory has been moved to ``/var/local/`` directory, most of role
dependencies have been dropped and role now needs less upkeep than before. You
can read about changes in `latest commit`_.

.. _GitLab: https://about.gitlab.com/
.. _debops.gitlab_ci_runner: https://github.com/debops/ansible-gitlab_ci_runner/
.. _latest commit: https://github.com/debops/ansible-gitlab_ci_runner/commit/b46089356e48b4f6719fd9eb64a5684ed0d55ae3

2014-12-02
^^^^^^^^^^

`DebOps mailing list`_ has been moved to `groups.io`_.

.. _DebOps mailing list: https://groups.io/org/groupsio/debops
.. _groups.io: https://groups.io/

Role updates
************

`debops.gitlab_ci`_ role has been significantly refactored. Due to bug in
GitLab CI 5.0 at the moment this version cannot be installed, so I decided to
use this opportunity to make some deep changes in the role. GitLab CI home has
been moved to ``/var/local/gitlab-ci/`` directory, and various tasks related to
updating the application have been streamlined. You can read more information
about various changes in the `commit message`_.

.. _debops.gitlab_ci: https://github.com/debops/ansible-gitlab_ci/
.. _commit message: https://github.com/debops/ansible-gitlab_ci/commit/64eb393569267f4eebd9264580d9c1fa22dc32e0

2014-12-01
^^^^^^^^^^

`Hartmut Goebel`_ has joined DebOps team and wrote an excellent guide for using
DebOps scripts and playbooks with Vagrant on single and multiple hosts. It's
available in `debops/examples`_ repository.

.. _Hartmut Goebel: https://github.com/htgoebel
.. _debops/examples: https://github.com/debops/examples/

Role updates
************

All DebOps roles again use Ansible `devel` branch on Travis CI for tests.

`debops.debops`_ role has been rewritten and updated to support current project
installation method. By default only DebOps scripts will be installed system
wide, but you can also install playbooks and roles to `/usr/local` by setting
a variable. Dependency on `debops.ansible`_ role has been dropped and that role
will be removed in the future. You can install Ansible from a Debian repository
or by providing your own ``.deb`` package.

`RedRampage`_ has provided a failover code for `debops.dhcpd`_ role which
should help set up failover DHCP servers. Thanks!

Several DebOps roles had a small fixes related to ``ansible-playbook --check``
command, which can now be used to check for possible changes before applying
them on the remote hosts. Due to bugs in older Ansible versions this
functionality works correctly on Ansible 1.8+ or current ``devel`` branch.

.. _debops.debops: https://github.com/debops/ansible-debops/
.. _debops.ansible: https://github.com/debops/ansible-role-ansible/
.. _RedRampage: https://github.com/redrampage
.. _debops.dhcpd: https://github.com/debops/ansible-dhcpd/

2014-11-27
^^^^^^^^^^

Role updates
************

Support for management of SSH host fingerprints in ``/etc/ssh/ssh_known_hosts``
(via `debops.sshd`_ role) and ``/root/.ssh/known_hosts`` on OpenVZ hosts (via
`debops.openvz`_ role) has been redesigned and no longer uses ``assemble``
Ansible module. Instead, Ansible checks already present fingerprints and adds
new ones if they are not present in the files. This helps better obfuscate
scanned hosts, which previously could be inferred from filenames of parts
assembled earlier.

Instances of ``with_items`` using multiple lists in a few roles have been
replaced with ``with_flattened`` which works better in new release of Ansible,
1.8+.

`debops.openvz`_ role has been slightly updated and redundant configuration of
``ferm`` and ``sysctl``, already configured by `debops.ferm`_ role, has been
dropped to prevent duplication.

.. _debops.sshd: https://github.com/debops/ansible-sshd/
.. _debops.openvz: https://github.com/debops/ansible-openvz/
.. _debops.ferm: https://githubc.om/debops/ansible-ferm/

2014-11-26
^^^^^^^^^^

Role updates
************

`debops.nginx`_ role will now preserve the status for ``default_server`` of
a particular configuration file in case that another instance of the role is
added in the Ansible run. Saved local fact about which server is the default
one will take precedence over automatically calculated setting.

If ``nginx`` role notices that Ansible local facts are missing, it will remove
all files and symlinks from ``/etc/nginx/sites-enabled/`` directory. This
should happen in two instances - either ``nginx`` is configured for the first
time, or ``/etc/ansible/facts.d/nginx.fact`` file has been removed. In that
case all active config symlinks will be removed to prevent accidental errors
from some old, not regenerated configuration files.

2014-11-25
^^^^^^^^^^

New roles
*********

- `debops.hwraid`_ is a role that configures access to `HWRaid`_ package
  repository and installs packages for recognized RAID storage arrays connected
  to your hosts. It can be used to quickly and easily setup basic monitoring
  for your storage - many packages contain automated scripts which send mail to
  ``root`` account in case of issues with RAID.

.. _debops.hwraid: https://github.com/debops/ansible-hwraid/
.. _HWRaid: http://hwraid.le-vert.net/

Role updates
************

`debops.auth`_ role will now manage ``/etc/ldap/ldap.conf`` configuration file.
By default, LDAP server on local domain is set up (currently without any
encryption, so treat this as experimental feature and don't use it in
production) with local domain specified as BaseDN. you can change this in role
default variables.

DebOps will automatically configure ``hidepid=2`` option in ``/proc``
filesystem on selected hosts (hardware servers and fully virtualized VMs),
using `debops.console`_ role. This functionality hides other users' process
information for unprivileged accounts. A separate system group, ``procadmins``
has been reserved for monitoring services and users that need full access to
the ``/proc`` filesystem.

.. _debops.auth: https://github.com/debops/ansible-auth/
.. _debops.console: https://github.com/debops/ansible-console/

2014-11-24
^^^^^^^^^^

New roles
*********

- `debops.slapd`_ role manages OpenLDAP server, ``slapd``. At the moment role
  is in beta stage - currently there is no SSL encryption available, no
  backup/restore scripts and no replication. But role installs a few useful
  scripts and ``slapd`` management is done using custom Ansible modules.
  Deeper integration between OpenLDAP and other DebOps services will be created
  in the future.

.. _debops.slapd: https://github.com/debops/ansible-slapd/

Role updates
************

Because of recent changes in `debops.tcpwrappers`_ role I decided to make the
ferm rules concenring SSH access more strict. From now on, ``iptables`` will
check new SSH connections over period of 1 hour, if more than 3 new connections
from 1 IP address are attempted during that time, and address is not in the
whitelist, it will be blocked for 2 hours, with each new connection attempt
resetting the timer. All this is now configurable in `debops.sshd`_  and
`debops.ferm`_ roles.

.. _debops.tcpwrappers: https://github.com/debops/ansible-tcpwrappers/
.. _debops.sshd: https://github.com/debops/ansible-sshd/
.. _debops.ferm: https://github.com/debops/ansible-ferm/

Thanks to `htgoebel's suggestion`_ I was able to refactor Postfix hash tables
management. They are now generated from all ``*.in`` files in current
directory, which means that other Ansible roles or even other scripts can put
their own files in ``/etc/postfix/hash_*/`` directories and if they are named
with ``*.in`` extension, their corresponding ``*.db`` files will be created
automatically. Thanks to that, `debops.postfix`_ role now generates tables from
templates using ``with_fileglob`` instead of static lists of templates, which
makes the process of adding new tables if necessary much easier.

.. _htgoebel's suggestion: https://github.com/debops/ansible-postfix/issues/11#issuecomment-64113942
.. _debops.postfix: https://github.com/debops/ansible-postfix/

2014-11-22
^^^^^^^^^^

Role updates
************

You can now specify default value for entries in `debops.tcpwrappers`_ role,
using ``item.default`` key. If this key is specified, and ``item.clients`` is
not present or is empty, default value will be used instead. Specify ``'ALL'``
to allow connections from any host.

Consequently, `debops.sshd`_ role now will allow connections from any host by
default in ``/etc/hosts.allow``. If you previously used a list of hosts using
``sshd_*_allow``, your configuration shouldn't be affected.

.. _debops.tcpwrappers: https://github.com/debops/ansible-tcpwrappers/
.. _debops.sshd: https://github.com/debops/ansible-sshd/

2014-11-20
^^^^^^^^^^

Role updates
************

`debops.ifupdown`_ will now check if previous network configuration in
``/etc/network/interfaces`` was using static IP addresses, which indicates that
DHCP is not available on the network. In that case, a basic static IPv4
interface configuration will be used with information gathered by Ansible to
setup a default network interface. This should prevent sudden loss of
communication in cases where hosts are configured statically.

.. _debops.ifupdown: https://github.com/debops/ansible-ifupdown/

Playbook updates
****************

``tools/hostname.yml`` playbook has been renamed to ``tools/fqdn.yml`` and can
get the new hostname and domain from ``fqdn`` variable defined in inventory,
which is less awkward to use than renaming the host in inventory file directly.

2014-11-19
^^^^^^^^^^

Role updates
************

Network forwarding configuration in ``iptables`` has been moved from
`debops.kvm`_, `debops.lxc`_ and `debops.subnetwork`_ roles into `debops.ferm`_
to avoid duplication. This will also result in forwarded network interfaces
being able to accept Router Advertisements and configure their IPv6 addresses
using SLAAC. In short, easier network configuration.

`Hartmut Goebel`_ has provided a set of `Raspbian`_ APT repositories for
`debops.apt`_ role, thanks! Unfortunately, at the moment Ansible does not
correctly recognize Raspian as a separate distribution which prevents automatic
source selection, but there are workarounds.

Because of the recent Debian Jessie freeze, DebOps project is starting
preparations for full Jessie support, both as a standalone install, as well as
an upgrade from Wheezy.

All `debops.ferm`_ configuration files had changed ownership from
``root:root`` to ``root:adm`` which is the default in Debian. This change
should prevent back-and-forth changes of ownership after system has been
upgraded, which forces ``ferm`` files to change ownership to ``root:adm``.

Some APT configuration files in `debops.apt`_ role have been renamed to avoid
conflicts with existing files during the upgrade, this should prevent
``debconf`` questions about replacing modified configuration files.

Both `debops.apt`_ and `debops.lxc`_ roles now support
``ansible_distribution_release`` in ``'release/sid`` format, which lets DebOps
function correctly on Jessie during the freeze. There might be other roles
which need to be updated to support this syntax, they will be fixed later.

`debops.auth`_ role now uses full templates instead of ``lineinfile`` module to
configure ``sudo`` and ``su`` admin access. This should prevent ``debconf``
asking about modifications in ``/etc/pam.d/su`` (which is now diverted), and
lets ``sudo`` have more configuration options for ``admins`` group.

.. _Hartmut Goebel: https://github.com/htgoebel
.. _Raspbian: http://raspbian.org/
.. _debops.apt: https://github.com/debops/ansible-apt/
.. _debops.kvm: https://github.com/debops/ansible-kvm/
.. _debops.lxc: https://github.com/debops/ansible-lxc/
.. _debops.ferm: https://github.com/debops/ansible-ferm/
.. _debops.subnetwork: https://github.com/debops/ansible-subnetwork/
.. _debops.auth: https://github.com/debops/ansible-auth/

Playbook updates
****************

New playbook, ``tools/hostname.yml`` can be used to change the hostname and
FQDN of a host to those defined in Ansible inventory (and yes, you can do
multiple hosts at once). It's advised to not do it after services have been
configured, since some of them may rely on the correct FQDN defined in DNS. If
you use DHCP to automatically configure DNS (for example with ``dnsmasq``,
rebooting the host after chaning the hostname should ensure that the new FQDN
is correct.

2014-11-13
^^^^^^^^^^

Role updates
************

`debops.postfix`_ role will now correctly work on hosts without FQDN
configured. On these hosts, Postfix will automatically override its configured
capabilities and enable local mail delivery, mail will be originating from the
host instead of the domain. Postfix role will also no longer modify
``/etc/hosts`` to rewrite IPv6 ``localhost`` address, it seems that the
annoying warning in the mail log about unknown connection source has been
fixed.

`debops.dnsmasq`_ role has been completely rewritten and now supports multiple
network interfaces and IPv6, among other things. It requires ``ipaddr()``
filter plugin to work, but thanks to that it can automatically configure
services based on IP addresses configured on specified interface - no more
separate IP subnet configuration is needed. Role now also creates more
fine-grained CNAME records and has more configuration options.
And it's out of beta! :-)

.. _debops.postfix: https://github.com/debops/ansible-postfix/
.. _debops.dnsmasq: https://github.com/debops/ansible-dnsmasq/

Playbook updates
****************

Old 'debops.nat' role has been obsoleted by `debops.subnetwork`_ and removed
from ``ansible-galaxy`` requirements file. It will also be removed from GitHub
and Ansible Galaxy in the future. Also, `debops.radvd`_ has been added to the
requirements.

Virtualization playbook has been modified and roles that previously
automatically configured internal network and DNS services have been removed
from KVM and LXC plays (yes, this will change instllation procedures in the
docs, which are not yet updated). New playbook, 'networking.yml' has been added
where you will find all network-related plays, like subnet creation and
management (via ``debops.subnetwork`` and DHCP/DNS management.

.. _debops.subnetwork: https://github.com/debops/ansible-subnetwork/
.. _debops.radvd: https://github.com/debops/ansible-radvd/

2014-11-07
^^^^^^^^^^

New roles
*********

`debops.subnetwork`_ is a replacement for old `debops.nat`_ role, with many
improvements. You can create a bridge interface with local network behind it
for virtual machines, or even switch to a real Ethernet interface for your
physical hosts. You can create both an IPv4 network, which will be
automatically configured behind NAT, and an IPv6 network (with multiple
prefixes). `debops.subnetwork`_ is not yet part of the main playbook, it will
replace the old NAT role when ``dnsmasq`` role is updated to support it.

.. _debops.subnetwork: https://github.com/debops/ansible-subnetwork/

Role updates
************

Because of the changes related to new networking, some code in `debops.lxc`_, `debops.kvm`_ and `debops.nat`_ had to be moved around. Specifically, parts of the firewall and sysctl settings related to the LAN interface were moved into `debops.subnetwork`_ role and parts of the forwarding configuration to external and internal networks were added respectively to LXC and KVM roles.

.. _debops.lxc: https://github.com/debops/ansible-lxc/
.. _debops.kvm: https://github.com/debops/ansible-kvm/
.. _debops.nat: https://github.com/debops/ansible-nat/
.. _debops.subnetwork: https://github.com/debops/ansible-subnetwork/

2014-11-05
^^^^^^^^^^

New playbooks
*************

New playbook has been added, ``net/ipv6/6to4.yml``. This playbook configures
`6to4 tunnel`_ interface on a host with public IPv4 address and allows you to
easily connect to IPv6 network. To do that, you need to put a host in
``[debops_6to4]`` group. Afterwards, you can run the playbook using ``debops``
script::

  debops net/ipv6/6to4 -l host

This is first step towards transition to playbooks placed in subdirectories.
These playbooks will probably work correctly only with ``debops`` script, which
automatically generates ``ansible.cfg`` with correct configuration parameters.
To use these playbooks standalone, you will need to create your own
``ansible.cfg`` and include in it paths to DebOps roles and plugins.

.. _6to4 tunnel: https://en.wikipedia.org/wiki/6to4

Role updates
************

You can now configure custom `ferm`_ rules using a ``custom`` template in
`debops.ferm`_. New ``ferm_*_rules`` variables allow you to create rules in
``/etc/ferm/ferm.d/`` directory which can configure tables and chains other
than ``INPUT``.

.. _ferm: http://ferm.foo-projects.org/
.. _debops.ferm: https://github.com/debops/ansible-ferm/

2014-11-04
^^^^^^^^^^

New roles
*********

Finally, it's time to start bringing out new toys. :-) For starters,
`debops.radvd`_ role, which installs and lets you configure ``radvd``, IPv6
Router Advertisement daemon. It will be used in future IPv6 router roles.

.. _debops.radvd: https://github.com/debops/ansible-radvd/

Playbook updates
****************

``ipaddr()`` filter has been rewritten again and it works now correctly with
lists of values. Filter was completely refactored internally and its output
should be now consistent with expectations. Hopefully for the last time.

2014-11-02
^^^^^^^^^^

Playbook updates
****************

More fixes in filters! ``split()`` filter will now handle incorrect input
values gracefully and return them in a list, since output is usually expected
to be a list. If a string cannot be split by specified separator, whole string
will be returned in a list.

``ipaddr('6to4')`` filter has been updated to not convert private IPv4
addresses, since their behaviour is unspecified, this way Ansible can easily
determine if a given IPv4 address can be used in ``6to4`` tunnel.

``6to4`` query will also now return proper ``::/48`` subnet instead of a single
IPv6 address, this way a subnet can be further manipulated to for example split
it into smaller ``::/64`` subnets.

New ``ipaddr()`` query type has been added - you can now specify positive or
negative numbers in a query, for example ``{{ '192.168.0.1/24' | ipaddr('-1') }}``
will return last IPv4 address from a specified subnet. It's an easy way to
define DHCP dynamic ranges in ``dnsmasq`` configuration.

New filter, ``ipsubnet()`` has been added. It lets you manipulate IPv4 and IPv6
subnets; given a subnet and CIDR prefix you can check the number of subnets
that it can be divided into, adding an index number to the query lets you get
a specific subnet. You can also check the biggest subnet an address can be in
by specifying the smallest prefix you're interested in.

You can now pass a list to ``ipaddr()`` filter and it will return only items
that pass specified criteria, for example returns only list of IP addresses and
subnets by default, or only IPv6 addresses and subnets, etc. It's not yet 100%
correct all the time and not all queries work (or make sense in this context).

2014-10-31
^^^^^^^^^^

Playbook updates
****************

New filter, ``split()`` has been added into filter plugins. It lets you split
strings into a list on a specified separator (by default, space). I'm amazed it
hasn't been included yet in core Ansible. :-) ``split()`` filter has been
written by Tim Raasveld and is included with his blessing, thanks!

``ipaddr()`` filter will from now on correctly handle false values like
``False`` and ``""`` by returning ``False`` when encountered. It also gained
new query type, ``'6to4'`` which lets you convert public IPv4 addresses into
`6to4`_ IPv6 addresses or check if a specified IPv6 address/network is in
``2002::/16`` address range.

.. _6to4: https://en.wikipedia.org/wiki/6to4

2014-10-28
^^^^^^^^^^

Role updates
************

APT repository management in `debops.apt`_ role has been rewritten. Now role
supports multiple APT mirrors, as well as custom lists of repositories
dependent on the current distribution (repository lists for Debian and Ubuntu
are included). Configuration of default APT repositories has been moved from
a separate config file in ``/etc/apt/sources.list.d/`` directly to
``/etc/apt/sources.list``, original configuration file is preserved using
``dpkg-divert``. Additionally, if `debops.apt`_ cannot recognize current
distribution, it won't modify the default ``sources.list`` file, this can also
be enforced manually if needed.

.. _debops.apt: https://github.com/debops/ansible-apt/

2014-10-17
^^^^^^^^^^

Role updates
************

Many more roles have now partial or full tests on `Travis-CI`_, more to come.

Default version of `Etherpad`_ installed by `debops.etherpad`_ role has been
changed from ``1.4.0`` to ``develop``, because current stable release does not
recognize new ``npm`` installed in Debian. It will be switched to the next
stable release when it's available.

Because of the recent IPv6 changes in `debops.nginx`_, management of ``nginx``
configuration and daemon had to be changed slightly. Role will try to
automatically pick a sane server as the "default server", if none are marked as
one, due to ``ipv6only=off`` parameter tied to ``default_server`` parameter.
Another added functionality is full nginx server restart when configuration
symlinks in ``/etc/nginx/sites-enabled/`` directory are added or removed - this
should help with requirement to restart the service on interface changes.

Default admin username and SSH keys are now exposed as ``defaults/`` variables
in `debops.openvz`_ role; SSH keys are also sourced from ``ssh-agent`` instead
of directly from the ``~/.ssh/id_rsa.pub`` file.

.. _Travis-CI: https://travis-ci.org/
.. _Etherpad: http://etherpad.org/
.. _debops.etherpad: https://github.com/debops/ansible-etherpad/
.. _debops.nginx: http://nginx.org/
.. _debops.openvz: https://github.com/debops/ansible-openvz/

2014-10-10
^^^^^^^^^^

Playbook updates
****************

`Maciej Delmanowski`_ wrote a set of custom filter plugins for Ansible which
let you manipulate IPv4 and IPv6 addresses. You can test if a string is a valid
IP address or convert them between various formats.

.. _Maciej Delmanowski: https://github.com/drybjed/

2014-10-09
^^^^^^^^^^

Role updates
************

IPv6 firewall has been enabled by default in `debops.ferm`_ after all roles
that configure ``ferm`` directly had their configuration files fixed to support
both ``iptables`` and ``ip6tables`` commands.

`debops.boxbackup`_ has been finally converted from a "common" role (run from
``common.yml`` playbook) to a group-based role. First host in
``debops_boxbackup`` will be configured as the BoxBackup server and the rest
will be set up as its clients.

.. _debops.ferm: https://github.com/debops/ansible-ferm/
.. _debops.boxbackup: https://github.com/debops/ansible-boxbackup/

2014-10-07
^^^^^^^^^^

Role updates
************

`debops.ferm`_ role is now IPv6-aware and can generate rules for ``iptables``
and ``ip6tables`` at the same time. The way you use the role as a dependency
hasn't changed at all, so if you use dependent variables in your roles, you
should be fine. However, because some roles are managing their firewall rules
by themselves, IPv6 support is disabled by default - this will change when all
roles are updated to be IPv6-aware.

`debops.nginx`_ also gained support for IPv6 and will now listen for
connections on both types of networks by default. If you have an already
running nginx server, it will require manual restart for the new configuration
to take effect.

.. _debops.ferm: https://github.com/debops/ansible-ferm/
.. _debops.nginx: https://github.com/debops/ansible-nginx/

2014-10-05
^^^^^^^^^^

All role README files have been converted to reStructuredText format.
Unfortunately, `Ansible Galaxy`_ does not support ``README.rst`` files at this
time, so role information cannot be udpated there.

.. _Ansible Galaxy: http://galaxy.ansible.com/

2014-10-02
^^^^^^^^^^

Role updates
************

`debops.nginx`_ role has been updated. Most changes are either cleanup (change
names of some internal role files, remove unused redundant variables, etc.).

``/etc/nginx/http-default.d/`` directory has been renamed to
``/etc/nginx/site-default.d/`` which hopefully better shows the purpose of this
directory in relation to nginx server configuration. Old directories haven't
been removed; if you use it, you will need to move the configuration files
manually.

Support for ``map { }`` configuration sections has been added. It works
similarly to upstreams and servers, that means you can define your maps in
hashes and enable them using ``nginx_maps`` list. More information about
`nginx map module`_ can be found at the nginx website.

You can now remove configuration of servers, upstreams and maps from hosts by
adding ``delete: True`` to the configuration hashes.

Old remnants of the ``fastcgi_params`` configuration files are now
automatically removed by the nginx role. This is the second step of the switch
from custom to stock configuration file. Task which removes these old files
will be removed in the future.

.. _debops.nginx: https://github.com/debops/ansible-nginx/
.. _nginx map module: http://nginx.org/en/docs/http/ngx_http_map_module.html

2014-09-29
^^^^^^^^^^

Playbook updates
****************

"{{ lookup('file','~/.ssh/id_rsa.pub) }}" considered harmful
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The lookup above is common thruought Ansible playbooks and examples, and it is
used as a prime method of accessing SSH public keys of current account on
Ansible Controller host to, for example, install them on remote hosts using
``authorized_key`` Ansible module.

However, this is by no means a portable solution. Users can have public SSH key
files with completely different names, or don't even have them at all and
instead use other means of SSH authentication, like GPG keys or smartcards.

Because of that, I'm changing the way that SSH public keys will be accessed by
default in DebOps. For now, only ``playbooks/bootstrap.yml`` playbook will be
updated (this playbook is used to bootstrap new hosts and get them ready for
Ansible management), changes in other roles will come later. I hope that
authors of other roles will follow suit.

New way of accessing SSH keys will use SSH agent (or its alternatives): instead
of accessing the keys directly, Ansible will request a list of currently
enabled public keys from the SSH agent using ``"{{ lookup('pipe','ssh-add -L') }}"``
lookup. Because that lookup can return an empty value which will not create an
error, you want to safeguard against that in a key configuration task using
``failed_when:`` condition. Look in ``playbooks/bootstrap.yml`` to see how it's
used with ``authorized_key`` task.

2014-09-22
^^^^^^^^^^

inventory.secret is renamed to secret
*************************************

If you use DebOps, or at least some roles from it, you probably are familiar
with `debops.secret`_ role, which makes handling sensitive and confidental
data easier within Ansible playbooks and roles. I'm mentioning this because
``secret`` variable is used thruought the DebOps project and this change will
be significant - that's why I want to do it right away instead of changing the
role suddenly some time down the line.

Previously `debops.secret`_ role created directory for secrets adjacent to the
Ansible inventory directory. Because it was assumed that inventories are kept
in the same directory, `debops.secret`_ automatically took the name of the
inventory directory and appended ``.secret`` suffix to it, making the resulting
directory ``inventory.secret/``.

Now, because each DebOps project lives in its own directory, this feature is no
longer needed. Additionally in the current state secret directory is kind of
a show stopper, interfering for example with ``<Tab>``-completion. Because of
that, I'm changing the "formula" to instead just use the ``secret/`` directory
by default. It will be still created beside the ``inventory/`` directory.

All DebOps scripts will be updated at the same time, and should work with new
directory name. However, existing directories will need to be renamed manually,
otherwise DebOps might create new certificates, passwords, etc.

``inventory.secret`` directory becomes ``secret``.

If you use ``debops-padlock`` script, then ``.encfs.inventory.secret``
directory becomes ``.encfs.secret``.

.. _debops.secret: https://github.com/debops/ansible-secret/

2014-09-21
^^^^^^^^^^

Role updates
************

* `debops.postfix`_ has been cleaned up, all Ansible tasks have been rewritten
  from "inline" syntax to YAML syntax. Task conditions have been rearranged,
  now almost all of them can be found in ``tasks/main.yml`` file instead of in
  the file that are included.

* The way that `Postfix`_ configuration files (``main.cf`` and ``master.cf``)
  are created by Ansible has been changed - instead of templating individual
  pieces on the remote servers and assembling them to finished files,
  configuration file templates are generated on Ansible Controller from parts
  included by Jinja and then templated on the servers as a whole. This makes
  the process much faster and easier to manage.

* Postfix role has gained a new capability, ``archive``. If it's enabled, each
  mail that passes through the SMTP server is blind carbon-copied to a separate
  archive mail account on local or remote SMTP server. This function is
  configured automatically by the role, but can be modified using inventory
  variables. Archive account and/or archive server need to be configured
  separately by the system administrator.

.. _debops.postfix: https://github.com/debops/ansible-postfix/
.. _Postfix: http://www.postfix.org/

2014-09-19
^^^^^^^^^^

Role updates
************

* `debops.postfix`_ role has gained support for `SMTP client SASL authentication`_,
  in other words the ability to send mail through remote relay MX hosts with
  client authentication, like public or commercial SMTP servers. You can either
  configure one username/password pair for a specified relayhost, or enable
  sender dependent authentication and specify relayhost, user and password for
  each sender mail address separately. Passwords are never stored in the
  inventory; instead Postfix role uses `debops.secret`_ role to store user
  passwords securely.

.. _debops.postfix: https://github.com/debops/ansible-postfix/
.. _SMTP client SASL authentication: http://www.postfix.org/SASL_README.html#client_sasl
.. _debops.secret: https://github.com/debops/ansible-secret/

2014-09-18
^^^^^^^^^^

Role updates
************

* `debops.kvm`_ role has been cleaned up from old and unused code, tasks were
  put in order and list of administrator accounts that should have access to
  ``libvirt`` group changed name from ``auth_admin_accounts`` to ``kvm_admins``
  (Ansible account is enabled automatically).

* `debops.lxc`_ role has been updated with changes to the LXC 1.0.5 package
  from Debian Jessie (some package dependencies and build requirements were
  changed). You can read more in the `lxc package changelog`_.

.. _debops.kvm: https://github.com/debops/ansible-kvm/
.. _debops.lxc: https://github.com/debops/ansible-lxc/
.. _lxc package changelog: http://metadata.ftp-master.debian.org/changelogs/main/l/lxc/testing_changelog

2014-09-17
^^^^^^^^^^

Playbook updates
****************

* You can now disable early APT cache update using ``apt_update_cache_early``
  variable from `debops.apt`_ role. This is useful in rare case when your APT
  mirror suddenly catches fire, and you need to switch to a different one using
  Ansible.

.. _debops.apt: https://github.com/debops/ansible-apt/

Role updates
************

* `debops.ferm`_ role has gained new list variable,
  ``ferm_ansible_controllers``, which can be used to configure CIDR hostnames
  or networks that shouldn't be blocked by ssh recent filter in the firewall. This
  is useful in case you don't use DebOps playbook itself, which does that
  automatically. In addition, `debops.ferm`_ saves list of known Ansible
  Controllers using local Ansible facts, and uses it to enforce current
  configuration.

* similar changes as above are now included in `debops.tcpwrappers`_ role, you
  can specify a list of Ansible Controllers in
  ``tcpwrappers_ansible_controllers`` list variable.

* `Debian bug #718639`_ has been fixed which results in changes to serveral
  configuration files, including ``/etc/nginx/fastcgi_params`` and inclusion of
  a new configuration file ``/etc/nginx/fastcgi.conf``. `debops.nginx`_ role
  will now check the version of installed ``nginx`` server and select correct
  file to include in PHP5-based server configuration.

.. _debops.ferm: https://github.com/debops/ansible-ferm/
.. _debops.tcpwrappers: https://github.com/debops/ansible-tcpwrappers/
.. _Debian bug #718639: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=718639
.. _debops.nginx: https://github.com/debops/ansible-nginx/

2014-09-14
^^^^^^^^^^

* Start of a new, separate changelog for DebOps_ playbooks and roles. This is
  a continuation of `previous Changelog`_ from `ginas`_ project.

* all DebOps roles have been moved to `Ansible Galaxy`_ and are now available
  via ``ansible-galaxy`` utility directly. You can also browse them on the
  `DebOps Galaxy page`_

.. _previous Changelog: https://github.com/ginas/ginas/blob/master/CHANGELOG.md
.. _ginas: https://github.com/ginas/ginas/
.. _Ansible Galaxy: https://galaxy.ansible.com/
.. _DebOps Galaxy page: https://galaxy.ansible.com/list#/users/6081

New roles
*********

* `debops.elasticsearch`_ is a role written to manage `Elasticsearch`_
  clusters, either standalone or on multiple hosts separated and configured
  using Ansible groups. Author: `Nick Janetakis`_.

* `debops.golang`_ role can be used to install and manage `Go language`_
  environment. By default it will install packages present in the distribution,
  but on Debian Wheezy a backport of ``golang`` package from Debian Jessie can
  be automatically created and installed.

.. _Nick Janetakis: https://github.com/nickjj
.. _debops.elasticsearch: https://github.com/debops/ansible-elasticsearch
.. _Elasticsearch: http://elasticsearch.org/
.. _debops.golang: https://github.com/debops/ansible-golang
.. _Go language: http://golang.org/

Role updates
************

* `debops.ruby`_ role has changed the way how different Ruby versions can be
  selected for installation. By default, ``ruby_version: 'apt'`` variable tells
  the role to install any Ruby packages available via APT (by default 1.9.3
  version will be installed on most distributions). If you change the value of
  ``ruby_version`` to ``'backport'``, a backported Ruby 2.1 packages will be
  created if not yet available, and installed.

* Also in `debops.ruby`_, ``rubygems-integration`` package is installed
  separately from other packages and can be disabled using
  ``ruby_gems_integration: False`` variable (this option was required for
  backwards compatibility with `Ubuntu 12.04 LTS (Precise Pangolin)`_
  distribution).

.. _debops.ruby: https://github.com/debops/ansible-ruby
.. _Ubuntu 12.04 LTS (Precise Pangolin): http://releases.ubuntu.com/12.04/

.. _DebOps: http://debops.org/

