.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Configuration of preferred NTP servers
--------------------------------------

The :command:`systemd-timesyncd` service can use NTP servers provided via DHCP
or configured in the :command:`systemd-networkd` service to perform time
synchronization. If both cases are not defined, the service uses the ``NTP=``
and ``FallbackNTP=`` configuration options to find the preferred NTP servers.
By default, Debian installation defines a list of ``{0,3}.debian.pool.ntp.org``
NTP servers to use if no others are specified.

Users can define their own preferred NTP servers in the Ansible inventory:

.. code-block:: yaml

   ---
   # File: ansible/inventory/group_vars/all/timesyncd.yml

   # Needed to enable custom configuration deployment
   timesyncd__deploy_state: 'present'

   timesyncd__configuration:

     - name: 'NTP'
       value:
         - '0.pool.ntp.org'
         - '1.pool.ntp.org'
         - '2.pool.ntp.org'
         - '3.pool.ntp.org'
       state: 'present'

Timezone configuration is performed using the :ref:`debops.tzdata` Ansible
role, via the :envvar:`tzdata__timezone` variable.


Support for container environments
----------------------------------

The :file:`systemd-timesyncd.service` unit contains a conditional check for
a containerized environment (LXC, Docker, nspawn). Such environments don't have
complete control over system clock, therefore inside of them the time daemon
will not be started.


Support for other NTP services
------------------------------

The role checks if one of the APT packages listed in the
:envvar:`timesyncd__skip_packages` variable is already installed on the host
before doing any modifiaction on the system. If such package is detected, the
role will skip further tasks to avoid messing up existing configuration.


Example inventory
-----------------

The ``debops.timesyncd`` role is included by default in the ``common.yml`` DebOps
playbook; you don't need to add hosts to any Ansible groups to enable it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.timesyncd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/timesyncd.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::timesyncd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
