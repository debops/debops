Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

The ``unattended-upgrades`` package will be configured differently depending on
whether or not a DNS domain is configured on the host:

- if the ``ansible_domain`` variable is not empty (domain is present), only
  packages released through the security repository of a given OS distribution
  will be upgraded automatically. E-mail messages with the information about
  the unattended upgrades will be sent to the ``root@{{ ansible_domain }}``
  mail account.

- if the ``ansible_domain`` variable is empty, role assumes that the host is
  a workstation or a laptop (end-user device) and will configure the
  ``unattended-upgrades`` package to upgrade packages from all official
  repositories of the given OS distribution (main, updates, backports,
  security). The e-mail messages about the upgrades won't be generated.

You can control the above behaviour using :envvar:`unattended_upgrades__release` and
:envvar:`unattended_upgrades__mail_to` default variables.

Example inventory
-----------------

``debops.unattended_upgrades`` is included by default in the :file:`common.yml`
DebOps playbook; you don't need to do anything to have it installed.

If you want to disable the :program:`unattended-upgrades` service on a host or
set of hosts, you can do this by the setting variable:

.. code:: YAML

   unattended_upgrades__enabled: False

in Ansible's inventory. The ``unattended-upgrades`` package won't be installed.
If it is already present on the host, it won't be removed, but its
configuration will be reset to the distribution defaults.

Example playbook
----------------

Here's an example playbook that can be used to enable and manage the
``unattended-upgrades`` service on a set of hosts:

.. literalinclude:: ../../../../ansible/playbooks/service/unattended_upgrades.yml
   :language: yaml

Use as a role dependency
------------------------

The ``debops.unattended_upgrades`` Ansible role can be used by other Ansible
roles as a dependency, to allow unattended upgrades of packages from other
repositories than the official ones, or allow automatic blacklisting of
important packages by a given Ansible role. To do this, you can specify
``debops.unattended_upgrades`` role as a dependency and use two custom
variables:

:envvar:`unattended_upgrades__dependent_origins`
  This is a list of package origins which should be considered for unattended
  upgrades of packages.

:envvar:`unattended_upgrades__dependent_blacklist`
  This is a list of APT packages which should be exempt from unattended
  upgrades.

Configuration passed to the role through above variables will be stored on the
remote host in Ansible local facts. This prevents idempotency loops and allows
users to use ``debops.unattended_upgrades`` in different playbooks without
issues. This method works on the host with unattended upgrades disabled through
Ansible inventory.
