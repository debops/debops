Other projects
==============

There are third-party projects that might be interesting for DebOps users,
either as source of inspiration or as an alternative configuration management
framework.

Third-party projects based on DebOps
------------------------------------

DebOps is very suitable to usage as a base for other IT infrastructure projects
based on Ansible. Here you can find some of them, that are available publicly.

`Drupsible`__
~~~~~~~~~~~~~

The Drupsible Project, managed by `Mariano Barcia`__, uses DebOps as a
deployment platform for Drupal applications.

.. __: https://www.drupal.org/project/drupsible
.. __: https://www.drupal.org/u/marianobarcia


`DebOps for WordPress`__
~~~~~~~~~~~~~~~~~~~~~~~~

The DebOps for WordPress project, maintained by `Carl Alexander`__, provides a
custom set of playbooks and roles that can be run on top of DebOps to deploy a
secure WordPress site.

.. __: https://github.com/carlalexander/debops-wordpress
.. __: https://carlalexander.ca/

`ypid-ansible-common`__
~~~~~~~~~~~~~~~~~~~~~~~

This is a git repository which bundles all the building blocks of config
management code, managed by `Robin 'ypid' Schneider`__. The building blocks are
included as git submodules. The repository can be thought of an alternative and
more generic (not limited to DebOps roles) form of distributing and updating
config management related assets (Ansible playbooks, roles, inventory presets
and more) in an end-to-end authenticated way. The repo also bundles a script to
review and pull down the latest changes of the git submodules.

.. __: https://github.com/ypid/ypid-ansible-common/
.. __: https://me.ypid.de/


Third-party projects similar to DebOps
--------------------------------------

Other people and teams are developing software projects which are similar to
DebOps either in scope or used software. You might find some of them
interesting, or if you don't want to use DebOps specifically, other projects
here might be more to your liking.

`Open Source Infrastructure`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a website that aggreagates information about, and links to, Open Source
infrastructure projects.

.. __: https://opensourceinfra.org/


`Sovereign`__
~~~~~~~~~~~~~

Sovereign is a set of Ansible playbooks that you can use to build and maintain
your own personal cloud based entirely on free software. It was one of the
original inspirations to create DebOps.

.. __: https://github.com/sovereign/sovereign


`Streisand`__
~~~~~~~~~~~~~

Streisand uses Ansible to set up a new server running L2TP/IPsec, OpenConnect,
OpenSSH, OpenVPN, Shadowsocks, sslh, Stunnel, a Tor bridge, and WireGuard. It
also generates custom instructions for all of these services. At the end of the
run you are given an HTML file with instructions that can be shared with
friends, family members, and fellow activists.

.. __: https://github.com/StreisandEffect/streisand


`gluster.org Infrastructure`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Gluster team maintains a `set of Ansible playbooks and roles`__ that power
the project's server infrastructure. The environment seems to be based on
CentOS and FreeBSD hosts, and has very detailed documentation.

.. __: https://gluster-infra-docs.readthedocs.io/
.. __: https://github.com/gluster/gluster.org_ansible_configuration


`ansible-lanparty`__
~~~~~~~~~~~~~~~~~~~~

Collection of integrated Ansible roles used to run LAN events. This repository
consists of roles that are purpose-built, lean and as easy as possible to
understand and modify. The roles are built to simplify and accelerate, not to
obscure.

.. __: https://github.com/ti-mo/ansible-lanparty


`FOSDEM Infrastructure`__
~~~~~~~~~~~~~~~~~~~~~~~~~

This repository contains a set of Ansible playbooks used to manage the video
recording infrastructure used at the `FOSDEM`__ conference.

.. __: https://github.com/FOSDEM/infrastructure
.. __: https://fosdem.org/


`Linux System Roles`__
~~~~~~~~~~~~~~~~~~~~~~

This is a small collection of Ansible roles focused on system administration,
available on GitHub and through Ansible Galaxy. Project is focused on Fedora
and Red Hat Enterprise Linux OS platforms.

.. __: https://linux-system-roles.github.io/


`Simple Ansible roles`__
~~~~~~~~~~~~~~~~~~~~~~~~

This is a set of interdependent Ansible roles maintained by Robert de Bock.
Roles work on multiple platforms, and are designed to integrate well using
"soft" dependencies on the playbook level, similarly to DebOps.

.. __: https://robertdebock.nl/


`LEAP Platform`__
~~~~~~~~~~~~~~~~~

The LEAP Platform is set of complementary packages and Puppet server recipes to
automate the maintenance of LEAP services in a hardened Debian environment. Its
goal is to make it as painless as possible for sysadmins to deploy and maintain
a service provider's infrastructure for secure communication. These recipes
define an abstract service provider. It is a set of Puppet modules designed to
work together to provide to sysadmins everything they need to manage a service
provider infrastructure that provides secure communication services.

.. __: https://github.com/leapcode/leap_platform


`System Integrity Management Platform`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The System Integrity Management Platform (SIMP) is a Puppet-based framework
designed around the concept that individuals and organizations should not need
to repeat the work of automating the basic components of their operating system
infrastructure.

.. __: https://github.com/NationalSecurityAgency/SIMP
