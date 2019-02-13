Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

The role comes with a small set of APT packages, useful on pretty much any
Debian or Ubuntu host. Some of the packages are installed conditionally,
depending on different Ansible facts - for example, firmware packages are
installed on rack servers, which may contain network cards that require custom
firmware loaded by the kernel for proper operation.

The role is not meant to be used as a dependency of other roles, but you can use it
like that if you want to take advantage of the custom lookup template that uses
conditional package installation depending on installed operating system, its
release or available archive areas.

The difference between :ref:`debops.apt` and ``debops.apt_install`` Ansible roles
is that the former role is used to configure the APT package manager itself,
and latter just installs packages using APT package manager, depending on its
configuration.

Similar Ansible roles
---------------------

There are more comprehensive Ansible roles that install packages:

- `ypid.packages <https://github.com/ypid/ansible-packages>`_ - provides
  an advanced framework meant to allow installation of packages according to
  different host classes, with a large selection of packages. The role is focused
  on workstations, live systems and server environments.

Example inventory
-----------------

The ``debops.apt_install`` role is included by default in the :file:`common.yml`
DebOps playbook. You don't need to configure anything in the inventory to
enable it.

The role provides a set of default variables to specify what packages should be
installed on hosts, depending on the inventory level:

:envvar:`apt_install__packages`
  This variable should be used in
  :file:`ansible/inventory/group_vars/all/apt_install.yml` file and is meant to
  specify packages present on all hosts in the inventory.

:envvar:`apt_install__group_packages`
  This variable should be used in
  :file:`ansible/inventory/group_vars/<group-name>/apt_install.yml` files and is
  meant to contain packages that should be installed on hosts in different
  Ansible groups. Only one level of this variable is supported, so you should
  be careful about your inventory design. Or, you can use it as a master list
  that contains different per-group variables.

:envvar:`apt_install__host_packages`
  This variable should be used in
  :file:`ansible/inventory/host_vars/<hostname>/apt_install.yml` files and is meant
  to contain list of packages that should be installed on specific hosts.

Example playbook
----------------

``debops.apt_install`` is designed to be used from a playbook or a role as role
dependency. Here's an example configuration:

.. literalinclude:: ../../../../ansible/playbooks/service/apt_install.yml
   :language: yaml
