.. image:: ../lib/images/debops.png
   :align: right
   :width: 10em
   :target: https://github.com/debops/debops

DebOps
======

*Your Debian-based data center in a box*

|Travis CI| |GitLab CI| |CII Best Practices|

.. |Travis CI| image:: https://img.shields.io/travis/debops/debops.svg?style=flat
   :target: https://travis-ci.org/debops/debops

.. |GitLab CI| image:: https://gitlab.com/debops/debops/badges/master/pipeline.svg
   :target: https://gitlab.com/debops/debops/pipelines

.. |CII Best Practices| image:: https://bestpractices.coreinfrastructure.org/projects/237/badge
   :target: https://bestpractices.coreinfrastructure.org/en/projects/237

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
   introduction/faq

.. toctree::
   :caption: User Manual
   :maxdepth: 2
   :hidden:

   user-guide/debops-for-ansible
   user-guide/configuration
   user-guide/project-directories
   user-guide/scripts
   user-guide/custom-environment
   user-guide/playbooks
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
   meta/policy
   meta/philosophy
   meta/timeline
   meta/references
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
