DebOps playbooks Changelog
==========================


This is a Changelog related to DebOps_ playbooks and roles. You can also read
`DebOps Changelog`_ to see changes to the DebOps project itself.

.. _DebOps Changelog: https://github.com/debops/debops/blob/master/CHANGELOG.md


v0.1.0 (release pending)
------------------------

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

