.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2015-2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


.. _apparmor__ref_dependent_use:

Using debops.apparmor from other roles
--------------------------------------

One common use case for ``debops.apparmor`` is to use it from other roles
to perform customizations to the AppArmor profiles shipped with various
packages and stored under the :file:`/etc/apparmor.d/` directory.

To do this, you can define the desired AppArmor modifications in your
:file:`defaults/main.yml` file. For example:

.. code-block:: yaml

   # Configuration for the ``debops.apparmor`` role, customizing the system
   # profile for slapd to work in a DebOps environment.
   slapd__apparmor__dependent_locals:

      - name: 'usr.sbin.slapd'
        options:

          - name: '/etc/pki/**'
            value: 'r'
            comment: 'Allow slapd access to DebOps PKI data'

And then in the playbook for this role, pass the
``slapd__apparmor__dependent_locals`` variable over to the ``debops.apparmor``
role:

.. code-block:: yaml

   ---

   - name: Manage OpenLDAP service
     ...
     hosts: [ 'debops_service_slapd']
     ...

     roles:

       - role: debops.apparmor
         tags: [ 'role::apparmor', 'skip::apparmor' ]
         apparmor__dependent_locals:
           - '{{ slapd__apparmor__dependent_locals }}'

There are three different variables which can be used to perform customizations
of the local AppArmor configuration via role dependencies
(:envvar:`apparmor__dependent_profiles`, :envvar:`apparmor__dependent_locals`
and :envvar:`apparmor__dependent_tunables`), see :ref:`apparmor__ref_profiles`,
:ref:`apparmor__ref_locals` and :ref:`apparmor__ref_tunables` for more details,
including the syntax of each variable.

Containers
----------

.. warning:: Note that AppArmor will not necessarily work properly inside
             containers and may cause issues with applications running in
             a containerized environment.

As an example, if you setup a :man:`systemd-nspawn(1)` container/guest and
AppArmor is enabled on the host system, the AppArmor profiles from the host
will be enforced inside the container, even though they are not configured
inside the container and tools such as :command:`aa-enabled` will, if executed
inside the container, report that AppArmor is *not* enabled.

Any changes to an AppArmor profile that interferes with the proper running of
a given service would therefore have to be performed on the host, rather than
the container/guest.

Your mileage might vary depending on the container technology used and its
level (and maturity) of support for AppArmor.

Example inventory
-----------------

``debops.apparmor`` is included by default in the :file:`common.yml` DebOps
playbook; you don't need to do anything to have it executed.

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.apparmor`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/apparmor.yml
   :language: yaml
   :lines: 1,5-

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::apparmor``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::apparmor:pkgs``
  Tasks related to the installation of packages.

``role::apparmor:grub``
  Tasks related to the configuration of kernel parameters via GRUB.

``role::apparmor:tunables``
  Tasks related to the management of AppArmor tunables (i.e. files under
  :file:`/etc/apparmor.d/tunables/`).

``role::apparmor:locals``
  Tasks related to the management of local modifications to AppArmor
  profiles (i.e. files under :file:`/etc/apparmor.d/local/`).

``role::apparmor:profiles``
  Tasks related to the management of whether profiles should be
  in the enabled/disabled/complain state.

``role::apparmor:service``
  Tasks related to starting/stopping/enabling/disabling the AppArmor
  service.

Other resources
---------------

List of other useful resources related to the ``debops.apparmor`` Ansible role:

- Manual pages: :man:`apparmor(7)`, :man:`apparmor.d(5)` and the manpages for
  the various ``aa-*`` utilities (like :man:`aa-status(8)`,
  :man:`aa-enabled(1)`, :man:`aa-disable(8)`, :man:`aa-complain(8)` and
  :man:`aa-enforce(8)`)

- The website of the `AppArmor Project`__

  .. __: https://apparmor.net/

- The `Ubuntu Wiki Page`__

  .. __: https://wiki.ubuntu.com/AppArmor

- The `Ubuntu Documentation`__

  .. __: https://help.ubuntu.com/community/AppArmor

- The `Debian Wiki Page`__, including the `HowToUse`__ subpage

  .. __: https://wiki.debian.org/AppArmor
  .. __: https://wiki.debian.org/AppArmor/HowToUse
