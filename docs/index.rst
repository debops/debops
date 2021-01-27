.. Copyright (C) 2017-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Nicolas Quiniou-Briand <nqb@inverse.ca>
.. Copyright (C) 2019      Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2017-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. image:: ../lib/images/debops.png
   :align: right
   :width: 10em
   :target: https://github.com/debops/debops

DebOps
======

*Your Debian-based data center in a box*

|GitHub CI| |GitLab CI| |CII Best Practices| |REUSE Status|

.. |GitHub CI| image:: https://github.com/debops/debops/workflows/Continuous%20Integration/badge.svg
   :target: https://github.com/debops/debops/actions?query=workflow%3A%22Continuous+Integration%22

.. |GitLab CI| image:: https://gitlab.com/debops/debops/badges/master/pipeline.svg
   :target: https://gitlab.com/debops/debops/pipelines

.. |CII Best Practices| image:: https://bestpractices.coreinfrastructure.org/projects/237/badge
   :target: https://bestpractices.coreinfrastructure.org/en/projects/237

.. |REUSE Status| image:: https://api.reuse.software/badge/github.com/debops/debops
   :target: https://api.reuse.software/info/github.com/debops/debops

.. include:: includes/global.rst

The DebOps project is `a set of Free and Open Source tools`__ that let users
bootstrap and manage an IT infrastructure based on Debian_ or Ubuntu_ operating
systems. Ansible_ is used as the main configuration management platform.
DebOps provides a :ref:`collection of Ansible roles <role_index>` that manage
various services, as well as a `set of Ansible playbooks`__ that tie them
together in a highly integrated environment.

.. __: https://github.com/debops/debops
.. __: https://github.com/debops/debops/tree/master/ansible/playbooks

Ansible roles and playbooks provided by DebOps can be used to manage a single
host, a set of Debian or Ubuntu hosts, or an entire data center. The hosts in
question can be physical or virtual machines, or even LXC/Docker containers.

Some of the applications and services supported in DebOps are:

- :ref:`X.509 certificate management <debops.pki>` with support for `Let's Encrypt`__
  certificates

- a :ref:`git hosting platform <debops.gitlab>` based on `GitLab`__

- :ref:`host and network monitoring <debops.librenms>` using `LibreNMS`__

- :ref:`cloud file hosting <debops.owncloud>` based on `Nextcloud`__ or
  `ownCloud`__

.. __: https://www.letsencrypt.org/
.. __: https://about.gitlab.com/
.. __: https://www.librenms.org/
.. __: https://nextcloud.com/
.. __: https://owncloud.org/

You can :ref:`try out DebOps <quick_start>` without installing it on your
computer, using Docker or Vagrant. Alternatively, a set of scripts can be
installed on your own computer, that will let you manage multiple, separate IT
infrastructure environments.

.. toctree::
   :caption: Introduction
   :maxdepth: 1
   :hidden:

   overview
   introduction/quick-start
   introduction/install
   introduction/getting-started
   introduction/configuration
   introduction/faq

.. toctree::
   :caption: User Manual
   :maxdepth: 2
   :hidden:

   user-guide/debops-for-ansible
   user-guide/project-directories
   user-guide/scripts
   user-guide/global-variables
   user-guide/custom-environment
   user-guide/playbooks
   user-guide/universal-configuration
   ansible/role-index
   ansible/roles/index

.. toctree::
   :caption: Admin Recipes
   :maxdepth: 2
   :hidden:

   admin-guide/linux-containers
   admin-guide/service-ports
   admin-guide/local-apt-repository

.. toctree::
   :caption: Developer Guide
   :maxdepth: 2
   :hidden:

   developer-guide/contributing
   developer-guide/contribution-workflow
   developer-guide/contributing-docs
   developer-guide/testing
   developer-guide/development-model
   dep/index

.. toctree::
   :caption: The DebOps Project
   :maxdepth: 2
   :hidden:

   meta/community
   meta/goals
   meta/policy
   meta/philosophy
   meta/timeline
   meta/references
   meta/logo
   meta/other-projects
   meta/debops-oid-registry
   debops-api/index

.. toctree::
   :caption: News
   :maxdepth: 1
   :hidden:

   news/releases
   news/changelog
   news/upgrades

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
