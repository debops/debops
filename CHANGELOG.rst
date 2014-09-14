DebOps playbooks Changelog
==========================


This is a Changelog related to DebOps_ playbooks and roles. You can also read
`DebOps Changelog`_ to see changes to the DebOps project itself.

.. _DebOps Changelog: https://github.com/debops/debops/blob/master/CHANGELOG.md


v0.1.0 (release pending)
------------------------

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

