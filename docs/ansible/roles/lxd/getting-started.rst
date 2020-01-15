Getting started
===============

.. contents::
   :local:


LXD installation details
------------------------

At the time of writing this role (December 2019) LXD was not available natively
in Debian. `Packaging efforts are ongoing`__, however there's no telling if LXD
will be included in the next Debian release (Bullseye). The upstream developers
`suggest installation on Debian via Snap`__, however this brings its own set of
issues which are offtopic here.

.. __: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=768073
.. __: https://stgraber.org/2017/01/18/lxd-on-debian/

Instead, on Debian hosts the :ref:`debops.lxd` role utilizes the
:ref:`debops.golang` role to install the :command:`lxd` and :command:`lxc`
binaries from upstream :command:`git` repository by compiling them from source.
The role will configure the rest of the needed infrastructure
(:command:`systemd` unit files, :command:`logrotate` and :command:`sysctl`
configuration, POSIX groups, log directory, etc.) so that the LXD service
should work out of the box on Debian without the need of a Snap installation.
This also installs the old ``lxc`` APT package due to ``lxc-dev`` dependency,
but this shouldn't be an issue.

At the moment the role builds the latest release of LXD due to issue with
`missing raft dependency required for build`__. The issue is in the LXD
repository :file:`Makefile`, and was corrected in newer releases (3.15 onwards)
but the LTS release (3.0.x) still contains the faulty code. The plan is to
switch to the LTS release in the future, when one is available with a working
build instructions. The :ref:`debops.golang` configuration for building and
installing LXD is defined in the :envvar:`lxd__golang__dependent_packages`
variable.

.. __: https://github.com/lxc/lxd/issues/5875


Example inventory
-----------------

To enable LXD support on a host, it needs to be added to the
``[debops_service_lxd]`` Ansible inventory group:

.. code-block:: none

   [debops_all_hosts:children]
   lxd_hosts
   lxd_containers

   [debops_service_lxd:children]
   lxd_hosts

   [lxd_hosts]
   lxd-host    ansible_host=lxd-host.example.org

   [lxd_containers]
   webserver   ansible_host=webserver.example.org

By default, containers will use the ``lxdbr0`` bridge managed by the LXD
service, with their own internal ``lxd`` subdomain. You can use the
:ref:`debops.ifupdown` Ansible role to configure additional network bridges on
the LXD host, if you want to attach the containers to the public network.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.lxd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/lxd.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::lxd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::lxd:init``
  Re-apply the LXD preseeding configuration. Requires the
  :envvar:`lxd__init_preseed` variable to be set to ``True`` to be effective.


Other resources
---------------

List of other useful resources related to the ``debops.lxd`` Ansible role:

- Manual pages: :man:`lxc(7)`

- `LXD`__ page in Debian Wiki, with packaging information and current progress

  .. __: https://wiki.debian.org/LXD

- `LXD`__ page in Arch Linux Wiki

  .. __: https://wiki.archlinux.org/index.php/LXD

- `LXD`__ page in Ubuntu Wiki

  .. __: https://help.ubuntu.com/lts/serverguide/lxd.html

- `LXD 2.0 blog post series`__ written by Stéphane Graber

  .. __: https://stgraber.org/2016/03/11/lxd-2-0-blog-post-series-012/

- `LXD documentation page`__

  .. __: https://lxd.readthedocs.io/en/latest/
