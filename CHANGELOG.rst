DebOps playbooks Changelog
==========================


This is a Changelog related to DebOps_ playbooks and roles. You can also read
`DebOps Changelog`_ to see changes to the DebOps project itself.

.. _DebOps Changelog: https://github.com/debops/debops/blob/master/CHANGELOG.md


v0.1.0 (release pending)
------------------------

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

